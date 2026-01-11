# 函數文檔 (func.md)

## 目錄

- [主程式](#主程式)
- [核心模組](#核心模組)
- [服務模組](#服務模組)

---

## 主程式

### AI_News_Agent.run(topic: str) -> bool

**功能：** 執行完整的 AI News 分析流程，從 RSS 爬取到 HTML 報告生成

**參數：**
- `topic`: str - 報告主題標題

**回傳：**
- `bool`: True 表示成功，False 表示失敗

**流程：**
1. 從 CNBC、CNN Business 獲取新聞列表
2. 使用 crawl4ai 並發爬取新聞內容
3. **逐一呼叫 AI 翻譯並分析新聞（避免上下文限制）**
4. **每篇新聞分析完成後立即追加到 Markdown 文件**
5. 生成市場總評
6. 使用 Jinja2 渲染 HTML 報告

**範例：**
```python
agent = AI_News_Agent(config, logger)
success = agent.run("美國財經新聞分析 - 2026年01月10日")
```

---

### AI_News_Agent._generate_markdown_report_sequentially(articles: List[Dict], topic: str) -> str

**功能：** 逐一分析新聞並生成 Markdown 報告

**參數：**
- `articles`: List[Dict] - 新聞列表
- `topic`: str - 報告主題

**回傳：**
- `str`: 完整的 Markdown 報告，失敗時返回空字符串

**特點：**
- 每篇新聞獨立傳送給 AI，避免上下文限制
- 每篇新聞分析完成後立即保存到 Markdown 文件
- 記錄每篇新聞的處理進度

---

### AI_News_Agent._save_markdown_part(markdown_part: str, topic: str, part_num: int, total_parts: int) -> None

**功能：** 追加單篇新聞分析結果到 Markdown 文件

**參數：**
- `markdown_part`: str - 單篇新聞的 Markdown 內容
- `topic`: str - 報告主題
- `part_num`: int - 當前新聞編號
- `total_parts`: int - 總新聞數量

---

## 核心模組

### Config

**檔案：** `backend/app/core/config.py`

**功能：** 集中管理所有設定參數

**主要屬性：**
- `OPENROUTER_API_KEY`: AI 模型 API 金鑰
- `TAVILY_API_KEY`: Tavily API 金鑰（用於爬取 CNN 新聞）
- `AVAILABLE_MODELS`: 可用 AI 模型列表
- `ANALYSIS_OUTPUT_MODEL`: 分析模型名稱
- `CNBC_RSS_URLS`: CNBC RSS 來源列表
- `CNN_BUSINESS_RSS_URLS`: CNN RSS 來源列表
- `HTML_OUTPUT_PATH`: HTML 輸出路徑（可透過 .env 設置）
- `MARKDOWN_LOG_OUTPUT_PATH`: Markdown 日誌輸出路徑（可透過 .env 設置）

**使用方式：**
```python
from backend.app.core.config import Config
config = Config()
print(config.HTML_OUTPUT_PATH)
```

---

### setup_logger(log_dir: Path, log_filename: str) -> Logger

**檔案：** `backend/app/core/logger.py`

**功能：** 設定日誌系統，輸出到控制台和檔案

**參數：**
- `log_dir`: Path - 日誌檔案目錄
- `log_filename`: str - 日誌檔案名稱

**回傳：**
- `Logger`: 配置好的 logger 實例

**使用方式：**
```python
from backend.app.core.logger import setup_logger
from pathlib import Path
logger = setup_logger(Path("./logs"), "app.log")
logger.info("系統啟動")
```

---

## 服務模組

### RSSReader.fetch_all_rss() -> List[Dict]

**檔案：** `backend/app/services/rss_reader.py`

**功能：** 從所有配置的 RSS 來源獲取新聞列表

**回傳：**
- `List[Dict]`: 新聞列表，每個字典包含 title, url, description, source_domain, source_name, published

**使用方式：**
```python
from backend.app.services.rss_reader import RSSReader
reader = RSSReader(config, logger)
news_items = reader.fetch_all_rss()
```

---

### NewsCrawler.scrape_articles_concurrently(rss_items: List[Dict]) -> List[Dict]

**檔案：** `backend/app/services/news_crawler.py`

**功能：** 並發爬取新聞內容，優先使用 crawl4ai，失敗時回退到 BeautifulSoup

**參數：**
- `rss_items`: List[Dict] - RSS 新聞列表

**回傳：**
- `List[Dict]`: 包含完整內容的新聞列表

**使用方式：**
```python
from backend.app.services.news_crawler import NewsCrawler
crawler = NewsCrawler(config, logger)
articles = crawler.scrape_articles_concurrently(news_items)
```

**爬取策略：**
- CNN 新聞：優先使用 Tavily API → crawl4ai → BeautifulSoup
- Bloomberg 新聞：優先使用 crawl4ai (with retry) → 改進請求頭 → Tavily API
- 其他新聞（CNBC、Fortune、Yahoo Finance、MarketWatch）：優先使用 crawl4ai (with retry) → BeautifulSoup

**crawl4ai 優化配置：**
- 真實瀏覽器 User-Agent
- 完整瀏覽器請求頭（Accept、Accept-Language 等）
- 支援重試機制（默認 3 次，Bloomberg 2 次）
- 禁用外部圖片和 JavaScript 以加速爬取
- 繞過快取以確保獲取最新內容

---

### NewsCrawler._get_crawl4ai_config() -> (BrowserConfig, CrawlerRunConfig)

**檔案：** `backend/app/services/news_crawler.py`

**功能：** 獲取 crawl4ai 的優化配置

**回傳：**
- `BrowserConfig`: 瀏覽器配置
- `CrawlerRunConfig`: 爬取配置

**配置特點：**
- 真實瀏覽器 User-Agent
- 完整瀏覽器請求頭
- 禁用外部圖片
- 繞過快取

---

### NewsCrawler._crawl_with_crawl4ai_with_retry(url: str, max_retries: int = 3) -> Optional[str]

**檔案：** `backend/app/services/news_crawler.py`

**功能：** 使用 crawl4ai 爬取，支援重試機制

**參數：**
- `url`: str - 新聞 URL
- `max_retries`: int - 最多重試次數（默認 3）

**回傳：**
- `Optional[str]`: 新聞內容，失敗返回 None

**重試機制：**
- 首次失敗後等待 2 秒重試
- 連線關閉錯誤（ERR_CONNECTION_CLOSED）後等待 3 秒重試
- 達到最大重試次數後返回 None

---

### NewsCrawler._crawl_with_crawl4ai(url: str) -> Optional[str]

**檔案：** `backend/app/services/news_crawler.py`

**功能：** 使用 crawl4ai 爬取（內部方法，調用 _crawl_with_crawl4ai_with_retry）

**參數：**
- `url`: str - 新聞 URL

**回傳：**
- `Optional[str]`: 新聞內容，失敗返回 None

---

### NewsCrawler._scrape_with_tavily(url: str) -> Optional[str]

**檔案：** `backend/app/services/news_crawler.py`

**功能：** 使用 Tavily API 爬取新聞內容（專門用於 CNN 新聞）

**參數：**
- `url`: str - 新聞 URL

**回傳：**
- `Optional[str]`: 新聞內容，失敗返回 None

---

### AIModelClient.call(prompt: str, model_name: str, max_model_failures: int = 3) -> Optional[str]

**檔案：** `backend/app/services/ai_client.py`

**功能：** 呼叫 OpenRouter AI 模型進行文字生成，支援自動切換模型

**參數：**
- `prompt`: str - 提示詞
- `model_name`: str - 模型名稱
- `max_model_failures`: int - 最多嘗試多少個模型

**回傳：**
- `Optional[str]`: AI 生成的文字，失敗返回 None

**使用方式：**
```python
from backend.app.services.ai_client import AIModelClient
client = AIModelClient(config, logger)
result = client.call("請翻譯以下文字...", "mistralai/devstral-2512:free")
```

---

### HTMLGenerator.parse_and_render_html(markdown_report: str, market_summary_md: str, topic_title: str) -> bool

**檔案：** `backend/app/services/html_generator.py`

**功能：** 解析 Markdown 並渲染 HTML 報告

**參數：**
- `markdown_report`: str - AI 生成的 Markdown 報告
- `market_summary_md`: str - 市場總評 Markdown
- `topic_title`: str - 報告主題

**回傳：**
- `bool`: 成功返回 True，失敗返回 False

**特點：**
- 自動清理新聞內容中的裝飾性元素（導航連結、Logo、客服訊息）
- 移除無意義的裝飾性圖片
- 過濾質量不佳的 AI 評論（短評論、客服訊息、空泛內容）
- 只保留有實質見解的專業評論

**使用方式：**
```python
from backend.app.services.html_generator import HTMLGenerator
generator = HTMLGenerator(config, logger)
success = generator.parse_and_render_html(md_report, summary, "主題")
```

---

### HTMLGenerator._clean_markdown_content(content: str) -> str

**檔案：** `backend/app/services/html_generator.py`

**功能：** 清理 Markdown 內容，移除裝飾性元素和無意義內容

**參數：**
- `content`: str - 原始 Markdown 內容

**回傳：**
- `str`: 清理後的 Markdown 內容

**過濾內容：**
- 導航連結（如：[市場]、[商業]、[投資]）
- CNBC Logo 和裝飾性圖片
- 頁面底部連結（聯繫我們、隱私政策等）
- 純連結行和過長的導航欄
- 客服訊息（如：聯繫我們、訂閱等）

**使用方式：**
```python
from backend.app.services.html_generator import HTMLGenerator
generator = HTMLGenerator(config, logger)
cleaned = generator._clean_markdown_content(raw_content)
```

---

### HTMLGenerator._is_comment_meaningful(comment: str, content: str) -> bool

**檔案：** `backend/app/services/html_generator.py`

**功能：** 檢查評論是否有實質意義

**參數：**
- `comment`: str - 評論內容
- `content`: str - 新聞內容（用於檢查相似度）

**回傳：**
- `bool`: True 表示評論有意義，False 表示需要移除

**判斷標準：**
- 評論長度 < 50 字符 → False
- 包含客服訊息（如：請聯繫、如需更多資訊）→ False
- 只是空泛的結尾語（如：總體而言、總的來說）且無其他內容 → False
- 與新聞內容重複度 > 80% → False

**使用方式：**
```python
from backend.app.services.html_generator import HTMLGenerator
generator = HTMLGenerator(config, logger)
is_good = generator._is_comment_meaningful(comment, news_content)
```

---

## 命令列使用

### 基本使用

```bash
# 使用默認主題執行
python AI_News.py

# 指定主題
python AI_News.py -t "AI 產業分析"

# 指定輸出路徑
python AI_News.py -o /path/to/output

# 設置日誌級別
python AI_News.py --log-level DEBUG

# 顯示說明
python AI_News.py --help
```

### Crontab 設定

```bash
# 每天早上 8 點執行
0 8 * * * cd /path/to/AI_News && python AI_News.py >> logs/cron.log 2>&1
```

---

## 配置檔案

### .env 配置範例

```bash
OPENROUTER_API_KEY=sk-or-v1-your-key
ANALYSIS_OUTPUT_MODEL=mistralai/devstral-2512:free
HTML_OUTPUT_PATH=./output
MARKDOWN_LOG_OUTPUT_PATH=./financial_reports
MAX_ARTICLES_PER_SOURCE=15
MAX_TOTAL_ARTICLES=50
```
