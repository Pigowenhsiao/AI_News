# AI News 分析系統 - 部署指南

本文件說明如何將 AI News 分析系統轉移到其他電腦並執行。

---

## 必要檔案清單

### 1. 核心程式碼

```
AI_News/
├── AI_News.py                      # 主程式入口
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPI 應用程式
│   │   ├── api/
│   │   │   └── __init__.py         # API 路由
│   │   ├── core/
│   │   │   ├── config.py           # 配置管理
│   │   │   └── logger.py           # 日誌設定
│   │   └── services/
│   │       ├── ai_client.py        # AI 客戶端
│   │       ├── html_generator.py   # HTML 生成器
│   │       ├── news_crawler.py     # 新聞爬蟲
│   │       └── rss_reader.py       # RSS 讀取器
│   └── templates/
│       ├── template.html           # HTML 模板
│       └── template.py             # Jinja2 模板設定
├── .env.example                    # 環境變數範例
├── requirements.txt                 # Python 套件依賴
├── func.md                         # 函數文檔
└── README.md                       # 專案說明
```

### 2. 不需要轉移的檔案

以下檔案和目錄**不需要**轉移（會在新電腦上自動生成）：

- `.venv/` - 虛擬環境（需在新電腦上重新安裝）
- `output/` - HTML 輸出目錄
- `financial_reports/` - Markdown 報告目錄
- `*.log` - 日誌檔案
- `.env` - 環境變數（需在新電腦上設置）
- `__pycache__/` - Python 快取
- `removable/` - 測試檔案

---

## 部署步驟

### 步驟 1: 安裝必要軟體

在新電腦上安裝：

```bash
# Python 3.11 或更高版本
python3 --version

# 檢查 pip 是否可用
pip3 --version
```

### 步驟 2: 複製專案檔案

將以下檔案/目錄複製到新電腦：

```bash
# 在原電腦上，使用 tar 壓縮（Linux/macOS）
tar -czf AI_News.tar.gz \
  AI_News.py \
  backend/ \
  .env.example \
  requirements.txt \
  func.md \
  README.md

# 或使用 rsync
rsync -av --exclude='.venv' \
  --exclude='output' \
  --exclude='financial_reports' \
  --exclude='*.log' \
  --exclude='removable' \
  /path/to/AI_News/ user@new-computer:/path/to/destination/
```

### 步驟 3: 建立虛擬環境

```bash
cd AI_News
python3 -m venv .venv
source .venv/bin/activate  # Linux/macOS
# 或
.venv\Scripts\activate  # Windows
```

### 步驟 4: 安裝套件依賴

```bash
pip install -r requirements.txt
```

### 步驟 5: 安裝 Playwright 瀏覽器

```bash
source .venv/bin/activate
playwright install chromium
```

### 步驟 6: 設置環境變數

複製並編輯 `.env` 檔案：

```bash
cp .env.example .env
nano .env  # 或使用其他編輯器
```

**必要設置：**

```bash
# OpenRouter API Key（必要）
OPENROUTER_API_KEY=sk-or-v1-your-api-key-here

# Tavily API Key（建議，用於 CNN 新聞爬取）
TAVILY_API_KEY=tvly-your-api-key-here

# 自訂輸出路徑（可選）
MARKDOWN_LOG_OUTPUT_PATH=./financial_reports
HTML_OUTPUT_PATH=./output
# 例如：HTML_OUTPUT_PATH=/home/user/Documents/AI_News_Output
```

### 步驟 7: 測試執行

```bash
# 基本測試
python AI_News.py -t "測試報告"

# 指定輸出路徑
python AI_News.py -t "測試報告" -o /custom/output/path
```

### 步驟 8: 設置定時任務（可選）

```bash
# 編輯 crontab
crontab -e

# 添加每日早上 8 點執行
0 8 * * * cd /path/to/AI_News && source .venv/bin/activate && python AI_News.py -t "美國財經新聞分析 - $(date +\%Y年\%m月\%d日)" >> logs/cron.log 2>&1
```

---

## 環境變數說明

### 必要配置

| 變數 | 說明 | 範例 |
|------|------|------|
| `OPENROUTER_API_KEY` | OpenRouter API 金鑰 | `sk-or-v1-xxxxx` |

### 選用配置

| 變數 | 說明 | 範例 |
|------|------|------|
| `TAVILY_API_KEY` | Tavily API 金鑰（CNN 新聞爬取） | `tvly-xxxxx` |
| `ANALYSIS_OUTPUT_MODEL` | AI 模型名稱 | `mistralai/devstral-2512:free` |
| `MAX_ARTICLES_PER_SOURCE` | 每個來源最多文章數 | `10` |
| `MAX_TOTAL_ARTICLES` | 總文章數上限 | `20` |
| `HTML_OUTPUT_PATH` | HTML 輸出路徑 | `./output` 或 `/home/user/Reports` |
| `MARKDOWN_LOG_OUTPUT_PATH` | Markdown 輸出路徑 | `./financial_reports` |
| `MAX_WORKERS` | 並發爬取線程數 | `10` |

---

## 常見問題

### Q: 如何驗證 API Key 是否正確？

```bash
# 測試 OpenRouter
curl https://openrouter.ai/api/v1/models \
  -H "Authorization: Bearer $OPENROUTER_API_KEY"

# 測試 Tavily
curl https://api.tavily.com/search \
  -H "Content-Type: application/json" \
  -d '{"api_key": "tvly-your-key", "query": "test"}'
```

### Q: 輸出路徑設定後目錄不存在怎麼辦？

系統會自動建立輸出目錄，無需手動建立。

### Q: 如何在同一台電腦上執行多個實例？

可以透過修改 `HTML_OUTPUT_PATH` 和 `MARKDOWN_LOG_OUTPUT_PATH` 來區分不同實例：

```bash
# 實例 1
export HTML_OUTPUT_PATH=./output_instance1
python AI_News.py

# 實例 2
export HTML_OUTPUT_PATH=./output_instance2
python AI_News.py
```

---

## 最小化部署清單

如果只想執行基本功能，最少需要以下檔案：

```
AI_News.py
backend/app/main.py
backend/app/core/__init__.py
backend/app/core/config.py
backend/app/core/logger.py
backend/app/services/__init__.py
backend/app/services/ai_client.py
backend/app/services/html_generator.py
backend/app/services/news_crawler.py
backend/app/services/rss_reader.py
backend/templates/template.html
backend/templates/template.py
requirements.txt
.env.example
```

---

## API 服務部署

如果要部署 API 服務：

### 開發模式

```bash
source .venv/bin/activate
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 生產模式（使用 Gunicorn）

```bash
pip install gunicorn
gunicorn backend.app.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000
```

### 使用 systemd 守護進程

```bash
# 建立服務檔案 /etc/systemd/system/ai-news.service
[Unit]
Description=AI News Analysis API
After=network.target

[Service]
Type=notify
User=www-data
WorkingDirectory=/path/to/AI_News
Environment="PATH=/path/to/AI_News/.venv/bin"
EnvironmentFile=/path/to/AI_News/.env
ExecStart=/path/to/AI_News/.venv/bin/gunicorn backend.app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
Restart=always

[Install]
WantedBy=multi-user.target

# 啟動服務
sudo systemctl daemon-reload
sudo systemctl enable ai-news
sudo systemctl start ai-news
```

---

## 檔案權限確保

```bash
# 確保輸出目錄可寫入
chmod 755 ./output
chmod 755 ./financial_reports

# 確保 .env 檔案權限安全
chmod 600 .env
```

---

## 備份與還原

### 備份

```bash
# 備份程式碼
tar -czf ai-news-code-$(date +%Y%m%d).tar.gz \
  AI_News.py \
  backend/ \
  requirements.txt \
  .env.example \
  func.md \
  README.md

# 備份輸出檔案
tar -czf ai-news-data-$(date +%Y%m%d).tar.gz \
  output/ \
  financial_reports/
```

### 還原

```bash
# 還原程式碼
tar -xzf ai-news-code-YYYYMMDD.tar.gz

# 還原輸出檔案
tar -xzf ai-news-data-YYYYMMDD.tar.gz
```

---

## 版本控制建議

建議將以下檔案提交到 Git：

```
AI_News.py
backend/
requirements.txt
.env.example
func.md
README.md
DEPLOYMENT.md
```

**不要提交的檔案（已在 .gitignore 中設定）：**

```
.venv/
.env
output/
financial_reports/
*.log
__pycache__/
```

---

## 技術支援

如有問題，請參考：
- [README.md](./README.md) - 專案說明
- [func.md](./func.md) - 函數文檔
- [AGENTS.md](./AGENTS.md) - 開發者指南
