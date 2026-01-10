## Context
當前 HTML 樣題僅顯示主題名稱，缺少以下資訊：
- AI 模型名稱（已存在於模板中但未在標題顯示）
- 主機名稱（已存在於模板中但未在標題顯示）
- 報告生成時間
- 現在時間（需要 JavaScript 動態更新）

## Goals / Non-Goals
**Goals:**
- 在 HTML 標題顯示完整的使用環境資訊
- 提供實時時間更新功能
- 保持現有功能不變

**Non-Goals:**
- 不修改後端 API 邏輯
- 不改變 HTML 主體內容結構

## Decisions

**前端方案：** 使用 JavaScript 定時更新時間
- 優點：無需後端支援，輕量級
- 實作方式：在 HTML 標題中嵌入 JavaScript `setInterval`

**時間格式：**
- 生成時間：`YYYY年MM月DD日 HH:mm:ss`
- 現在時間：`YYYY-MM-DD HH:mm:ss`（ISO 格式）

**模板變數：**
- `title` - 報告主題
- `ai_model` - AI 模型名稱（如：mistralai/devstral-2512:free）
- `hostname` - 主機名稱
- `generation_time` - 報告生成時間
- `current_year` - 當前年份

## Risks / Trade-offs
- JavaScript 需要在使用者瀏覽器中啟用
- 時區問題：使用瀏覽器本地時間而非伺服器時間
- 緩解方案：在標題中註明時間基準

## Migration Plan
1. 修改 HTML 模板添加 JavaScript 時間更新
2. 更新 `HTMLGenerator` 傳遞新變數
3. 測試動態時間更新功能
4. 部署新版本
