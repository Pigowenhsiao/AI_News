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

    def _clean_markdown_content(self, content: str) -> str:
        """清理 Markdown 內容，移除裝飾性元素和無意義內容"""
        if not content:
            return ""

        lines = content.split("\n")
        cleaned_lines = []
        skip_until_empty = False

        for line in lines:
            # 跳過導航連結
            if any(
                skip_text in line
                for skip_text in [
                    "[跳過導航",
                    "[CNBC]",
                    "CNBC標誌",
                    "CNBC logo",
                    "[市場]",
                    "[商業]",
                    "[投資]",
                    "[科技]",
                    "[政治]",
                    "[影片]",
                    "[觀察清單]",
                    "[投資俱樂部]",
                    "[PRO]",
                    "[Pro新聞]",
                    "[登入]",
                    "[建立免費帳戶",
                    "菜單",
                    "搜尋報價",
                    "訂閱CNBC PRO",
                    "[訂閱投資俱樂部]",
                    "[授權與轉載]",
                    "[CNBC委員會]",
                    "[選擇個人理財]",
                    "[加入CNBC小組]",
                    "[字幕]",
                    "[數位產品]",
                    "[新聞稿]",
                    "[實習]",
                    "[更正]",
                    "[關於CNBC]",
                    "[網站地圖]",
                    "[播客]",
                    "[職業]",
                    "[幫助]",
                    "[聯繫]",
                    "[聯繫我們]",
                    "#### 新聞提示",
                    "有機密新聞提示嗎",
                    "免費訂閱新聞通訊",
                    "獲取此內容發送到您的收件箱",
                    "[立即訂閱]",
                    "#### 與我們廣告合作",
                    "[請聯繫我們]",
                    "[廣告選擇]",
                    "[隱私政策]",
                    "您的隱私選擇",
                    "[加州通知]",
                    "[服務條款]",
                    "Copyright",
                    "版權所有",
                    "Versant Media",
                    "數據是實時快照",
                    "數據至少延遲",
                    "市場數據使用條款和免責聲明",
                    "路透社標誌",
                    "發布日期",
                    "重點摘要",
                    "詳細內容",
                    "延伸閱讀",
                    "專家觀點",
                    "更多",
                    "查看直播",
                    "立即觀看",
                    "觀看影片",
                    "影片:",
                    "數位原創",
                    "新聞提示",
                    "與我們廣告合作",
                    "訂閱免費新聞稿",
                    "隱私選項",
                    "加州消費者隱私法",
                ]
            ):
                skip_until_empty = True
                continue

            # 如果處於跳過模式，直到遇到空行才停止
            if skip_until_empty:
                if line.strip() == "":
                    skip_until_empty = False
                continue

            # 跳過裝飾性圖片（CNBC logo 等）
            if re.search(
                r"!\[.*?(CNBC|logo|標誌|圖示|縮圖|導航|footer|header|ad|廣告|裝飾|裝飾性|decorative|icon).*?\]",
                line,
                re.IGNORECASE,
            ):
                continue
            # 跳過小尺寸縮圖圖片
            if re.search(r"!\[縮圖.*?\].*w=\d+&h=\d+", line):
                continue

            # 跳過純連結行（不包含文字內容的單行連結）
            if re.match(r"^\s*\*?\s*\[.*?\]\(.*?\)\s*$", line) and len(line) < 200:
                continue

            # 跳過過長的導航欄（包含很多連結和符號的行）
            if len(line) > 500 and "*" in line and "[" in line:
                continue

            cleaned_lines.append(line)

        cleaned_content = "\n".join(cleaned_lines)
        cleaned_content = re.sub(r"\n{3,}", "\n\n", cleaned_content)
        cleaned_content = cleaned_content.strip()

        return cleaned_content

    def _is_comment_meaningful(self, comment: str, content: str) -> bool:
        """檢查評論是否有實質意義"""
        if not comment:
            return False

        # 移除空白字元後計算實際字符數
        stripped_comment = comment.strip()
        # 計算中文字符和英文單詞的總數
        import unicodedata

        char_count = len(
            [c for c in stripped_comment if unicodedata.category(c)[0] != "Z"]
        )
        if char_count < 20:  # 調整為 20 個字符
            return False

        comment_lower = comment.lower()

        # 檢查是否包含客服/聯絡訊息
        if any(
            phrase in comment_lower
            for phrase in [
                "請聯絡",
                "聯繫我們",
                "如需更多資訊",
                "如有疑問",
                "請聯繫",
                "歡迎聯繫",
                "聯絡方式",
                "客服",
                "如需協助",
                "需要更多資訊",
            ]
        ):
            return False

        # 檢查是否只是空泛的結尾語
        meaningless_patterns = [
            r"^總體而言[，,。]?.*$",
            r"^總的來說[，,。]?.*$",
            r"^整體而言[，,。]?.*$",
            r"^值得注意的是[，,。]?.*$",
            r"^以上分析[，,。]?.*$",
        ]

        for pattern in meaningless_patterns:
            if re.match(pattern, comment.strip()):
                # 如果匹配但還有其他內容，則保留
                if len(comment.strip()) > 100:
                    break
                else:
                    return False

        # 計算評論與新聞內容的相似度
        if content:
            content_words = set(content.split())
            comment_words = set(comment.split())
            if content_words and comment_words:
                common_words = content_words & comment_words
                similarity = (
                    len(common_words) / len(comment_words) if comment_words else 0
                )
                if similarity > 0.8:
                    return False

        return True

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

            # 清理新聞內容：移除裝飾性圖片和導航連結
            content_text = self._clean_markdown_content(content_text)
            comment_text = self._clean_markdown_content(comment_text)

            # 檢查評論質量，如果評論空泛則不顯示
            is_meaningful = self._is_comment_meaningful(comment_text, content_text)
            if not is_meaningful:
                self.logger.info(
                    f"評論質量不足或包含無意義內容，已移除評論: {title_match.group(1)[:50]}"
                )
                comment_text = ""

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
