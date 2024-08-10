import asyncio
from libs import UPDATER
from libs import ECONOMIC_CALENDAR, RssFeed, NewsFeed
import os
import platform

async def main():
    enable_headless = True
    wait_hour = 1

    if platform.system() == "Linux": enable_headless = True
    calendar_economic = os.environ.get('CALENDAR_ECONOMIC')
    calendar_rss = os.environ.get("CALENDAR_RSS")
    calendar_news = os.environ.get("CALENDAR_NEWS")
    calendar_sony = os.environ.get("CALENDAR_SONY")
    economic_calendar = ECONOMIC_CALENDAR(enable_headless=enable_headless)
    economic_rss = RssFeed(json_path="rss.json")
    news_feed = NewsFeed(json_path="news.json")
    sony_feed = RssFeed(json_path="rss_sony.json")

    while True:
        token_path = 'token.pickle'
        # df_economic_calendar = economic_calendar.get_calendar_info()
        # df_economic_rss = economic_rss.get_rss_info()
        df_news_feed = news_feed.get_news_info()
        # df_sony = sony_feed.get_rss_info()

        service = UPDATER.authenticate(token_path=token_path)
        # UPDATER.update_events(service, csv_file=df_economic_calendar, calendar_id=calendar_economic)
        # UPDATER.update_events(service, csv_file=df_economic_rss, calendar_id=calendar_rss)
        UPDATER.update_events(service, csv_file=df_news_feed, calendar_id=calendar_news, verbose=True)
        # UPDATER.update_events(service, csv_file=df_sony, calendar_id=calendar_sony, verbose=True)
        print(f"Waiting for {wait_hour} hours...")
        await asyncio.sleep(wait_hour * 60 * 60)  # 24 hours in seconds

if __name__ == '__main__':
    asyncio.run(main())
