from libs import UPDATER, ECONOMIC_CALENDAR, RssFeed, NewsFeed
import logging
from fastapi import FastAPI
import os
import uvicorn 

logging.basicConfig(level=logging.ERROR)  # DEBUG로 설정하면 모든 로그 메시지가 출력됨
app = FastAPI()


@app.get("/run_calendar")
def run_calendar():

    secret_path = "web-driver.json"
    service = UPDATER.authenticate(json_path=secret_path)
    dict_all_calendar = {}

    # # 경제 캘린더 정보 가져오기
    # try:
    #     logging.info("Fetching economic calendar information...")
    #     economic_calendar = ECONOMIC_CALENDAR(json_path="json/calendar.json")        
    #     dict_all_calendar.update(economic_calendar.get_calendar_info())
    #     logging.info("Economic calendar information fetched successfully.")
    # except Exception as e:
    #     logging.error(f"Error fetching economic calendar information: {e}")
    
    # 뉴스 RSS 정보 가져오기
    try:
        logging.info("Fetching news RSS information...")
        json_path = "https://raw.githubusercontent.com/xikest/app_calendar/main/json/rss_news.json"
        skip_json_path = "https://raw.githubusercontent.com/xikest/app_calendar/main/json/filter_words.json"
        news_rss = RssFeed(json_path=json_path, skip_json_path=skip_json_path)    
        dict_all_calendar.update(news_rss.get_rss_info())
        logging.info("News RSS information fetched successfully.")
    except Exception as e:
        logging.error(f"Error fetching news RSS information: {e}")
    
    # 웹 뉴스 정보 가져오기
    # try:
    #     logging.info("Fetching news web information...")
    #     json_path = "https://raw.githubusercontent.com/xikest/app_calendar/main/json/web_news.json"
    #     news_web = NewsFeed(json_path="json/web_news.json")    
    #     dict_all_calendar.update(news_web.get_news_info())
    #     logging.info("News web information fetched successfully.")
    # except Exception as e:
    #     logging.error(f"Error fetching news web information: {e}")

    # 모든 캘린더에 이벤트 업데이트
    for calendar_id, df_calendar in dict_all_calendar.items():
        try: 
            logging.info(f"Updating events for calendar ID: {calendar_id}...")
            UPDATER.update_events(service, csv_file=df_calendar, calendar_id=calendar_id)
            logging.info(f"Events updated successfully for calendar ID: {calendar_id}.")
        except Exception as e:
            logging.error(f"Error updating events for calendar ID '{calendar_id}': {e}")
        
    logging.info("All tasks completed.")


if __name__ == "__main__":
    uvicorn.run("app_calendar:app", host="0.0.0.0", port=8800)
    

