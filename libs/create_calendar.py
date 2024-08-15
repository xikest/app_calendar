import pandas as pd
import time
import json
from selenium.webdriver.common.by import By
from tools._scaper_scheme import Scraper




# class ECONOMIC_CALENDAR(Scraper):
#     def __init__(self, json_path:str, enable_headless=False, wait_time=2, verbose=False):

#         super().__init__(enable_headless=enable_headless)
#         self.wait_time = wait_time
#         self.base_url = "https://datacenter.hankyung.com/economic-calendar"
#         self.verbose = verbose
#         with open(json_path, 'r', encoding='utf-8') as file:
#             prifile_dict = json.load(file)
#             self.calendar_id = prifile_dict.get("calendar_id")

#     def get_calendar_info(self, convert_format_google=True) -> dict:
#         headers = None
#         rows = []
#         driver = self.web_driver.get_chrome()

#         try:
#             driver.get(self.base_url)
#             iframe = self._find_element_with_retry(driver, By.XPATH, "//iframe[@src='https://asp.zeroin.co.kr/eco/hkd/wei/0601.php']")
#             driver.switch_to.frame(iframe)

#             self._select_all_countries(driver)
#             self._click_this_month(driver)
            
#             headers, rows = self._scrape_table_data(driver, headers)

#             while True:
#                 if not self._click_next_page(driver):
#                     break

#                 _, new_rows = self._scrape_table_data(driver, headers)
#                 rows.extend(new_rows)

#             df_calendar = pd.DataFrame(rows).drop(2, axis=1)
#             df_calendar.columns = headers

#             if convert_format_google:
#                 df_calendar = self._convert_to_google_calendar_format(df_calendar)
#             return {self.calendar_id: df_calendar}

#         except Exception as e:
#             if self.verbose:
#                 print(f"Error: {e}")
#             return pd.DataFrame()

#         finally:
#             driver.quit()

#     def _find_element_with_retry(self, driver, by, value, retries=3):
#         for attempt in range(retries):
#             try:
#                 return driver.find_element(by, value)
#             except Exception as e:
#                 if self.verbose:
#                     print(f"Attempt {attempt + 1}/{retries} failed: {e}")
#                 time.sleep(self.wait_time)
#         raise Exception(f"Element {value} not found after {retries} attempts")

#     def _select_all_countries(self, driver):
#         try:
#             country_selection = self._find_element_with_retry(driver, By.XPATH, "//button[@class='btn_nation open_bodPop']")
#             country_selection.click()
#             time.sleep(self.wait_time)

#             chk_all = self._find_element_with_retry(driver, By.XPATH, "//input[@name='chk_all']")
#             chk_all.click()
#             time.sleep(self.wait_time)

#             confirm_button = self._find_element_with_retry(driver, By.XPATH, "//button[@class='btn_popClose']")
#             confirm_button.click()
#             time.sleep(self.wait_time)
#         except Exception as e:
#             if self.verbose:
#                 print(f"Failed to select all countries: {e}")

#     def _click_this_month(self, driver):
#         try:
#             link = self._find_element_with_retry(driver, By.XPATH, "//a[text()='이번 달']")
#             self.web_driver.move_element_to_center(link)
#             driver.execute_script("arguments[0].click();", link)
#             time.sleep(self.wait_time)
#         except Exception as e:
#             if self.verbose:
#                 print(f"Failed to click 'This Month': {e}")

#     def _scrape_table_data(self, driver, headers):
#         rows = []
#         try:
#             table = self._find_element_with_retry(driver, By.XPATH, "//div[@class='tab_cnts']//table")
#             if headers is None:
#                 headers = [th.text for th in table.find_elements(By.XPATH, ".//thead//th")]

#             table_body = driver.find_element(By.XPATH, "//tbody[@id='tbody_data']")
#             for row in table_body.find_elements(By.XPATH, ".//tr"):
#                 cells = row.find_elements(By.XPATH, ".//td | .//th")
#                 rows.append([cell.text.strip() for cell in cells])

#         except Exception as e:
#             if self.verbose:
#                 print(f"Failed to scrape table data: {e}")
        
#         return headers, rows

#     def _click_next_page(self, driver):
#         try:
#             next_page = driver.find_element(By.XPATH, "//div[@class='paging']//a[text()='다음']")
#             next_page.click()
#             time.sleep(5)
#             return True
#         except:
#             if self.verbose:
#                 print("No more pages to navigate.")
#             return False

class ECONOMIC_CALENDAR(Scraper):
    def __init__(self, json_path:str, enable_headless=False, wait_time=2, verbose=False):
        super().__init__(enable_headless=enable_headless)
        self.wait_time = wait_time
        self.base_url = "https://datacenter.hankyung.com/economic-calendar"
        self.verbose = verbose
        
        with open(json_path, 'r', encoding='utf-8') as file:
            prifile_dict = json.load(file)
            self.calendar_id = prifile_dict.get("calendar_id")

    def get_calendar_info(self, convert_format_google=True) -> pd.DataFrame:
        headers = None
        RUN = True
        rows = []

        # 웹 드라이버 가져오기
        driver = self.web_driver.get_chrome()
        try:
            # 웹 페이지 요청
            driver.get(self.base_url)
            iframe = driver.find_element(By.XPATH, "//iframe[@src='https://asp.zeroin.co.kr/eco/hkd/wei/0601.php']")
            driver.switch_to.frame(iframe)

            time.sleep(self.wait_time)
            country_selection = driver.find_element(By.XPATH, "//button[@class='btn_nation open_bodPop']")
            country_selection.click()

            time.sleep(self.wait_time)
            chk_all = driver.find_element(By.XPATH, "//input[@name='chk_all']")
            chk_all.click()

            time.sleep(self.wait_time)
            confirm_button = driver.find_element(By.XPATH, "//button[@class='btn_popClose']")
            confirm_button.click()

            time.sleep(self.wait_time)
            link = driver.find_element(By.XPATH, "//a[text()='이번 달']")
            self.web_driver.move_element_to_center(link)
            driver.execute_script("arguments[0].click();", link)

            time.sleep(self.wait_time)
            if headers is None:
                table = driver.find_element(By.XPATH, "//div[@class='tab_cnts']//table")
                headers = [th.text for th in table.find_elements(By.XPATH, ".//thead//th")]

            # time.sleep(5)
            while RUN:

                time.sleep(self.wait_time)
                paging_elements = driver.find_elements(By.XPATH,
                                                       "//div[@class='paging']//a[not(contains(@class, 'btn_'))]")



                table = driver.find_element(By.XPATH, "//tbody[@id='tbody_data']")
                for row in table.find_elements(By.XPATH, ".//tr"):
                    cells = row.find_elements(By.XPATH, ".//td | .//th")
                    rows.append([cell.text.strip() for cell in cells])

       

                page_numbers = [elem.text for elem in paging_elements if elem.text.isdigit()]
                if self.verbose:
                    print(page_numbers)
                for page_number in page_numbers[1:]:
                    for cnt in range(5):
                        try:
                            if self.verbose:
                                print(f"page_number: {page_number}")

                            page = driver.find_element(By.XPATH, f"//div[@class='paging']//a[text()='{page_number}']")
                            page.click()
                            time.sleep(5)

                            table = driver.find_element(By.XPATH, "//tbody[@id='tbody_data']")
                            for row in table.find_elements(By.XPATH, ".//tr"):
                                cells = row.find_elements(By.XPATH, ".//td | .//th")
                                rows.append([cell.text.strip() for cell in cells])
                            break
                        except Exception as e:
                            if self.verbose:
                                print(f"page {page_number}, try {cnt + 1}/5")
                                driver.save_screenshot("try error.png")
                                print(e)
                            driver.quit()
                                
                            driver = self.web_driver.get_chrome()
                            driver.get(self.base_url)
                            iframe = driver.find_element(By.XPATH, "//iframe[@src='https://asp.zeroin.co.kr/eco/hkd/wei/0601.php']")
                            driver.switch_to.frame(iframe)

                            time.sleep(self.wait_time)
                            country_selection = driver.find_element(By.XPATH, "//button[@class='btn_nation open_bodPop']")
                            country_selection.click()

                            time.sleep(self.wait_time)
                            chk_all = driver.find_element(By.XPATH, "//input[@name='chk_all']")
                            chk_all.click()

                            time.sleep(self.wait_time)
                            confirm_button = driver.find_element(By.XPATH, "//button[@class='btn_popClose']")
                            confirm_button.click()

                            time.sleep(self.wait_time)
                            link = driver.find_element(By.XPATH, "//a[text()='이번 달']")
                            self.web_driver.move_element_to_center(link)
                            driver.execute_script("arguments[0].click();", link)   
                            
                            next_click = page_number/10
                            for click in next_click:
                                next_page = driver.find_element(By.XPATH, f"//div[@class='paging']//a[text()='다음']")
                                next_page.click()
                                time.sleep(5)
                            

                            table = driver.find_element(By.XPATH, "//tbody[@id='tbody_data']")
                            for row in table.find_elements(By.XPATH, ".//tr"):
                                cells = row.find_elements(By.XPATH, ".//td | .//th")
                                rows.append([cell.text.strip() for cell in cells])
                                            
                            pass

                for cnt in range(2):
                    try:
                        next_page = driver.find_element(By.XPATH, f"//div[@class='paging']//a[text()='다음']")
                        next_page.click()
                        time.sleep(5)
                        break
                    except:
                        driver.refresh()
                        time.sleep(self.wait_time)
                        if self.verbose:
                            driver.save_screenshot("next error.png")
                        if cnt + 1 == 2:
                            if self.verbose:
                                print("더 이상 다음 페이지가 없습니다.")
                                driver.save_screenshot("finish.png")
                            RUN = False
                            break

            df_calendar = pd.DataFrame(rows).drop(2, axis=1)
            df_calendar.columns = headers

            if convert_format_google:
                df_calendar = self._convert_to_google_calendar_format(df_calendar)
            return {self.calendar_id: df_calendar}
        except Exception as e:
            if self.verbose:
                print(e)
            pass
        finally:
            driver.quit()

    def _convert_to_google_calendar_format(self, df):
        # 구글 캘린더 업로드에 필요한 컬럼 생성
        df = df[df["중요도"] == "상"]

        calendar_df = pd.DataFrame(columns=[
            'Subject', 'Start Date', 'Start Time', 'End Date', 'End Time', 'Description', 'Location', 'All Day Event',
            'Reminder'
        ])

        for index, row in df.iterrows():
            # 날짜와 시간을 합쳐서 시작 날짜와 시작 시간 생성
            date_str = row['날짜'].split('\n')[0]  # '08.31'
            start_date = pd.to_datetime(date_str, format='%m.%d').strftime('2024-%m-%d')  # '2024-08-31' 형식으로 변환
            start_time = row['시간']  # '10:30'

            # 이벤트 제목 생성
            subject = f"{row['국가']} - {row['경제지표']}"

            # 이벤트 설명 생성
            description = f"실제: {row['실제']}, 예상: {row['예상']}, 이전: {row['이전']}, 중요도: {row['중요도']}"

            # 종료 날짜와 시간 (시작 시간에 1시간 더하기)
            start_datetime = pd.to_datetime(f"{start_date} {start_time}")
            end_datetime = start_datetime + pd.Timedelta(hours=1)
            end_date = end_datetime.strftime('%Y-%m-%d')
            end_time = end_datetime.strftime('%H:%M')

            # 위치와 알림 설정
            location = row['국가']
            all_day_event = 'False'
            reminder = '1440'  # 15분 전 알림 24 * 60min

            # 새로운 이벤트 데이터 추가
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
