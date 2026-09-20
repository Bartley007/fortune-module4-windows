from typing import Any

from app.services.llm import OpenAICompatibleExplanationProvider


class FakeResponse:
    def raise_for_status(self) -> None:
        return None

    def json(self) -> dict[str, Any]:
        return {"choices": [{"message": {"content": "test explanation"}}]}


def test_openai_compatible_provider_sends_reasoning_effort(monkeypatch: Any) -> None:
    captured: dict[str, Any] = {}

    def fake_post(url: str, **kwargs: Any) -> FakeResponse:
        captured["url"] = url
        captured.update(kwargs)
        return FakeResponse()

    monkeypatch.setattr("app.services.llm.httpx.post", fake_post)
    provider = OpenAICompatibleExplanationProvider(
        base_url="http://127.0.0.1:11434/v1",
        api_key="ollama",
        model="qwen3.8:27b",
        timeout=30,
        reasoning_effort="none",
    )

    assert provider.explain_recommendation({"title": "candidate-a"}) == "test explanation"
    assert captured["url"] == "http://127.0.0.1:11434/v1/chat/completions"
    assert captured["json"]["reasoning_effort"] == "none"
