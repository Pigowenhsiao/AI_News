#!/usr/bin/env python3
import requests
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup

print("=" * 70)
print("CNN 新聞爬取替代方案測試")
print("=" * 70)

# 方案 1: 使用第三方 RSS 聚合服務
print("\n【方案 1】第三方 RSS 聚合服務")
print("-" * 70)

alternative_rss_feeds = [
    {
        "name": "RSS2JSON (CNN Business)",
        "url": "https://rss2json.com/v1/api.json?rss_url=https://edition.cnn.com/business/rss",
        "parser": "json",
    },
    {
        "name": "Feedrabbit (CNN)",
        "url": "https://feedrabbit.com/rss/cnn-business.rss",
        "parser": "xml",
    },
    {
        "name": "NewsAPI.org (需要 API Key)",
        "note": "免費版每天 100 次請求，有 CNN Business 分類",
        "url": "https://newsapi.org/v2/everything?domains=cnn.com&apiKey=YOUR_KEY",
        "requires_key": True,
    },
]

# 測試可用的第三方 RSS
for feed in alternative_rss_feeds[:2]:
    if feed.get("requires_key"):
        print(f"\n{feed['name']}:")
        print(f"  📝 {feed['note']}")
        print(f"  🔑 需要 API Key")
        continue

    print(f"\n測試: {feed['name']}")
    print(f"  URL: {feed['url']}")
    try:
        response = requests.get(feed["url"], timeout=10)
        print(f"  狀態: {response.status_code}")

        if response.status_code == 200:
            if feed["parser"] == "json":
                data = response.json()
                if "status" in data and data["status"] == "ok":
                    items = data.get("items", [])
                    print(f"  ✅ 成功! 找到 {len(items)} 則新聞")
                    if items:
                        print(f"  範例: {items[0].get('title', '')[:60]}...")
                else:
                    print(f"  ⚠️ API 返回錯誤: {data.get('message', 'Unknown')}")
            else:
                root = ET.fromstring(response.text)
                items = root.findall(".//item")
                print(f"  ✅ 成功! 找到 {len(items)} 則新聞")
        else:
            print(f"  ❌ 請求失敗")
    except Exception as e:
        print(f"  ❌ 錯誤: {e}")

# 方案 2: 使用新聞 API
print("\n\n【方案 2】新聞 API 服務")
print("-" * 70)

news_apis = [
    {
        "name": "NewsAPI.org",
        "description": "支援 CNN，分類完備，免費 100 次/天",
        "pricing": "免費: $0/月 | 開發者: $449/月",
        "domains": "cnn.com",
        "url": "https://newsapi.org/",
    },
    {
        "name": "GNews.io",
        "description": "包含 CNN 來源，實時新聞",
        "pricing": "免費: 100 次/天 | 付費: $9.99/月",
        "domains": "cnn.com",
        "url": "https://gnews.io/",
    },
    {
        "name": "Currents API",
        "description": "多語言，包含英文新聞",
        "pricing": "免費: 100 次/月 | 付費: $8/月",
        "url": "https://currentsapi.services/",
    },
]

for api in news_apis:
    print(f"\n{api['name']}:")
    print(f"  說明: {api['description']}")
    print(f"  定價: {api['pricing']}")
    if "domains" in api:
        print(f"  篩選: domains={api['domains']}")
    print(f"  網站: {api['url']}")

# 方案 3: 使用其他類似新聞源（更容易爬取）
print("\n\n【方案 3】替代新聞源（更容易爬取）")
print("-" * 70)

easier_sources = [
    {
        "name": "Reuters (路透社)",
        "description": "全球財經新聞，文章完整，有 RSS",
        "rss": "https://www.reutersagency.com/feed/?best-topics=business-finance&post_type=best",
        "website": "https://www.reuters.com/",
    },
    {
        "name": "AP News",
        "description": "美聯社，權威新聞來源",
        "rss": "https://feeds.apnews.com/rss/apnews-business",
        "website": "https://apnews.com/",
    },
    {
        "name": "BBC Business",
        "description": "BBC 商業新聞，國際視角",
        "rss": "https://feeds.bbci.co.uk/news/business/rss.xml",
        "website": "https://www.bbc.com/news/business",
    },
    {
        "name": "Yahoo Finance",
        "description": "雅虎財經，更新頻繁",
        "rss": "https://finance.yahoo.com/news/rssindex",
        "website": "https://finance.yahoo.com/",
    },
]

# 測試這些更容易爬取的來源
for source in easier_sources:
    print(f"\n{source['name']}:")
    print(f"  說明: {source['description']}")
    print(f"  RSS: {source['rss']}")
    print(f"  網站: {source['website']}")

    try:
        response = requests.get(source["rss"], timeout=10)
        if response.status_code == 200:
            root = ET.fromstring(response.text)
            items = root.findall(".//item")
            print(f"  ✅ RSS 可用: {len(items)} 則新聞")

            # 測試爬取文章
            if items:
                test_url = items[0].findtext("link")
                print(f"  測試爬取: {test_url[:60]}...")
                try:
                    article_resp = requests.get(test_url, timeout=10)
                    if article_resp.status_code == 200:
                        soup = BeautifulSoup(article_resp.text, "html.parser")
                        paragraphs = soup.find_all("p")
                        print(f"  ✅ 爬取成功: {len(paragraphs)} 個段落")
                    else:
                        print(f"  ❌ 爬取失敗: {article_resp.status_code}")
                except Exception as e:
                    print(f"  ⚠️ 爬取錯誤: {e}")
        else:
            print(f"  ❌ RSS 失敗: {response.status_code}")
    except Exception as e:
        print(f"  ⚠️ 錯誤: {e}")

# 方案 4: 使用 Headless Browser (Selenium/Playwright)
print("\n\n【方案 4】Headless Browser 方案")
print("-" * 70)

print("""
Selenium / Playwright:
  優點:
    - 模擬真實瀏覽器行為，繞過部分反爬蟲
    - 可執行 JavaScript
    - 可處理動態內容
  
  缺點:
    - 資源消耗較大
    - 速度較慢
    - 可能仍被識別為爬蟲
  
  狀態: Playwright 已安裝，可直接使用
  
  推薦配置:
    - 使用 random-useragent
    - 設置合理的請求間隔 (2-5 秒)
    - 使用代理輪換 (如有需要)
""")

print("\n" + "=" * 70)
print("推薦方案排序:")
print("=" * 70)
print("""
【推薦 1】使用 NewsAPI.org
  - 最穩定，官方 API
  - 支援 CNN 和其他來源
  - 免費版足夠日常使用

【推薦 2】使用 Reuters 或 AP News
  - 質量相當於 CNN
  - RSS 可用
  - 容易爬取

【推薦 3】使用 Yahoo Finance
  - RSS 更新快
  - 爬取成功率較高
  - 內容豐富

【備選】Playwright + CNN
  - 最複雜但可能成功
  - 需要調試反爬蟲策略
  - 資源消耗大
""")
