import pandas as pd
import time
import json
import logging
from bs4 import BeautifulSoup
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from libs._scaper_scheme import Scraper

class ECONOMIC_CALENDAR(Scraper):
    def __init__(self, json_path: str, enable_headless=True, wait_time=2):
        super().__init__(enable_headless=enable_headless)
        self.wait_time = wait_time
        self.base_url = "https://datacenter.hankyung.com/economic-calendar"

        with open(json_path, 'r', encoding='utf-8') as file:
            prifile_dict = json.load(file)
            self.calendar_id = prifile_dict.get("calendar_id")

    def get_calendar_info(self, convert_format_google=True) -> pd.DataFrame:
        headers = None
        rows = []
        operating = True
        driver = self.web_driver.get_chrome()

        try:
            self._initialize_driver(driver)
            # self._select_all_countries(driver)
            # self._click_this_month(driver)
            headers = self._extract_headers(driver)
            loop_cnt = 1
            while operating:
                
                for try_cnt in range(5):  
                    try: 
                        paging_div = driver.find_element(By.CLASS_NAME, "paging")
                        id_links = paging_div.find_elements(By.XPATH, ".//a[@id]")
                        id_list = [link.get_attribute("id") for link in id_links]
                        break
                    except:
                        continue
                logging.debug("Extracted IDs: %s", id_list)
                rows.extend(self._extract_table_data(driver))   #처음페이지
                for id in id_list:
                    for try_cnt in range(5):
                        try: 
                            logging.info(f"Clicking on page: {id}")
                            nextpage = driver.find_element(By.XPATH, f'//*[@id="{id}"]')
                            nextpage.click()
                            time.sleep(10) # wating page loading
                            break
                        except:
                            if try_cnt+1 == 5: logging.error(f"page{id} click error")
                            continue
                    try:
                        rows.extend(self._extract_table_data(driver))  
                        # driver.save_screenshot(f"page{id}.png") 
                    except Exception as e:
                        logging.error(e)
                        
                for try_cnt in range(5):    
                    try:
                        next_btn = driver.find_element(By.CLASS_NAME, "btn_next")
                        next_btn.click()
                        logging.debug(f"Clicking on next page")
                        break
                    except Exception as e:
                        if try_cnt+1 == 5:
                                operating = False
                        continue
                loop_cnt +=10               

            df_calendar = pd.DataFrame(rows).drop(2, axis=1)
            df_calendar.columns = headers
            if convert_format_google:
                df_calendar = self._convert_to_google_calendar_format(df_calendar)
                
            return {self.calendar_id: df_calendar}

        except Exception as e:
            logging.error(f"An error occurred: {e}")
        finally:
            driver.quit()

    def _initialize_driver(self, driver):
        driver.get(self.base_url)
        driver.switch_to.frame(driver.find_element(By.XPATH, "//iframe[@src='https://asp.zeroin.co.kr/eco/hkd/wei/0601.php']"))


    def _extract_headers(self, driver):
        table = driver.find_element(By.XPATH, "//div[@class='tab_cnts']//table")
        return [th.text for th in table.find_elements(By.XPATH, ".//thead//th")]

    def _extract_table_data(self, driver):
        for _ in range(5):
            try:
                board_list = driver.find_element(By.XPATH, '/html/body/div[2]/div/table')
                sub_html = board_list.get_attribute('innerHTML')
                soup = BeautifulSoup(sub_html, 'html.parser')
                rows = soup.select('tr')  
                table_data = []
                for row in rows:
                    cells = row.find_all(['td', 'th'])  
                    row_data = [cell.get_text(strip=True) for cell in cells] 
                    if row_data:
                        table_data.append(row_data)
                for data in table_data:
                    logging.debug(data)
                return table_data   
            except:
                continue


    def _select_all_countries(self, driver):
        for _ in range(5):
            try:
                popup_btn = driver.find_element(By.XPATH, "//button[@class='btn_nation open_bodPop']")
                popup_btn.click() 
                break
            except:
                continue
            
        for _ in range(5):
            try:
                check_all= driver.find_element(By.XPATH, "//input[@name='chk_all']")
                check_all.click()
                break
            except:
                continue
            
        for _ in range(5):
            try:
                close_btn = driver.find_element(By.XPATH, "//button[@class='btn_popClose']")
                close_btn.click()
                break
            except:
                continue
        logging.info("selected all countries")

    def _click_this_month(self, driver):
        for _ in range(5):
            try:
                link = driver.find_element(By.XPATH, "//a[text()='이번 달']")
                # self.web_driver.move_element_to_center(link)
                driver.execute_script("arguments[0].click();", link)
                logging.info("selected this month")
                break
            except:
                continue


    def _convert_to_google_calendar_format(self, df):
        df = df[df["중요도"] == "상"]

        calendar_df = pd.DataFrame(columns=[
            'Subject', 'Start Date', 'Start Time', 'End Date', 'End Time', 'Description', 'Location', 'All Day Event',
            'Reminder'
        ])

        for index, row in df.iterrows():
            date_str = row['날짜'].split('(')[0]
            start_date = pd.to_datetime(date_str, format='%m.%d').strftime('2024-%m-%d')
            start_time = row['시간']

            subject = f"{row['국가']} - {row['경제지표']}"

            description = f"실제: {row['실제']}, 예상: {row['예상']}, 이전: {row['이전']}, 중요도: {row['중요도']}"

            start_datetime = pd.to_datetime(f"{start_date} {start_time}")
            end_datetime = start_datetime + pd.Timedelta(hours=1)
            end_date = end_datetime.strftime('%Y-%m-%d')
            end_time = end_datetime.strftime('%H:%M')

            location = row['국가']
            all_day_event = 'False'
            reminder = '' ## 리마인더 안함

            new_event = pd.DataFrame([{
                'Subject': subject,
                'Start Date': start_date,
                'Start Time': start_time,
                'End Date': end_date,
                'End Time': end_time,
                'Description': description,
                'Location': location,
                'All Day Event': all_day_event,
                'Reminder': reminder
            }])

            calendar_df = pd.concat([calendar_df, new_event], ignore_index=True)

        return calendar_df