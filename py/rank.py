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
        news_items = soup.select('.newsFeed_item_body')  # Changed selector to match the provided HTML
        news_data = []

        for idx, item in enumerate(news_items, 1):
            # タイトルを取得
            title_element = item.select_one('.sc-3ls169-0.dHAJpi')
            # メディアと日付を取得
            media_element = item.select_one('.sc-1hy2mez-3.gNVspC')
            date_element = item.select_one('time')
            # リンクを取得 (親要素の <a> タグを探す)
            link_element = item.find_parent('a')
            # ランクを取得 (親要素から探す)
            rank_element = item.find_parent().select_one('.sc-1hy2mez-11')

            # 要素が見つからない場合の処理
            if not all([title_element, media_element, date_element, link_element, rank_element]):
                print(f"Warning: Some elements not found for item {idx}, skipping...")
                continue

            # 各要素のテキストを取得
            title = title_element.text.strip()
            media = media_element.text.strip()
            date = date_element.text.strip()
            link = link_element['href'].strip()
            rank = rank_element.text.strip()

            # デバッグ: 取得したランクを出力して確認
            print(f"Debug: Rank for item {idx}: {rank}")

            # リンクが相対パスの場合、絶対パスに変換
            if not link.startswith('http'):
                link = requests.compat.urljoin(url, link)

            # データリストに追加
            news_data.append([
                scrape_datetime.strftime('%Y-%m-%d'),
                scrape_datetime.strftime('%H:%M'),
                genre_en, genre_jp,
                rank, media, title,
                link, date
            ])

        # CSVファイルに保存
        if news_data:  # データがある場合のみ保存
            if not os.path.exists(folder_name):
                os.makedirs(folder_name)
            filename = os.path.join(folder_name, f"{scrape_datetime.strftime('%Y_%m%d_%H%M')}_rank_{genre_en}.csv")
            df = pd.DataFrame(news_data, columns=[
                'scrp_date', 'scrp_time', 'genre_en', 'genre_jp', 'rank', 'media_jp', 'title', 'link', 'date_original'
            ])
            df.to_csv(filename, index=False)
            print(f"CSV file saved as {filename}")
        else:
            print(f"No data to save for {genre_en} at {url}")

    except requests.RequestException as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Scraping error: {e}")
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
