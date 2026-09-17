# Acceptance evidence — add-critic

Change: `openspec/changes/add-critic`
Tickets: GitHub #118 (the Critic half of `docs/00-project-overview.md` §7; follows #113)
Date: 2026-09-17
Delivered by this change: the Critic the challenge capability declared a place for. Opening a challenge dispatches a run on the `challenge.execute` worker task; the task reads a brief built from the Option and its confirmed evidence, makes one call on the visible tier, checks every returned finding and stores them as proposals a human settles. No screen, no new HTTP operation.

Status: **passing.** Every row names a test that exists and runs green. Rows marked `partial` or `gap` say exactly what is missing.

## Scenario → evidence

| Scenario | Evidence | Status |
| --- | --- | --- |
| Opening a challenge dispatches the run | `tests/integration/test_challenge_execution.py::test_opening_a_challenge_dispatches_the_run` (the fake queue receives the run id) | passing |
| The Critic's findings are stored on the run | `tests/integration/test_challenge_execution.py::test_the_critic_result_is_stored_as_proposals_and_completes_the_run` | passing |
| The run reports the model that was called | same test (`run.model == "fake-critic"`, read back through the HTTP read) | passing |
| A completed run keeps its findings | `tests/integration/test_challenge.py::test_completed_run_keeps_its_findings` | passing |
| A run executed before this capability reads as having no model | `tests/integration/test_challenge.py::test_open_round_trip` (`model is None`; `failure_reason is None`) | passing |
| The brief carries the question and the Option | `tests/unit/challenge/test_brief.py::test_the_brief_carries_the_question_and_the_option` | passing |
| A narrative field present is carried, absent is omitted | `tests/unit/challenge/test_brief.py::test_a_narrative_field_that_is_present_is_carried`, `::test_a_narrative_field_that_is_absent_is_omitted`, `::test_a_blank_narrative_field_is_read_as_absent`, `::test_every_narrative_field_is_carried_when_present` | passing |
| The brief carries the linked evidence, both sides, with identifiers | `tests/unit/challenge/test_brief.py::test_the_evidence_carries_both_sides_with_their_identifiers`, `::test_the_citable_ids_are_the_evidence_that_was_sent` | passing |
| A `suggested` Contribution is not carried | `tests/integration/test_challenge_execution.py::test_the_brief_carries_the_question_the_option_and_only_confirmed_evidence` (the brief holds the confirmed Contribution only, and the suggested one's title appears nowhere in it) | passing |
| Raw Branch material never promoted to a Contribution is never sent | The brief is assembled only from `repository.confirmed_evidence(...)`, which selects `Contribution` rows; a Branch is never read. The `suggested` Contribution title assertion above is the nearest written evidence | partial — no test asserts a Branch title is absent from the brief |
| A citation outside the brief is refused | `tests/unit/challenge/test_critic_findings.py::test_a_citation_outside_the_brief_is_refused`, `tests/integration/test_challenge_execution.py::test_a_citation_outside_the_brief_is_refused` | passing |
| A citation outside the brief stores no finding for that run | same integration test (the run is `FAILED` and `findings(run.id) == []`) | passing |
| The Critic raising an error ends the run with a reason | `tests/integration/test_challenge_execution.py::test_an_error_ends_the_run_with_a_reason_and_stores_nothing` | passing |
| The Critic returning no findings ends the run with a reason | `tests/integration/test_challenge_execution.py::test_an_empty_result_fails_the_run` | passing |
| A partly unusable result stores nothing | `tests/integration/test_challenge_execution.py::test_an_unusable_result_stores_nothing`, `tests/unit/challenge/test_critic_findings.py::test_one_bad_finding_refuses_the_whole_set` | passing |
| A dispatch that cannot be queued fails the run | `tests/integration/test_challenge_execution.py::test_a_dispatch_that_cannot_be_queued_fails_the_run` | passing |
| A failed run can be tried again and its reason stays readable | The failure paths above prove the reason is stored and readable, and `test_open_round_trip` proves opening is not blocked. No test opens a second run on the same Option after a failure | partial |
| A Critic finding arrives `proposed` with the `critic` origin | `tests/integration/test_challenge_execution.py::test_the_critic_result_is_stored_as_proposals_and_completes_the_run` | passing |
| A human confirms a Critic finding through the existing operation | `tests/integration/test_challenge_execution.py::test_a_human_settles_a_critic_finding` | passing |
| A dismissed finding is kept as a row | `tests/integration/test_challenge.py::test_confirm_and_dismiss_keep_the_record` | passing |
| The Critic never resolves its own findings | `test_the_critic_result_is_stored_as_proposals_and_completes_the_run` (every stored row is `proposed`) | passing |
| An unknown kind is refused | `tests/unit/challenge/test_critic_findings.py::test_an_unknown_check_is_refused` | passing |
| An unknown severity is refused | `tests/unit/challenge/test_critic_findings.py::test_an_unknown_severity_is_refused` | passing |
| A blank statement is refused | `tests/unit/challenge/test_critic_findings.py::test_a_blank_statement_is_refused` | passing |
| The read carries no verdict, ranking or score | `tests/integration/test_challenge_execution.py::test_the_read_carries_no_verdict` | passing |
| Coverage still gates nothing | `tests/integration/test_challenge.py::test_coverage_gates_nothing` | passing |
| A French run reaches the Critic in French | `tests/integration/test_challenge_execution.py::test_the_brief_carries_the_question_the_option_and_only_confirmed_evidence` (the gateway receives `locale == "fr"`) | passing |
| An English run behaves identically | `_open(..., lang="en")` is the default and every execution test uses it; no test asserts the English locale reaching the gateway explicitly | partial |

Command:

```
TEST_DATABASE_URL=postgresql+asyncpg://kollio:<password>@localhost:54329/kollio_test \
  uv run pytest tests/integration/test_challenge_execution.py tests/integration/test_challenge.py \
  tests/unit/challenge -q
```

Result: `10 passed` (`test_challenge_execution.py`), `22 passed` (`test_challenge.py`), 26 passed (`tests/unit/challenge`).

## Boundary evidence

- **The model call is the only non-determinism.** Every execution rule is proved with a fake gateway implementing the declared `ChallengeGateway` port. `tests/` contains no HTTP stubbing anywhere, so the house pattern holds: the port is faked at the boundary rather than the wire.
- **The gateway adapter itself is exercised only through a recorded fixture or a guarded live evaluation.** A recorded fixture is a declared debt (see below): recording one needs a live call, and a hand-authored file would not be a recording. `LiveEvaluationGuard` keeps any live call budgeted, opt-in and out of CI.
- **Types.** Strict Mypy now includes `apps/api/src/modules/challenge/domain`; `uv run mypy` reports no issues in 18 source files.
- **Persistence.** One migration adds a nullable `failure_reason` column (`f3a9d1b7c582`); `uv run alembic check` reports no drift, and a row written before this change reads with a null model and a null reason.
- **Contract.** No HTTP operation is added, changed or removed; `ChallengeRunResponse` gained an optional `failure_reason` field, so `make contract` regenerates `contracts/openapi.json` without changing the operation count.
- **Existing scenarios.** The 22 challenge integration tests keep passing with the real queue replaced by a fake, so nothing in this change reaches Redis from the test suite.

## Explicitly deferred (not gaps)

- The Memory Retriever (§11): the Critic does not read prior confirmed Learnings yet. The brief is assembled in one place so that slice has a single seam to extend.
- Scenario variables are not sent as evidence.
- A recorded critic fixture under `tests/evals/fixtures/`, and the live evaluation that would produce it. **Eval debt.**
- Any screen: a run is visible through the existing HTTP read only.

## Known gaps

- No test asserts that raw Branch material never promoted to a Contribution is absent from the brief (the query makes it structurally impossible, and the `suggested` assertion covers the sibling case).
- No test opens a second challenge on the same Option after a failed run.
- No test asserts the English locale reaching the gateway; every execution test passes `lang="en"` through `execute_run`, and the French case is asserted directly.
