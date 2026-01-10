## ADDED Requirements

### Requirement: 新聞分析 API
系統 MUST 提供 `/api/analyze` 端點以觸發新聞分析流程。

#### Scenario: 成功觸發分析
- **WHEN** 客戶端發送 POST 請求到 `/api/analyze`
- **THEN** 系統 SHALL 啟動完整的 RSS 爬取、AI 分析、HTML 生成流程
- **AND** 系統 SHALL 返回分析任務的狀態和結果

#### Scenario: 指定主題分析
- **WHEN** 客戶端在請求中指定 `topic` 參數
- **THEN** 系統 MUST 使用該主題生成報告
- **AND** 主題 SHALL 出現在 HTML 報告標題中

### Requirement: 新聞列表 API
系統 MUST 提供 `/api/news` 端點以獲取爬取的新聞列表。

#### Scenario: 獲取最新新聞
- **WHEN** 客戶端發送 GET 請求到 `/api/news`
- **THEN** 系統 SHALL 返回最新的新聞列表
- **AND** 回應 MUST 包含標題、連結、來源、日期等資訊

#### Scenario: 分頁查詢
- **WHEN** 客戶端指定 `page` 和 `limit` 參數
- **THEN** 系統 SHALL 返回對應頁面的新聞
- **AND** 回應 MUST 包含總數和頁面資訊

### Requirement: 報告檢視 API
系統 MUST 提供 `/api/report` 端點以獲取 HTML 報告。

#### Scenario: 獲取最新報告
- **WHEN** 客戶端發送 GET 請求到 `/api/report`
- **THEN** 系統 SHALL 返回最新生成的 HTML 報告
- **AND** 回應內容類型 MUST 為 `text/html`

#### Scenario: 指定日期報告
- **WHEN** 客戶端指定 `date` 參數
- **THEN** 系統 SHALL 返回該日期的 HTML 報告（如果存在）

### Requirement: 系統狀態 API
系統 MUST 提供 `/api/status` 端點以查詢系統狀態。

#### Scenario: 查詢系統健康狀態
- **WHEN** 客戶端發送 GET 請求到 `/api/status`
- **THEN** 系統 SHALL 返回服務運行狀態
- **AND** 回應 MUST 包含 API 金鑰配置、上次更新時間等資訊

### Requirement: 錯誤處理
系統 MUST 對 API 請求進行適當的錯誤處理。

#### Scenario: 處理無效請求
- **WHEN** 客戶端發送無效請求
- **THEN** 系統 SHALL 返回 HTTP 4xx 錯誤碼
- **AND** 回應 MUST 包含錯誤訊息描述

#### Scenario: 處理伺服器錯誤
- **WHEN** 伺服器發生內部錯誤
- **THEN** 系統 SHALL 返回 HTTP 500 錯誤碼
- **AND** 系統 MUST 記錄詳細錯誤日誌
