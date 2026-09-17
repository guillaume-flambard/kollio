# Acceptance evidence — add-challenge

Change: `openspec/changes/add-challenge`
Tickets: GitHub #113 (migration step 5, Challenge structure, of `docs/00-project-overview.md` §20)
Date: 2026-09-17
Delivered by this change: the structure the Critic of §7 writes into - challenge runs, findings over the six checks, confirmation by a human, and a coverage read. No model call.

Status: **implemented and verified.** Every row below names the real test that proves it.

## Scenario → evidence

| Scenario | Evidence | Status |
| --- | --- | --- |
| Member reads a challenge | `tests/integration/test_challenge.py::test_member_reads_a_challenge` | passing |
| Non-member requests a challenge | `::test_non_member_is_refused_everywhere` (404 on the list, the open and the record) | passing |
| Unauthenticated request | `::test_unauthenticated_request_is_unauthorized` (401) | passing |
| No leak across workspaces | `::test_run_never_leaks_across_spaces_or_options` (member of the other workspace refused by id) | passing |
| No leak across Options or runs | `::test_option_lookup_is_scoped_to_its_space`, `::test_finding_lookup_is_scoped_to_its_run` (a run under the wrong Option and a finding under the wrong run both 404) | passing |
| Run opened | `::test_open_round_trip` (`RUNNING`, opener, no model, `lang` follows locale, listed back) | passing |
| Uninvolved member cannot write | `::test_uninvolved_member_cannot_write` (403 on open, record, resolve and complete; reading still allowed) | passing |
| Participant can write | `::test_participant_can_write` (extra beyond the spec) | passing |
| Lifecycle is a closed set | `::test_run_lifecycle_is_closed` (second completion is 422) | passing |
| A completed run keeps its findings | `::test_completed_run_keeps_its_findings` (findings unchanged, coverage still reported) | passing |
| Each kind recorded | `::test_every_kind_recorded` (all six, status `confirmed`, origin `human`, coverage full) | passing |
| Unknown check refused | `::test_unknown_kind_or_severity_refused` (422 on `weakness` and on `blocker`, nothing stored) | passing |
| Detail required | `::test_blank_detail_refused` (422 on `` and on whitespace) | passing |
| Finding about a Contribution keeps the reference | `::test_contribution_reference_round_trip` | passing |
| Finding cannot name a foreign Contribution | `::test_foreign_contribution_refused` (422, nothing stored) | passing |
| Human finding is canonical | `::test_every_kind_recorded` | passing |
| Machine finding is not canonical | `::test_critic_finding_arrives_proposed` (service-level, no model, origin `critic`) | passing |
| Human confirms a proposal | `::test_confirm_and_dismiss_keep_the_record` | passing |
| Human dismisses, keeping the record | `::test_confirm_and_dismiss_keep_the_record` (both findings still returned) | passing |
| Resolving is a writer action | `::test_uninvolved_member_cannot_write` | passing |
| Coverage reported | `::test_member_reads_a_challenge` (six uncovered on an empty run), `::test_every_kind_recorded` (full coverage) | passing |
| Dismissed findings do not cover | `::test_dismissed_findings_do_not_cover` (dismissed finding still returned, coverage empty) | passing |
| Unchallenged Option | `::test_unchallenged_option` (no runs, six uncovered, not an error) | passing |
| Coverage gates nothing | `::test_coverage_gates_nothing` (a run completes with no findings and another opens) | passing |
| French and English behave identically | `::test_messages_are_localized` (`Option introuvable` / `Option not found`, `Content-Language` per request) | passing |
| Vocabularies (unit) | `tests/unit/challenge/test_vocabularies.py` (36 cases) | passing |
| Finding shape (unit) | `tests/unit/challenge/test_findings.py` (9 cases) | passing |
| Run lifecycle (unit) | `tests/unit/challenge/test_lifecycle.py` (20 cases) | passing |
| Coverage (unit) | `tests/unit/challenge/test_coverage.py` (6 cases) | passing |
| Access rule (unit) | `tests/unit/challenge/test_access.py` (6 cases) | passing |

Command: `TEST_DATABASE_URL=… uv run pytest tests/integration/test_challenge.py tests/unit/challenge -q` → 101 passed (22 integration, 79 unit).

## Boundary evidence

- OpenAPI export: `make contract` regenerated `contracts/openapi.json` and the TypeScript client. Diff review: 0 operations removed, 6 added (`list_challenges`, `open_challenge`, `get_challenge`, `record_challenge_finding`, `resolve_challenge_finding`, `complete_challenge`); 0 paths removed, 5 added; 66 → 72 operations; 87 → 94 schemas, 0 removed.
- Migration `b9f1c3e7d520` applied cleanly on the disposable database; `alembic check` reports no drift on the first check.
- Strict Mypy includes `apps/api/src/modules/challenge/domain` (Makefile + CI).
- No model call anywhere in the slice; `service/ports.py` declares `ChallengeGateway` and `ChallengeQueue` with no implementation.
- Permissions are proved by PostgreSQL integration tests, not browser tests.
- Vocabulary recorded: `apps/api/CONTEXT.md` and `docs/05-data-model.md`.

## Review findings applied

One defect was found by the evidence and fixed rather than papered over:

- `test_confirm_and_dismiss_keep_the_record` failed with 403 because the test used a workspace member who had never been added as a Space participant. The implementation was right: the 403 is exactly the write rule. The test was corrected to add the participant first.

One design change was made during implementation, and the documents were corrected to match the code rather than the reverse:

- Confirming and dismissing were specified as two operations; they ship as one resolution operation carrying a closed `confirmed`/`dismissed` value, since both are the same transition. The proposal, tasks and this file now say six operations, not seven.

## Explicitly deferred (not gaps)

- The Critic proposer: no prompt, no model, no queue, no agent graph. The gateway protocol is declared so the next slice adds an adapter rather than reshaping the module.
- The machine path is nevertheless proven: a finding with a critique origin is verified through the service, not through the API, because no client may declare one.
- Assumptions as their own §18 entity.
- The Decision Record and any gating of a commitment (step 6). Coverage is information and refuses nothing.

## Known gaps

- None. The implementation tasks are complete.
