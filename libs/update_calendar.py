from googleapiclient.discovery import build
import pandas as pd
import os
import pickle


class UPDATER:
    @staticmethod
    def authenticate(token_path: str = 'token.pickle'):
        """Authenticate and return a Google Calendar service object."""
        creds = None
        if os.path.exists(token_path):
            with open(token_path, 'rb') as token:
                creds = pickle.load(token)
        service = build('calendar', 'v3', credentials=creds)
        return service

    @staticmethod
    def update_events(service, csv_file,
                      calendar_id: str = '00f7efaef0c7f43b99139b9a62b682bd3307b962aa36e015069c8aaae10aebaa@group.calendar.google.com'):

        if isinstance(csv_file, pd.DataFrame):
            df = csv_file
        elif isinstance(csv_file, str):
            if not os.path.exists(csv_file):
                print(f"Error: CSV file '{csv_file}' not found.")
                return
            df = pd.read_csv(csv_file)
        else:
            raise ValueError("Invalid input for calendar data")

        for index, row in df.iterrows():
            # 이벤트 데이터
            event_summary = row['Subject']
            event_start_date = row['Start Date']
            event_start_time = row['Start Time']
            event_end_date = row['End Date']
            event_end_time = row['End Time']
            event_description = row['Description']
            event_location = row['Location']

            # Reminder가 있는 경우만 리마인더 설정
            reminder_minutes = row.get('Reminder', None)
            reminders = {
                'useDefault': False
            }
            if reminder_minutes is not None:
                reminders['overrides'] = [{'method': 'popup', 'minutes': reminder_minutes}]

            # 기존 일정 검색
            existing_events = service.events().list(
                calendarId=calendar_id,
                q=event_summary,  # 제목으로 검색
                timeMin=f"{event_start_date}T{event_start_time}:00+09:00",  # 시작 시간으로 검색 범위 설정
                timeMax=f"{event_end_date}T{event_end_time}:00+09:00",  # 종료 시간으로 검색 범위 설정
                singleEvents=True,
                orderBy='startTime'
            ).execute()

            # 이벤트 데이터 설정
            event = {
                'summary': event_summary,
                'location': event_location,
                'description': event_description,
                'start': {
                    'dateTime': f"{event_start_date}T{event_start_time}:00",
                    'timeZone': 'Asia/Seoul',
                },
                'end': {
                    'dateTime': f"{event_end_date}T{event_end_time}:00",
                    'timeZone': 'Asia/Seoul',
                },
                'reminders': reminders,  # 리마인더가 있을 경우만 포함됨
            }

            # 기존 일정이 있으면 업데이트, 없으면 새로 생성
            updated = True

            for existing_event in existing_events.get('items', []):
                if existing_event['summary'] == event_summary:
                    event_id = existing_event['id']
                    service.events().update(calendarId=calendar_id, eventId=event_id, body=event).execute()
                    print(f"Event updated: {existing_event.get('htmlLink')}")
                    break
            else:
                # 기존 일정이 없으면 새로 생성
                updated = False

            if not updated:
                created_event = service.events().insert(calendarId=calendar_id, body=event).execute()
                print(f"Event created: {created_event.get('htmlLink')}")

        print("Finish uploading")
        return None
