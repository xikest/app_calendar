import asyncio
import platform
from libs import UPDATER
from libs import ECONOMIC_CALENDAR, RssFeed, NewsFeed


async def main():
    enable_headless = True
    wait_hour = 1

    if platform.system() == "Linux": enable_headless = True

    while True:
        token_path = 'token.pickle'
        service = UPDATER.authenticate(token_path=token_path)
        
        dict_all_calendar = {}
        try:
            economic_calendar = ECONOMIC_CALENDAR(json_path="json/calendar.json", enable_headless=enable_headless, verbose=False)        
            dict_calendar = economic_calendar.get_calendar_info()
            dict_all_calendar.update(dict_calendar)
        except:
            pass
        news_rss = RssFeed(json_path="json/rss_news.json")
        dict_calendar = news_rss.get_rss_info()
        dict_all_calendar.update(dict_calendar)
        
        news_web = NewsFeed(json_path="json/web_news.json", verbose=False)
        dict_calendar = news_web.get_news_info()
        dict_all_calendar.update(dict_calendar)
        

        for calendar_id, df_calendar in dict_all_calendar.items():
            UPDATER.update_events(service, csv_file=df_calendar, calendar_id=calendar_id)
            
            
        print(f"Waiting for {wait_hour} hours...")
        await asyncio.sleep(wait_hour * 60 * 60)  # 24 hours in seconds

if __name__ == '__main__':
    asyncio.run(main())
