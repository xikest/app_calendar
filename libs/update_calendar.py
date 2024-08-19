from googleapiclient.discovery import build
import pandas as pd
import os
import pickle
from datetime import datetime
import time

class UPDATER:
    @staticmethod
    def authenticate(token_path: str = 'token.pickle'):
        creds = None
        if os.path.exists(token_path):
            with open(token_path, 'rb') as token:
                creds = pickle.load(token)
        service = build('calendar', 'v3', credentials=creds)
        return service

    @staticmethod
    def update_events(service, csv_file, calendar_id: str, verbose: bool = False):
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
            event_summary = row['Subject']
            event_start_date = row['Start Date']
            event_start_time = row['Start Time']
            event_end_date = row['End Date']
            event_end_time = row['End Time']
            event_description = row['Description']
            event_location = row['Location']

            reminder_minutes = row.get('Reminder', None)
            reminders = {'useDefault': True}
            if reminder_minutes is not None:
                reminders = {'useDefault': False, 'overrides': [{'method': 'popup', 'minutes': reminder_minutes}]}

            is_all_day = not event_start_time and not event_end_time

            if is_all_day:
                start = {'date': event_start_date, 'timeZone': 'Asia/Seoul'}
                end = {'date': event_end_date, 'timeZone': 'Asia/Seoul'}
            else:
                start = {'dateTime': f"{event_start_date}T{event_start_time}:00+09:00", 'timeZone': 'Asia/Seoul'}
                end = {'dateTime': f"{event_end_date}T{event_end_time}:00+09:00", 'timeZone': 'Asia/Seoul'}

            time_min = f"{event_start_date}T00:00:00+09:00"
            time_max = f"{event_end_date}T23:59:59+09:00"

            existing_events = service.events().list(
                calendarId=calendar_id,
                timeMin=time_min,
                timeMax=time_max,
                singleEvents=True,
                orderBy='startTime'
            ).execute()

            event = {
                'summary': event_summary,
                'location': event_location,
                'description': event_description,
                'start': start,
                'end': end,
                'reminders': reminders,
            }
            
            create = True
            for existing_event in existing_events.get('items', []):
                existing_is_all_day = 'date' in existing_event['start']
                existing_start = existing_event['start'].get('date') or existing_event['start'].get('dateTime')
                existing_end = existing_event['end'].get('date') or existing_event['end'].get('dateTime')

                if is_all_day and existing_is_all_day:
                    existing_start_date = datetime.strptime(existing_start, '%Y-%m-%d').date()
                    existing_end_date = datetime.strptime(existing_end, '%Y-%m-%d').date()

                    if (existing_event['summary'].strip() == event_summary.strip() and
                        existing_start_date == datetime.strptime(event_start_date, '%Y-%m-%d').date() and
                        existing_end_date == datetime.strptime(event_end_date, '%Y-%m-%d').date()):
                        
                        if existing_event['description'].strip() != event_description.strip():
                            event_id = existing_event['id']
                            service.events().update(calendarId=calendar_id, eventId=event_id, body=event).execute()
                            if verbose:
                                print(f"Event updated: {existing_event.get('htmlLink')}")
                        create = False
                        break

                elif not is_all_day and not existing_is_all_day:
                    existing_start_datetime = datetime.strptime(existing_start, '%Y-%m-%dT%H:%M:%S%z')
                    existing_end_datetime = datetime.strptime(existing_end, '%Y-%m-%dT%H:%M:%S%z')
                    new_start_datetime = datetime.strptime(f"{event_start_date}T{event_start_time}:00+09:00", '%Y-%m-%dT%H:%M:%S%z')
                    new_end_datetime = datetime.strptime(f"{event_end_date}T{event_end_time}:00+09:00", '%Y-%m-%dT%H:%M:%S%z')

                    if (existing_event['summary'].strip() == event_summary.strip() and
                        existing_start_datetime == new_start_datetime and
                        existing_end_datetime == new_end_datetime):
                            
                        if existing_event['description'].strip() != event_description.strip():
                            event_id = existing_event['id']
                            service.events().update(calendarId=calendar_id, eventId=event_id, body=event).execute()
                            if verbose:
                                print(f"Event updated: {existing_event.get('htmlLink')}")
                        create = False
                        break

            if create:
                created_event = service.events().insert(calendarId=calendar_id, body=event).execute()
                if verbose:
                    print(f"Event created: {created_event.get('htmlLink')}")

            time.sleep(1)
        if verbose:
            print("Finish updating")
        return None
