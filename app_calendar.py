from libs import UPDATER, ECONOMIC_CALENDAR, RssFeed, NewsFeed
import logging
from fastapi import FastAPI


logging.basicConfig(level=logging.DEBUG)  # DEBUG로 설정하면 모든 로그 메시지가 출력됨
app = FastAPI()


@app.post("/run")
def run_calendar():
    enable_headless = True
    verbose = False        

    service = UPDATER.authenticate()
    
    # token_path = 'token.pickle'
    # logging.info("Authenticating Google Calendar service...")
    # service = UPDATER.authenticate(token_path=token_path)
    


    dict_all_calendar = {}

    # 경제 캘린더 정보 가져오기
    try:
        logging.info("Fetching economic calendar information...")
        economic_calendar = ECONOMIC_CALENDAR(json_path="json/calendar.json", enable_headless=enable_headless, verbose=verbose)        
        dict_calendar = economic_calendar.get_calendar_info()
        dict_all_calendar.update(dict_calendar)
        logging.info("Economic calendar information fetched successfully.")
    except Exception as e:
        logging.error(f"Error fetching economic calendar information: {e}")
    
    # 뉴스 RSS 정보 가져오기
    try:
        logging.info("Fetching news RSS information...")
        news_rss = RssFeed(json_path="json/rss_news.json", verbose=verbose)    
        dict_calendar = news_rss.get_rss_info()
        dict_all_calendar.update(dict_calendar)
        logging.info("News RSS information fetched successfully.")
    except Exception as e:
        logging.error(f"Error fetching news RSS information: {e}")
    
    # 웹 뉴스 정보 가져오기
    try:
        logging.info("Fetching news web information...")
        news_web = NewsFeed(json_path="json/web_news.json", verbose=verbose)    
        dict_calendar = news_web.get_news_info()
        dict_all_calendar.update(dict_calendar)
        logging.info("News web information fetched successfully.")
    except Exception as e:
        logging.error(f"Error fetching news web information: {e}")

    # 모든 캘린더에 이벤트 업데이트
    for calendar_id, df_calendar in dict_all_calendar.items():
        try: 
            logging.info(f"Updating events for calendar ID: {calendar_id}...")
            # CSV 파일 대신 df_calendar 데이터를 사용하는 경우 추가 처리 필요
            UPDATER.update_events(service, csv_file=df_calendar, calendar_id=calendar_id, verbose=verbose)
            logging.info(f"Events updated successfully for calendar ID: {calendar_id}.")
        except Exception as e:
            logging.error(f"Error updating events for calendar ID '{calendar_id}': {e}")
        
    logging.info("All tasks completed.")

