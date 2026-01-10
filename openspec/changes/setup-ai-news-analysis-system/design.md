## Context
現有 `Gemini_AI_Search.py` 是單一檔案腳本，使用 requests + BeautifulSoup 爬取新聞，透過 OpenRouter API 進行 AI 分析，並輸出 Markdown 和 HTML 報告。需要重構為模組化架構，並使用 crawl4ai 替換舊的爬取方法。

## Goals / Non-Goals
**Goals:**
- 建立可維護的 FastAPI 後端架構
- 使用 crawl4ai 提升爬取效能與可靠性
- 保留現有的 AI 分析與 HTML 生成功能
- 提供 RESTful API 介面

**Non-Goals:**
- 前端 UI 開發（此階段不包含）
- 資料庫持久化（暫不使用資料庫）
- 用戶認證系統

## Decisions
- **Backend Framework**: FastAPI - 快速、現代、自動 API 文檔
- **Crawling**: crawl4ai - 支援 JavaScript 渲染，比 BeautifulSoup 更強大
- **AI API**: 保留 OpenRouter API，相容現有設定
- **Template Engine**: Jinja2 - 保留現有模板邏輯
- **Concurrency**: ThreadPoolExecutor - 保留現有並發策略

**Alternatives considered:**
- Scrapy: 功能強大但學習曲線較陡，crawl4ai 更適合快速開發
- Flask: 不如 FastAPI 現代化，缺少自動 API 文檔
- Playwright: 功能完整但較重，crawl4ai 輕量且足夠

## Risks / Trade-offs
- crawl4ai 可能與某些網站有相容性問題 → 保留 BeautifulSoup 作為備選
- FastAPI 異步特性可能需要調整現有同步程式碼 → 逐步遷移
- API 介面可能增加複雜度 → 先實現核心功能，API 為附加層

## Migration Plan
1. 先建立新架構的目錄結構
2. 逐模組遷移並測試
3. 最後整合所有模組到 FastAPI
4. 保留原腳本作為參考

## Open Questions
- 是否需要資料庫儲存歷史報告？
- 是否需要排程任務自動執行分析？
