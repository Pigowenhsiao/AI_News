# Project Context

## Purpose
基於 AI 的美國財經新聞分析與報告生成系統。系統會自動從 CNBC、CNN Business 等財經媒體網站爬取最新新聞，使用 AI 進行翻譯、分析和專業評論，生成格式化的 HTML 和 Markdown 報告。

## Tech Stack
- **Python 3.11+**
- **FastAPI** - Web 框架和 RESTful API
- **Crawl4AI** - 網頁爬取（使用 Playwright 底層）
- **BeautifulSoup4** - HTML 解析（備用方案）
- **Tavily API** - CNN 新聞爬取（專用）
- **OpenRouter API** - AI 模型調用
- **Jinja2** - 模板引擎
- **Markdown** - Markdown 轉換
- **Uvicorn/Gunicorn** - ASGI 伺服器

## Project Conventions

### Code Style
- 使用標準庫 → 第三方庫 → 本地模組的導入順序
- 使用絕對導入
- 避免通配符導入
- 顯式返回類型
- 變數使用 camelCase
- 常量使用 UPPER_SNAKE_CASE
- 類別使用 PascalCase
- 檔案使用 kebab-case

### Architecture Patterns
- 服務導向架構（Service-Oriented Architecture）
- 依賴注入模式
- 分層架構：API → Services → Core
- 日誌集中管理
- 配置集中管理

### Testing Strategy
- 目前使用手動測試驗證功能
- 測試重點：內容清理、評論過濾、HTML 生成

### Git Workflow
- 主分支：main
- 提交訊息使用繁體中文
- 修改前先測試，確保系統穩定執行

## Domain Context

### 新聞來源
- **CNBC** - 美國財經新聞主要來源
- **CNN Business** - 商業和金融新聞
- **Reuters** - 國際新聞
- **Bloomberg** - 金融市場新聞
- **Fortune** - 商業雜誌
- **Yahoo Finance** - 財經資訊
- **MarketWatch** - 市場分析

### AI 分析流程
1. 爬取新聞內容
2. 逐一翻譯並分析（避免上下文限制）
3. 生成專業評論
4. 生成市場總評
5. 生成 HTML 報告

### 台灣投資人需求
- 需要台灣繁體中文翻譯
- 需要使用台灣金融術語（聯準會、美金）
- 需要具體的投資建議和分析

## Important Constraints

- AI 模型有上下文容量限制，需要逐一處理新聞
- 爬取受網站反爬蟲機制限制
- API 有請求頻率限制和額度限制
- 需要清理裝飾性內容（導航、Logo、客服訊息）
- 需要過濾質量不佳的 AI 評論

## External Dependencies

- **OpenRouter API** - AI 模型服務（免費模型：mistralai/devstral-2512:free）
- **Tavily API** - CNN 新聞爬取服務
- **Playwright** - 瀏覽器自動化（由 Crawl4AI 使用）
- **CNBC RSS** - 新聞來源
- **CNN Business** - 網站直接爬取
