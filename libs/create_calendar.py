import pandas as pd
import time
import json
import logging
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from libs._scaper_scheme import Scraper

class ECONOMIC_CALENDAR(Scraper):
    def __init__(self, json_path: str, enable_headless=True, wait_time=2, verbose=False):
        super().__init__(enable_headless=enable_headless)
        self.wait_time = wait_time
        self.base_url = "https://datacenter.hankyung.com/economic-calendar"
        self.verbose = verbose

        with open(json_path, 'r', encoding='utf-8') as file:
            profile_dict = json.load(file)
            self.calendar_id = profile_dict.get("calendar_id")

        # 로깅 설정
        logging.basicConfig(level=logging.DEBUG)  # DEBUG로 설정하면 모든 로그 메시지가 출력됨
        self.logger = logging.getLogger(__name__)

    def get_calendar_info(self, convert_format_google=True) -> pd.DataFrame:
        headers = None
        rows = []
        driver = self.web_driver.get_chrome()

        try:
            self._initialize_driver(driver)
            headers = self._extract_headers(driver)

            while True:
                rows.extend(self._extract_table_data(driver))
                
                # 페이지 번호 탐색 및 데이터 수집
                paging_elements = driver.find_elements(By.XPATH, "//div[@class='paging']//a[not(contains(@class, 'btn_'))]")
                page_numbers = [elem.text for elem in paging_elements if elem.text.isdigit()]
                self.logger.info(f"Found page numbers: {page_numbers}")

                for page_number in page_numbers:
                    for cnt in range(5):  # 5번까지 재시도 가능
                        try:
                            self.logger.info(f"Navigating to page {page_number}")
                            page = driver.find_element(By.XPATH, f"//div[@class='paging']//a[text()='{page_number}']")
                            page.click()
                            time.sleep(self.wait_time)
                            rows.extend(self._extract_table_data(driver))
                            break
                        except Exception as e:
                            self.logger.error(f"Error navigating to page {page_number}, attempt {cnt + 1}/5: {e}")
                            driver.save_screenshot(f"try_error_page{page_number}.png")
                            driver.quit()  # 드라이버 재시작
                            driver = self.web_driver.get_chrome()  
                            self._initialize_driver(driver)
                            
                            # 다음 페이지로 이동하는 부분
                            next_click = int(page_number) // 10
                            for _ in range(next_click):
                                next_page = driver.find_element(By.XPATH, "//div[@class='paging']//a[text()='다음']")
                                next_page.click()
                                time.sleep(self.wait_time)
                            continue

                # 마지막 페이지 탐색 후 종료
                if not self._navigate_pages(driver):
                    break

            df_calendar = pd.DataFrame(rows).drop(2, axis=1)
            df_calendar.columns = headers
            # if self.verbose:
            #     df_calendar.to_excel("e_calendar.xlsx")
            #     self.logger.info("Calendar data exported to e_calendar.xlsx.")
            if convert_format_google:
                df_calendar = self._convert_to_google_calendar_format(df_calendar)
                
            return {self.calendar_id: df_calendar}

        except Exception as e:
            self.logger.error(f"An error occurred while getting calendar info: {e}")
        finally:
            driver.quit()

    def _initialize_driver(self, driver):
        driver.get(self.base_url)
        driver.switch_to.frame(driver.find_element(By.XPATH, "//iframe[@src='https://asp.zeroin.co.kr/eco/hkd/wei/0601.php']"))
        self._select_all_countries(driver)
        self._click_this_month(driver)

    def _extract_headers(self, driver):
        table = driver.find_element(By.XPATH, "//div[@class='tab_cnts']//table")
        return [th.text for th in table.find_elements(By.XPATH, ".//thead//th")]

    def _extract_table_data(self, driver):
        rows = []
        table = driver.find_element(By.XPATH, "//tbody[@id='tbody_data']")
        for row in table.find_elements(By.XPATH, ".//tr"):
            cells = row.find_elements(By.XPATH, ".//td | .//th")
            rows.append([cell.text.strip() for cell in cells])
        return rows

    def _navigate_pages(self, driver):
        try:
            for attempt in range(2):
                try:
                    next_page = driver.find_element(By.XPATH, "//div[@class='paging']//a[text()='다음']")
                    if "disabled" in next_page.get_attribute("class"):
                        self.logger.info("No more pages to navigate.")
                        return False
                    next_page.click()
                    time.sleep(self.wait_time)
                    return True
                except NoSuchElementException:
                    self.logger.warning(f"Attempt {attempt + 1}: 'Next' button not found. Retrying...")
                    continue
            
            self.logger.error("Failed to navigate to the next page after 2 attempts.")
            return False
        except NoSuchElementException:
            self.logger.error("No more pages to navigate.")
            return False

    def _select_all_countries(self, driver):
        button = driver.find_element(By.XPATH, "//button[@class='btn_nation open_bodPop']")
        time.sleep(self.wait_time)
        button.click() 
        time.sleep(self.wait_time)
        driver.find_element(By.XPATH, "//input[@name='chk_all']").click()
        time.sleep(self.wait_time)
        driver.find_element(By.XPATH, "//button[@class='btn_popClose']").click()
        time.sleep(self.wait_time)

    def _click_this_month(self, driver):
        link = driver.find_element(By.XPATH, "//a[text()='이번 달']")
        self.web_driver.move_element_to_center(link)
        driver.execute_script("arguments[0].click();", link)
        time.sleep(self.wait_time)

    def _convert_to_google_calendar_format(self, df):
        df = df[df["중요도"] == "상"]

        calendar_df = pd.DataFrame(columns=[
            'Subject', 'Start Date', 'Start Time', 'End Date', 'End Time', 'Description', 'Location', 'All Day Event',
            'Reminder'
        ])

        for index, row in df.iterrows():
            date_str = row['날짜'].split('\n')[0]
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
            reminder = '10'

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
