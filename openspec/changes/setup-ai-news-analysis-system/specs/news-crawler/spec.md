## ADDED Requirements

### Requirement: RSS Feed Parsing
系統 MUST 能夠從指定的 RSS 來源（CNBC）讀取新聞列表，並使用 Tavily API 搜尋其他來源的新聞。

#### Scenario: 成功解析 RSS feed
- **WHEN** 系統從有效的 RSS URL 獲取數據
- **THEN** 系統 SHALL 回傳標題、連結、描述、發布日期等新聞資訊
- **AND** 每個來源最多獲取 25 則新聞

#### Scenario: 使用 Tavily API 搜尋新聞
- **WHEN** 系統使用 Tavily API 搜尋特定網域的新聞
- **THEN** 系統 SHALL 返回搜尋結果中的新聞列表
- **AND** 搜尋查詢 SHALL 包含域名和時間篩選（昨天）

#### Scenario: CNN Business 網站爬取
- **WHEN** CNN RSS 不可用時
- **THEN** 系統 SHALL 直接從 CNN Business 網站爬取文章連結
- **AND** 系統 MUST 過濾圖片說明文字和無效連結

#### Scenario: RSS 獲取失敗處理
- **WHEN** RSS URL 無法訪問或返回錯誤
- **THEN** 系統 SHALL 記錄錯誤日誌
- **AND** 系統 SHALL 繼續處理其他來源

### Requirement: 網頁內容爬取
系統 MUST 使用多種爬取策略（crawl4ai、Tavily API、BeautifulSoup）從新聞連結爬取完整的文章內容。

#### Scenario: Bloomberg 新聞爬取策略
- **WHEN** 爬取 Bloomberg 新聞時
- **THEN** 系統 SHALL 優先使用 crawl4ai
- **AND** 失敗時 SHALL 嘗試改進請求頭
- **AND** 再失敗時 SHALL 使用 Tavily API

#### Scenario: CNN 新聞爬取策略
- **WHEN** 爬取 CNN 新聞時
- **THEN** 系統 SHALL 優先使用 Tavily API
- **AND** 失敗時 SHALL 嘗試 crawl4ai

#### Scenario: 其他新聞爬取策略
- **WHEN** 爬取其他來源新聞時
- **THEN** 系統 SHALL 優先使用 crawl4ai
- **AND** 失敗時 SHALL 回退到 BeautifulSoup

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
- **AND** 總新聞數量 SHALL 限制在 40 篇以下

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
