# Acceptance evidence - fix-analysis-llm-timeout

A launched constraint analysis failed in production with `httpx.ReadTimeout` on
its first model call. This change disables model reasoning on structured
output and makes the request timeout configurable. Status: in progress.

| Spec scenario | Evidence | State |
| --- | --- | --- |
| Structured call disables model reasoning | `test_analysis_payload_disables_thinking` captures the outbound body and asserts the reasoning directive is false, with model and schema unchanged | Passing |
| Analysis survives provider latency variance | Live pilot re-run after deploy: workflow `6b121a13-8235-46cf-96d1-90ff9110f270` reached `human_review` with a stored result instead of `unavailable`, no error code | Passing |
| Timeout is configuration | `test_chat_client_uses_the_configured_timeout` and `test_default_timeout_is_generous` | Passing |

## Verification runs (2026-09-15)

Live, in production, after the deploy:

- The fix shipped in PR #95, merged as `6004414`. The `publish` job rebuilt the
  API and worker images, and the autodeploy timer restarted the stack on them.
- A relaunched analysis on the pilot idea produced workflow
  `6b121a13-8235-46cf-96d1-90ff9110f270`, which finished at the human review gate
  with `status = awaiting_review`, `current_step = human_review` and no error
  code. The previous two runs on the same idea ended `failed` with `ReadTimeout`
  before this change and `ValidationError` after it, so the timeout is gone and
  the remaining failure was a separate defect addressed by the
  `fix-synthesis-abstention-rule` change.
- The full pipeline of five sequential model calls ran in roughly five minutes
  against live provider latency, which the previous 90 second bound could not
  survive.

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
