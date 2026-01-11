## ADDED Requirements

### Requirement: Jinja2 模板渲染
系統 MUST 使用 Jinja2 模板引擎將 Markdown 內容轉換為 HTML。

#### Scenario: 渲染新聞列表頁面
- **WHEN** 系統擁有解析後的新聞資料
- **THEN** 系統 MUST 使用模板渲染包含所有新聞的 HTML 頁面
- **AND** 系統 SHALL 將 Markdown 內容轉換為 HTML

#### Scenario: 渲染市場總評
- **WHEN** 系統擁有市場總評 Markdown 內容
- **THEN** 系統 SHALL 將其轉換為 HTML 並整合到報告中

### Requirement: HTML 輸出
系統 MUST 將渲染的 HTML 輸出到指定路徑。

#### Scenario: 生成 index.html 檔案
- **WHEN** 模板渲染完成
- **THEN** 系統 SHALL 將 HTML 寫入 `HTML_OUTPUT_PATH/index.html`
- **AND** 系統 MUST 使用 UTF-8 編碼

#### Scenario: 包含生成資訊
- **WHEN** 生成 HTML 報告
- **THEN** 頁面 SHALL 包含生成時間、AI 模型名稱、主機名稱等資訊
- **AND** 資訊 MUST 格式化為易讀的頁面頁尾

### Requirement: 響應式設計
系統輸出的 HTML MUST 支援響應式設計。

#### Scenario: 在不同裝置上正常顯示
- **WHEN** 使用者在桌面或行動裝置上查看報告
- **THEN** 頁面 SHALL 自動調整佈局
- **AND** 頁面 MUST 保持內容可讀性

### Requirement: 暗黑模式支援（暫不實作）
系統輸出的 HTML SHOULD 支援暗黑模式。

#### Scenario: 切換暗黑模式
- **WHEN** 使用者選擇暗黑模式
- **THEN** 頁面 SHALL 顯示暗色主題
- **AND** 文字對比度 MUST 保持可讀
- **NOTE**: 此功能目前未實作，可能未來版本加入
