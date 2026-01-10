## ADDED Requirements

### Requirement: RSS Feed Parsing
系統 MUST 能夠從指定的 RSS 來源（CNBC、CNN Business）讀取新聞列表。

#### Scenario: 成功解析 RSS feed
- **WHEN** 系統從有效的 RSS URL 獲取數據
- **THEN** 系統 SHALL 回傳標題、連結、描述、發布日期等新聞資訊
- **AND** 每個來源最多獲取 15 則新聞

#### Scenario: RSS 獲取失敗處理
- **WHEN** RSS URL 無法訪問或返回錯誤
- **THEN** 系統 SHALL 記錄錯誤日誌
- **AND** 系統 SHALL 繼續處理其他來源

### Requirement: 網頁內容爬取
系統 MUST 使用 crawl4ai 從新聞連結爬取完整的文章內容。

#### Scenario: 成功爬取文章內容
- **WHEN** 提供有效的新聞連結
- **THEN** 系統 SHALL 返回完整的文章正文內容
- **AND** 內容長度至少 250 個字符

#### Scenario: 爬取失敗重試
- **WHEN** 爬取首次失敗
- **THEN** 系統 SHALL 嘗試最多 3 次重試
- **AND** 失敗後系統 SHALL 記錄錯誤日誌

#### Scenario: 並發爬取
- **WHEN** 有多個新聞連結需要爬取
- **THEN** 系統 MUST 使用最多 10 個工作線程並發執行
- **AND** 每個連結的爬取結果 SHALL 獨立處理

### Requirement: 內容清洗與提取
系統 MUST 清洗爬取的 HTML 內容並提取純文字。

#### Scenario: 提取主要正文內容
- **WHEN** 爬取到網頁內容
- **THEN** 系統 SHALL 識別並提取主要文章內容
- **AND** 系統 SHALL 移除廣告、導航等非正文元素

#### Scenario: 不同來源內容提取
- **WHEN** 爬取不同網域（CNBC、CNN）的內容
- **THEN** 系統 SHALL 根據網域使用對應的 CSS 選擇器
- **AND** 系統 SHALL 提取正確的正文區塊
