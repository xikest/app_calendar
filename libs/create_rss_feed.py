import pandas as pd
import feedparser
import json
import html
import re

class RssFeed:
    def __init__(self, json_path: str, verbose=False):
        self.verbose = verbose
        
        with open(json_path, 'r', encoding='utf-8') as file:
            self.profile_dict = json.load(file)

    def get_rss_info(self, convert_format_google: bool=True) -> dict:
        dict_feed = {}


        for category, details in self.profile_dict.items():
            df_calendar = pd.DataFrame(columns=['title', 'published', 'link'])
            calendar_id = details.get('calendar_id', '')
            contents = details.get('contents', {})
            for src, urls in contents.items():
                if isinstance(urls, dict):  # Check if `urls` is a dictionary of feed URLs
                    for feed_name, url in urls.items():
                        if self.verbose:
                            print(f"Processing feed '{feed_name}' from source '{src}' at URL: {url}")

                        # Parse the RSS feed
                        feed = feedparser.parse(url)
                        for entry in feed.entries:
                            entry_title = entry.get("title", '')
                            link = entry.get("link", '')
                            published = entry.get("published", pd.NaT)
                            # 초가 하나만 있을 경우 ":0"을 ":00"으로 수정
                            if isinstance(published, str) and published.endswith(":0"):
                                published += "0"
                            published_date = pd.to_datetime(published, errors='coerce')

                            if src == 'rss':
                                if RssFeed.skip(feed_name, entry_title):
                                    continue
                            elif src == 'google':
                                link = link.replace('https://www.google.com/url?rct=j&sa=t&url=', '').split('&ct=ga&cd')[0]
                                entry_title = html.unescape(entry_title)
                                entry_title = re.sub(r'<[^>]*>', '', entry_title)
                            if self.verbose:
                                print(category, entry_title, published_date, link)
                            # Add new row to the DataFrame
                            df = pd.DataFrame([[entry_title, published_date, link]], columns=['title', 'published', 'link'])
                            if not df.empty:    
                                df_calendar = pd.concat([df_calendar, df], ignore_index=True, copy=False)

                            
            if convert_format_google:
                df_calendar = RssFeed.convert_to_google_calendar_format(df_calendar)
            dict_feed[calendar_id] = df_calendar
        return dict_feed

    @staticmethod
    def skip(feed_name, title):
        if feed_name.lower() == "sony":
            skip_list = ["notice", "stock"]
            for skip_word in skip_list:
                if skip_word in title.lower():
                    return True
        return False

    @staticmethod
    def re_trim(text: str):
        return text.replace("[현지정보]", "").replace("[동향분석]", "").replace("(현지정보)", "")

    @staticmethod
    def convert_to_google_calendar_format(df):
        calendar_df = pd.DataFrame(columns=[
            'Subject', 'Start Date', 'Start Time', 'End Date', 'End Time', 'Description', 'Location', 'All Day Event',
        ])

        for index, row in df.iterrows():
            start_date = row['published'].strftime('%Y-%m-%d')
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
