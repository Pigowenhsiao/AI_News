import os
import socket
from pathlib import Path
from typing import List, Dict
from dataclasses import dataclass, field
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Config:
    OPENROUTER_API_KEY: str = os.getenv(
        "OPENROUTER_API_KEY",
        "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",
    )
    TAVILY_API_KEY: str = os.getenv("TAVILY_API_KEY", "")
    AVAILABLE_MODELS: List[str] = field(
        default_factory=lambda: [
            "mistralai/devstral-2512:free",
            "moonshotai/kimi-k2:free",
            "deepseek/deepseek-r1-0528:free",
            "nex-agi/deepseek-v3.1-nex-n1:free",
        ]
    )
    ANALYSIS_OUTPUT_MODEL: str = "mistralai/devstral-2512:free"
    SUMMARY_GENERATION_MODEL: str = "mistralai/devstral-2512:free"
    OPENROUTER_API_URL: str = "https://openrouter.ai/api/v1/chat/completions"
    OPENROUTER_TIMEOUT: int = 300
    OPENROUTER_MAX_TOKENS: int = 8192
    OPENROUTER_MAX_RETRIES: int = 3
    OPENROUTER_BASE_DELAY: int = 5
    WAYBACK_API_URL: str = "https://archive.org/wayback/available?url="
    CNN_BUSINESS_HOME_URL: str = "https://edition.cnn.com/business"
    RSS_REQUEST_HEADERS: Dict[str, str] = field(
        default_factory=lambda: {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/rss+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9,zh-TW;q=0.8,zh;q=0.7",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
        }
    )
    CNBC_RSS_URLS: List[str] = field(
        default_factory=lambda: [
            "https://www.cnbc.com/id/100003114/device/rss/rss.html",
            "https://www.cnbc.com/id/100727362/device/rss/rss.html",
        ]
    )
    REUTERS_BUSINESS_RSS_URLS: List[str] = field(default_factory=lambda: [])
    BLOOMBERG_RSS_URLS: List[str] = field(
        default_factory=lambda: [
            "https://feeds.bloomberg.com/markets/news.rss",
        ]
    )
    FORTUNE_RSS_URLS: List[str] = field(
        default_factory=lambda: [
            "https://fortune.com/feed/",
        ]
    )
    YAHOO_FINANCE_RSS_URLS: List[str] = field(
        default_factory=lambda: [
            "https://finance.yahoo.com/news/rss",
        ]
    )
    MARKETWATCH_RSS_URLS: List[str] = field(
        default_factory=lambda: [
            "https://feeds.marketwatch.com/marketwatch/topstories",
        ]
    )
    CNN_BUSINESS_RSS_URLS: List[str] = field(default_factory=lambda: [])
    MAX_ARTICLES_PER_SOURCE: int = 10
    MAX_TOTAL_ARTICLES: int = 40
    ALLOWED_DOMAINS: List[str] = field(
        default_factory=lambda: [
            "wsj.com",
            "bloomberg.com",
            "cnbc.com",
            "marketwatch.com",
            "fortune.com",
            "cnn.com",
            "apnews.com",
            "bbc.com",
        ]
    )
    MAX_SEARCH_RESULTS: int = 50
    ARTICLE_MIN_LENGTH: int = 250
    SCRAPE_TIMEOUT: int = 20
    MAX_WORKERS: int = 10
    MARKDOWN_LOG_OUTPUT_PATH: Path = Path(
        os.getenv("MARKDOWN_LOG_OUTPUT_PATH", "./financial_reports")
    )
    HTML_OUTPUT_PATH: Path = Path(os.getenv("HTML_OUTPUT_PATH", "./output"))
    HTML_FILENAME: str = "index.html"
    MARKDOWN_FILENAME_TEMPLATE: str = "美國財經新聞分析_{date}_{topic_slug}.md"
    LOG_FILENAME: str = "ai_news_analyzer.log"
    JINJA_TEMPLATE_FILE: str = "template.html"
    SINGLE_ARTICLE_ANALYSIS_PROMPT: str = (
        "您是一位具有20年工作經驗的金融分析師，專精美國財經市場並熟悉台灣的投資環境。請根據以下提供的 **英文原文** 新聞：\n\n"
        "--- START OF NEWS ARTICLE ---\n\n{news_content}\n\n--- END OF NEWS ARTICLE ---\n\n"
        "您的任務是：\n"
        "1.  將新聞的【標題】和【完整內容】專業地翻譯成 **台灣繁體中文**。翻譯時需確保金融術語的準確性，並符合台灣讀者的閱讀習慣。公司名稱（如 Apple, NVIDIA）和常見金融商品（如 S&P 500, NASDAQ）可保留英文原文，人名除非有廣為人知的標準台灣譯名（例如：葉倫、鮑爾），否則也請保留英文原文。\n"
        "2.  在新聞的【完整內容】（即翻譯後的中文新聞全文）之後，立即添加您的【專業評論】。此評論需針對該新聞事件提供犀利且獨到的見解，並使用台灣常用的金融術語（例如：聯準會、美金）。\n\n"
        "最終，請將此篇新聞的分析結果按照以下 Markdown 格式輸出。不要包含任何額外的對話或解釋。\n\n"
        "範例格式：\n"
        "## [翻譯後的新聞標題]\n"
        "- **新聞日期**: [YYYY-MM-DD]\n"
        "- **新聞來源**: [來源中文名](原始URL)\n\n"
        "### 內容\n"
        "[翻譯後的新聞全文...]\n\n"
        "### 專業評論\n"
        "[您的專業評論...]\n\n"
        "---\n"
    )
    ANALYSIS_PROMPT_TEMPLATE: str = (
        "您是一位具有20年工作經驗的金融分析師，專精美國財經市場並熟悉台灣的投資環境。請根據以下提供的 **英文原文** 新聞：\n\n"
        "--- START OF NEWS ARTICLES ---\n\n{news_content}\n\n--- END OF NEWS ARTICLES ---\n\n"
        "您的任務是：\n"
        "1.  將每則新聞的【標題】和【完整內容】專業地翻譯成 **台灣繁體中文**。翻譯時需確保金融術語的準確性，並符合台灣讀者的閱讀習慣。公司名稱（如 Apple, NVIDIA）和常見金融商品（如 S&P 500, NASDAQ）可保留英文原文，人名除非有廣為人知的標準台灣譯名（例如：葉倫、鮑爾），否則也請保留英文原文。\n"
        "2.  在每一則新聞的【完整內容】（即翻譯後的中文新聞全文）之後，立即添加您的【專業評論】。此評論需針對該新聞事件提供犀利且獨到的見解，並使用台灣常用的金融術語（例如：聯準會、美金）。\n"
        "3.  保留新聞的【新聞日期】和【新聞來源】（包含原始連結）資訊。\n\n"
        "最終，請將所有處理完畢的新聞整合起來，並嚴格按照以下 Markdown 格式輸出。不要包含任何額外的對話或解釋。\n\n"
        "範例格式：\n"
        "## [翻譯後的新聞標題]\n"
        "- **新聞日期**: [YYYY-MM-DD]\n"
        "- **新聞來源**: [來源中文名](原始URL)\n\n"
        "### 內容\n"
        "[翻譯後的新聞全文...]\n\n"
        "### 專業評論\n"
        "[您的專業評論...]\n\n"
        "---\n"
    )
    RAW_NEWS_MARKDOWN_TEMPLATE: str = (
        "## {title}\n"
        "- **新聞來源**: [{source_display_name}]({url})\n\n"
        "### 內容\n{content}\n"
    )
    SUMMARY_PROMPT_TEMPLATE: str = (
        "您是一位具有20年工作經驗的資深財經專家。請基於以下已翻譯並附上單篇評論的財經新聞內容，撰寫一段約200-300字的 **『本日市場總評』**。\n\n"
        "這段總評需要：\n"
        "- **宏觀視角**：整合所有新聞的觀點，而不僅是重複單篇評論。\n"
        "- **深入獨到**：提出對未來市場趨勢的綜合性、前瞻性看法。\n"
        "- **專業語言**：使用台灣投資人熟悉的金融術語。\n"
        "- **直接輸出**：請直接輸出總評內容，不要包含任何額外的標題或引言。確保所有文字輸出均為 **台灣繁體中文**。\n\n"
        "--- START OF ANALYZED NEWS ---\n\n{analyzed_markdown}\n\n--- END OF ANALYZED NEWS ---"
    )
    HOSTNAME: str = socket.gethostname()

    def __post_init__(self):
        self.MARKDOWN_LOG_OUTPUT_PATH.mkdir(parents=True, exist_ok=True)
        self.HTML_OUTPUT_PATH.mkdir(parents=True, exist_ok=True)
