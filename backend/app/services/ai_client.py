import time
import requests
import logging
from typing import Optional
from ..core.config import Config


class AIModelClient:
    def __init__(self, config: Config, logger: logging.Logger):
        self.config = config
        self.logger = logger

        # Provider 策略（從 Config 讀取，若無則使用默認值）
        self.current_provider = getattr(config, "AI_PROVIDER", "auto")
        self.ollama_base_url = getattr(
            config, "OLLAMA_BASE_URL", "http://192.168.2.192:11434"
        )

        # OpenRouter headers
        self.openrouter_headers = {
            "Authorization": f"Bearer {self.config.OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
        }

        # Ollama 優先模型清單（已過濾 VL）
        preferred_models = getattr(
            config,
            "OLLAMA_PREFERRED_MODELS",
            [
                "ministral-3:14b-cloud",
                "ministral-3:8b-cloud",
                "ministral-3:3b-cloud",
                "gpt-oss:20b-cloud",
            ],
        )
        exclude_keywords = getattr(
            config, "OLLAMA_EXCLUDE_NAME_KEYWORDS", ["vl", "qwen3-vl"]
        )
        self.ollama_preferred_models = self._filter_ollama_models(
            preferred_models, exclude_keywords
        )

        # 是否已獲取本機模型清單
        self.local_models_fetched = False
        self.available_ollama_models = []

        # 追蹤已經失敗的模型，避免重複嘗試
        self.failed_models = set()

    def _filter_ollama_models(self, preferred: list, exclude_keywords: list) -> list:
        """過濾 Ollama 模型：排除關鍵詞和 VL 類型"""
        filtered = []
        for model in preferred:
            # 檢查是否在排除清單中
            excluded = any(keyword in model.lower() for keyword in exclude_keywords)
            if excluded:
                self.logger.info(f"跳過排除模型: {model}")
                continue

            # 只接受名稱含 -cloud 的模型（cloud 模型優先）
            if "-cloud" in model.lower():
                self.logger.info(f"採用 cloud 模型: {model}")
                filtered.append(model)

        return filtered

    def _fetch_local_ollama_models(self) -> list:
        """獲取本機 Ollama 模型清單並過濾"""
        try:
            response = requests.get(
                f"{self.ollama_base_url}/api/tags", timeout=self.config.SCRAPE_TIMEOUT
            )
            response.raise_for_status()
            data = response.json()

            models = data.get("models", [])

            # 過濾 VL 類型模型
            exclude_patterns = ["vl", "qwen3-vl"]
            filtered_models = []

            for model_info in models:
                model_name = model_info.get("name", "")

                # 排除 VL 類型
                if any(pattern in model_name.lower() for pattern in exclude_patterns):
                    self.logger.info(f"排除 VL 模型: {model_name}")
                    continue

                # 如果啟用 cloud 優先，只保留 cloud 模型或本機模型（不含 :cloud）
                if getattr(self.config, "OLLAMA_PREFER_CLOUD_MODELS", True):
                    if ":cloud" not in model_name and "cloud" not in model_name:
                        self.logger.info(
                            f"跳過非 cloud 模型（cloud 模式）: {model_name}"
                        )
                        continue

                filtered_models.append(model_name)

            self.available_ollama_models = filtered_models
            self.local_models_fetched = True

            self.logger.info(f"✅ 獲取本機 Ollama 模型清單: {len(filtered_models)} 個")
            if filtered_models:
                self.logger.info(f"可用模型: {', '.join(filtered_models[:5])}...")
            return filtered_models

        except Exception as e:
            self.logger.warning(f"獲取 Ollama 模型清單失敗: {e}")
            return []

    def _call_openrouter(self, prompt: str, model_name: str) -> Optional[str]:
        """呼叫 OpenRouter API"""
        self.logger.info(f"🧠 正在使用模型: {model_name} (OpenRouter)")
        payload = {
            "model": model_name,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": self.config.OPENROUTER_MAX_TOKENS,
        }

        max_retries = self.config.OPENROUTER_MAX_RETRIES

        for attempt in range(max_retries):
            try:
                res = requests.post(
                    self.config.OPENROUTER_API_URL,
                    headers=self.openrouter_headers,
                    json=payload,
                    timeout=self.config.OPENROUTER_TIMEOUT,
                )
                res.raise_for_status()
                response_data = res.json()
                content = (
                    response_data.get("choices", [{}])[0]
                    .get("message", {})
                    .get("content")
                )
                if content:
                    self.logger.info(f"✅ 模型 {model_name} 成功返回內容。")
                    return content.strip()
                else:
                    raise ValueError(
                        f"AI 模型返回了空的或無效的 content。Response: {response_data}"
                    )
            except (
                requests.exceptions.RequestException,
                KeyError,
                IndexError,
                TypeError,
                ValueError,
            ) as e:
                error_msg = str(e)
                self.logger.warning(
                    f"模型 {model_name} 發生錯誤 (嘗試 {attempt + 1}/{max_retries}): {e}"
                )

                # 401 Unauthorized 表示授權問題，重試無意義
                if "401" in error_msg or "Unauthorized" in error_msg:
                    self.logger.error(f"❌ OpenRouter 授權失敗（401）: {model_name}")
                    return None

                if attempt < max_retries - 1:
                    time.sleep(self.config.OPENROUTER_BASE_DELAY * (2**attempt))
                else:
                    self.logger.error(
                        f"❌ 模型 {model_name} 在 {max_retries} 次重試後依然失敗。"
                    )
                    return None

    def _call_ollama_chat(self, prompt: str, model_name: str) -> Optional[str]:
        """呼叫 Ollama API"""
        self.logger.info(f"🧠 正在使用模型: {model_name} (Ollama)")

        payload = {
            "model": model_name,
            "messages": [
                {"role": "system", "content": "請使用台灣繁體中文回答，避免簡體字。"},
                {"role": "user", "content": prompt},
            ],
            "stream": False,
        }

        try:
            response = requests.post(
                f"{self.ollama_base_url}/api/chat",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=self.config.SCRAPE_TIMEOUT,
            )
            response.raise_for_status()
            response_data = response.json()

            # 只取 message.content，忽略 thinking 欄位
            message = response_data.get("message", {})
            content = message.get("content", "")

            if content:
                self.logger.info(f"✅ 模型 {model_name} 成功返回內容。")
                return content.strip()
            else:
                raise ValueError("Ollama 返回了空的 content")

        except Exception as e:
            self.logger.error(f"❌ 模型 {model_name} 呼叫失敗: {e}")
            # 標記模型失敗
            self.failed_models.add(model_name)
            self.logger.warning(f"模型 {model_name} 已加入失敗清單")
            # 模型失敗，嘗試其他模型
            self.logger.info("嘗試使用其他 Ollama 模型")
            return self._try_ollama_models_implicitly(prompt)

    def _try_ollama_models_implicitly(
        self, prompt: str, exclude: bool = False
    ) -> Optional[str]:
        """隱性嘗試 Ollama 模型（當指定模型失效時）"""
        if exclude:
            self.logger.info("跳過隱性嘗試（已排除該模型）")
            return None

        # 獲取本地模型清單（不過濾，保留所有模型）
        try:
            response = requests.get(
                f"{self.ollama_base_url}/api/tags", timeout=self.config.SCRAPE_TIMEOUT
            )
            response.raise_for_status()
            data = response.json()
            all_models = [m.get("name", "") for m in data.get("models", [])]
            self.logger.info(f"獲取 {len(all_models)} 個本地模型")

            # 排除 VL類型模型和已經失敗的模型
            exclude_keywords = getattr(
                self.config, "OLLAMA_EXCLUDE_NAME_KEYWORDS", ["vl", "qwen3-vl"]
            )
            filtered_models = []
            for model in all_models:
                if any(keyword in model.lower() for keyword in exclude_keywords):
                    continue
                if model in self.failed_models:
                    continue
                filtered_models.append(model)

            all_models = filtered_models
            self.logger.info(
                f"過濾後剩餘 {len(all_models)} 個模型（已排除 {len(self.failed_models)} 個失敗模型）"
            )
        except Exception as e:
            self.logger.warning(f"獲取本地模型清單失敗: {e}")
            return None

        # 嘗試優先模型（如果啟用了 cloud 優先）
        if getattr(self.config, "OLLAMA_PREFER_CLOUD_MODELS", True):
            for model in self.ollama_preferred_models:
                if model in self.failed_models:
                    self.logger.warning(f"跳過已失敗的優先模型: {model}")
                    continue

                if model in all_models:
                    self.logger.info(f"嘗試優先 cloud 模型: {model}")
                    result = self._call_ollama_chat(prompt, model)
                    if result:
                        self.logger.info(f"✅ 模型 {model} 成功")
                        return result
                    else:
                        # 記錄失敗的模型
                        self.failed_models.add(model)
                        self.logger.warning(f"優先模型 {model} 失敗，已加入失敗清單")
                else:
                    self.logger.warning(f"優先模型 {model} 不在本地清單")

        # 如果啟用 try_all_models 或優先模型都失敗，嘗試所有本地模型
        if getattr(self.config, "OLLAMA_TRY_ALL_MODELS", True):
            self.logger.info("嘗試所有本地模型")
            for model in all_models:
                # 跳過已經嘗試過的優先模型
                if model in self.ollama_preferred_models:
                    continue

                if model in self.failed_models:
                    continue

                self.logger.info(f"嘗試本地模型: {model}")
                result = self._call_ollama_chat(prompt, model)
                if result:
                    self.logger.info(f"✅ 模型 {model} 成功")
                    return result
                else:
                    # 記錄失敗的模型
                    self.failed_models.add(model)
                    self.logger.warning(f"本地模型 {model} 失敗，已加入失敗清單")

        self.logger.warning("所有 Ollama 模型都失敗")
        return None

        # 獲取本地模型清單（不過濾，保留所有模型）
        try:
            response = requests.get(
                f"{self.ollama_base_url}/api/tags", timeout=self.config.SCRAPE_TIMEOUT
            )
            response.raise_for_status()
            data = response.json()
            all_models = [m.get("name", "") for m in data.get("models", [])]
            self.logger.info(f"獲取 {len(all_models)} 個本地模型")

            # 排除 VL 類型模型
            exclude_keywords = getattr(
                self.config, "OLLAMA_EXCLUDE_NAME_KEYWORDS", ["vl", "qwen3-vl"]
            )
            filtered_models = []
            for model in all_models:
                if any(keyword in model.lower() for keyword in exclude_keywords):
                    continue
                filtered_models.append(model)

            all_models = filtered_models
            self.logger.info(f"過濾後剩餘 {len(all_models)} 個模型")
        except Exception as e:
            self.logger.warning(f"獲取本地模型清單失敗: {e}")
            return None

        # 嘗試優先模型（如果啟用了 cloud 優先）
        if getattr(self.config, "OLLAMA_PREFER_CLOUD_MODELS", True):
            for model in self.ollama_preferred_models:
                if model in all_models:
                    self.logger.info(f"嘗試優先 cloud 模型: {model}")
                    result = self._call_ollama_chat(prompt, model)
                    if result:
                        self.logger.info(f"✅ 模型 {model} 成功")
                        return result
                else:
                    self.logger.warning(f"優先模型 {model} 不在本地清單")

        # 如果啟用 try_all_models 或優先模型都失敗，嘗試所有本地模型
        if getattr(self.config, "OLLAMA_TRY_ALL_MODELS", True):
            self.logger.info("嘗試所有本地模型")
            for model in all_models:
                # 跳過已經嘗試過的優先模型
                if model in self.ollama_preferred_models:
                    continue

                self.logger.info(f"嘗試本地模型: {model}")
                result = self._call_ollama_chat(prompt, model)
                if result:
                    self.logger.info(f"✅ 模型 {model} 成功")
                    return result

        self.logger.warning("所有 Ollama 模型都失敗")
        return None

    def _handle_all_models_failed(self) -> Optional[str]:
        """處理所有模型都失敗的情況"""
        on_all_fail = getattr(self.config, "OLLAMA_ON_ALL_FAIL", "terminate")
        if on_all_fail == "fallback_openrouter":
            self.logger.info("Ollama 全部失敗，fallback 到 OpenRouter")
            # 但 OpenRouter 也可能沒 key，這裡只做標記
            return None
        elif on_all_fail == "terminate":
            self.logger.critical("❌ 所有 Ollama 模型均已嘗試失敗，終止流程。")
            raise RuntimeError("All Ollama models failed, terminating workflow.")
        else:
            self.logger.critical("❌ 所有 AI 模型均已嘗試失敗。")
            return None

    def call(
        self, prompt: str, model_name: str = None, max_model_failures: int = 3
    ) -> Optional[str]:
        """統一呼叫入口：根據 provider 選擇 OpenRouter 或 Ollama"""

        # 如果沒指定 model_name，使用默認
        if not model_name:
            if self.current_provider == "openrouter":
                model_name = (
                    self.config.AVAILABLE_MODELS[0]
                    if self.config.AVAILABLE_MODELS
                    else "mistralai/devstral-2512:free"
                )
            elif self.current_provider == "ollama":
                model_name = (
                    self.ollama_preferred_models[0]
                    if self.ollama_preferred_models
                    else "qwen3:14b"
                )
            else:  # auto
                model_name = (
                    self.config.AVAILABLE_MODELS[0]
                    if self.config.AVAILABLE_MODELS
                    else "mistralai/devstral-2512:free"
                )

        # 根據 provider 選擇呼叫方式
        if self.current_provider == "openrouter":
            return self._call_openrouter(prompt, model_name)
        elif self.current_provider == "ollama":
            return self._call_ollama_chat(prompt, model_name)
        else:  # auto: 優先 OpenRouter
            self.logger.info("Provider: auto (優先 OpenRouter)")
            result = self._call_openrouter(prompt, model_name)
            if result:
                return result
            else:
                self.logger.warning("OpenRouter 失敗，fallback 到 Ollama")
                self.current_provider = "ollama"
                # 嘗試隱性調用（模型失效時自動換下一個）
                return self._try_ollama_models_implicitly(prompt)

        self.logger.critical("❌ 所有可用 AI 模型均已嘗試失敗。")
        return None
