import requests
from bs4 import BeautifulSoup
import pandas as pd
from send_email import send_email

def scrape_stock_table(url):

  headers = {
    "User-Agent": "Mozilla/5.0" 
  }

  response = requests.get(url, headers=headers)

  if response.status_code == 200:

    soup = BeautifulSoup(response.text, 'html.parser')
    table = soup.find("table")

    if table:

      # 提取表頭作為DataFrame的column
      headers = [th.text.strip() for th in table.find_all("th")]
      
      # 存储表格数据的列表
      data = []

      # 迭代表格的每一行,加入data列表
      for row in table.find_all("tr")[1:]:
        row_data = [td.text.strip() for td in row.find_all("td")]
        data.append(row_data)

      # 建立DataFrame
      df = pd.DataFrame(data, columns=headers)

      return df

    else:
      return "No table found"
  
  else:
    return f"Response status: {response.status_code}"

# 呼叫函數並列印結果
url = "https://stock.wespai.com/p/70449" 
df = scrape_stock_table(url)

# 将DataFrame写入CSV文件
output_file = "Stock.csv"
df.to_csv(output_file, index=False)  # index=False表示不写入行索引
print(df)
print(f"数据已成功写入 {output_file}")
send_email(output_file)

