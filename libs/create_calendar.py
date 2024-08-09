import pandas as pd
import time
from selenium.webdriver.common.by import By
from tools._scaper_scheme import Scraper


class ECONOMIC_CALENDAR(Scraper):
    def __init__(self, enable_headless=False, wait_time=1):
        super().__init__(enable_headless=enable_headless)
        self.wait_time = wait_time
        self.base_url = "https://datacenter.hankyung.com/economic-calendar"

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
            link = driver.find_element(By.XPATH, "//a[text()='이번 달']")
            self.web_driver.move_element_to_center(link)
            driver.execute_script("arguments[0].click();", link)
            time.sleep(self.wait_time)

            if headers is None:
                table = driver.find_element(By.XPATH, "//div[@class='tab_cnts']//table")
                headers = [th.text for th in table.find_elements(By.XPATH, ".//thead//th")]

            while RUN:
                paging_elements = driver.find_elements(By.XPATH,
                                                       "//div[@class='paging']//a[not(contains(@class, 'btn_'))]")
                page_numbers = [elem.text for elem in paging_elements if elem.text.isdigit()]
                # print(page_numbers)

                for page_number in page_numbers:
                    for cnt in range(5):
                        try:
                            driver.find_element(By.XPATH, f"//div[@class='paging']//a[text()='{page_number}']").click()
                            # print(f"page_number: {page_number}")
                            time.sleep(self.wait_time)
                            tbody = driver.find_element(By.XPATH, "//tbody[@id='tbody_data']")
                            for row in tbody.find_elements(By.XPATH, ".//tr"):
                                cells = row.find_elements(By.XPATH, ".//td | .//th")
                                rows.append([cell.text.strip() for cell in cells])
                            break
                        except:
                            print(f"page {page_number}, try {cnt+1}/5")
                            pass

                for cnt in range(2):
                    try:
                        next_page = driver.find_element(By.XPATH, f"//div[@class='paging']//a[text()='다음']")
                        next_page.click()
                        time.sleep(5)
                        break
                    except:
                        print(f"next, try {cnt+1}")
                        if cnt+1 == 2:
                            print("더 이상 다음 페이지가 없습니다.")
                            RUN = False
                            break
                        else:
                            pass
            df_calendar = pd.DataFrame(rows).drop(2, axis=1)
            df_calendar.columns = headers

            if convert_format_google:
                df_calendar = self._convert_to_google_calendar_format(df_calendar)
            return df_calendar
        except Exception as e:
            print(e)
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