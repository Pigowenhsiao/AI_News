# AI News 分析系統

基於 AI 的美國財經新聞分析與報告生成系統，使用 Crawl4AI 爬取新聞內容，整合 OpenRouter API 進行智能分析，生成 HTML 報告。

## 功能特點

- 📰 **自動爬取新聞** - 從 CNBC、CNN Business 網站獲取最新新聞
- 🤖 **AI 智能分析** - 翻譯、摘要、專業評論、市場總評
- 📄 **生成 HTML 報告** - 響應式設計、動態時間顯示
- ⚡ **高效並發爬取** - 使用 Crawl4AI 和線程池並發處理
- 🔄 **逐一分析** - 每篇新聞獨立分析，避免上下文容量限制
- 💾 **實時保存** - 每篇新聞分析完成後立即保存到 Markdown 文件
- 🕒 **定時執行支援** - 可通過 crontab 設置每日自動執行
- 🌐 **RESTful API** - 提供完整的 API 介面供整合使用
- 🧹 **智能內容清理** - 自動移除裝飾性圖片、導航連結、客服訊息
- ✅ **評論質量過濾** - 自動移除空泛評論，只保留有實質見解的專業評論

## 快速開始

### 1. 建立虛擬環境

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. 安裝依賴

```bash
pip install -r requirements.txt
```

### 3. 安裝 Playwright 瀏覽器

Crawl4AI 使用 Playwright 底層進行網頁爬取。首次運行時需要安裝瀏覽器：

```bash
source .venv/bin/activate
playwright install chromium
```

### 4. 配置環境變數

```bash
cp .env.example .env
# 編輯 .env 設置您的 OPENROUTER_API_KEY 和 TAVILY_API_KEY
```

**必要配置：**
- `OPENROUTER_API_KEY`: AI 模型 API 金鑰
- `TAVILY_API_KEY`: Tavily API 金鑰（用於 CNN 新聞爬取）

**可選配置：**
- `HTML_OUTPUT_PATH`: HTML 報告輸出路徑（默認：`./output`）
- `MARKDOWN_LOG_OUTPUT_PATH`: Markdown 報告輸出路徑（默認：`./financial_reports`）
- `MAX_ARTICLES_PER_SOURCE`: 每個來源最多文章數（默認：25）
- `MAX_TOTAL_ARTICLES`: 總文章數上限（默認：50）

### 5. 執行分析

```bash
# 基本執行
python AI_News.py

# 指定主題
python AI_News.py -t "AI 產業分析 - 2026年01月10日"

# 指定輸出路徑
python AI_News.py -o /path/to/output
```

### 6. 查看 HTML 報告

執行完成後，HTML 報告將輸出到 `output/index.html`

**執行特性：**
- ✅ **逐一分析** - 每篇新聞獨立傳送給 AI，避免上下文限制
- ✅ **實時保存** - 每篇新聞分析完成後立即保存到 Markdown 文件
- ✅ **進度顯示** - 日誌顯示「第 X/50 篇新聞分析完成」
- ✅ **容錯恢復** - 中斷後可從已保存的 Markdown 繼續處理

**注意：** 完整分析流程大約需要 **5-10 分鐘**（50 篇新聞），取決於 AI 模型回應速度和網路連線狀況。

---

## 轉移到其他電腦

如需將系統轉移到其他電腦執行，請參考 [DEPLOYMENT.md](./DEPLOYMENT.md) 部署指南。

**快速打包：**
```bash
# 使用自動打包腳本
./package.sh

# 或手動打包
cd /path/to/AI_News
mkdir -p /tmp/ai-news-package
cp AI_News.py backend/ requirements.txt .env.example README.md func.md DEPLOYMENT.md /tmp/ai-news-package/
cd /tmp
tar -czf ai-news-package.tar.gz ai-news-package/
```

## 快速打包

**方法 1：使用自動打包腳本（推薦）**
```bash
cd /path/to/AI_News
./package.sh
```

**方法 2：手動打包**
```bash
# 使用自動打包腳本
./package.sh

# 或手動打包
cd /path/to/AI_News
mkdir -p /tmp/ai-news-package
cp AI_News.py backend/ requirements.txt .env.example README.md func.md DEPLOYMENT.md /tmp/ai-news-package/
cd /tmp
tar -czf ai-news-package.tar.gz ai-news-package/
```

**打包內容：**
- ✅ 核心程式碼（AI_News.py + backend/）
- ✅ 依賴配置（requirements.txt + .env.example）
- ✅ 文檔（README.md + func.md + DEPLOYMENT.md）
- ✅ 打包說明（DEPLOY_README.txt）

**不需要打包：**
- .venv/ - 需在新電腦重建
- output/ - 會自動建立
- financial_reports/ - 會自動建立
- .env - 包含 API Key

---

## API 服務

### 啟動 API 服務

#### 開發模式

```bash
source venv/bin/activate
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```

#### 生產模式

```bash
# 使用 gunicorn 啟動
gunicorn backend.app.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --access-logfile logs/access.log \
  --error-logfile logs/error.log
```

### API 文檔

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### API 端點

#### GET /

API 根端點，返回可用端點列表。

**回傳：**
```json
{
  "message": "AI News Analysis API",
  "version": "1.0.0",
  "docs": "/docs",
  "endpoints": {
    "POST /api/analyze": "觸發新聞分析",
    "GET /api/news": "獲取新聞列表",
    "GET /api/report": "獲取 HTML 報告",
    "GET /api/status": "系統狀態"
  }
}
```

#### GET /api/status

獲取系統狀態資訊。

**回傳：**
```json
{
  "status": "running",
  "api_key_configured": true,
  "model": "mistralai/devstral-2512:free",
  "last_update": "2026-01-10T08:09:11.263956",
  "hostname": "pigo-T156"
}
```

#### POST /api/analyze

觸發新聞分析任務（背景執行）。

**請求：**
```json
{
  "topic": "美國重要財經新聞分析 - 2026年01月10日",
  "return_html": false
}
```

**回傳：**
```json
{
  "message": "分析任務已啟動",
  "topic": "美國重要財經新聞分析 - 2026年01月10日",
  "status": "running"
}
```

#### GET /api/report

獲取 HTML 報告。

**回傳：** HTML 文件（Content-Type: text/html）

**錯誤回傳：**
```json
{
  "detail": "尚未生成報告，請先執行 /api/analyze"
}
```

#### GET /api/news

獲取新聞列表（目前返回提示信息，建議使用 /api/report 查看完整報告）。

**參數：**
- `limit`: 每頁數量（默認 10）
- `offset`: 偏移量（默認 0）

#### GET /api/health

健康檢查端點。

**回傳：**
```json
{
  "status": "healthy",
  "timestamp": "2026-01-10T08:13:33.177652"
}
```

## 定時任務設置

```bash
# 編輯 crontab
crontab -e

# 添加每日早上 8 點執行
0 8 * * * cd /path/to/AI_News && source venv/bin/activate && python AI_News.py -t "美國財經新聞分析 - $(date +\%Y年\%m月\%d日)" >> logs/cron.log 2>&1
```

## 專案結構

```
AI_News/
├── AI_News.py                 # 主入口腳本
├── backend/
│   ├── app/
│   │   ├── api/            # FastAPI 路由
│   │   ├── core/           # 核心模組（設定、日誌）
│   │   └── services/       # 服務模組（爬取、AI、HTML）
│   ├── main.py             # FastAPI 主應用程式
│   ├── templates/          # Jinja2 模板
│   └── requirements.txt    # Python 依賴
├── venv/                    # 虛擬環境
├── output/                  # HTML 輸出目錄
├── financial_reports/        # Markdown 報告目錄
├── .env.example            # 環境變數範例
├── func.md                  # 函數文檔
└── README.md
```

## 配置說明

主要配置項（.env 檔案）：

| 選項 | 說明 | 默認值 |
|------|------|--------|
| OPENROUTER_API_KEY | AI 模型 API 金鑰 | - |
| ANALYSIS_OUTPUT_MODEL | 分析模型名稱 | mistralai/devstral-2512:free |
| MAX_ARTICLES_PER_SOURCE | 每個來源最多文章數 | 15 |
| MAX_TOTAL_ARTICLES | 總文章數上限 | 50 |
| MAX_WORKERS | 並發爬取線程數 | 10 |
| HTML_OUTPUT_PATH | HTML 輸出路徑 | ./output |

## 技術棧

- **Python 3.11+**
- **FastAPI** - Web 框架
- **Crawl4AI** - 網頁爬取（使用 Playwright 底層）
- **BeautifulSoup4** - HTML 解析（備用方案）
- **Tavily API** - CNN 新聞爬取（專用）
- **OpenRouter API** - AI 模型
- **Jinja2** - 模板引擎
- **Markdown** - Markdown 轉 HTML
- **Uvicorn/Gunicorn** - ASGI 伺服器

## Crawl4AI 配置

Crawl4AI 使用 Playwright 底層進行網頁爬取。安裝步驟：

```bash
# 安裝 Playwright 瀏覽器
source .venv/bin/activate
playwright install chromium
```

爬取策略：
1. **CNN 新聞** - 優先使用 Tavily API → crawl4ai → BeautifulSoup
2. **CNBC 新聞** - 優先使用 crawl4ai → BeautifulSoup
3. 兩者都失敗時使用 RSS 摘要

## 新聞來源

- **CNBC** - 從 RSS 獲取
- **CNN Business** - 從網站直接爬取（替代失效的 RSS）

**新聞數量配置：**
```bash
# 每個來源最多文章數（默認：10）
MAX_ARTICLES_PER_SOURCE=10

# 總文章數上限（默認：20）
MAX_TOTAL_ARTICLES=20
```
usage: AI_News.py [-h] [-t TOPIC] [-o OUTPUT] [--log-level {DEBUG,INFO,WARNING,ERROR}] [--version]

AI News 分析與報告生成器

optional arguments:
  -h, --help            show this help message and exit
  -t TOPIC, --topic TOPIC
                        報告的主題標題
  -o OUTPUT, --output OUTPUT
                        自訂 HTML 輸出路徑
  --log-level {DEBUG,INFO,WARNING,ERROR}
                        日誌輸出級別
  --version             show program's version number and exit
```

## 生產環境部署

### 使用 Supervisor 守護進程

```bash
# 安裝 supervisor
sudo apt install supervisor

# 建立配置檔案 /etc/supervisor/conf.d/ai-news.conf
[program:ai-news-api]
directory=/path/to/AI_News
command=/path/to/AI_News/venv/bin/gunicorn backend.app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
user=www-data
autostart=true
autorestart=true
stderr_logfile=/var/log/ai-news/err.log
stdout_logfile=/var/log/ai-news/out.log

# 重新載入配置
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start ai-news-api
```

### 使用 systemd 服務

```bash
# 建立服務檔案 /etc/systemd/system/ai-news.service
[Unit]
Description=AI News Analysis API
After=network.target

[Service]
Type=notify
User=www-data
WorkingDirectory=/path/to/AI_News
Environment="PATH=/path/to/AI_News/venv/bin"
ExecStart=/path/to/AI_News/venv/bin/gunicorn backend.app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
Restart=always

[Install]
WantedBy=multi-user.target

# 啟動服務
sudo systemctl daemon-reload
sudo systemctl enable ai-news
sudo systemctl start ai-news
```

## 故障排除

### 爬取失敗

- 檢查網路連線
- 確認 RSS 來源可訪問
- 確認 Playwright 瀏覽器已安裝：`playwright install chromium`
- 查看 Crawl4AI 是否正確安裝：`pip show Crawl4AI`
- 查看日誌 `financial_reports/ai_news_analyzer.log`

### AI 分析失敗

- 確認 OPENROUTER_API_KEY 已設置
- 檢查 API 額度是否足夠
- 日誌中查看錯誤訊息

### HTML 未生成

- 檢查 `output/` 目錄權限
- 查看日誌中的錯誤資訊
- 確認模板檔案 `backend/templates/template.html` 存在

### API 啟動失敗

- 確認虛擬環境已啟動
- 檢查 8000 埠口是否被佔用
- 查看日誌：`logs/access.log` 和 `logs/error.log`

## 日誌

- 控制台：INFO 級別
- 檔案：`financial_reports/ai_news_analyzer.log`（DEBUG 級別）
- API 日誌：`logs/access.log` 和 `logs/error.log`

## 新聞來源說明

### CNN Business 爬取

**問題：** CNN RSS `https://rss.cnn.com/rss/edition_business.rss` 已失效，只返回 2017 年的舊文章。

**解決方案：** 直接從 CNN Business 網站爬取最新文章。

**爬取方式：**
- CNN 新聞 → Tavily API → crawl4ai → BeautifulSoup
- CNBC 新聞 → crawl4ai → BeautifulSoup

**過濾條件：**
- URL 去重
- 過濾圖片說明文字（Getty Images、Reuters、Bloomberg）
- 過濾短標題（< 30 字符）

### 新聞數量配置

可在 `.env` 檔案中自訂新聞數量：

```bash
# 每個來源最多文章數（默認：25）
MAX_ARTICLES_PER_SOURCE=25

# 總文章數上限（默認：50）
MAX_TOTAL_ARTICLES=50
```

---

## 授權

MIT License

## 貢獻

歡迎提交 Issue 和 Pull Request！

## 相關文檔

- [func.md](./func.md) - 函數文檔
- [AGENTS.md](./AGENTS.md) - 開發者指南
- [DEPLOYMENT.md](./DEPLOYMENT.md) - 部署指南

---

## 內容清理與評論過濾

系統會自動清理新聞內容並過濾質量不佳的 AI 評論，確保報告內容精簡且有意義。

### 自動清理的內容

#### 裝飾性圖片和 Logo
- CNBC Logo 和網站標誌
- 頁面導航圖示
- 廣告相關圖片
- Footer/Header 裝飾圖

#### 導航連結和選單
- 頁面導航欄（[市場]、[商業]、[投資]、[科技] 等）
- 底部功能連結（[訂閱]、[登入]、[建立帳戶] 等）
- 社群媒體連結（Facebook、Twitter、LinkedIn 等）

#### 客服和聯絡訊息
- 「聯繫我們」、「請聯絡」等客服訊息
- 「如需更多資訊」、「如有疑問」等提示
- 隱私政策、服務條款連結
- 新聞提示、廣告合作連結

#### 其他無意義內容
- 純連結行（不包含文字內容的單行連結）
- 過長的導航欄（包含大量連結和符號的行）
- 重複的標題或導航區塊

### 評論質量過濾

系統會自動檢查 AI 生成的專業評論，移除質量不佳的內容：

#### 過濾標準

1. **長度檢查**
   - 評論長度 < 50 字符 → 移除

2. **客服訊息檢查**
   - 包含「請聯絡」、「聯繫我們」、「如需更多資訊」等字眼 → 移除

3. **空泛內容檢查**
   - 只有「總體而言」、「總的來說」等空泛結尾語且無其他內容 → 移除

4. **相似度檢查**
   - 評論與新聞內容重複度 > 80% → 移除（避免評論只是重複新聞）

#### 保留標準

評論需要包含以下之一才會被保留：
- 具體的投資建議
- 對市場趨勢的分析
- 與台灣投資環境相關的見解
- 針對新聞事件的專業評論

### 實作位置

- **檔案：** `backend/app/services/html_generator.py`
- **函數：**
  - `_clean_markdown_content()` - 內容清理
  - `_is_comment_meaningful()` - 評論質量檢查
  - `parse_and_render_html()` - 應用清理和過濾

---

## 系統特性

### 逐一分析新聞

為了避免 AI 模型的上下文容量限制，系統採用**逐一分析**的方式：

```
新聞 1 → AI 分析 → 保存到 Markdown
新聞 2 → AI 分析 → 追加到 Markdown
新聞 3 → AI 分析 → 追加到 Markdown
...
新聞 50 → AI 分析 → 追加到 Markdown
```

**優點：**
- ✅ 避免單次請求超出上下文限制
- ✅ 實時保存，中斷後可從斷點繼續
- ✅ 進度可見（日誌顯示「第 X/50 篇新聞分析完成」）
- ✅ 容錯性強（單篇失敗不影響其他新聞）

### 動態時間顯示

HTML 報告標題區包含：
- 🤖 AI 模型名稱
- 🖥 主機名稱
- 📄 生成時間（靜態）
- 📝 文章日期
- 🕒 現在時間（每秒自動更新，白色文字）

### 輸出路徑自訂

可在 `.env` 檔案中自訂輸出路徑：

```bash
# HTML 報告輸出
HTML_OUTPUT_PATH=/path/to/your/output

# Markdown 報告輸出
MARKDOWN_LOG_OUTPUT_PATH=/path/to/your/reports
```

---

## 故障排除

### 爬取失敗

- 檢查網路連線
- 確認 RSS 來源可訪問
- 確認 Playwright 瀏覽器已安裝：`playwright install chromium`
- 查看 Crawl4AI 是否正確安裝：`pip show Crawl4AI`
- 查看日誌 `financial_reports/ai_news_analyzer.log`

### AI 分析失敗

- 確認 OPENROUTER_API_KEY 已設置
- 檢查 API 額度是否足夠
- 日誌中查看錯誤訊息

### HTML 未生成

- 檢查 `output/` 目錄權限
- 查看日誌中的錯誤資訊
- 確認模板檔案 `backend/templates/template.html` 存在

### API 啟動失敗

- 確認虛擬環境已啟動
- 檢查 8000 埠口是否被佔用
- 查看日誌：`logs/access.log` 和 `logs/error.log`

---

## 日誌

- 控制台：INFO 級別
- 檔案：`financial_reports/ai_news_analyzer.log`（DEBUG 級別）
- API 日誌：`logs/access.log` 和 `logs/error.log`

---

## 授權

MIT License

## 貢獻

歡迎提交 Issue 和 Pull Request！

---

## 相關文檔

- [func.md](./func.md) - 函數文檔
- [AGENTS.md](./AGENTS.md) - 開發者指南
- [DEPLOYMENT.md](./DEPLOYMENT.md) - 部署指南
