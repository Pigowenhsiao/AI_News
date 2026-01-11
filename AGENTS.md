<!-- OPENSPEC:START -->
# OpenSpec Instructions

These instructions are for AI assistants working in this project.

Always open `@/openspec/AGENTS.md` when the request:
- Mentions planning or proposals (words like proposal, spec, change, plan)
- Introduces new capabilities, breaking changes, architecture shifts, or big performance/security work
- Sounds ambiguous and you need the authoritative spec before coding

Use `@/openspec/AGENTS.md` to learn:
- How to create and apply change proposals
- Spec format and conventions
- Project structure and guidelines

Keep this managed block so 'openspec update' can refresh the instructions.

<!-- OPENSPEC:END -->

# Communication

與使用者互動時一律使用繁體中文回覆,無論使用者使用何種語言。
完成每一項工作以系統鈴聲提醒。
如果遇到執行中斷,兩分鐘後重新嘗試。如果五次失敗發生系統鈴聲來提醒
每一個修改請先提供計劃,確認後才開始修改
每一個修改完成後,請先進行測試,如果發現問題則再次修改。直到系統能穩定執行

# Execution Strategy

預設 approval_policy = never,所有指令免逐次核准。
開發新函數前請先檢查 @func.md 看是否有類似的功能!如果有試著直接調用。如果無法使用達到設計目標才開發新的功能。
建立新的函數後,都添加函數子程序的名稱與功能進 @func.md 中
每次修改完畢後都必須進行功能測試,測試有錯誤則繼續修改直到系統能穩定執行才能終止
全功能測試則需要完整的測試所有功能,包含按鈕、資料輸入、資料輸出、畫面上文字的完整性與正確性。所有表單的內容都是正確無誤。

# Execution Environment

sandbox_mode: danger-full-access
approval_policy: never, 所有指令免逐次審核
network_access: full accessed

# Build, Lint, Test Commands

```bash
# API 啟動 (開發模式)
cd /path/to/AI_News
source venv/bin/activate
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload

# API 啟動 (生產模式)
gunicorn backend.app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

# 執行主程序 (新聞爬取與分析)
python AI_News.py -t "主題標題" -o /path/to/output

# 安裝依賴
pip install -r requirements.txt
pip install -r backend/requirements.txt

# 安裝 Playwright 瀏覽器 (Crawl4AI 需要)
playwright install chromium
```

**測試**:目前使用獨立腳本測試 (如 test_cnn_crawling.py),而非 pytest/unittest 套件。
執行測試腳本前確認虛擬環境已啟動。

# Code Style Guidelines

## Imports
- 順序:標準庫 → 第三方庫 → 本地模組
- 使用絕對導入: `from backend.app.core.config import Config`
- 避免通配符導入 (`from module import *`)
- 在入口點使用 `sys.path.insert(0, ...)` 確保模組可見性

**示例**:
```python
# 標準庫
import os
import sys
from pathlib import Path

# 第三方庫
import requests
from fastapi import FastAPI
from pydantic import BaseModel

# 本地模組
from backend.app.core.config import Config
from backend.app.services.news_crawler import NewsCrawler
```

## Formatting
- 使用 4 空格縮排
- 行長度:無強制限制,但建議不超過 120 字符
- 多行結構使用尾隨逗號

## Types
- 在類別和函數使用型別提示
- 使用 `typing.Optional`、`typing.List`、`typing.Dict`
- `Config` 類別使用 `@dataclass` 裝飾器
- FastAPI 請求使用 `pydantic.BaseModel`

## Naming Conventions
- 變量:snake_case (`news_items`, `article_url`)
- 常數:UPPER_SNAKE_CASE (主要在 Config 類別內)
- 函數:snake_case (`scrape_articles_concurrently`, `generate_report`)
- 類別:PascalCase (`AI_News_Agent`, `NewsCrawler`)
- 檔案:kebab-case (`news_crawler.py`, `config.py`)
- 目錄:kebab-case (`backend/app/services/`)

## Error Handling
- 預期錯誤使用 try/except 處理
- 使用 logging 模組記錄錯誤: `logger.error()`, `logger.warning()`
- 永不使用空 catch 區塊
- 保留錯誤上下文: `logger.error(f"錯誤: {e}", exc_info=True)`

**示例**:
```python
try:
    result = some_operation()
except Exception as e:
    logger.error(f"操作失敗: {e}", exc_info=True)
    raise
```

## Architecture
- 服務導向架構: `api/` (路由), `core/` (核心設定), `services/` (業務邏輯)
- 依賴注入:服務在建構時接收 `config` 和 `logger`
- 單例模式:單一 `Config` 類別管理環境變數
- 優雅降級:多個爬取策略 (crawl4ai → Tavily → BeautifulSoup → RSS)

## Documentation
- 公開 API 使用 docstrings
- 日誌和註解使用繁體中文
- 更新 `@func.md` 記錄新函數
- 簡潔的行內註解,僅用於非顯而易見的邏輯

## Logging
- 使用 `backend.app.core.logger.setup_logger()`
- 控制台輸出:INFO 級別
- 檔案輸出:`financial_reports/ai_news_analyzer.log` (DEBUG 級別)
- API 日誌:`logs/access.log` 和 `logs/error.log`

# Project Structure

```
AI_News/
├── AI_News.py                 # 主入口腳本
├── backend/
│   ├── app/
│   │   ├── api/            # FastAPI 路由
│   │   ├── core/           # 核心模組 (config.py, logger.py)
│   │   └── services/       # 服務模組 (rss_reader, news_crawler, ai_client, html_generator)
│   ├── main.py             # FastAPI 主應用程式
│   └── templates/          # Jinja2 模板
├── openspec/               # OpenSpec 變更提案和規格
├── requirements.txt         # 根目錄依賴
├── func.md               # 函數文檔
└── README.md
```

# OpenSpec Workflow

Before implementing features:
1. Check `openspec spec list --long` for existing specs
2. Create change proposal for new features or breaking changes
3. Validate with `openspec validate [change-id] --strict`
4. Implement after proposal approval
5. Archive with `openspec archive <change-id>` after deployment

See `openspec/AGENTS.md` for detailed OpenSpec instructions.
