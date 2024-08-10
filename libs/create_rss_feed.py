import pandas as pd
import feedparser
import json


class RSS_FEED():
    def __init__(self):
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
        df_calendar['title'] = df_calendar['title'].str.replace("[현지정보]", "").str.replace("[동향분석]", "")
        if convert_format_google:
            df_calendar = self._convert_to_google_calendar_format(df_calendar)
        return df_calendar

    def _convert_to_google_calendar_format(self, df):
        # Define the structure of the Google Calendar DataFrame
        calendar_df = pd.DataFrame(columns=[
            'Subject', 'Start Date', 'Start Time', 'End Date', 'End Time', 'Description', 'Location', 'All Day Event',
            # 'Reminder'
        ])

        for index, row in df.iterrows():
            # Extract date and time from the 'published' field
            start_date = row['published'].strftime('%Y-%m-%d')

            # Set the event subject and description
            subject = row['title']
            description = f"More information: {row['link']}"

            # Set the end time as 1 hour after the start time
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
