#!/usr/bin/env python3
import requests
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup

print("=" * 60)
print("測試不同的 CNN RSS Feed")
print("=" * 60)

# 測試不同的 CNN RSS feeds
cnn_rss_feeds = [
    "https://rss.cnn.com/rss/edition.rss",
    "https://rss.cnn.com/rss/edition_business.rss",
    "https://rss.cnn.com/rss/edition_world.rss",
    "https://rss.cnn.com/rss/money_news_international.rss",
]

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/rss+xml,application/xml;q=0.9,*/*;q=0.8",
}

working_feeds = []

for feed_url in cnn_rss_feeds:
    print(f"\n測試: {feed_url}")
    try:
        response = requests.get(feed_url, headers=headers, timeout=10)
        print(f"  狀態: {response.status_code}")

        if response.status_code == 200:
            root = ET.fromstring(response.text)
            items = root.findall(".//item")
            print(f"  ✅ 找到 {len(items)} 則新聞")

            # 檢查最新一篇文章的連結格式
            if items:
                latest_link = items[0].findtext("link") or ""
                print(f"  連結範例: {latest_link}")
                working_feeds.append(feed_url)
        else:
            print(f"  ❌ 失敗")
    except Exception as e:
        print(f"  ❌ 錯誤: {e}")

print("\n" + "=" * 60)
print("可用的 RSS Feeds:")
for feed in working_feeds:
    print(f"  - {feed}")
print("=" * 60)

# 測試用不同方法爬取 CNN 文章
print("\n" + "=" * 60)
print("測試不同爬蟲方法")
print("=" * 60)

test_urls = [
    (
        "https://edition.cnn.com/2025/01/09/business/us-stock-markets-today/index.html",
        "CNN Edition",
    ),
    (
        "https://www.cnn.com/2025/01/09/business/apple-stock-earnings/index.html",
        "CNN Main",
    ),
]

test_methods = [
    (
        "直接請求",
        {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"},
    ),
    (
        "模擬 Googlebot",
        {
            "User-Agent": "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
        },
    ),
    (
        "Chrome UA",
        {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        },
    ),
]

for url, url_type in test_urls:
    print(f"\n測試 URL ({url_type}):")
    print(f"  {url[:80]}...")

    for method_name, headers in test_methods:
        print(f"\n  方法: {method_name}")
        try:
            response = requests.get(
                url, headers=headers, timeout=15, allow_redirects=True
            )
            print(f"    狀態碼: {response.status_code}")
            print(f"    Content-Length: {len(response.text)}")
            print(f"    Content-Type: {response.headers.get('Content-Type', 'N/A')}")

            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")

                # 嘗試多種選擇器
                selectors = [
                    "div.article__content",
                    "div.article__content-container",
                    "section#body-text",
                    "div.zn-body__paragraph",
                    "div.l-container",
                    "article",
                    "div.pg-rail-tall__body",
                ]

                for selector in selectors:
                    nodes = soup.select(selector)
                    if nodes:
                        text = nodes[0].get_text(separator=" ", strip=True)
                        if len(text) > 100:
                            print(f"    ✅ {selector}: {len(text)} 字符")
                            break
                else:
                    print(f"    ⚠️ 所有選擇器都失敗")
            else:
                print(f"    ❌ 請求失敗")
        except Exception as e:
            print(f"    ❌ 錯誤: {e}")

print("\n" + "=" * 60)
print("測試完成")
print("=" * 60)
