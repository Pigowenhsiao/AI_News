#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
添加 config.ini 讀取功能到 config.py
"""

import re

# 讀取 config.py
config_path = "backend/app/core/config.py"
with open(config_path, "r", encoding="utf-8") as f:
    config_content = f.read()

# 找到 __post_init__ 方法
pattern = r"(    def __post_init__\(self\):)"

if re.search(pattern, config_content):
    # 在 __post_init__ 方法後插入新的 AI Provider 配置
    ai_provider_config = '''

    # ===== AI Provider 相關配置（從 config.ini 讀取） =====
    def __post_init__(self):
        self._load_ai_config_from_ini()

    def _load_ai_config_from_ini(self):
        """從 config.ini 讀取 [AI] 區塊"""
        import os
        import configparser
        from pathlib import Path

        config_ini_path = Path(__file__).parent.parent.parent / "config.ini"
        
        if not config_ini_path.exists():
            # config.ini 不存在，使用默認值
            self.AI_PROVIDER = "auto"
            self.OLLAMA_BASE_URL = "http://192.168.2.192:11434"
            self.OLLAMA_PREFERRED_MODELS = ["qwen3:14b"]
            self.OLLAMA_PREFER_CLOUD_MODELS = True
            self.OLLAMA_TRY_ALL_LOCAL_MODELS = False
            self.OLLAMA_EXCLUDE_NAME_KEYWORDS = ["vl", "qwen3-vl"]
            self.OLLAMA_ON_ALL_FAIL = "terminate"
            self.OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
            self.OPENROUTER_MODELS = [
                "mistralai/devstral-2512:free",
                "moonshotai/kimi-k2:free",
                "deepseek/deepseek-r1-0528:free",
            ]
            return

        parser = configparser.ConfigParser()
        parser.read(config_ini_path, encoding='utf-8')

        # Provider 選擇
        self.AI_PROVIDER = parser.get("AI", "provider", fallback="auto").strip()

        # Ollama 基礎設定
        self.OLLAMA_BASE_URL = parser.get("AI", "ollama_base_url", fallback="http://192.168.2.192:11434").strip()

        # Ollama 優先模型
        preferred_models_str = parser.get("AI", "ollama_preferred_models", fallback="").strip()
        self.OLLAMA_PREFERRED_MODELS = [m.strip() for m in preferred_models_str.split(",") if m.strip()] if preferred_models_str else []

        # Cloud 模型偏好
        self.OLLAMA_PREFER_CLOUD_MODELS = parser.getboolean("AI", "ollama_prefer_cloud_models", fallback=True)

        # 是否嘗試所有模型
        self.OLLAMA_TRY_ALL_LOCAL_MODELS = parser.getboolean("AI", "ollama_try_all_models", fallback=False)

        # 排除關鍵詞
        exclude_keywords_str = parser.get("AI", "ollama_exclude_name_keywords", fallback="").strip()
        self.OLLAMA_EXCLUDE_NAME_KEYWORDS = [k.strip() for k in exclude_keywords_str.split(",") if k.strip()] if exclude_keywords_str else []

        # 失敗處理方式
        self.OLLAMA_ON_ALL_FAIL = parser.get("AI", "ollama_on_all_fail", fallback="terminate").strip()

        # OpenRouter 模型列表
        models_str = parser.get("AI", "openrouter_models", fallback="").strip()
        self.OPENROUTER_MODELS = [m.strip() for m in models_str.split(",") if m.strip()] if models_str else []
'''

    # 在 __post_init__ 後插入
    new_content = re.sub(pattern, ai_provider_config, config_content, flags=re.DOTALL)

    # 寫入更新後的檔案
    with open(config_path, "w", encoding="utf-8") as f:
        f.write(new_content)

    print("✅ 成功添加 config.ini 讀取功能到 config.py")
    print("✅ 新增的配置項目：")
    print("  - AI_PROVIDER (auto/ollama/openrouter)")
    print("  - OLLAMA_BASE_URL")
    print("  - OLLAMA_PREFERRED_MODELS")
    print("  - OLLAMA_PREFER_CLOUD_MODELS")
    print("  - OLLAMA_TRY_ALL_LOCAL_MODELS")
    print("  - OLLAMA_EXCLUDE_NAME_KEYWORDS")
    print("  - OLLAMA_ON_ALL_FAIL")
    print("  - OPENROUTER_MODELS")
else:
    print("❌ 無法找到 __post_init__ 方法")
    print("請手動檢查 config.py 檔案結構")
    exit(1)
