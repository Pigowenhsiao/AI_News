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

        if "bloomberg.com" in source_domain:
            try:
                text = self._crawl_with_crawl4ai_with_retry(url, max_retries=2)
                if text and len(text) > self.config.ARTICLE_MIN_LENGTH:
                    self.logger.info(f"Bloomberg 使用 crawl4ai 成功: {url}")
                    return self._clean_control_characters(self._clean_text(text))
            except Exception as e:
                self.logger.warning(f"Bloomberg crawl4ai 爬取失敗: {url} - {e}")

            try:
                text = self._scrape_with_enhanced_headers(url, source_domain)
                if text and len(text) > self.config.ARTICLE_MIN_LENGTH:
                    self.logger.info(f"Bloomberg 使用改進請求頭成功: {url}")
                    return self._clean_control_characters(self._clean_text(text))
            except Exception as e:
                self.logger.warning(f"Bloomberg 改進請求頭爬取失敗: {url} - {e}")

            if self.config.TAVILY_API_KEY:
                try:
                    text = self._scrape_with_tavily(url)
                    if text and len(text) > self.config.ARTICLE_MIN_LENGTH:
                        self.logger.info(f"Bloomberg 使用 Tavily 成功: {url}")
                        return self._clean_control_characters(self._clean_text(text))
                except Exception as e:
                    self.logger.warning(f"Bloomberg Tavily 爬取失敗: {url} - {e}")
            return None

        if "cnn.com" in source_domain and self.config.TAVILY_API_KEY:
            try:
                text = self._scrape_with_tavily(url)
                if text and len(text) > self.config.ARTICLE_MIN_LENGTH:
                    return self._clean_control_characters(self._clean_text(text))
            except Exception as e:
                self.logger.warning(f"Tavily 爬取失敗: {url} - {e}")

        try:
            text = self._crawl_with_crawl4ai_with_retry(url, max_retries=2)
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

    def _get_crawl4ai_config(self):
        """獲取 crawl4ai 的優化配置"""
        from crawl4ai import BrowserConfig, CrawlerRunConfig

        browser_config = BrowserConfig(
            headless=True,
            verbose=False,
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            headers={
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9,zh-CN;q=0.8,zh-TW;q=0.7",
                "Accept-Encoding": "gzip, deflate, br",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
            },
            ignore_https_errors=True,
        )

        crawler_config = CrawlerRunConfig(
            cache_mode="bypass",
            word_count_threshold=10,
            excluded_tags=["script", "style", "iframe", "noscript"],
            exclude_external_images=True,
            js_code=None,
        )

        return browser_config, crawler_config

    def _crawl_with_crawl4ai_with_retry(
        self, url: str, max_retries: int = 3
    ) -> Optional[str]:
        """使用 crawl4ai 爬取，支援重試"""
        from crawl4ai import AsyncWebCrawler
        import asyncio
        import time

        browser_config, crawler_config = self._get_crawl4ai_config()

        for attempt in range(1, max_retries + 1):
            try:

                async def fetch():
                    async with AsyncWebCrawler(
                        config=browser_config, verbose=False
                    ) as crawler:
                        result = await crawler.arun(url=url, config=crawler_config)
                        return result.markdown if result and result.markdown else None

                text = asyncio.run(fetch())

                if text and len(text) > self.config.ARTICLE_MIN_LENGTH:
                    self.logger.info(
                        f"crawl4ai 成功 (嘗試 {attempt}/{max_retries}): {url[:60]}..."
                    )
                    return text
                elif text:
                    self.logger.warning(
                        f"crawl4ai 內容較短 (嘗試 {attempt}/{max_retries}): {len(text)} 字符"
                    )
                    if attempt < max_retries:
                        time.sleep(2)
                        continue
                    return text
                else:
                    self.logger.warning(
                        f"crawl4ai 返回空內容 (嘗試 {attempt}/{max_retries})"
                    )
                    if attempt < max_retries:
                        time.sleep(2)
                        continue
                    return None

            except ImportError:
                self.logger.debug("crawl4ai 未安裝,使用備用方法")
                return None
            except Exception as e:
                error_msg = str(e)
                if "ERR_CONNECTION_CLOSED" in error_msg:
                    self.logger.warning(
                        f"crawl4ai 連線被關閉 (嘗試 {attempt}/{max_retries}): {e}"
                    )
                else:
                    self.logger.warning(
                        f"crawl4ai 錯誤 (嘗試 {attempt}/{max_retries}): {e}"
                    )

                if attempt < max_retries:
                    self.logger.info("等待 3 秒後重試...")
                    time.sleep(3)
                    continue
                return None

        self.logger.error(f"crawl4ai 在 {max_retries} 次重試後仍然失敗: {url}")
        return None

    def _crawl_with_crawl4ai(self, url: str) -> Optional[str]:
        """使用 crawl4ai 爬取（內部方法，重試邏輯已移至 _crawl_with_crawl4ai_with_retry）"""
        return self._crawl_with_crawl4ai_with_retry(url, max_retries=3)

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

    def _scrape_with_enhanced_headers(
        self, url: str, source_domain: str
    ) -> Optional[str]:
        enhanced_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
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
            "Referer": "https://www.bloomberg.com/",
        }

        res = requests.get(
            url, headers=enhanced_headers, timeout=self.config.SCRAPE_TIMEOUT
        )
        res.raise_for_status()
        soup = BeautifulSoup(res.text, "html.parser")

        if "bloomberg.com" in source_domain:
            text = self._extract_bloomberg_text(soup)
        elif "cnbc.com" in source_domain:
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

    def _extract_bloomberg_text(self, soup: BeautifulSoup) -> Optional[str]:
        selectors = [
            "div[class*='body-text']",
            "div[class*='article-content']",
            "article[class*='article']",
            "div[data-component='articleBody']",
            "section[data-type='article-body']",
            "div.body-text-v2__body-text",
            "div.body-text",
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
