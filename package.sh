#!/bin/bash
# AI News 系統打包腳本
# 用於打包所有必要檔案以轉移到其他電腦

set -e

echo "======================================"
echo "  AI News 系統打包工具"
echo "======================================"
echo ""

# 顏色定義
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 創建臨時打包目錄
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
PACKAGE_NAME="ai-news-deploy-${TIMESTAMP}"
TEMP_DIR="/tmp/${PACKAGE_NAME}"

echo -e "${BLUE}1/5 創建打包目錄...${NC}"
rm -rf "$TEMP_DIR"
mkdir -p "$TEMP_DIR"
echo -e "${GREEN}✅ 臨時目錄已創建: ${TEMP_DIR}${NC}"
echo ""

# 複製核心程式碼
echo -e "${BLUE}2/5 複製核心程式碼...${NC}"
cp AI_News.py "$TEMP_DIR/"
cp -r backend/ "$TEMP_DIR/"
echo -e "${GREEN}✅ 核心程式碼已複製${NC}"
echo ""

# 複製配置文件
echo -e "${BLUE}3/5 複製配置文件...${NC}"
cp requirements.txt "$TEMP_DIR/"
cp .env.example "$TEMP_DIR/"
cp .gitignore "$TEMP_DIR/"
echo -e "${GREEN}✅ 配置文件已複製${NC}"
echo ""

# 複製文檔
echo -e "${BLUE}4/5 複製文檔...${NC}"
cp README.md "$TEMP_DIR/"
cp func.md "$TEMP_DIR/"
if [ -f DEPLOYMENT.md ]; then
    cp DEPLOYMENT.md "$TEMP_DIR/"
fi
if [ -f AGENTS.md ]; then
    cp AGENTS.md "$TEMP_DIR/"
fi
echo -e "${GREEN}✅ 文檔已複製${NC}"
echo ""

# 創建 README 文件
echo -e "${BLUE}5/5 創建打包說明...${NC}"
cat > "$TEMP_DIR/DEPLOY_README.txt" << 'EOF'
===========================================
  AI News 系統部署包
===========================================

【打包時間】：TIMESTAMP_PLACEHOLDER
【系統版本】：v1.0.0

===========================================
  目錄結構
===========================================

AI_News-deploy/
├── AI_News.py              # 主程式入口
├── requirements.txt          # Python 套件依賴
├── .env.example             # 環境變數範例（重要！）
├── .gitignore             # Git 忽略文件
├── README.md              # 專案說明
├── func.md                # 函數文檔
├── DEPLOYMENT.md          # 部署指南
├── AGENTS.md              # 開發者指南
├── backend/              # 後端程式碼
│   ├── app/
│   │   ├── api/         # API 路由
│   │   ├── core/        # 核心模組（設定、日誌）
│   │   └── services/     # 服務模組（爬取、AI、HTML）
│   ├── main.py           # FastAPI 主應用程式
│   └── templates/        # HTML 模板
└── DEPLOY_README.txt    # 本文件

===========================================
  部署步驟
===========================================

1. 解壓縮打包文件
   tar -xzf ai-news-deploy-*.tar.gz
   cd AI_News-deploy-*/

2. 建立虛擬環境
   python3 -m venv .venv
   source .venv/bin/activate

3. 安裝套件依賴
   pip install -r requirements.txt

4. 安裝 Playwright 瀏覽器
   playwright install chromium

5. 設置環境變數（重要！）
   cp .env.example .env
   nano .env  # 或使用其他編輯器

   需要設置的變數：
   - OPENROUTER_API_KEY: AI 模型 API 金鑰（必須）
   - TAVILY_API_KEY: Tavily API 金鑰（用於 CNN 新聞爬取）

6. 測試執行
   python AI_News.py -t "測試報告"

===========================================
  重要注意事項
===========================================

【必須設置的 API 金鑰】
- OPENROUTER_API_KEY: 必須！從 https://openrouter.ai/ 獲取
- TAVILY_API_KEY: 建議！從 https://tavily.com/ 獲取

【不需要轉移的文件/目錄】
- .venv/ - 需要在新電腦上重新建立
- output/ - 會自動建立
- financial_reports/ - 會自動建立
- .env - 包含 API Key，不應打包
- *.log - 日誌文件
- __pycache__/ - Python 快取

【新聞數量配置】
- 每個來源上限：10 篇（在 .env 中設置 MAX_ARTICLES_PER_SOURCE）
- 總文章數上限：20 篇（在 .env 中設置 MAX_TOTAL_ARTICLES）

【輸出路徑自訂】
- HTML 輸出路徑：在 .env 中設置 HTML_OUTPUT_PATH
- Markdown 輸出路徑：在 .env 中設置 MARKDOWN_LOG_OUTPUT_PATH

===========================================
  技術支援
===========================================

- 完整文檔：README.md
- 函數文檔：func.md
- 部署指南：DEPLOYMENT.md
- 問題回報：https://github.com/xxx/issues

===========================================
EOF

# 替換時間戳記
sed -i "s/TIMESTAMP_PLACEHOLDER/$(date '+%Y-%m-%d %H:%M:%S')/" "$TEMP_DIR/DEPLOY_README.txt"

echo -e "${GREEN}✅ 打包說明已創建${NC}"
echo ""

# 顯示打包內容
echo "======================================"
echo "  打包內容統計"
echo "======================================"
echo ""
echo "核心文件："
find "$TEMP_DIR" -maxdepth 1 -type f -name "*.py" -o -name "*.txt" -o -name "*.md" | while read f; do
    echo "  - $(basename "$f")"
done
echo ""
echo "目錄："
find "$TEMP_DIR" -maxdepth 1 -type d | while read d; do
    echo "  - $(basename "$d")/"
done
echo ""

# 創建壓縮包
echo -e "${BLUE}創建壓縮包...${NC}"
cd /tmp
tar -czf "${PACKAGE_NAME}.tar.gz" "${PACKAGE_NAME}/"
echo -e "${GREEN}✅ 壓縮包已創建: /tmp/${PACKAGE_NAME}.tar.gz${NC}"
echo ""

# 計算大小
PACKAGE_SIZE=$(du -h "/tmp/${PACKAGE_NAME}.tar.gz" | cut -f1)
echo -e "${BLUE}打包大小: ${YELLOW}${PACKAGE_SIZE}${NC}"
echo ""

# 顯示完整路徑
FULL_PATH="/tmp/${PACKAGE_NAME}.tar.gz"
echo "======================================"
echo -e "${GREEN}打包完成！${NC}"
echo "======================================"
echo ""
echo -e "${YELLOW}打包文件位置：${NC}"
echo "  ${FULL_PATH}"
echo ""
echo -e "${YELLOW}複製到 USB/雲端儲存：${NC}"
echo "  cp ${FULL_PATH} ~/Desktop/"
echo "  # 或"
echo "  cp ${FULL_PATH} /media/YOUR_USB/"
echo ""
echo -e "${YELLOW}解壓縮指令：${NC}"
echo "  tar -xzf ${PACKAGE_NAME}.tar.gz"
echo "  cd ${PACKAGE_NAME}/"
echo ""

# 詢問是否要移動到桌面
echo -e "${YELLOW}是否要將打包文件移動到桌面？ [Y/n]${NC}"
read -r -p "> " " choice
if [[ "$choice" =~ ^[Yy]$ ]]; then
    DESKTOP_DIR="$HOME/Desktop"
    if [ -d "$DESKTOP_DIR" ]; then
        mv "$FULL_PATH" "$DESKTOP_DIR/"
        echo -e "${GREEN}✅ 已移動到桌面: ${DESKTOP_DIR}/${PACKAGE_NAME}.tar.gz${NC}"
    else
        echo -e "${YELLOW}⚠️  桌面目錄不存在: ${DESKTOP_DIR}${NC}"
    fi
fi

echo ""
echo "======================================"
echo -e "${GREEN}打包流程完成！${NC}"
echo "======================================"
echo ""
echo -e "${BLUE}下一步：${NC}"
echo "1. 將打包文件轉移到目標電腦"
echo "2. 解壓縮打包文件"
echo "3. 按照 DEPLOY_README.txt 進行部署"
echo ""
