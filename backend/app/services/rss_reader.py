import requests
import xml.etree.ElementTree as ET
import logging
from typing import List, Dict
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from ..core.config import Config


class RSSReader:
    def __init__(self, config: Config, logger: logging.Logger):
        self.config = config
        self.logger = logger

    def fetch_all_rss(self) -> List[Dict[str, str]]:
        self.logger.info("--- [步驟 1/6] 從多個新聞來源獲取新聞列表...")
        items: List[Dict[str, str]] = []

        # CNBC 使用 RSS (內容完整，不需要再爬取)
        for feed_url in self.config.CNBC_RSS_URLS:
            rss_items = self._fetch_rss(
                feed_url, "CNBC", self.config.MAX_ARTICLES_PER_SOURCE
            )
            # 為 CNBC 的 RSS item 標記已有完整內容
            for item in rss_items:
                item["has_full_content"] = True  # 標記已有完整內容
            items.extend(rss_items)

        # 其他來源使用 Crawl 爬取完整的新聞（不用 RSS）
        items.extend(
            self._crawl_website_articles(
                "Bloomberg", "bloomberg.com", self.config.MAX_ARTICLES_PER_SOURCE
            )
        )
        items.extend(
            self._crawl_website_articles(
                "Fortune", "fortune.com", self.config.MAX_ARTICLES_PER_SOURCE
            )
        )
        items.extend(
            self._crawl_website_articles(
                "Yahoo Finance",
                "finance.yahoo.com",
                self.config.MAX_ARTICLES_PER_SOURCE,
            )
        )
        items.extend(
            self._crawl_website_articles(
                "MarketWatch", "marketwatch.com", self.config.MAX_ARTICLES_PER_SOURCE
            )
        )

        # 其他來源使用 RSS 獲取列表（即使內容不完整，由 NewsCrawler 後續爬取完整內容）
        for feed_url in self.config.BLOOMBERG_RSS_URLS:
            items.extend(
                self._fetch_rss(
                    feed_url, "Bloomberg", self.config.MAX_ARTICLES_PER_SOURCE
                )
            )
        for feed_url in self.config.FORTUNE_RSS_URLS:
            items.extend(
                self._fetch_rss(
                    feed_url, "Fortune", self.config.MAX_ARTICLES_PER_SOURCE
                )
            )
        for feed_url in self.config.YAHOO_FINANCE_RSS_URLS:
            items.extend(
                self._fetch_rss(
                    feed_url, "Yahoo Finance", self.config.MAX_ARTICLES_PER_SOURCE
                )
            )
        for feed_url in self.config.MARKETWATCH_RSS_URLS:
            items.extend(
                self._fetch_rss(
                    feed_url, "MarketWatch", self.config.MAX_ARTICLES_PER_SOURCE
                )
            )

        # 其他來源使用 Crawl 爬取 (RSS 內容不完整)
        items.extend(
            self._crawl_website_articles(
                "Bloomberg", "bloomberg.com", self.config.MAX_ARTICLES_PER_SOURCE
            )
        )
        items.extend(
            self._crawl_website_articles(
                "Fortune", "fortune.com", self.config.MAX_ARTICLES_PER_SOURCE
            )
        )
        items.extend(
            self._crawl_website_articles(
                "Yahoo Finance",
                "finance.yahoo.com",
                self.config.MAX_ARTICLES_PER_SOURCE,
            )
        )
        items.extend(
            self._crawl_website_articles(
                "MarketWatch", "marketwatch.com", self.config.MAX_ARTICLES_PER_SOURCE
            )
        )

        # CNN Business (網頁爬取)
        cnn_web_items = self._fetch_cnn_web_articles(
            self.config.MAX_ARTICLES_PER_SOURCE
        )
        items.extend(cnn_web_items)
        deduped: List[Dict[str, str]] = []
        seen = set()
        for item in items:
            url = item.get("url")
            if not url or url in seen:
                continue
            seen.add(url)
            deduped.append(item)
        if self.config.MAX_TOTAL_ARTICLES > 0:
            deduped = deduped[: self.config.MAX_TOTAL_ARTICLES]
        self.logger.info(f"RSS 獲取 {len(deduped)} 則新聞")
        return deduped

    def _fetch_rss(
        self, feed_url: str, source_name: str, limit: int
    ) -> List[Dict[str, str]]:
        headers = self.config.RSS_REQUEST_HEADERS
        try:
            res = requests.get(
                feed_url, headers=headers, timeout=self.config.SCRAPE_TIMEOUT
            )
            res.raise_for_status()
        except requests.exceptions.SSLError as e:
            if feed_url.startswith("https://"):
                http_url = "http://" + feed_url[len("https://") :]
                try:
                    res = requests.get(
                        http_url, headers=headers, timeout=self.config.SCRAPE_TIMEOUT
                    )
                    res.raise_for_status()
                except Exception as inner:
                    self.logger.warning(f"RSS 獲取失敗: {http_url} - {inner}")
                    return []
            else:
                self.logger.warning(f"RSS 獲取失敗: {feed_url} - {e}")
                return []
        except Exception as e:
            self.logger.warning(f"RSS 獲取失敗: {feed_url} - {e}")
            return []
        try:
            root = ET.fromstring(res.text)
        except Exception as e:
            self.logger.warning(f"RSS 解析失敗: {feed_url} - {e}")
            return []
        items: List[Dict[str, str]] = []
        for item in root.findall(".//item")[:limit]:
            title = (item.findtext("title") or "").strip()
            link = (item.findtext("link") or "").strip()
            pub_date = self._parse_pub_date(item.findtext("pubDate") or "")
            description_html = item.findtext("description") or ""
            description = self._clean_text(
                BeautifulSoup(description_html, "html.parser").get_text(" ", strip=True)
            )
            if not title or not link:
                continue
            source_domain = urlparse(link).netloc.replace("www.", "")
            items.append(
                {
                    "title": title,
                    "url": link,
                    "description": description,
                    "source_domain": source_domain,
                    "source_name": source_name,
                    "published": pub_date,
                }
            )
        return items

    def _parse_pub_date(self, value: str) -> str:
        if not value:
            return ""
        try:
            from email.utils import parsedate_to_datetime

            dt = parsedate_to_datetime(value)
            return dt.strftime("%Y-%m-%d")
        except Exception:
            return ""

    def _clean_text(self, text: str) -> str:
        import re

        return re.sub(r"\s+", " ", text).strip() if text else ""

    # _search_with_tavily() 方法已棄用 - 改用 _crawl_website_articles()

    def _crawl_website_articles(
        self, source_name: str, domain: str, limit: int
    ) -> List[Dict[str, str]]:
        """爬取網站新聞列表（用於非 CNBC 來源）"""
        try:
            import requests
            from bs4 import BeautifulSoup
            from datetime import datetime
            import re

            # 根據域名設定目標 URL
            domain_urls = {
                "bloomberg.com": "https://www.bloomberg.com/markets",
                "fortune.com": "https://fortune.com",
                "finance.yahoo.com": "https://finance.yahoo.com/news",
                "marketwatch.com": "https://www.marketwatch.com",
            }

            url = domain_urls.get(domain)
            if not url:
                self.logger.warning(f"未知域名: {domain}")
                return []

            # 增強請求頭，模擬真實瀏覽器
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9,zh-CN;q=0.8,zh-TW;q=0.7",
                "Accept-Encoding": "gzip, deflate, br",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "none",
                "Sec-Fetch-User": "?1",
                "Cache-Control": "max-age=0",
            }

            res = requests.get(url, headers=headers, timeout=self.config.SCRAPE_TIMEOUT)
            res.raise_for_status()
            soup = BeautifulSoup(res.text, "html.parser")

            items = []
            article_links = []

            # 根據不同網站使用不同的選擇器
            if "bloomberg.com" in domain:
                article_links = soup.select("a[data-component='link']")
            elif "fortune.com" in domain:
                article_links = soup.select("a[href^='/']")
            elif "finance.yahoo.com" in domain:
                article_links = soup.select("h3 a")
            elif "marketwatch.com" in domain:
                article_links = soup.select("h3 a, article a")

            # 去重和過濾
            seen_urls = set()

            for link in article_links:
                href = link.get("href")
                href = str(href) if href else ""

                if not href.startswith("http"):
                    # 處理相對路徑
                    if href.startswith("/"):
                        href = f"https://{domain}{href}"
                    else:
                        continue

                # 過濾條件
                if href in seen_urls:
                    continue

                title = link.get_text(strip=True)

                # 過濾無效標題
                if not title or len(title) < 30:
                    continue

                # 過濾圖片/媒體連結
                skip_keywords = [
                    "gettyimages",
                    "reuters.com/media",
                    "images.",
                    "/gallery/",
                    "/video/",
                    "mailto:",
                    "javascript:",
                ]

                skip = False
                for keyword in skip_keywords:
                    if keyword in href.lower():
                        skip = True
                        break

                if skip:
                    continue

                seen_urls.add(href)

                items.append(
                    {
                        "title": title,
                        "url": href,
                        "description": "",  # 空描述，內容由 NewsCrawler 爬取
                        "source_domain": domain,
                        "source_name": source_name,
                        "published": datetime.now().strftime("%Y-%m-%d"),
                    }
                )

                if len(items) >= limit:
                    break

            if items:
                self.logger.info(f"從 {source_name} 網站爬取 {len(items)} 篇新聞")

            return items

        except Exception as e:
            self.logger.warning(f"從 {source_name} 網站爬取失敗: {e}")
            return []

    def _fetch_cnn_web_articles(self, limit: int) -> List[Dict[str, str]]:
        try:
            import requests
            from bs4 import BeautifulSoup
            from datetime import datetime, timedelta
            import re

            url = "https://edition.cnn.com/business"
            headers = self.config.RSS_REQUEST_HEADERS
            res = requests.get(url, headers=headers, timeout=self.config.SCRAPE_TIMEOUT)
            res.raise_for_status()
            soup = BeautifulSoup(res.text, "html.parser")

            items = []
            article_links = soup.select('a[data-link-type="article"]')
            if not article_links:
                article_links = soup.select("a.container__link--type-article")

            # 去重和過濾
            seen_urls = set()
            valid_items = []

            for link in article_links:
                href = link.get("href")
                href = str(href) if href else ""
                if not href.startswith("http"):
                    href = "https://edition.cnn.com" + href

                # 過濾條件
                if href in seen_urls:
                    continue

                title = link.get_text(strip=True)

                # 過濾無效標題
                skip_patterns = [
                    r"^/\d+/\d+/\d+/",  # 只包含日期
                    r"^\s*$",  # 空標題
                    r"^(CNN|CNN Underscored)\s*$",  # 只包含 CNN
                ]

                # 過濾圖片說明文字（包含攝影師/圖庫名稱且長度較短）
                image_credit_patterns = [
                    r"Getty Images",
                    r"^[A-Z][a-z]+ [A-Z][a-z]+/(Reuters|Bloomberg|Shutterstock|AFP)$",
                ]

                should_skip = False
                for pattern in skip_patterns:
                    if re.match(pattern, title):
                        should_skip = True
                        break

                for pattern in image_credit_patterns:
                    if re.search(pattern, title) and len(title) < 50:
                        should_skip = True
                        break

                # 過濾圖片/媒體連結
                skip_keywords = [
                    "gettyimages",
                    "reuters.com/media",
                    "bloomberg.com",
                    "images.",
                    "/gallery/",
                ]

                for keyword in skip_keywords:
                    if keyword in href.lower():
                        should_skip = True
                        break

                if should_skip or len(title) < 30:
                    continue

                seen_urls.add(href)

                valid_items.append(
                    {
                        "title": title,
                        "url": href,
                        "description": "",
                        "source_domain": "edition.cnn.com",
                        "source_name": "CNN Business",
                        "published": datetime.now().strftime("%Y-%m-%d"),
                    }
                )

                if len(valid_items) >= limit:
                    break

            if valid_items:
                self.logger.info(f"從 CNN Business 網站獲取 {len(valid_items)} 篇新聞")
            return valid_items

        except Exception as e:
            self.logger.warning(f"從 CNN Business 網站獲取失敗: {e}")
            return []
