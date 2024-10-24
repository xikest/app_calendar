import pandas as pd
import feedparser
import json
import html
import re
from dateutil import parser
import logging


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

                        logging.debug(f"Processing feed '{feed_name}' from source '{src}' at URL: {url}")

                        # Parse the RSS feed
                        feed = feedparser.parse(url)
                        for entry in feed.entries:
                            entry_title = entry.get("title", '')
                            link = entry.get("link", '')
                            parsed_date = parser.parse(entry.get("published", pd.NaT)).strftime('%Y-%m-%d %H:%M:%S')
                            published_date = pd.to_datetime(parsed_date)
                            if src == 'rss':
                                if RssFeed.skip(feed_name, entry_title):
                                    continue
                            elif src == 'google':
                                link = link.replace('https://www.google.com/url?rct=j&sa=t&url=', '').split('&ct=ga&cd')[0]
                                entry_title = html.unescape(entry_title)
                                entry_title = re.sub(r'<[^>]*>', '', entry_title)
                            # if self.verbose == True:
                            #     print(category, entry_title, published_date, link)
                            df = pd.DataFrame([[entry_title, published_date, link]], columns=['title', 'published', 'link'])
                            
                            df_calendar = pd.concat([df_calendar, df], ignore_index=True)
            
            if convert_format_google:
                df_calendar = RssFeed.convert_to_google_calendar_format(df_calendar)
            if calendar_id in dict_feed:
                df_existing = dict_feed[calendar_id]
                df_updated = df_existing.combine_first(df_calendar)  
                dict_feed[calendar_id] = df_updated
            else:
                dict_feed[calendar_id] = df_calendar
            if self.verbose == True:
                try:
                    with pd.ExcelWriter("rss_calendar.xlsx", engine='openpyxl') as writer:
                        for calendar_id, df_calendar in dict_feed.items():
                            sheet_name = re.sub(r'[\\/*?[\]:]', '', str(calendar_id))[:31]
                            df_calendar.to_excel(writer, sheet_name=sheet_name, index=False)
                except Exception as e:
                    logging.error(e)
                    raise ValueError
        return dict_feed

    @staticmethod
    def skip(feed_name, title):
        feed_name = feed_name.lower()
        title = title.lower()
        
        if feed_name == "sony":
            skip_words = ["notice", "stock"]
            if any(word in title for word in skip_words):
                return True
        
        if feed_name in ["sony support", "sony official"]:
            if "bravia" not in title:
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