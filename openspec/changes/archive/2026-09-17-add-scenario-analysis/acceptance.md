# Acceptance evidence — add-scenario-analysis

Change: `openspec/changes/add-scenario-analysis`
Tickets: GitHub #115 (migration step 7 of `docs/00-project-overview.md` §20)
Date: 2026-09-17
Delivered by this change: scenario variables with editable ranges, scenario runs with levels and explicit assumptions, and a deterministic sensitivity read. No model, no forecast, no screen.

Status: **implemented and verified.** Every row below names the real test that proves it.

Note: the spec planned the integration file as `tests/integration/test_scenarios.py`; it ships as `tests/integration/test_scenario_analysis.py`. A few planned test names also changed when the tests were written; the rows below carry the real names.

## Scenario → evidence

| Scenario | Evidence | Status |
| --- | --- | --- |
| Member reads the variables | `tests/integration/test_scenario_analysis.py::test_variable_round_trip` (unit and range, `lang` follows locale) | passing |
| Member reads an option's runs | `::test_run_round_trip` (level, assumptions, declared values) | passing |
| Non-member requests scenarios | `::test_non_member_is_refused_everywhere` (404 on every operation, no disclosure) | passing |
| Unauthenticated request | `::test_unauthenticated_request_is_unauthorized` (401) | passing |
| Nothing leaks across spaces or workspaces | `::test_scenarios_stay_inside_their_space` (member of the other workspace refused by id) | passing |
| Variable created | `::test_variable_round_trip` | passing |
| Range must be ordered | `::test_unordered_range_refused` (422, nothing stored) | passing |
| Blank name refused | `::test_blank_variable_name_refused` (parametrized `` and whitespace, 422, nothing stored) | passing |
| A name is unique inside its space | `::test_duplicate_variable_name_refused` (422 in one space) | passing |
| Variable edited and deleted | `::test_variable_update_and_delete` | passing |
| Run created | `::test_run_round_trip` | passing |
| Assumptions are required | `::test_blank_assumptions_refused` (422, nothing stored) | passing |
| Unknown level refused | `::test_unknown_run_level_refused` (422, nothing stored) | passing |
| One base case per option | `::test_second_base_run_refused` (second base refused, repeated optimistic accepted) | passing |
| A value must belong to the space | `::test_run_with_foreign_variable_refused` (422, nothing stored) | passing |
| Declaring the same variable twice is refused | `::test_duplicate_variable_in_one_run_refused` (422, nothing stored) | passing |
| Run edited and deleted | `::test_run_update_and_delete` (values go with the run) | passing |
| A criterion flips inside a declared range | `::test_sensitivity_reports_the_flip_and_the_ranking` (exact interval and interpolated point) | passing |
| No declared point straddles the threshold | `::test_sensitivity_reports_beyond_the_declared_range` (travel direction, no crossing invented) | passing |
| Too few points | `tests/unit/scenarios/test_sensitivity.py::test_a_single_point_is_insufficient_and_not_ranked` (reported, ordered last) | passing |
| Several crossings are surfaced | unit `::test_several_crossings_report_the_narrowest_interval_and_the_count` | passing |
| Runs missing the metric are reported, not averaged | `::test_sensitivity_reports_incomplete_runs` | passing |
| Variables are ranked by implied impact | `::test_sensitivity_reports_the_flip_and_the_ranking` (exact order and slope range) + unit `::test_variables_rank_by_absolute_implied_slope` | passing |
| Evidence is reported without being attributed to a variable | `::test_evidence_counts_are_reported` (counts only; no per-variable field exists) | passing |
| The response carries no forecast | `::test_sensitivity_reports_the_flip_and_the_ranking` (exact top-level key set, and no occurrence of `predic` or `forecast` anywhere in the payload) | passing |
| No runs yet | unit `::test_no_runs_gives_an_empty_ranking` (empty ranking, not an error) | passing |
| A participant writes | `::test_participant_can_write` | passing |
| An uninvolved member cannot write | `::test_uninvolved_member_cannot_write` (403 on write, 200 on read) | passing |
| A refused write leaves no trace | the refusal tests assert `items == []` afterwards (`::test_blank_variable_name_refused`, `::test_unordered_range_refused`, `::test_unknown_run_level_refused`, `::test_run_with_foreign_variable_refused`, `::test_duplicate_variable_in_one_run_refused`) | passing |
| Variable rules (unit) | `tests/unit/scenarios/test_variables.py` (8 cases) | passing |
| Run rules (unit) | `tests/unit/scenarios/test_runs.py` (12 cases) | passing |
| Sensitivity computation (unit) | `tests/unit/scenarios/test_sensitivity.py` (12 cases, exact decimal results) | passing |
| Access rule (unit) | `tests/unit/scenarios/test_access.py` (6 cases) | passing |

Beyond the spec, two operations prove the criterion itself is checked: `::test_sensitivity_unknown_metric_is_not_found` (404) and `::test_sensitivity_requires_a_criterion` (422 when a query parameter is missing).

Command: `TEST_DATABASE_URL=… uv run pytest tests/integration/test_scenario_analysis.py tests/unit/scenarios -q` → 67 passed (24 integration, 43 unit).
Whole integration suite: 196 passed (was 172 after step 6).

## Boundary evidence

- OpenAPI export: `make contract` regenerated `contracts/openapi.json` and the TypeScript client. Canonical diff review: **0 operations removed, 0 updated, 9 added** (`list_scenario_variables`, `create_scenario_variable`, `update_scenario_variable`, `delete_scenario_variable`, `list_scenario_runs`, `create_scenario_run`, `update_scenario_run`, `delete_scenario_run`, `read_sensitivity`); paths 0 removed, 5 added; operations 75 → 84; schemas 100 → 112, **0 removed**.
- Migration `e1b7c9d3f425` applied cleanly on the disposable database; `alembic check` reports no drift.
- Strict Mypy includes `apps/api/src/modules/scenarios/domain` (Makefile + CI).
- Permissions are proved by PostgreSQL integration tests, not browser tests.
- Vocabulary recorded: `apps/api/CONTEXT.md` (ScenarioVariable, ScenarioRun, Sensitivity) and `docs/05-data-model.md`.

## Review findings applied

- **A real defect, found by the integration tests:** `Numeric(18, 6)` returns `Decimal("2.000000")`, so the API echoed `"2.000000"` for a range endpoint a user had set to `2`. Fixed on the read side with a plain-decimal serializer that normalizes integral values back to `"2"` (and keeps `100` from becoming `"1E+2"`).
- Three test-side corrections, the implementation being right: a cross-space test used a path that does not exist (405, not 404); the "incomplete run" test declared the metric it was meant to omit; two ruff findings in the test file.
- Two unit-test bugs of my own at the domain stage: a helper passing UUIDs as keyword arguments, and one "travels down without crossing" case whose numbers did in fact cross the threshold.

## Explicitly deferred (not gaps)

- No LLM. The Scenario Analyst (§13) and the Critic remain declared debts; this slice is deterministic by decision, so that the sensitivity promise is proved before a model can muddy it.
- Probabilistic models, Monte Carlo, workspace priors and validated narrow predictive models are deferred by §9 itself.
- Evidence is not attributed to a variable: nothing in the data model says which variable a Contribution is about. §9's "highest-impact variable with the weakest Evidence" is answerable by reading both, and becomes attributable only in a later slice that lets a Contribution name a variable.
- No user interface.

## Known gaps

- None. The implementation tasks are complete; the deferred items above belong to their own steps or to §9's later tiers.
