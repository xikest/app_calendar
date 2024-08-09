import asyncio
from libs import UPLOADER, ECONOMIC_CALENDAR
import os

async def main():
        calendar_id = os.environ.get('CALENDAR_ID')
        ec = ECONOMIC_CALENDAR(enable_headless=True)
        while True:
            """Main function to authenticate and upload events."""

            token_path = 'token.pickle'
            csv_path = 'economics_calendar.csv'

            df_calendar = ec.get_calendar_info(convert_format_google=True)
            df_calendar.to_csv(csv_path, index=False)
            service = UPLOADER.authenticate(token_path=token_path)
            UPLOADER.upload_events(service, csv_file= df_calendar, calendar_id=calendar_id)

            print("Waiting for 1 hours...")
            await asyncio.sleep(60 * 60)  # 24 hours in seconds

if __name__ == '__main__':
    asyncio.run(main())