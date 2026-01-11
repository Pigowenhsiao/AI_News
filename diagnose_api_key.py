#!/usr/bin/env python3
"""
診斷 OpenRouter API Key 問題
"""

import os
import sys
import requests
from pathlib import Path


def check_env_file():
    """檢查 .env 檔案是否存在"""
    env_path = Path(".env")
    if not env_path.exists():
        print("❌ .env 檔案不存在")
        print("   請在專案根目錄創建 .env 檔案")
        return False
    print("✅ .env 檔案存在")
    return True


def check_api_key():
    """檢查 API Key 是否設置"""
    from dotenv import load_dotenv

    load_dotenv()

    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("❌ OPENROUTER_API_KEY 未設置")
        print("   請在 .env 檔案中設置：OPENROUTER_API_KEY=your-key-here")
        return None

    if api_key.startswith("sk-or-v1-"):
        print(f"✅ API Key 格式正確")
        print(f"   Key 前綴: {api_key[:10]}...{api_key[-4:]}")
        return api_key
    else:
        print("⚠️  API Key 格式可能不正確")
        print(f"   Key: {api_key[:10]}...{api_key[-4:]}")
        return api_key


def test_api_key(api_key):
    """測試 API Key 是否有效"""
    print("\n正在測試 API Key...")
    url = "https://openrouter.ai/api/v1/auth/key"
    headers = {
        "Authorization": f"Bearer {api_key}",
    }

    try:
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code == 200:
            data = res.json()
            print("✅ API Key 有效！")
            print(f"   用戶 ID: {data.get('user_id', 'N/A')}")
            print(f"   模式: {data.get('mode', 'N/A')}")
            print(f"   餘額信息: {data.get('data', {}).get('balance', 'N/A')}")
            return True
        elif res.status_code == 401:
            print("❌ API Key 無效或過期 (401 Unauthorized)")
            print("   請檢查您的 API Key 是否正確")
            return False
        else:
            print(f"⚠️  API 返回錯誤: {res.status_code}")
            print(f"   回應: {res.text}")
            return False
    except Exception as e:
        print(f"❌ 測試時發生錯誤: {e}")
        return False


def test_model_call(api_key):
    """測試模型調用"""
    print("\n正在測試模型調用...")
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": "mistralai/devstral-2512:free",
        "messages": [{"role": "user", "content": "Say hello"}],
        "max_tokens": 50,
    }

    try:
        res = requests.post(url, headers=headers, json=payload, timeout=30)
        if res.status_code == 200:
            print("✅ 模型調用成功！")
            data = res.json()
            content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            print(f"   回應: {content}")
            return True
        elif res.status_code == 401:
            print("❌ 模型調用失敗 (401 Unauthorized)")
            print("   API Key 可能無效或過期")
            return False
        else:
            print(f"⚠️  模型調用返回錯誤: {res.status_code}")
            print(f"   回應: {res.text[:200]}")
            return False
    except Exception as e:
        print(f"❌ 測試模型調用時發生錯誤: {e}")
        return False


def main():
    print("=" * 70)
    print("OpenRouter API Key 診斷工具")
    print("=" * 70)

    # 檢查 .env 檔案
    if not check_env_file():
        print("\n請先創建 .env 檔案")
        sys.exit(1)

    # 檢查 API Key
    api_key = check_api_key()
    if not api_key:
        print("\n請設置有效的 API Key")
        sys.exit(1)

    # 測試 API Key
    if not test_api_key(api_key):
        print("\n請到 https://openrouter.ai 更新您的 API Key")
        sys.exit(1)

    # 測試模型調用
    if not test_model_call(api_key):
        print("\n無法調用模型，請檢查 API Key 或嘗試其他模型")
        sys.exit(1)

    print("\n" + "=" * 70)
    print("✅ 診斷完成，API Key 正常工作！")
    print("=" * 70)


if __name__ == "__main__":
    main()
