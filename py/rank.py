import requests
from bs4 import BeautifulSoup
import csv
from datetime import datetime

def scrape_yahoo_news_ranking():
    url = "https://news.yahoo.co.jp/ranking/access/news"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        news_items = soup.find_all('li', class_='newsFeed_item')

        results = []
        for item in news_items:
            try:
                rank_element = item.find('span', class_='sc-1hy2mez-11')
                if rank_element is None:
                    raise ValueError("Rank element not found")
                rank = rank_element.text.strip()

                title_element = item.find('div', class_='newsFeed_item_title')
                if title_element is None:
                    raise ValueError("Title element not found")
                title = title_element.text.strip()

                link_element = item.find('a', class_='newsFeed_item_link')
                if link_element is None:
                    raise ValueError("Link element not found")
                link = link_element['href']

                source_element = item.find('span', class_='sc-1hy2mez-3')
                source = source_element.text.strip() if source_element else "N/A"

                time_element = item.find('time', class_='sc-1hy2mez-4')
                time = time_element.text.strip() if time_element else "N/A"

                results.append({
                    'rank': rank,
                    'title': title,
                    'link': link,
                    'source': source,
                    'time': time
                })

            except Exception as e:
                print(f"Error processing item: {e}")
                continue

        return results

    except requests.RequestException as e:
        print(f"Error fetching the webpage: {e}")
        return []

def save_to_csv(data, filename):
    with open(filename, 'w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=['rank', 'title', 'link', 'source', 'time'])
        writer.writeheader()
        writer.writerows(data)

if __name__ == "__main__":
    news_data = scrape_yahoo_news_ranking()
    if news_data:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"yahoo_news_ranking_{timestamp}.csv"
        save_to_csv(news_data, filename)
        print(f"Data saved to {filename}")
    else:
        print("No data was scraped.")
