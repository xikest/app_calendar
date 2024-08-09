import pandas as pd
import feedparser
import json


class RSS_FEED():
    def __init__(self):
        # self.rss_dict = {
        #     '뉴욕사무소': 'https://www.bok.or.kr/portal/bbs/P0002017/news.rss?menuNo=200365',
        #     '워싱턴주재원': 'https://www.bok.or.kr/portal/bbs/P0002223/news.rss?menuNo=200082',
        #     '프랑크푸르트사무소': 'https://www.bok.or.kr/portal/bbs/P0002226/news.rss?menuNo=200083',
        #     '동경사무소': 'https://www.bok.or.kr/portal/bbs/P0002229/news.rss?menuNo=200084',
        #     '런던사무소': 'https://www.bok.or.kr/portal/bbs/P0002231/news.rss?menuNo=200085',
        #     '북경사무소': 'https://www.bok.or.kr/portal/bbs/P0002232/news.rss?menuNo=200086',
        #     '홍콩주재원': 'https://www.bok.or.kr/portal/bbs/P0002233/news.rss?menuNo=200087',
        #     '상해주재원': 'https://www.bok.or.kr/portal/bbs/P0002234/news.rss?menuNo=200088'
        # }


        # JSON 파일을 읽어오기
        with open('rss.json', 'r', encoding='utf-8') as file:
            self.rss_dict = json.load(file)

    def get_rss_info(self, convert_format_google=True) -> pd.DataFrame:
        df_calendar = pd.DataFrame(columns=["title", "published", "link"])

        for src, url in self.rss_dict.items():
            for feed in feedparser.parse(url).entries:
                published = pd.to_datetime(feed.get("published"))
                link = feed.get("link")
                title = feed.get("title")
                df = pd.DataFrame([[title, published, link]], columns=["title", "published", "link"])
                df_calendar = pd.concat([df_calendar, df], ignore_index=True)

        if convert_format_google:
            df_calendar = self._convert_to_google_calendar_format(df_calendar)
        return df_calendar

    def _convert_to_google_calendar_format(self, df):
        # Define the structure of the Google Calendar DataFrame
        calendar_df = pd.DataFrame(columns=[
            'Subject', 'Start Date', 'Start Time', 'End Date', 'End Time', 'Description', 'Location', 'All Day Event',
            'Reminder'
        ])

        for index, row in df.iterrows():
            # Extract date and time from the 'published' field
            start_date = row['published'].strftime('%Y-%m-%d')
            start_time = row['published'].strftime('%H:%M')

            # Set the event subject and description
            subject = row['title']
            description = f"More information: {row['link']}"

            # Set the end time as 1 hour after the start time
            start_datetime = row['published']
            end_datetime = start_datetime + pd.Timedelta(hours=1)
            end_date = end_datetime.strftime('%Y-%m-%d')
            end_time = end_datetime.strftime('%H:%M')

            # No specific location, all-day event is False, reminder set to 1440 minutes (1 day before)
            location = 'Online'
            all_day_event = 'True'
            reminder = ''

            # Create a new event entry
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

            # Add the new event to the calendar DataFrame
            calendar_df = pd.concat([calendar_df, new_event], ignore_index=True)

        return calendar_df