import json
from typing import Iterator, Protocol

import httpx


class LLMProviderError(RuntimeError):
    pass


class LLMProvider(Protocol):
    def generate(self, messages: list[dict[str, str]], temperature: float = 0.3) -> str:
        ...

    def stream_generate(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.3,
    ) -> Iterator[str]:
        ...


class DeepSeekProvider:
    def __init__(
        self,
        api_key: str,
        base_url: str,
        model: str,
        client: httpx.Client | None = None,
    ) -> None:
        if not api_key:
            raise LLMProviderError("缺少 DEEPSEEK_API_KEY，无法调用 DeepSeek。")
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.client = client or httpx.Client(timeout=60)

    def generate(self, messages: list[dict[str, str]], temperature: float = 0.3) -> str:
        response = self.client.post(
            f"{self.base_url}/chat/completions",
            headers={"Authorization": f"Bearer {self.api_key}"},
            json={
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
            },
        )
        if response.status_code >= 400:
            raise LLMProviderError(f"DeepSeek 调用失败：HTTP {response.status_code}")
        data = response.json()
        try:
            return data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise LLMProviderError("DeepSeek 响应格式异常。") from exc

    def stream_generate(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.3,
    ) -> Iterator[str]:
        with self.client.stream(
            "POST",
            f"{self.base_url}/chat/completions",
            headers={"Authorization": f"Bearer {self.api_key}"},
            json={
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
                "stream": True,
            },
        ) as response:
            if response.status_code >= 400:
                response.read()
                raise LLMProviderError(f"DeepSeek 调用失败：HTTP {response.status_code}")

            for line in response.iter_lines():
                if not line:
                    continue
                payload = line.removeprefix("data:").strip()
                if payload == "[DONE]":
                    break
                try:
                    data = json.loads(payload)
                    delta = data["choices"][0].get("delta", {})
                    content = delta.get("content", "")
                except (json.JSONDecodeError, KeyError, IndexError, TypeError) as exc:
                    raise LLMProviderError("DeepSeek 流式响应格式异常。") from exc
                if content:
                    yield content
