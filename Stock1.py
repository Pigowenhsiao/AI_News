import requests
from bs4 import BeautifulSoup
import pandas as pd
from send_email import send_email


def scrape_stock_table(url, output_file):
    # 定義請求標頭，模擬瀏覽器請求
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.0.0 Safari/537.36"
    }

    # 發送GET請求，帶上請求標頭
    response = requests.get(url, headers=headers)

    # 檢查請求是否成功
    if response.status_code == 200:
        # 使用Beautiful Soup解析HTML內容
        soup = BeautifulSoup(response.text, 'html.parser')

        # 查找表格元素
        table = soup.find("table")

        if table:
            # 提取表頭（第一行）
            headers = [header.text.strip() for header in table.find_all("th")]
            # 插入新的表頭 "合理股價" 到第7个位置
            headers.insert(6, "合理股價")

            # 提取表格数据
            data = []
            rows = table.find_all("tr")[1:]  # 忽略表头行
            for row in rows:
                row_data = [cell.text.strip() for cell in row.find_all("td")]
                # 計算合理股價並插入到第7个位置
                calculated_value = round(float(row_data[3]) * float(row_data[4]) / 10, 2)
                row_data.insert(6, str(calculated_value))
                data.append(row_data)

            # 创建DataFrame
            df = pd.DataFrame(data, columns=headers)
            
            # 转换列数据为数值类型，以便进行过滤
            df["股價"] = df["股價"].str.replace(',', '').astype(float)
            df["合理股價"] = df["合理股價"].str.replace(',', '').astype(float)
            df["(年)每股淨值(元)"] = df["(年)每股淨值(元)"].str.replace(',', '').astype(float)
            
            # 过滤条件
            filtered_df = df[(df["股價"] <= df["合理股價"]) & (df["(年)每股淨值(元)"] > 10)]

            # 将过滤后的DataFrame写入CSV文件
            filtered_df.to_csv(output_file, index=False, encoding='utf-8')
            
            print(f"過濾後的表格已成功輸出到 {output_file}")
            print(filtered_df)
        else:
            print("未找到表格")
    else:
        print(f"無法訪問頁面，狀態碼: {response.status_code}")

# 调用函数并输出为CSV文件
url = "https://stock.wespai.com/p/70449"
output_file = "Filtered_STOCK.CSV"
scrape_stock_table(url, output_file)
send_email(output_file)

