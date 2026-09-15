## Context

`LiteLLMConstraintAnalysisGateway._complete` in
`apps/api/src/modules/constraint_analysis/adapters/litellm.py` builds an
OpenAI-shaped chat completion body and posts it with
`httpx.AsyncClient(timeout=90)`. `Gateway.assess` in
`apps/api/src/platform/llm.py` does the same with `timeout=60`. Both talk to
the same LiteLLM gateway and the same routed model.

The routed model is a thinking model. Measurement on a realistic analyst
payload, sent directly to the provider:

| directive | latency | completion tokens | reasoning tokens |
| --- | --- | --- | --- |
| default | 25.9s | 1177 | 953 |
| `enable_thinking: false` | 4.5s | 165 | 0 |

`reasoning_effort` is rejected by the gateway with HTTP 400
(`litellm.UnsupportedParamsError`), so it is not an option. `enable_thinking`
survives the gateway pass-through as a top-level wire field.

## Goals / Non-Goals

**Goals:**

- A launched analysis completes against the real provider instead of timing
  out on its first step.
- The non-thinking directive and the timeout live in one place, so the two
  call sites cannot disagree.
- The timeout stays operator-tunable without a code change.

**Non-Goals:**

- Model selection, step count, retries, or a fallback provider.
- Changing the request contract, the response schema, or the stored result.
- Embedding or telemetry timeouts.

## Decisions

### Disable thinking on structured output
Kollio pins every model reply to a strict JSON schema and validates it in
Pydantic. The reasoning the model performs before answering buys nothing the
schema does not already enforce, while multiplying latency several fold and
producing tokens that `max_tokens` does not bound. Sending
`enable_thinking: false` is the smallest change that removes the multiplier.

Alternative considered: setting the flag in the LiteLLM config entry for
`kollio-default`. Rejected because that config is baked into the gateway image
at `/app/config.yaml` and is not mounted, so it would require an image rebuild
through the deployment path for a one-line wire field.

### One configurable timeout, defaulting to 600 seconds
The old limits (90s, 60s) were hardcoded constants inside two functions. A
single `Settings.llm_request_timeout_seconds` with a generous default covers
the provider variance observed (up to 55.6s on trivial calls) with room for a
five step pipeline, and can be tuned per deployment through the environment
without touching code.

### A shared platform helper
`apps/api/src/platform/llm_chat.py` exposes `chat_payload` (the request body,
including the non-thinking directive) and `chat_client` (the client, built
from the configured timeout). Both gateways use it. The alternative, editing
two payloads and two client constructions, was rejected because the directive
is a correctness-critical detail that must not drift.

## Migration Plan

1. Add `Settings.llm_request_timeout_seconds` and the platform helper with its
   unit tests; nothing else changes and existing tests pass.
2. Rewire both gateways onto the helper and add the regression test asserting
   the outbound body carries `enable_thinking: false`.
3. Run the suite, then deploy and re-run the pilot loop in production.

Rollback restores the two hardcoded timeouts and removes the field from the
payload; no data migration either direction.
