import requests
from bs4 import BeautifulSoup
import csv
from datetime import datetime
# 导入您的翻译模块
from Azure_Translator import translate_with_microsoft

# 修改后的翻译函数，现在调用您的Azure翻译程序
def translate_text(text):
    try:
        # 使用您的翻译函数替换原有的Google翻译API调用
        translated_text = translate_with_microsoft(text, 'zh-tw')  # 假设translate_with_microsoft函数接受目标语言作为第二个参数
        print(text, ":", "\n", translated_text)
        return translated_text
    except:
        return "Translation failed"

# Function to scrape titles from webpage, translate them, and write to CSV
def scrape_translate_titles(url, output_filename):
    html = requests.get(url)

    if html.status_code == requests.codes.ok:
        html.encoding = "utf-8"
        soup = BeautifulSoup(html.text, 'html.parser')
        
        # Extract current year
        current_year = str(datetime.now().year)[0:2]

        # Scrape titles from webpage
        titles = [a_tag.text.strip() for a_tag in soup.find_all('a', href=lambda href: href and href.startswith('https://www.cnbc.com/' + current_year)) if a_tag.text.strip()]

        # Translate titles
        translated_titles = [translate_text(title) for title in titles]
        
        # Get current date and time
        current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Write translated titles to a CSV file
        with open(output_filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([current_datetime.split()[0], current_datetime.split()[1], "\n"])
            writer.writerow(["Original Title", "Translated Title"])
            writer.writerows(zip(titles, translated_titles))

    else:
        print("Failed to fetch the page:", html.status_code)
