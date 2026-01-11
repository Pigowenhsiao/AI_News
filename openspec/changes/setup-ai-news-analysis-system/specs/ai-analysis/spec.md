## ADDED Requirements

### Requirement: 逐一分析新聞
系統 MUST 採用逐一分析方式處理新聞，避免 AI 模型的上下文容量限制。

#### Scenario: 單篇新聞獨立分析
- **WHEN** 系統開始分析新聞
- **THEN** 系統 SHALL 每次只傳送一篇新聞給 AI 模型
- **AND** 系統 MUST 使用單篇文章分析提示詞（SINGLE_ARTICLE_ANALYSIS_PROMPT）

#### Scenario: 實時保存分析結果
- **WHEN** 每篇新聞分析完成
- **THEN** 系統 SHALL 立即將分析結果追加到 Markdown 文件
- **AND** 日誌 SHALL 顯示「第 X/50 篇新聞分析完成」

#### Scenario: 容錯恢復機制
- **WHEN** 單篇新聞分析失敗
- **THEN** 系統 SHALL 記錄錯誤並跳過該篇新聞
- **AND** 系統 SHALL 繼續分析下一篇新聞
- **AND** 中斷後可從已保存的 Markdown 繼續處理

### Requirement: AI 新聞翻譯
系統 MUST 能夠將英文新聞翻譯成台灣繁體中文。

#### Scenario: 翻譯新聞標題和內容
- **WHEN** 系統接收到英文新聞內容
- **THEN** 系統 MUST 使用指定的 AI 模型進行翻譯
- **AND** 系統 SHALL 保留公司名稱（如 Apple、NVIDIA）和金融術語（如 S&P 500）的英文原文
- **AND** 系統 SHALL 使用台灣慣用金融術語（如：聯準會、美金）

### Requirement: 專業評論生成
系統 MUST 為每則新聞生成專業的金融評論。

#### Scenario: 生成單篇評論
- **WHEN** 系統完成新聞翻譯
- **THEN** 系統 SHALL 生成針對該新聞的專業評論
- **AND** 評論 MUST 提供犀利且獨到的見解
- **AND** 評論 SHALL 使用台灣投資人熟悉的金融術語

### Requirement: 市場總評生成
系統 MUST 基於所有新聞評論生成綜合市場總評。

#### Scenario: 生成每日市場總評
- **WHEN** 系統完成所有新聞的分析
- **THEN** 系統 SHALL 整合所有新聞的觀點生成 200-300 字的市場總評
- **AND** 市場總評 MUST 提供對未來市場趨勢的綜合性、前瞻性看法

### Requirement: AI 模型故障切換
系統 MUST 在主要 AI 模型失敗時切換到備用模型。

#### Scenario: 模型失敗自動切換
- **WHEN** 主要 AI 模型請求失敗
- **THEN** 系統 SHALL 自動切換到下一個可用模型
- **AND** 每個模型 MUST 嘗試最多 3 次重試
- **AND** 所有模型失敗後系統 SHALL 記錄錯誤日誌

### Requirement: 結構化 Markdown 輸出
系統 MUST 將 AI 分析結果輸出為結構化的 Markdown 格式。

#### Scenario: 生成符合格式的 Markdown
- **WHEN** AI 完成新聞分析
- **THEN** 輸出 SHALL 包含標題、日期、來源、內容、評論等區塊
- **AND** 輸出 MUST 使用指定的 Markdown 標題層級（##、###）
