import httpx
import pytest

from backend.react_resume.llm import DeepSeekProvider, LLMProviderError


def test_deepseek_provider_returns_message_content():
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/chat/completions"
        assert request.headers["Authorization"] == "Bearer test-key"
        return httpx.Response(
            200,
            json={
                "choices": [
                    {"message": {"content": "优化建议"}},
                ],
            },
        )

    client = httpx.Client(transport=httpx.MockTransport(handler))
    provider = DeepSeekProvider(
        api_key="test-key",
        base_url="https://api.deepseek.com",
        model="deepseek-chat",
        client=client,
    )

    result = provider.generate([{"role": "user", "content": "分析简历"}])

    assert result == "优化建议"


def test_deepseek_provider_requires_api_key():
    with pytest.raises(LLMProviderError) as error:
        DeepSeekProvider(api_key="", base_url="https://api.deepseek.com", model="deepseek-chat")

    assert "DEEPSEEK_API_KEY" in str(error.value)


def test_deepseek_provider_rejects_unexpected_response_shape():
    client = httpx.Client(transport=httpx.MockTransport(lambda _: httpx.Response(200, json={})))
    provider = DeepSeekProvider(
        api_key="test-key",
        base_url="https://api.deepseek.com",
        model="deepseek-chat",
        client=client,
    )

    with pytest.raises(LLMProviderError) as error:
        provider.generate([{"role": "user", "content": "分析简历"}])

    assert "响应格式异常" in str(error.value)
