import re
import socket
import logging
import markdown
from datetime import datetime
from pathlib import Path
from typing import Optional
from jinja2 import Environment, FileSystemLoader
from ..core.config import Config


class HTMLGenerator:
    def __init__(self, config: Config, logger: logging.Logger):
        self.config = config
        self.logger = logger
        script_dir = Path(__file__).resolve().parent.parent.parent
        self.jinja_env = Environment(loader=FileSystemLoader(script_dir / "templates"))

    def parse_and_render_html(
        self, markdown_report: str, market_summary_md: str, topic_title: str
    ) -> bool:
        self.logger.info(f"--- [步驟 6/6] 正在解析 Markdown 並生成 HTML...")
        articles = []
        normalized_report = markdown_report.replace("\r\n", "\n").strip()
        # 使用更簡單的匹配：以 ## 開頭，後面不是 #
        blocks = re.split(r"(?m)(?=^##[^#])", normalized_report)
        self.logger.info(f"Markdown 報告共分割成 {len(blocks)} 個區塊")
        for i, block in enumerate(blocks):
            block = block.strip()
            if not block or len(block) < 50:
                continue
            title_match = re.search(r"^##\s*(.*?)\s*$", block, re.M)
            date_match = re.search(
                r"^- \*\*新聞日期\*\*:\s*(\d{4}-\d{2}-\d{2}[^\n]*)\s*$", block, re.M
            )
            source_match = re.search(
                r"^- \*\*新聞來源\*\*:\s*\[(.*?)\]\((.*?)\)\s*$", block, re.M
            )
            if not title_match or not source_match:
                title_preview = title_match.group(1)[:60] if title_match else "無標題"
                source_preview = (
                    source_match.group(1)[:30] if source_match else "無來源"
                )
                self.logger.warning(
                    f"跳過無效的 Markdown 區塊 #{i + 1}: 標題={title_preview}, 來源={source_preview}"
                )
                continue
            section_headers = list(
                re.finditer(r"^###\s*(內容|專業評論)\s*$", block, re.M)
            )
            content_text = ""
            comment_text = ""
            if section_headers:
                content_start = section_headers[0].end()
                content_end = (
                    section_headers[1].start()
                    if len(section_headers) > 1
                    else len(block)
                )
                content_text = block[content_start:content_end].strip()
                if len(section_headers) > 1:
                    comment_start = section_headers[1].end()
                    comment_text = block[comment_start:].strip()
            content_text = re.sub(r"\n---\s*$", "", content_text).strip()
            comment_text = re.sub(r"\n---\s*$", "", comment_text).strip()
            articles.append(
                {
                    "title": title_match.group(1).strip(),
                    "date": date_match.group(1).strip() if date_match else "",
                    "source": source_match.group(1).strip(),
                    "url": source_match.group(2).strip(),
                    "content_html": markdown.markdown(content_text),
                    "comment_html": markdown.markdown(comment_text),
                }
            )
        if not articles:
            self.logger.error("無法從 AI 分析結果解析出新聞,跳過 HTML 生成")
            self._log_html_fail()
            return False
        self.logger.info(f"從 Markdown 解析出 {len(articles)} 則新聞")
        now = datetime.now()
        article_gen_time = (
            articles[0]["date"]
            if articles and "date" in articles[0]
            else now.strftime("%Y年%m月%d日 %H:%M:%S")
        )
        ai_model = self.config.ANALYSIS_OUTPUT_MODEL
        hostname = socket.gethostname()
        template_data = {
            "title": topic_title,
            "articles": articles,
            "market_summary_html": markdown.markdown(market_summary_md),
            "current_year": now.year,
            "html_gen_time": now.strftime("%Y年%m月%d日 %H:%M:%S"),
            "now_time": now.strftime("%Y-%m-%d %H:%M:%S"),
            "ai_model": ai_model,
            "hostname": hostname,
            "article_gen_time": article_gen_time,
        }
        try:
            template = self.jinja_env.get_template(self.config.JINJA_TEMPLATE_FILE)
            html_output = template.render(template_data)
            output_path = self.config.HTML_OUTPUT_PATH / self.config.HTML_FILENAME
            output_path.write_text(html_output, encoding="utf-8")
            self.logger.info(f"完成報告生成! HTML 已輸出到: {output_path}")
            return True
        except Exception as e:
            self.logger.error(f"生成 HTML 時發生錯誤: {e}", exc_info=True)
            self._log_html_fail()
            return False

    def _log_html_fail(self):
        fail_report_path = (
            self.config.MARKDOWN_LOG_OUTPUT_PATH / "Generat_Fail_Report.txt"
        )
        today_str = datetime.now().strftime("%Y-%m-%d")
        fail_count = 1
        try:
            if fail_report_path.exists():
                with fail_report_path.open("r", encoding="utf-8") as f:
                    lines = f.readlines()
                today_lines = [line for line in lines if line.startswith(today_str)]
                if today_lines:
                    last_line = today_lines[-1]
                    try:
                        last_count = int(last_line.strip().split()[-1])
                        fail_count = last_count + 1
                    except Exception:
                        fail_count = 1
        except Exception:
            fail_count = 1
        try:
            with fail_report_path.open("a", encoding="utf-8") as f:
                f.write(f"{today_str} Generate fail {fail_count}\n")
        except Exception as e:
            self.logger.error(f"寫入失敗報告時發生錯誤: {e}")
