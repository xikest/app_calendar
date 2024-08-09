from googleapiclient.discovery import build
import pandas as pd
import os
import pickle

class UPLOADER:
    @staticmethod
    def authenticate(token_path:str='token.pickle'):
        """Authenticate and return a Google Calendar service object."""
        creds = None
        if os.path.exists(token_path):
            with open(token_path, 'rb') as token:
                creds = pickle.load(token)
        service = build('calendar', 'v3', credentials=creds)
        return service
    @staticmethod
    def upload_events(service, csv_file, calendar_id:str = '00f7efaef0c7f43b99139b9a62b682bd3307b962aa36e015069c8aaae10aebaa@group.calendar.google.com'):

        if isinstance(csv_file, pd.DataFrame):
            df=csv_file
        elif isinstance(csv_file, str):
            if not os.path.exists(csv_file):
                print(f"Error: CSV file '{csv_file}' not found.")
                return
            df = pd.read_csv(csv_file)
        else:
            raise ValueError("no calendar data")

        for index, row in df.iterrows():
            event = {
                'summary': row['Subject'],
                'location': row['Location'],
                'description': row['Description'],
                'start': {
                    'dateTime': f"{row['Start Date']}T{row['Start Time']}:00",
                    'timeZone': 'Asia/Seoul',
                },
                'end': {
                    'dateTime': f"{row['End Date']}T{row['End Time']}:00",
                    'timeZone': 'Asia/Seoul',
                },
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'popup', 'minutes': row['Reminder']}
                    ],
                },
            }

            created_event = service.events().insert(calendarId=calendar_id, body=event).execute()
            print(f"Event created: {created_event.get('htmlLink')}")
        print("finish uploading")
        return None
