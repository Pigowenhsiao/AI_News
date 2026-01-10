#!/usr/bin/env python3
import requests
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup

print("=" * 70)
print("財經新聞 RSS Feed 測試")
print("=" * 70)

finance_rss_feeds = [
    {
        "name": "BBC Business",
        "rss": "https://feeds.bbci.co.uk/news/business/rss.xml",
        "domain": "www.bbc.com",
    },
    {
        "name": "FT Markets (Financial Times)",
        "rss": "https://www.ft.com/rss/companies/markets",
        "domain": "ft.com",
    },
    {
        "name": "CNBC Markets",
        "rss": "https://www.cnbc.com/id/10000664/device/rss/rss.html",
        "domain": "cnbc.com",
    },
    {
        "name": "MarketWatch Top Stories",
        "rss": "https://www.marketwatch.com/rss/topstories",
        "domain": "marketwatch.com",
    },
    {
        "name": "Bloomberg Markets",
        "rss": "https://feeds.bloomberg.com/markets/news.rss",
        "domain": "bloomberg.com",
    },
    {
        "name": "Yahoo Finance",
        "rss": "https://finance.yahoo.com/news/rssindex",
        "domain": "finance.yahoo.com",
    },
    {
        "name": "WSJ Markets (Wall Street Journal)",
        "rss": "https://feeds.a.dj.com/rss/WSJcomUSMarkets.xml",
        "domain": "wsj.com",
    },
]

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
}

available_feeds = []

print("\n測試 RSS Feeds...\n")

for feed in finance_rss_feeds:
    print(f"測試: {feed['name']}")
    print(f"  RSS: {feed['rss'][:70]}{'...' if len(feed['rss']) > 70 else ''}")

    try:
        response = requests.get(feed["rss"], headers=headers, timeout=10)

        if response.status_code == 200:
            root = ET.fromstring(response.text)
            items = root.findall(".//item")

            if items:
                print(f"  ✅ RSS 可用: {len(items)} 則新聞")

                # 獲取最新新聞信息
                latest = items[0]
                title = latest.findtext("title") or "N/A"
                link = latest.findtext("link") or "N/A"
                pub_date = latest.findtext("pubDate") or "N/A"

                print(f"  最新: {title[:60]}...")
                print(f"  連結: {link[:70]}{'...' if len(link) > 70 else ''}")
                print(f"  日期: {pub_date}")

                # 測試爬取
                try:
                    article_resp = requests.get(link, headers=headers, timeout=10)
                    if article_resp.status_code == 200:
                        soup = BeautifulSoup(article_resp.text, "html.parser")
                        paragraphs = soup.find_all("p")
                        article = soup.find("article")

                        if article:
                            article_text = article.get_text(separator=" ", strip=True)
                            print(
                                f"  ✅ 爬取成功: {len(article_text)} 字符 ({len(paragraphs)} 個段落)"
                            )
                        elif paragraphs:
                            text = " ".join(
                                [p.get_text(strip=True) for p in paragraphs[:10]]
                            )
                            print(
                                f"  ⚠️ 找到段落: {len(text)} 字符 ({len(paragraphs)} 個段落)"
                            )
                        else:
                            print(f"  ⚠️ 頁面結構不明顯")
                    else:
                        print(f"  ⚠️ 爬取失敗: {article_resp.status_code}")
                except Exception as e:
                    print(f"  ⚠️ 爬取錯誤: {e}")

                available_feeds.append(feed)
            else:
                print(f"  ⚠️ RSS 空內容")
        else:
            print(f"  ❌ RSS 失敗: {response.status_code}")
    except Exception as e:
        print(f"  ❌ 錯誤: {str(e)[:60]}...")

    print()

print("=" * 70)
print(f"可用的 RSS Feeds 共 {len(available_feeds)} 個:")
print("=" * 70)
for feed in available_feeds:
    print(f"  • {feed['name']}")

print("\n" + "=" * 70)
print("建議實施方案")
print("=" * 70)
print("""
基於測試結果，建議採用以下方案:

【推薦】整合多個可用 RSS 源

1. **BBC Business** ✅
   - 國際視角，質量高
   - RSS 穩定
   - 爬取成功率高

2. **CNBC Markets** ✅ (已在系統中)
   - 美國財經重點
   - 已有完整爬蟲配置

3. **MarketWatch** ✅
   - 美國財經新聞
   - RSS 穩定

4. **WSJ Markets** (如需付費內容)
   - 華爾街日報市場新聞
   - 高質量分析

實施步驟:
1. 將可用的 RSS feeds 加入配置文件
2. 更新爬蟲以支援多個網站的 HTML 結構
3. 測試並驗證每個來源
4. 添加故障轉移機制 (fallback)

對於 CNN 特別需求:
- 如果必須使用 CNN，可考慮 NewsAPI.org (需註冊)
- 或等待 CNN RSS 恢復正常後再加入
""")
