import re
import requests
import logging
from typing import List, Dict, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from bs4 import BeautifulSoup
from ..core.config import Config


class NewsCrawler:
    def __init__(self, config: Config, logger: logging.Logger):
        self.config = config
        self.logger = logger

    def scrape_articles_concurrently(self, rss_items: List[Dict]) -> List[Dict]:
        self.logger.info(f"--- [步驟 2/6] 正在爬取 {len(rss_items)} 則新聞內容...")
        articles = []
        with ThreadPoolExecutor(max_workers=self.config.MAX_WORKERS) as executor:
            future_to_item = {
                executor.submit(self._scrape_single_article, item): item
                for item in rss_items
            }
            for future in as_completed(future_to_item):
                item = future_to_item[future]
                try:
                    content = future.result()
                    if not content:
                        content = item.get("description") or ""
                        if content:
                            self.logger.info(f"使用 RSS 摘要 {item['url']} 作為內容")
                        else:
                            self.logger.warning(f"RSS 摘要為空,跳過: {item['url']}")
                            continue
                    articles.append(
                        {
                            "title": item["title"],
                            "url": item["url"],
                            "content": content,
                            "source_domain": item["source_domain"],
                            "source_name": item.get("source_name"),
                        }
                    )
                except Exception as e:
                    self.logger.error(f"爬取失敗: {item.get('url', '')} - {e}")
        self.logger.info(f"爬取完成,獲取 {len(articles)} 則新聞內容")
        return articles

    def _scrape_single_article(self, article: Dict[str, str]) -> Optional[str]:
        url = article.get("url", "")
        source_domain = article.get("source_domain", "")
        self.logger.debug(f"嘗試爬取: {url}")
        if "cnn.com" in source_domain and self.config.TAVILY_API_KEY:
            try:
                text = self._scrape_with_tavily(url)
                if text and len(text) > self.config.ARTICLE_MIN_LENGTH:
                    return self._clean_control_characters(self._clean_text(text))
            except Exception as e:
                self.logger.warning(f"Tavily 爬取失敗: {url} - {e}")
        try:
            text = self._crawl_with_crawl4ai(url)
            if text and len(text) > self.config.ARTICLE_MIN_LENGTH:
                return self._clean_control_characters(self._clean_text(text))
        except Exception as e:
            self.logger.warning(f"crawl4ai 爬取失敗: {url} - {e}")
        try:
            text = self._scrape_with_beautifulsoup(url, source_domain)
            if text and len(text) > self.config.ARTICLE_MIN_LENGTH:
                return self._clean_control_characters(self._clean_text(text))
        except Exception as e:
            self.logger.warning(f"BeautifulSoup 爬取失敗: {url} - {e}")
        return None

    def _crawl_with_crawl4ai(self, url: str) -> Optional[str]:
        try:
            from crawl4ai import AsyncWebCrawler
            import asyncio

            async def fetch():
                async with AsyncWebCrawler(verbose=False) as crawler:
                    result = await crawler.arun(url=url)
                    return result.markdown if result and result.markdown else None

            return asyncio.run(fetch())
        except ImportError:
            self.logger.debug("crawl4ai 未安裝,使用備用方法")
            return None
        except Exception as e:
            self.logger.debug(f"crawl4ai 執行失敗: {e}")
            return None

    def _scrape_with_tavily(self, url: str) -> Optional[str]:
        try:
            tavily_api_url = "https://api.tavily.com/search"
            payload = {
                "api_key": self.config.TAVILY_API_KEY,
                "query": url,
                "search_depth": "advanced",
                "include_raw_content": True,
                "max_results": 1,
            }
            response = requests.post(
                tavily_api_url, json=payload, timeout=self.config.SCRAPE_TIMEOUT
            )
            response.raise_for_status()
            data = response.json()
            if data.get("results") and len(data["results"]) > 0:
                content = data["results"][0].get("content", "")
                return content
        except Exception as e:
            self.logger.warning(f"Tavily API 呼叫失敗: {url} - {e}")
        return None

    def _scrape_with_beautifulsoup(self, url: str, source_domain: str) -> Optional[str]:
        headers = self.config.RSS_REQUEST_HEADERS
        res = requests.get(url, headers=headers, timeout=self.config.SCRAPE_TIMEOUT)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, "html.parser")
        if "cnbc.com" in source_domain:
            text = self._extract_cnbc_text(soup)
        elif "cnn.com" in source_domain:
            text = self._extract_cnn_business_text(soup)
        else:
            article_tag = soup.find("article")
            if article_tag:
                text = article_tag.get_text(separator=" ", strip=True)
            else:
                body_tag = soup.find("body")
                text = body_tag.get_text(separator=" ", strip=True) if body_tag else ""
        return text

    def _extract_cnbc_text(self, soup: BeautifulSoup) -> Optional[str]:
        selectors = [
            "div.ArticleBody-articleBody",
            "div.articleBody",
            "div#ArticleBody",
            "div.group",
            "article",
        ]
        return self._extract_text_by_selectors(soup, selectors)

    def _extract_cnn_business_text(self, soup: BeautifulSoup) -> Optional[str]:
        selectors = [
            "div.article__content",
            "div.article__content-container",
            "section#body-text",
            "div.zn-body__paragraph",
            "article",
        ]
        return self._extract_text_by_selectors(soup, selectors)

    def _extract_text_by_selectors(
        self, soup: BeautifulSoup, selectors: List[str]
    ) -> Optional[str]:
        for selector in selectors:
            nodes = soup.select(selector)
            if not nodes:
                continue
            parts = []
            for node in nodes:
                paragraphs = node.find_all("p")
                if paragraphs:
                    parts.extend(
                        [p.get_text(separator=" ", strip=True) for p in paragraphs]
                    )
                else:
                    parts.append(node.get_text(separator=" ", strip=True))
            text = self._clean_text(" ".join(parts))
            if text:
                return text
        return None

    def _clean_text(self, text: str) -> str:
        return re.sub(r"\s+", " ", text).strip() if text else ""

    def _clean_control_characters(self, text: str) -> str:
        if not text:
            return ""
        return re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]", "", text)
