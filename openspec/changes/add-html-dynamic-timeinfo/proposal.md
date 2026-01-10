# Change: 新增 HTML 動態時間資訊

## Why
當前 HTML 報告的標題只顯示靜態資訊，使用者無法立即查看：
1. 使用的 AI 模型名稱
2. 報告生成的主機名稱
3. 報告生成時間
4. 現在時間（需要動態更新）

這些資訊對於追蹤和除錯很重要，特別是在定時執行或多次報告的場景中。

## What Changes
- **MODIFIED**: `html-report` 規格 - 新增 HTML 標題動態資訊需求
- **ADDED**: `html-report` 實作 - 動態時間更新功能

## Impact
- Affected specs: `html-report`（修改規格需求）
- Affected code:
  - `backend/templates/template.html` - 添加動態時間更新腳本
  - `backend/app/services/html_generator.py` - 傳遞更多模板變數
  - `backend/app/main.py` - API 端點返回時間資訊
