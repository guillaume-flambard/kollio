## Why

A constraint analysis launched in production never completes. The worker log
shows `httpx.ReadTimeout` on the first pipeline step (the analyst), with all
three retries failing identically, and the workflow ends `unavailable` with no
score, no factors and no contradictions.

Two measured facts explain it:

- The routed model `qwen3.8-flash` is a thinking model with thinking ON by
  default. On a realistic analyst-shaped call it took **25.9s** with **953
  reasoning tokens** against **4.5s** with thinking disabled, on the same
  payload. Reasoning tokens are not bounded by `max_tokens`: a request for 700
  tokens produced 1,177.
- Provider latency is high variance independently of thinking: trivial calls
  were observed between 1.5s and 55.6s.

The pipeline runs five sequential model calls, each with a hardcoded 90 second
`httpx` timeout. With per-call latency in the tens of seconds, the first step
alone can exceed that budget. Disabling thinking cuts real calls roughly six
fold, and a configurable timeout absorbs the remaining variance. Neither alone
is sufficient.

## What Changes

- Send `enable_thinking: false` on every structured-output chat completion the
  API issues, so the model returns the JSON the strict schema asks for instead
  of spending unbounded tokens reasoning about it. The flag was verified to
  survive the gateway pass-through and to be honoured by the provider.
- Replace the hardcoded 90 second and 60 second client timeouts with one
  `Settings.llm_request_timeout_seconds` (default 600), applied by both the
  constraint analysis gateway and the competition gateway.
- Centralise the request body and the client construction in one small
  platform helper, so the non-thinking directive and the timeout cannot drift
  between the two call sites.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `constraint-analysis-workflows`: add a requirement that structured model
  calls are explicitly non-thinking and bounded by a configurable timeout, so a
  launched analysis survives provider latency variance.

## Impact

Touches `Settings`, the constraint analysis adapter, the competition gateway,
and the new platform chat helper. No contract, migration, database or frontend
change: the wire request keeps its existing shape plus one field. Adds no
dependency and no secret.

The competition gateway is not on the pilot path, but it carries the same
defect against the same provider, so it is corrected in the same slice and
named here deliberately.

## Out of Scope

- Choosing a different or faster model for the visible-intelligence steps.
- Reducing the number of sequential pipeline steps.
- Adding a retry or fallback provider.
- Touching the embedding or telemetry client timeouts, which do not issue chat
  completions.
