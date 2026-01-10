#!/usr/bin/env python3
import sys
from pathlib import Path

backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

import logging
from app.core.config import Config
from app.services.rss_reader import RSSReader
from app.services.news_crawler import NewsCrawler

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger()

config = Config()
rss_reader = RSSReader(config, logger)
crawler = NewsCrawler(config, logger)

print("=" * 60)
print("測試 CNN 新聞爬取")
print("=" * 60)

# 測試 1: RSS Feed 獲取
print("\n[測試 1] 測試 CNN Business RSS Feed...")
print(f"RSS URL: {config.CNN_BUSINESS_RSS_URLS}")

rss_items = rss_reader._fetch_rss(
    config.CNN_BUSINESS_RSS_URLS[0], "CNN Business", limit=3
)

if rss_items:
    print(f"✅ RSS 獲取成功: {len(rss_items)} 則新聞")
    for i, item in enumerate(rss_items[:2], 1):
        print(f"\n  新聞 {i}:")
        print(f"    標題: {item['title'][:60]}...")
        print(f"    連結: {item['url']}")
        print(f"    發布日期: {item.get('published', 'N/A')}")
else:
    print("❌ RSS 獲取失敗")
    sys.exit(1)

# 測試 2: 爬取單篇文章內容
print("\n" + "=" * 60)
print("[測試 2] 測試爬取文章內容...")
print("=" * 60)

test_item = rss_items[0]
print(f"\n正在爬取: {test_item['url']}")

content = crawler._scrape_single_article(test_item)

if content:
    content_preview = content[:200].replace("\n", " ")
    print(f"✅ 爬取成功!")
    print(f"    內容長度: {len(content)} 字符")
    print(f"    內容預覽: {content_preview}...")
else:
    print("❌ 爬取失敗")
    print("\n嘗試直接請求看看 HTTP 狀態...")

    import requests

    try:
        headers = config.RSS_REQUEST_HEADERS
        response = requests.get(test_item["url"], headers=headers, timeout=10)
        print(f"HTTP 狀態碼: {response.status_code}")
        print(f"Content-Type: {response.headers.get('Content-Type', 'N/A')}")

        if response.status_code == 200:
            print("\n頁面內容分析...")
            from bs4 import BeautifulSoup

            soup = BeautifulSoup(response.text, "html.parser")

            # 檢查 CNN 特定選擇器
            selectors = [
                "div.article__content",
                "div.article__content-container",
                "section#body-text",
                "div.zn-body__paragraph",
                "article",
            ]

            found_selectors = []
            for selector in selectors:
                nodes = soup.select(selector)
                if nodes:
                    found_selectors.append(f"{selector} ({len(nodes)} 個)")

            if found_selectors:
                print("找到的選擇器:")
                for sel in found_selectors:
                    print(f"  - {sel}")
            else:
                print("⚠️ 未找到任何 CNN 選擇器")
                print("\n頁面主結構分析:")
                print(f"  - <article> 標籤: {'是' if soup.find('article') else '否'}")
                print(
                    f"  - <div class='article__content'>: {'是' if soup.select('div.article__content') else '否'}"
                )
                print(f"  - 段落 <p> 數量: {len(soup.find_all('p'))}")

                # 輸出部分 body 供檢查
                body = soup.find("body")
                if body:
                    print(f"\n  前 500 個字符的 body 內容:")
                    print(f"  {body.get_text()[:500]}...")
    except Exception as e:
        print(f"請求失敗: {e}")

# 測試 3: 完整流程測試
print("\n" + "=" * 60)
print("[測試 3] 完整流程測試 (RSS + 爬取)")
print("=" * 60)

articles = crawler.scrape_articles_concurrently(rss_items[:2])

if articles:
    print(f"✅ 完整流程成功: {len(articles)} 篇文章")
    for i, article in enumerate(articles, 1):
        print(f"\n  文章 {i}:")
        print(f"    標題: {article['title'][:50]}...")
        print(f"    來源: {article['source_name']}")
        print(f"    內容長度: {len(article.get('content', ''))} 字符")
else:
    print("❌ 完整流程失敗")

print("\n" + "=" * 60)
print("測試完成")
print("=" * 60)
