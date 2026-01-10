#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import time
import argparse
from datetime import datetime
from pathlib import Path
from typing import Optional
import smtplib
from email.mime.text import MIMEText
import ssl

sys.path.insert(0, str(Path(__file__).parent))

from backend.app.core.config import Config
from backend.app.core.logger import setup_logger
from backend.app.services.rss_reader import RSSReader
from backend.app.services.news_crawler import NewsCrawler
from backend.app.services.ai_client import AIModelClient
from backend.app.services.html_generator import HTMLGenerator


class AI_News_Agent:
    def __init__(self, config: Config, logger):
        self.config = config
        self.logger = logger
        self.rss_reader = RSSReader(config, logger)
        self.news_crawler = NewsCrawler(config, logger)
        self.ai_client = AIModelClient(config, logger)
        self.html_generator = HTMLGenerator(config, logger)
        self.all_models_failed = False

    def run(self, topic: str) -> bool:
        process_start_time = time.time()
        self.logger.info(f"🚀 === 開始執行 AI News 分析: {topic} === 🚀")
        try:
            rss_items = self.rss_reader.fetch_all_rss()
            if not rss_items:
                self.logger.warning("未獲取到任何 RSS 新聞")
                self._send_failure_notification("未獲取到任何 RSS 新聞")
                return False

            articles_with_content = self.news_crawler.scrape_articles_concurrently(
                rss_items
            )
            if not articles_with_content:
                self.logger.warning("未爬取到任何新聞內容")
                self._send_failure_notification("未爬取到任何新聞內容")
                return False

            markdown_report = self._generate_markdown_report_sequentially(
                articles_with_content, topic
            )
            if not markdown_report:
                self.logger.error("所有新聞分析失敗")
                self._send_failure_notification("所有 AI Model 分析失敗")
                return False

            self._save_markdown_report(markdown_report, topic)

            market_summary_md = self._generate_market_summary(markdown_report)

            self.html_generator.parse_and_render_html(
                markdown_report, market_summary_md, topic
            )

            self.logger.info("✅ 分析完成!")
            return True

        except Exception as e:
            self.logger.critical(f"分析過程發生錯誤: {e}", exc_info=True)
            self._send_failure_notification(f"分析過程發生錯誤: {e}")
            return False
        finally:
            elapsed_time = time.time() - process_start_time
            self.logger.info(f"⏱️ 總耗時: {elapsed_time:.2f} 秒")
            self.logger.info("🏁 ===== AI News 分析系統執行完畢 ===== 🏁")

    def _generate_markdown_report_sequentially(self, articles, topic: str) -> str:
        self.logger.info(f"--- [步驟 3/6] 正在逐一分析新聞（共 {len(articles)} 篇）...")
        source_map = {
            "wsj.com": "華爾街日報",
            "bloomberg.com": "彭博",
            "reuters.com": "路透",
            "cnbc.com": "CNBC",
            "money.cnn.com": "CNN Business",
            "edition.cnn.com": "CNN Business",
            "cnn.com": "CNN Business",
            "marketwatch.com": "MarketWatch",
            "fortune.com": "財富",
        }
        all_markdown_parts = []

        for i, article in enumerate(articles, 1):
            display_name = article.get("source_name") or source_map.get(
                article["source_domain"], article["source_domain"]
            )

            single_article_md = self.config.RAW_NEWS_MARKDOWN_TEMPLATE.format(
                title=article["title"],
                source_display_name=display_name,
                url=article["url"],
                content=article["content"],
            )

            # 使用單篇文章分析提示詞
            full_prompt = self.config.SINGLE_ARTICLE_ANALYSIS_PROMPT.format(
                news_content=single_article_md
            )

            self.logger.info(
                f"--- [步驟 4.{i}/6] 正在分析第 {i}/{len(articles)} 篇新聞..."
            )

            analyzed_part = self.ai_client.call(
                full_prompt, self.config.ANALYSIS_OUTPUT_MODEL
            )

            if not analyzed_part:
                self.logger.warning(f"第 {i} 篇新聞分析失敗,跳過")
                continue

            analyzed_part = self._clean_control_characters(analyzed_part)
            all_markdown_parts.append(analyzed_part)

            self._save_markdown_part(analyzed_part, topic, i, len(articles))
            self.logger.info(f"✅ 第 {i}/{len(articles)} 篇新聞分析完成並已保存")

        if not all_markdown_parts:
            self.logger.error("所有新聞分析失敗")
            return ""

        return "\n\n".join(all_markdown_parts)

    def _generate_markdown_report(self, articles) -> Optional[str]:
        self.logger.info(f"--- [步驟 3/6] 正在將新聞內容發送給 AI 進行分析...")
        source_map = {
            "wsj.com": "華爾街日報",
            "bloomberg.com": "彭博",
            "reuters.com": "路透",
            "cnbc.com": "CNBC",
            "money.cnn.com": "CNN Business",
            "edition.cnn.com": "CNN Business",
            "cnn.com": "CNN Business",
            "marketwatch.com": "MarketWatch",
            "fortune.com": "財富",
        }
        raw_news_md = ""
        for article in articles:
            display_name = article.get("source_name") or source_map.get(
                article["source_domain"], article["source_domain"]
            )
            raw_news_md += self.config.RAW_NEWS_MARKDOWN_TEMPLATE.format(
                title=article["title"],
                source_display_name=display_name,
                url=article["url"],
                content=article["content"],
            )

        full_prompt = self.config.ANALYSIS_PROMPT_TEMPLATE.format(
            news_content=raw_news_md
        )
        self.logger.info(
            f"--- [步驟 4/6] 正在調用 AI ({self.config.ANALYSIS_OUTPUT_MODEL}) 生成 Markdown 報告..."
        )

        markdown_report = self.ai_client.call(
            full_prompt, self.config.ANALYSIS_OUTPUT_MODEL
        )
        if not markdown_report:
            self.logger.error("AI 分析失敗,無法繼續")
            return None

        return self._clean_control_characters(markdown_report)

    def _save_markdown_report(self, markdown_content: str, topic: str):
        self.logger.info(f"--- [步驟] 保存 Markdown 報告...")
        try:
            topic_slug = (
                "".join(c for c in topic if c.isalnum() or c in " -")
                .rstrip()
                .replace(" ", "_")
            )
            filename = self.config.MARKDOWN_FILENAME_TEMPLATE.format(
                date=datetime.now().strftime("%Y%m%d"), topic_slug=topic_slug[:30]
            )
            path = self.config.MARKDOWN_LOG_OUTPUT_PATH / filename
            path.write_text(markdown_content, encoding="utf-8")
            self.logger.info(f"Markdown 報告已保存: {path}")
        except Exception as e:
            self.logger.error(f"保存 Markdown 報告時發生錯誤: {e}")

    def _save_markdown_part(
        self, markdown_part: str, topic: str, part_num: int, total_parts: int
    ):
        try:
            topic_slug = (
                "".join(c for c in topic if c.isalnum() or c in " -")
                .rstrip()
                .replace(" ", "_")
            )
            filename = self.config.MARKDOWN_FILENAME_TEMPLATE.format(
                date=datetime.now().strftime("%Y%m%d"), topic_slug=topic_slug[:30]
            )
            path = self.config.MARKDOWN_LOG_OUTPUT_PATH / filename

            # 如果是新文件，寫入標題
            if part_num == 1 or not path.exists():
                header = f"# {topic}\n\n---\n\n"
                content = header + markdown_part
            else:
                # 追加內容
                content = "\n\n" + markdown_part

            with open(path, "a", encoding="utf-8") as f:
                f.write(content)

            self.logger.info(f"已保存第 {part_num}/{total_parts} 篇新聞到: {path}")
        except Exception as e:
            self.logger.error(f"保存第 {part_num} 篇新聞時發生錯誤: {e}")

    def _generate_market_summary(self, analyzed_markdown: str) -> str:
        self.logger.info(f"--- [步驟 5/6] 正在生成市場總評...")
        summary_prompt = self.config.SUMMARY_PROMPT_TEMPLATE.format(
            analyzed_markdown=analyzed_markdown
        )
        market_summary_md = self.ai_client.call(
            summary_prompt, self.config.SUMMARY_GENERATION_MODEL
        )
        if not market_summary_md:
            self.logger.warning("市場總評生成失敗,將使用默認內容")
            return "市場總評生成失敗，請稍後再試。"
        return self._clean_control_characters(market_summary_md or "")

    def _clean_control_characters(self, text: str) -> str:
        if not text:
            return ""
        import re

        return re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]", "", text)

    def _send_failure_notification(self, error_message: str):
        try:
            fromaddr = "pigo@pigowen.serv00.net"
            toaddr = ["pigowen@gmail.com"]

            subject = (
                f"⚠️ AI News 分析失敗 - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            )
            body = f"""AI News 分析系統執行失敗！
 
時間: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
錯誤訊息: {error_message}
 
請檢查系統日誌檔案以獲得更多詳細資訊。
 
---
AI News Analysis System
"""

            msg = MIMEText(body, "plain", "utf-8")
            msg["From"] = fromaddr
            msg["To"] = ", ".join(toaddr)
            msg["Subject"] = subject

            context = ssl.create_default_context()
            server = smtplib.SMTP_SSL("mail5.serv00.com", 465, context=context)
            server.login(fromaddr, "3!qX%XsEBECO)ShNEhaS")
            text = msg.as_string()
            server.sendmail(fromaddr, toaddr, text)
            server.quit()

            self.logger.info("失敗通知信件已發送")
        except Exception as e:
            self.logger.error(f"發送失敗通知時發生錯誤: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="AI News 分析與報告生成器", add_help=True
    )
    parser.add_argument(
        "-t",
        "--topic",
        default=f"美國重要財經新聞分析 - {datetime.now().strftime('%Y年%m月%d日')}",
        help="報告的主題標題",
    )
    parser.add_argument("-o", "--output", type=str, help="自訂 HTML 輸出路徑")
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="日誌輸出級別",
    )
    parser.add_argument(
        "--version", action="version", version="AI News Analysis System v1.0.0"
    )
    args = parser.parse_args()

    config_instance = Config()

    if not config_instance.OPENROUTER_API_KEY:
        print(
            "[警告] ⚠️ OPENROUTER_API_KEY 未在 .env 檔案中設定，將使用程式碼中的備用金鑰。"
        )

    if args.output:
        config_instance.HTML_OUTPUT_PATH = Path(args.output)

    logger_instance = setup_logger(
        config_instance.MARKDOWN_LOG_OUTPUT_PATH, config_instance.LOG_FILENAME
    )
    logger_instance.setLevel(getattr(__import__("logging"), args.log_level))

    agent = AI_News_Agent(config_instance, logger_instance)
    success = agent.run(topic=args.topic)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
