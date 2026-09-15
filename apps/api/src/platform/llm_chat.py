"""Shared body and client for structured chat completions against the gateway.

Every Kollio agent call pins its reply to a strict JSON schema and validates it
with Pydantic. The visible-intelligence models behind the gateway default to
reasoning on, which multiplies latency several-fold on real payloads, and that
reasoning is not bounded by ``max_tokens`` because those tokens are spent before
the visible answer. Long calls were exceeding the request timeout and failing
whole analyses. The schema already constrains the shape, so the reasoning buys
nothing here: structured calls disable it explicitly.
"""

from typing import Any

import httpx

from src.platform.config import Settings


def chat_payload(
    *,
    model: str,
    system: str,
    user: str,
    schema_name: str,
    schema: dict[str, Any],
    max_tokens: int,
) -> dict[str, Any]:
    """Build a chat completion body that pins the reply to a strict JSON schema.

    ``enable_thinking`` is a top-level wire field. The provider honours it and it
    survives the gateway, unlike ``reasoning_effort``, which the gateway rejects
    for these models.
    """
    return {
        "model": model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "response_format": {
            "type": "json_schema",
            "json_schema": {"name": schema_name, "strict": True, "schema": schema},
        },
        "max_tokens": max_tokens,
        "enable_thinking": False,
    }


def chat_client(settings: Settings) -> httpx.AsyncClient:
    """Build the HTTP client with the operator-configured request timeout."""
    return httpx.AsyncClient(timeout=settings.llm_request_timeout_seconds)
