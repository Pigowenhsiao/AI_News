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

        # CNBC RSS (保持使用 RSS)
        for feed_url in self.config.CNBC_RSS_URLS:
            items.extend(
                self._fetch_rss(feed_url, "CNBC", self.config.MAX_ARTICLES_PER_SOURCE)
            )

        # 使用 Tavily 搜尋其他網站的新聞
        items.extend(
            self._search_with_tavily(
                "Bloomberg", "bloomberg.com", self.config.MAX_ARTICLES_PER_SOURCE
            )
        )
        items.extend(
            self._search_with_tavily(
                "Fortune", "fortune.com", self.config.MAX_ARTICLES_PER_SOURCE
            )
        )
        items.extend(
            self._search_with_tavily(
                "Yahoo Finance",
                "finance.yahoo.com",
                self.config.MAX_ARTICLES_PER_SOURCE,
            )
        )
        items.extend(
            self._search_with_tavily(
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

    def _search_with_tavily(
        self, source_name: str, domain: str, limit: int
    ) -> List[Dict[str, str]]:
        try:
            tavily_api_url = "https://api.tavily.com/search"
            from datetime import datetime, timedelta

            yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

            payload = {
                "api_key": self.config.TAVILY_API_KEY,
                "query": f"site:{domain} business finance news {yesterday}",
                "search_depth": "advanced",
                "max_results": limit * 2,
                "include_domains": [domain],
            }
            response = requests.post(
                tavily_api_url, json=payload, timeout=self.config.SCRAPE_TIMEOUT
            )
            response.raise_for_status()
            data = response.json()

            items = []
            seen_urls = set()

            if data.get("results"):
                for result in data["results"][:limit]:
                    url = result.get("url", "")
                    title = result.get("title", "")
                    content = result.get("content", "")

                    if not url or not title or url in seen_urls:
                        continue

                    seen_urls.add(url)

                    items.append(
                        {
                            "title": title,
                            "url": url,
                            "description": content[:200] + "..."
                            if len(content) > 200
                            else content,
                            "source_domain": domain,
                            "source_name": source_name,
                            "published": datetime.now().strftime("%Y-%m-%d"),
                        }
                    )

            if items:
                self.logger.info(f"從 {source_name} (Tavily) 獲取 {len(items)} 篇新聞")
            return items

        except Exception as e:
            self.logger.warning(f"從 {source_name} 搜尋失敗: {e}")
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
