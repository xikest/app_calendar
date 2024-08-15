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




    def get_rss_info(self, convert_format_google:bool=True) -> dict:
        dict_feed = {}
        title = "title"
        published = "published"
        link = "link"
        df_feed = pd.DataFrame(columns=[title, published, link])

        for category, details in self.profile_dict.items():
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
                            published_date = pd.to_datetime(entry.get("published", pd.NaT))
                            link = entry.get("link", '')
                            title = entry.get("title", '')

                            if src == 'rss':
                                if RssFeed.skip(feed_name, title):
                                    continue
                            elif src == 'google':
                                link = link.replace('https://www.google.com/url?rct=j&sa=t&url=', '').split('&ct=ga&cd')[0]
                                title = html.unescape(title)
                                title = re.sub(r'<[^>]*>', '', title)

                            if self.verbose:
                                print(category, title, published_date, link)

                            # Add new row to the DataFrame
                            df = pd.DataFrame([[title, published_date, link]], columns=[title, published, link])
                            df_feed = pd.concat([df_feed, df], ignore_index=True)
            if convert_format_google:
                df_feed = RssFeed.convert_to_google_calendar_format(df_feed)
            
            dict_feed[calendar_id] = df_feed
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
        # Define the structure of the Google Calendar DataFrame
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