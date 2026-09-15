# Acceptance evidence - fix-synthesis-abstention-rule

Status: in progress. The prompt fix and its regression test are in place and the
unit gate is green. The production observation is still pending deployment.

## Scenario map

| Spec scenario | Evidence | State |
| --- | --- | --- |
| Abstention rule is stated where the model can read it | `apps/api/tests/unit/constraint_analysis/test_gateway.py::test_synthesizer_prompt_states_the_abstention_rule` | Passing |
| No evidence yields a result the domain accepts | Four-variant live comparison against the gateway, with no supplied evidence; see the measured cause below | Passing |
| The boundary still fails closed | `ConstraintAnalysisResult.require_all_factors` and `ConstraintFactor.require_the_basis_shape` are unchanged | Passing |
| A production analysis reaches a stored result | Live pilot re-run after deployment | Pending |

## Measured cause

The production workflow `209e8e04-56cb-47f2-a212-f1e6e0b16c45` reached the
synthesis step and ended `failed` with `error_code` `ValidationError`:
`An unknown verdict requires every factor to be unknown`. The synthesizer had
returned `verdict = "unknown"` together with `known` and `assumed` factors. The
prompt stated that insufficient evidence requires an unknown verdict but never
stated the cross-field rule the Pydantic validator enforces, and a JSON schema
cannot express that rule.

The four-variant comparison held everything constant except the prompt text and
the reasoning flag:

| variant | result |
| --- | --- |
| previous prompt, reasoning on | transport timeout at 123s |
| previous prompt, reasoning off | invalid: `verdict=unknown` with bases `assumed, known, known, unknown, unknown` |
| fixed prompt, reasoning on | valid total abstention, 35.2s |
| fixed prompt, reasoning off | valid total abstention, 10.8s |

The previous prompt failed with reasoning off and the fixed prompt passed with
reasoning on, so the prompt was the cause and not the reasoning setting.

## Verification runs (2026-09-15)

- `uv run --project apps/api pytest apps/api/tests/unit/constraint_analysis apps/api/tests/unit/test_task_routing.py apps/api/tests/unit/test_llm_chat.py -q` -> 27 passed.
- `make verify` green end to end: Ruff, Ruff format check, strict Mypy on the five domain packages, API suite `129 passed, 54 skipped, 2 deselected`, pnpm lint, pnpm typecheck, the locale guard and the design token guard.
- Full API suite against a migrated disposable Postgres with `TEST_DATABASE_URL`: `183 passed, 2 deselected`.
- `make contract`: no drift in `contracts/` or the generated client.

## Known boundaries

- The production observation needs a deployed image and a reachable provider.
- No verdict quality claim beyond the recorded evaluations: this change only
  makes the abstention shape legal.
- An analysis with no supplied evidence can only abstain. A scored analysis
  requires evidence on the launch payload; company context is not evidence.
