import requests
import os
from typing import List, Dict, Any

# 從 .env 檔案中載入 API 金鑰
from dotenv import load_dotenv
load_dotenv()

# 取得 OpenRouter API 金鑰，如果 .env 中沒有，請在這裡設定
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "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")

def get_free_models() -> List[str]:
    """
    從 OpenRouter API 取得所有名稱中包含 "free" 的模型名稱。
    """
    url = "https://openrouter.ai/api/v1/models"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}"
    }

    try:
        print("正在向 OpenRouter API 請求模型列表...")
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # 如果請求失敗，拋出 HTTPError
        data = response.json()
        
        models_data = data.get("data", [])
        free_models = []
        
        print("正在篩選名稱中包含 'free' 的模型...")
        for model in models_data:
            model_id = model.get("id")
            if model_id and "free" in model_id.lower():
                free_models.append(model_id)
                
        return free_models

    except requests.exceptions.RequestException as e:
        print(f"請求 OpenRouter API 時發生錯誤: {e}")
        return []
    except KeyError:
        print("解析 API 回傳資料時發生錯誤，'data' 鍵不存在。")
        return []

if __name__ == "__main__":
    if not OPENROUTER_API_KEY:
        print("錯誤: 未找到 OPENROUTER_API_KEY。請在 .env 檔案中設定或直接在程式碼中填入。")
    else:
        model_list = get_free_models()
        if model_list:
            print("\n找到以下可用的免費模型：")
            for model_name in model_list:
                print(f"- {model_name}")
        else:
            print("\n沒有找到任何名稱中包含 'free' 的模型，或請求失敗。")
