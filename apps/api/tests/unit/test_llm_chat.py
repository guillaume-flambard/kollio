import pytest

from src.platform.config import Settings
from src.platform.llm_chat import chat_client, chat_payload


def _settings(**overrides) -> Settings:
    base = {
        "_env_file": None,
        "environment": "development",
        "database_url": "",
        "llm_api_key": "test-key",
    }
    base.update(overrides)
    return Settings(**base)


class _RecorderClient:
    timeouts: list[float] = []

    def __init__(self, *args, **kwargs) -> None:
        _RecorderClient.timeouts.append(kwargs["timeout"])

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc) -> bool:
        return False


def test_chat_payload_disables_model_reasoning() -> None:
    payload = chat_payload(
        model="cheap-model",
        system="System",
        user='{"a": 1}',
        schema_name="Thing",
        schema={"type": "object"},
        max_tokens=700,
    )

    assert payload["enable_thinking"] is False
    assert payload["model"] == "cheap-model"
    assert payload["max_tokens"] == 700
    assert payload["messages"] == [
        {"role": "system", "content": "System"},
        {"role": "user", "content": '{"a": 1}'},
    ]
    assert payload["response_format"] == {
        "type": "json_schema",
        "json_schema": {"name": "Thing", "strict": True, "schema": {"type": "object"}},
    }


async def test_chat_client_uses_the_configured_timeout(monkeypatch) -> None:
    monkeypatch.setattr("src.platform.llm_chat.httpx.AsyncClient", _RecorderClient)
    _RecorderClient.timeouts = []

    async with chat_client(_settings(llm_request_timeout_seconds=42.5)):
        pass

    assert _RecorderClient.timeouts == [42.5]


def test_default_timeout_is_generous() -> None:
    assert _settings().llm_request_timeout_seconds >= 300.0


def test_settings_reject_a_non_positive_timeout() -> None:
    with pytest.raises(ValueError):
        _settings(llm_request_timeout_seconds=0)
