# Acceptance evidence - fix-analysis-llm-timeout

A launched constraint analysis failed in production with `httpx.ReadTimeout` on
its first model call. This change disables model reasoning on structured
output and makes the request timeout configurable. Status: in progress.

| Spec scenario | Evidence | State |
| --- | --- | --- |
| Structured call disables model reasoning | `test_analysis_payload_disables_thinking` captures the outbound body and asserts the reasoning directive is false, with model and schema unchanged | Passing |
| Analysis survives provider latency variance | Live pilot re-run after deploy: the workflow reaches a terminal state with a score and five factors instead of `unavailable` | Pending |
| Timeout is configuration | `test_chat_client_uses_the_configured_timeout` and `test_default_timeout_is_generous` | Passing |

## Verification runs (2026-09-15)

Local, before deploy:

- `uv run ruff check .` in `apps/api`: all checks passed.
- `make verify`: green end to end. Ruff, Ruff format check, strict Mypy on the
  five domain packages, the API suite without live provider calls (128 passed,
  54 skipped, 2 deselected), `pnpm lint`, `pnpm typecheck`, the locale guard
  ("468 catalog keys cover their usages") and the design token guard.
- Full API suite against a migrated disposable Postgres
  (`TEST_DATABASE_URL` naming a `kollio_test` database): 182 passed, 2
  deselected. The 54 integration and performance tests that skip without that
  variable all ran and passed.
- `make contract`: no drift. The change alters no API surface.
- `make build`: the web, worker and API images all built.

The new tests are `apps/api/tests/unit/test_llm_chat.py` and
`test_analysis_payload_disables_thinking` in `apps/api/tests/unit/test_task_routing.py`.

## Measured cause (2026-09-15)

Direct provider measurements on a realistic analyst-shaped payload, strict JSON
schema, `max_tokens` 700:

- default (thinking on): 25.9s, 1,177 completion tokens, 953 reasoning tokens
- `enable_thinking: false`: 4.5s, 165 completion tokens, 0 reasoning tokens

Provider latency variance on trivial payloads: 1.5s to 55.6s, with thinking
both on and off. `reasoning_effort` is rejected by the gateway with HTTP 400.
The pipeline is five sequential calls, previously each bounded at 90 seconds.

## Known boundaries

- The live acceptance run depends on the production deployment and the
  provider's availability at that moment; a passing run is evidence of this
  fix, not a latency guarantee.
- No quality regression is claimed or measured beyond the existing recorded
  evaluations, which pin the output shape; a comparative quality judgment stays
  open under the existing benchmark capability.
- The competition gateway is corrected in the same slice although it is not on
  the pilot path.
