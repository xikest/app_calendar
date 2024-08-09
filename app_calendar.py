import asyncio
from libs import UPDATER
from libs import ECONOMIC_CALENDAR, RSS_FEED
import os
import platform

async def main():
    enable_headless = True
    wait_hour = 1
    if platform.system() == "Linux": enable_headless = True
    calendar_economic = os.environ.get('CALENDAR_ECONOMIC')
    calendar_rss = os.environ.get("CALENDAR_RSS")
    ec = ECONOMIC_CALENDAR(enable_headless=enable_headless)
    rf = RSS_FEED()

    while True:
        """Main function to authenticate and upload events."""

        token_path = 'token.pickle'
        # csv_path = 'economics_calendar.csv'

        df_calendar = ec.get_calendar_info(convert_format_google=True)
        # df_calendar.to_csv(csv_path, index=False)
        df_rss = rf.get_rss_info(convert_format_google=True)
        service = UPDATER.authenticate(token_path=token_path)
        UPDATER.update_events(service, csv_file=df_calendar, calendar_id=calendar_economic)
        UPDATER.update_events(service, csv_file=df_rss, calendar_id=calendar_rss)
        print(f"Waiting for {wait_hour} hours...")
        await asyncio.sleep(wait_hour * 60 * 60)  # 24 hours in seconds


if __name__ == '__main__':
    asyncio.run(main())
