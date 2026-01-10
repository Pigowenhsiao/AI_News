import time
import requests
import logging
from typing import Optional
from ..core.config import Config


class AIModelClient:
    def __init__(self, config: Config, logger: logging.Logger):
        self.config = config
        self.logger = logger
        self.headers = {
            "Authorization": f"Bearer {self.config.OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
        }

    def call(
        self, prompt: str, model_name: str, max_model_failures: int = 3
    ) -> Optional[str]:
        current_model = model_name
        available_models = self.config.AVAILABLE_MODELS
        max_retries = self.config.OPENROUTER_MAX_RETRIES
        base_delay = self.config.OPENROUTER_BASE_DELAY
        for _ in range(max_model_failures):
            self.logger.info(f"🧠 正在使用模型: {current_model}")
            payload = {
                "model": current_model,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": self.config.OPENROUTER_MAX_TOKENS,
            }
            for attempt in range(max_retries):
                try:
                    res = requests.post(
                        self.config.OPENROUTER_API_URL,
                        headers=self.headers,
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
                        self.logger.info(f"✅ 模型 {current_model} 成功返回內容。")
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
                    self.logger.warning(
                        f"模型 {current_model} 發生錯誤 (嘗試 {attempt + 1}/{max_retries}): {e}"
                    )
                    if attempt < max_retries - 1:
                        time.sleep(base_delay * (2**attempt))
                    else:
                        self.logger.error(
                            f"❌ 模型 {current_model} 在 {max_retries} 次重試後依然失敗。"
                        )
                        break
            try:
                current_index = available_models.index(current_model)
                next_index = (current_index + 1) % len(available_models)
                current_model = available_models[next_index]
                self.logger.info(f"🔄 模型切換至: {current_model}")
            except ValueError:
                current_model = available_models[0]
        self.logger.critical("❌ 所有可用 AI 模型均已嘗試失敗。")
        return None
