## ADDED Requirements

### Requirement: HTML 標題動態時間顯示
HTML 報告標題 MUST 顯示以下資訊：
1. 報告主題
2. 使用的 AI 模型名稱
3. 主機名稱
4. 報告生成時間
5. 現在時間（每秒更新）

#### Scenario: 標題完整資訊顯示
- **WHEN** 使用者開啟 HTML 報告頁面
- **THEN** 頁面標題 SHALL 顯示格式：`[主題] | [模型] | [主機] | 生成: [時間] | 現在: [時間]`
- **AND** 現在時間 SHALL 每秒自動更新

#### Scenario: 時間格式正確性
- **WHEN** 時間資訊顯示在標題中
- **THEN** 生成時間格式 SHALL 為 `YYYY年MM月DD日 HH:mm:ss`
- **AND** 現在時間格式 SHALL 為 `YYYY-MM-DD HH:mm:ss`

### Requirement: JavaScript 時間更新
系統 MUST 使用 JavaScript 在瀏覽器端實現時間動態更新。

#### Scenario: 自動時間更新
- **WHEN** HTML 頁面載入完成
- **THEN** JavaScript SHALL 啟動 `setInterval` 定時器
- **AND** 定時器 SHALL 每秒更新一次時間

#### Scenario: JavaScript 無法執行時的降級
- **WHEN** JavaScript 被禁用或無法執行
- **THEN** 頁面 SHALL 仍顯示生成時間
- **AND** 現在時間欄位 SHALL 顯示「無法更新」提示
