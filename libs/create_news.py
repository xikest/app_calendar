import pandas as pd
import json
from bs4 import BeautifulSoup
from urllib.request import urlopen, Request
from datetime import datetime


class NewsFeed:
    def __init__(self, json_path: str = 'news.json', verbose=False):
        self.verbose = verbose
        with open(json_path, 'r', encoding='utf-8') as file:
            self.news_dict = json.load(file)

    def get_news_info(self, convert_format_google=True) -> dict:
        dict_news = {}
        # Extracting the details from the JSON
        df_all_news_info = pd.DataFrame()
        for category, news_source in self.news_dict.items():
            # Extracting the details from the JSON
            calendar_id = news_source['calendar_id']
            news_url = news_source['url']
            class_key = news_source['class_key']
            query_suffix = news_source.get("query_suffix")

            try:
                last_page = 1
                if query_suffix is not None:
                    last_page = int(query_suffix["suffix"])
                for page in range(last_page):
                    if query_suffix is not None:
                        paginated_url = f"{news_url}{query_suffix['query']}={page + 1}"
                    else:
                        paginated_url = news_url

                    if category == 'web':
                        scraper = WebScraper()
                        df_news_info = scraper.get_info(
                            url=paginated_url,
                            position_class = class_key['position'],
                            title_class=class_key['title'],
                            date_class=class_key['date'],
                        )
                        df_all_news_info = pd.concat([df_all_news_info, df_news_info], ignore_index=True)
            except Exception as e:
                if self.verbose == True:
                    print(f"Error processing {e}")
        if self.verbose == True:
            df_all_news_info.to_excel("df_all_news_info.xlsx")
        if convert_format_google:
            df_all_news_info = NewsFeed.convert_to_google_calendar_format(df_all_news_info)
        dict_news[calendar_id] = df_all_news_info

        return dict_news

    @staticmethod
    def convert_to_google_calendar_format(df):
        # Define the structure of the Google Calendar DataFrame
        calendar_df = pd.DataFrame(columns=[
            'Subject', 'Start Date', 'Start Time', 'End Date', 'End Time', 'Description', 'Location', 'All Day Event',
            # 'Reminder'
        ])

        for index, row in df.iterrows():
            # Ensure 'date' is a datetime object
            if isinstance(row['date'], str):
                try:
                    row['date'] = datetime.strptime(row['date'], '%Y-%m-%d')
                except ValueError:
                    row['date'] = datetime.now()

            # Extract date and time from the 'date' field
            start_date = row['date'].strftime('%Y-%m-%d')

            # Set the event subject and description
            subject = row['title']
            description = f"More information: {row['link']}"

            # Set the end date same as start date for all-day events
            end_date = start_date

            # No specific location, all-day event is False, reminder set to 1440 minutes (1 day before)
            location = ''
            all_day_event = 'True'

            # Create a new event entry
            new_event = pd.DataFrame([{
                'Subject': subject,
                'Start Date': start_date,
                'Start Time': '',
                'End Date': end_date,
                'End Time': '',
                'Description': description,
                'Location': location,
                'All Day Event': all_day_event,
            }])

            # Add the new event to the calendar DataFrame
            calendar_df = pd.concat([calendar_df, new_event], ignore_index=True)

        return calendar_df


class WebScraper:
    def __init__(self, base_url=None):
        self.base_url = base_url

    def get_info(self, url, position_class:str, title_class: str, date_class: str) -> pd.DataFrame:
        full_url = self.base_url + url if self.base_url else url
        request = Request(full_url, headers={'User-Agent': 'Mozilla/5.0'})
        response = urlopen(request).read()
        content = response
        soup = BeautifulSoup(content, 'html.parser')

        # Extracting the title, link, and date
        content_elements = soup.find_all('div', class_=position_class)
        df_news_info = pd.DataFrame()
        for content in content_elements:
            try:
                title_element = content.find('h2', class_=title_class)
                title = title_element.get_text(strip=True)
                link = title_element.find('a')['href']
                date_element = content.find('span', class_=date_class)
                date_text = date_element.get_text(strip=True)
            except Exception as e:
                continue
            if not link:
                continue  # Skip if no link is found
            title = WebScraper.re_trim(title)
            try:
                date = pd.to_datetime(date_text.split(" ")[0])  # 2024.07.06 07:03
            except:
                date = datetime.now()
            df_news_info = pd.concat([df_news_info, pd.DataFrame(data=[[title, link, date]])])
        df_news_info.columns = ['title', 'link', 'date']
        return df_news_info
    @staticmethod
    def re_trim(text: str) -> str:
        return text.replace("[김현석의 월스트리트나우]", "").replace("[데스크 칼럼]", "")
