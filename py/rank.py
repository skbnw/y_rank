import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import os
import time
import pytz

# 日本時間を取得する関数
def get_japan_time():
    tokyo_timezone = pytz.timezone('Asia/Tokyo')
    return datetime.now(tokyo_timezone)

# ニュースデータをスクレイプしてCSVに保存する関数
def scrape_and_save_news(url, genre_en, genre_jp, folder_name, scrape_datetime):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        news_items = soup.select('.newsFeed_item')
        news_data = []

        for item in news_items:
            rank_element = item.select_one('.newsFeed_item_rankNum')
            title_element = item.select_one('.newsFeed_item_title')
            media_element = item.select_one('.newsFeed_item_sub span')
            date_element = item.select_one('.newsFeed_item_sub time')  # 修正点
            link_element = item.select_one('.newsFeed_item_link')

            if not rank_element:
                raise ValueError("Rank element not found")
            if not title_element:
                raise ValueError("Title element not found")
            if not media_element:
                raise ValueError("Media element not found")
            if not date_element:
                raise ValueError("Date element not found")
            if not link_element:
                raise ValueError("Link element not found")

            rank = rank_element.text
            title = title_element.text
            media = media_element.text
            date = date_element.text
            link = link_element['href']

            news_data.append([
                scrape_datetime.strftime('%Y-%m-%d'), 
                scrape_datetime.strftime('%H:%M'), 
                genre_en, genre_jp, 
                rank, media, title, 
                link, date
            ])

        # CSVファイルに保存
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)
        filename = os.path.join(folder_name, f"{scrape_datetime.strftime('%Y_%m%d_%H%M')}_rank_{genre_en}.csv")
        df = pd.DataFrame(news_data, columns=[
            'scrp_date', 'scrp_time', 'genre_en', 'genre_jp', 'rank', 'media_jp', 'title', 'link', 'date_original'
        ])
        df.to_csv(filename, index=False)
        print(f"CSV file saved as {filename}")

    except requests.RequestException as e:
        print(f"Error: {e}")
        raise
    except Exception as e:
        print(f"Scraping error: {e}")
        raise

# URLとジャンルのリスト
genres = [
    ("https://news.yahoo.co.jp/ranking/access/news", "TTL", "総合"),
    ("https://news.yahoo.co.jp/ranking/access/news/domestic", "domestic", "国内"),
    ("https://news.yahoo.co.jp/ranking/access/news/world", "world", "国際"),
    ("https://news.yahoo.co.jp/ranking/access/news/business", "business", "経済"),
    ("https://news.yahoo.co.jp/ranking/access/news/entertainment", "entertainment", "エンタメ"),
    ("https://news.yahoo.co.jp/ranking/access/news/sports", "sports", "スポーツ"),
    ("https://news.yahoo.co.jp/ranking/access/news/it-science", "it-science", "IT・科学"),
    ("https://news.yahoo.co.jp/ranking/access/news/life", "life", "ライフ"),
    ("https://news.yahoo.co.jp/ranking/access/news/local", "local", "地域")
]

# スクレイプ実行時間（日本時間）
scrape_time = get_japan_time()

# 保存先フォルダ名（日本時間の年月日、'data_rank'フォルダ内のサブフォルダとして）
folder_name = scrape_time.strftime('%Y_%m%d_rank')

# 各ジャンルのニュースをスクレイプしてCSVに保存
try:
    for url, genre_en, genre_jp in genres:
        scrape_and_save_news(url, genre_en, genre_jp, folder_name, scrape_time)
        time.sleep(3)  # 3秒間の休止
except Exception as e:
    print(f"Process stopped due to error: {e}")
    exit(1)
