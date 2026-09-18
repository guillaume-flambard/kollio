# Acceptance evidence - harden-agent-eval-recordings

The recorded corpus in `apps/api/tests/evals/fixtures` is the only evaluation net that runs without provider credentials, but it checked its own rules by hand: `test_recorded_findings.py` reimplemented the `source_ids` subset test instead of calling the runtime guard, the six constraint-analysis recordings were only measured through DeepEval metrics, and nothing asserted that every file in the folder is replayed. A recording could drift from the boundary it represents and still pass. This change replays every recording through the same validation the runtime applies: `validate_finding` from `apps/api/src/platform/llm.py:23` for the `GateFinding` recordings, and the strict `ConstraintAnalysisResult` model from `apps/api/src/modules/constraint_analysis/domain/models.py:75` for the six analysis recordings, with negative cases proving that a drifted recording fails and an inventory guard proving that no fixture is orphaned. No fixture, product file or provider call was added or changed.

Status: complete.

| Spec scenario | Evidence | State |
| --- | --- | --- |
| A recorded finding replays without credentials and is accepted only when its locale and citations are valid | `test_recorded_gate_finding_crosses_the_production_boundary` replays the six `competition.*` and `no_evidence.*` recordings through `validate_finding(output, input.locale, {item["id"] for item in input.evidence})` | Passing |
| A constraint analysis recording replays against the strict domain model, and an undeclared field is refused | `test_recorded_constraint_analysis_crosses_the_domain_boundary` validates the six `constraint_analysis.*` outputs with `ConstraintAnalysisResult.model_validate` and checks that the locale matches the request | Passing |
| A recording that drifted from the boundary fails the suite | `test_a_recording_with_the_wrong_locale_is_refused` (`wrong locale`), `test_a_recording_citing_an_identifier_never_supplied_is_refused` (`unknown evidence`) and `test_a_decided_recording_without_citations_is_refused` (`A decision requires evidence`) mutate reviewed recordings in memory and expect the guard to refuse them | Passing |
| A recording no test replays fails the suite | `test_every_recording_is_replayed_by_a_test` scans `apps/api/tests/evals` and `apps/api/tests/unit` for fixture names and families and asserts an empty orphan list | Passing |

## Verification runs (2026-09-18)

Live, in production, after the deploy:

- Not applicable. This change adds an offline test module; it ships nothing to `kollio.example.com` and calls no provider. The corpus runs in `make verify` and in the `verify` job of Foundations CI.

Local, before deploy:

- `uv run ruff check .`: `All checks passed!` (exit 0).
- `uv run ruff format --check .`: `1 file already formatted` (exit 0). The first draft raised two E501, a 107-character constant line and a 106-character guard line, and the project formatter rewrapped them before this check.
- `uv run pytest tests/evals/test_recorded_boundaries.py -q`: `16 passed` (6 gate recordings, 6 analysis recordings, 3 refusal cases, 1 inventory guard).
- `uv run pytest -m 'not live' -q`: `557 passed, 239 skipped, 2 deselected` (exit 0). The two deselections are the live cases; the skips are the Postgres-URL-dependent integration, performance and E2E modules.
- A first run of the same command failed two tests, `tests/unit/test_http.py::test_unauthenticated_idea_request_is_localized` and `tests/unit/test_http.py::test_liveness_does_not_require_database`, on `redis.exceptions.ConnectionError` against `localhost:63799`. That port is the repository's own development Redis (`src/platform/config.py:12` and the `redis` service in the root `docker-compose.yml`), which was not running. After `docker compose up -d redis` the same command returned the green result above. The failures were environmental and unrelated to this change, which only adds a test module.

## Known boundaries

- The boundary proved here is the code's, not a provider's. The recordings are replayed through the same validators the runtime uses, but nothing in this change contacts a model.
- The suite measures conformance to the boundary, not the quality of the judgment inside each recording. The reviewed verdicts keep the meaning they had when they were recorded.
- `local_retrieval.fr_en.json` is consumed by the unit suite (`apps/api/tests/unit/test_embeddings.py:11`), which is why the inventory guard scans both test roots instead of only `tests/evals`.
- The orphan guard matches a fixture either by its file name or by a declared family such as `constraint_analysis.no_evidence.*.json`. A future test that builds a fixture path from pieces the regex cannot see would need the guard extended.
