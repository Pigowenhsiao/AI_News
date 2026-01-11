## ADDED Requirements

### Requirement: 獨立腳本執行
系統 MUST 提供獨立執行腳本 `AI_News.py` 以便 crontab 直接調用。

#### Scenario: 成功執行完整分析流程
- **WHEN** 使用者執行 `python AI_News.py`
- **THEN** 系統 SHALL 執行完整的新聞爬取、AI 分析、HTML 生成流程
- **AND** 系統 SHALL 輸出執行進度和結果
- **AND** 系統 SHALL 將 HTML 報告寫入指定路徑

#### Scenario: 指定主題執行
- **WHEN** 使用者執行 `python AI_News.py -t "主題名稱"`
- **THEN** 系統 MUST 使用指定主題生成報告
- **AND** 主題 SHALL 出現在 HTML 報告標題中

### Requirement: 命令列參數支援
系統 MUST 支援命令列參數以自訂執行行為。

#### Scenario: 查看說明訊息
- **WHEN** 使用者執行 `python AI_News.py --help`
- **THEN** 系統 SHALL 顯示所有可用參數和說明

#### Scenario: 指定輸出路徑
- **WHEN** 使用者指定 `--output` 或 `-o` 參數
- **THEN** 系統 MUST 將 HTML 報告輸出到指定路徑

### Requirement: 日誌輸出
系統 MUST 將執行過程輸出到日誌檔案和控制台。

#### Scenario: 記錄執行過程
- **WHEN** 腳本執行過程中
- **THEN** 系統 SHALL 將重要步驟輸出到控制台
- **AND** 系統 MUST 將詳細日誌寫入日誌檔案

#### Scenario: 錯誤日誌記錄
- **WHEN** 執行過程中發生錯誤
- **THEN** 系統 SHALL 記錄詳細錯誤訊息到日誌檔案
- **AND** 系統 SHALL 在控制台顯示錯誤摘要

### Requirement: 執行狀態回傳
系統 MUST 回傳適當的退出狀態碼。

#### Scenario: 成功執行回傳 0
- **WHEN** 腳本成功完成所有步驟
- **THEN** 系統 SHALL 回傳退出碼 0

#### Scenario: 失敗執行回傳非 0
- **WHEN** 腳本執行過程中發生錯誤
- **THEN** 系統 SHALL 回傳非零退出碼
