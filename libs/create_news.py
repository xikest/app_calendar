import pandas as pd
import json
from bs4 import BeautifulSoup
from urllib.request import urlopen, Request
from datetime import datetime
import logging

class NewsFeed:
    def __init__(self, json_path: str = 'news.json', verbose=False):
        self.verbose = verbose
        with open(json_path, 'r', encoding='utf-8') as file:
            self.news_dict = json.load(file)

    def get_news_info(self, convert_format_google=True) -> dict:
        dict_news = {}
        df_all_news_info = pd.DataFrame()

        for category, news_source in self.news_dict.items():
            calendar_id = news_source['calendar_id']
            news_url = news_source['url']
            class_key = news_source['class_key']
            query_suffix = news_source.get("query_suffix")

            try:
                last_page = int(query_suffix["suffix"]) if query_suffix else 1
                for page in range(last_page):
                    paginated_url = f"{news_url}{query_suffix['query']}={page + 1}" if query_suffix else news_url

                    if category == 'web':
                        scraper = WebScraper()
                        df_news_info = scraper.get_info(
                            url=paginated_url,
                            position_class=class_key['position'],
                            title_class=class_key['title'],
                            date_class=class_key['date'],
                        )
                        df_all_news_info = pd.concat([df_all_news_info, df_news_info], ignore_index=True)
            except Exception as e:
                logging.error(f"Error processing news for category '{category}': {e}", exc_info=True)
        
        if self.verbose:
            df_all_news_info.to_excel("df_all_news_info.xlsx")
        
        if convert_format_google:
            df_all_news_info = NewsFeed.convert_to_google_calendar_format(df_all_news_info)
        
        dict_news[calendar_id] = df_all_news_info
        return dict_news

    @staticmethod
    def convert_to_google_calendar_format(df):
        calendar_df = pd.DataFrame(columns=[
            'Subject', 'Start Date', 'Start Time', 'End Date', 'End Time', 'Description', 'Location', 'All Day Event',
        ])

        for index, row in df.iterrows():
            if isinstance(row['date'], str):
                try:
                    row['date'] = datetime.strptime(row['date'], '%Y-%m-%d')
                except ValueError:
                    row['date'] = datetime.now()

            start_date = row['date'].strftime('%Y-%m-%d')
            subject = row['title']
            description = f"More information: {row['link']}"
            end_date = start_date
            location = ''
            all_day_event = 'True'

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

            calendar_df = pd.concat([calendar_df, new_event], ignore_index=True)

        return calendar_df


class WebScraper:
    def __init__(self, base_url=None):
        self.base_url = base_url

    def get_info(self, url, position_class: str, title_class: str, date_class: str) -> pd.DataFrame:
        full_url = self.base_url + url if self.base_url else url
        request = Request(full_url, headers={'User-Agent': 'Mozilla/5.0'})

        try:
            response = urlopen(request).read()
            content = response
            soup = BeautifulSoup(content, 'html.parser')

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
                    logging.warning(f"Error extracting news item: {e}")
                    continue
                
                if not link:
                    logging.warning("No link found, skipping this news item.")
                    continue
                
                title = WebScraper.re_trim(title)
                
                try:
                    date = pd.to_datetime(date_text.split(" ")[0])
                except Exception as e:
                    logging.warning(f"Error parsing date '{date_text}': {e}")
                    date = datetime.now()
                logging.debug(f"{title}, {link}, {date}")
                df_news_info = pd.concat([df_news_info, pd.DataFrame(data=[[title, link, date]])])

            df_news_info.columns = ['title', 'link', 'date']
            return df_news_info
        
        except Exception as e:
            logging.error(f"Error fetching news from URL '{full_url}': {e}", exc_info=True)
            return pd.DataFrame(columns=['title', 'link', 'date'])

    @staticmethod
    def re_trim(text: str) -> str:
        return text.replace("[김현석의 월스트리트나우]", "").replace("[데스크 칼럼]", "")
