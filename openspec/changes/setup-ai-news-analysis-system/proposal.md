# Change: 設置 AI News 分析系統

## Why
現有的 `Gemini_AI_Search.py` 是單一檔案腳本，缺乏模組化架構，難以維護和擴展。需要重構為現代化的 Python Web 應用架構，並使用 crawl4ai 替換舊的爬取方法，以提升效能和可靠性。

## What Changes
- **BREAKING**: 從單一腳本架構重構為模組化架構
- 新增 `news-crawler` 功能：使用 crawl4ai 爬取新聞內容
- 新增 `ai-analysis` 功能：整合 OpenRouter API 進行新聞分析
- 新增 `html-report` 功能：使用 Jinja2 模板生成 HTML 報告
- 新增 `api-interface` 功能：提供 RESTful API 介面
- 新增 `standalone-script` 功能：提供獨立腳本模式，支援 crontab 定時執行

## Impact
- Affected specs: 所有新功能規格（news-crawler, ai-analysis, html-report, api-interface, standalone-script）
- Affected code: 新增完整的後端程式碼和獨立執行腳本，保留並遷移現有邏輯
