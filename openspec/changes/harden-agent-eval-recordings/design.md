# Design - harden the recorded evaluation corpus

## Context

The corpus is thirteen JSON fixtures replayed by three test files under `apps/api/tests/evals`, and their shapes split in three:

- Gate findings: four `competition.*` recordings (`provenance`, `input`, `expected`, `output`) and two `no_evidence.*` recordings (`input`, `expected_verdict`, `output`, `model`). The recorded `output` is a `GateFinding`: `verdict`, `reason`, `source_ids`, `established_facts`, `locale`.
- Constraint analyses: six `constraint_analysis.{contradiction,no_evidence,reuse}.{en,fr}` recordings whose `output` carries `overall_score`, `verdict`, `summary`, `factors`, `contradictions`, `locale`.
- One retrieval recording, `local_retrieval.fr_en.json`, already replayed by `apps/api/tests/unit/test_embeddings.py`.

What the suite checks today: `test_recorded_findings.py` asserts the expected verdict and the provenance of each competition case, and re-implements the evidence rule with a hand-written subset test; `test_constraint_analysis_recordings.py` runs two DeepEval metrics over the recorded outputs; `test_contract.py` refuses synthetic invalid objects. The production boundaries are `validate_finding` for gate findings and the strict `ConstraintAnalysisResult` for the analysis. No recording is replayed through either, so the corpus can stay green while the boundary it stands for moves.

## Goals / Non-Goals

**Goals:**
- Every gate recording replayed through the production validator, with the identifiers it supplied.
- Every constraint recording replayed through the strict domain model.
- The negative path proven on a mutated copy of a reviewed recording.
- No orphan fixture: every file in the corpus is replayed by a test.
- No provider call introduced.

**Non-Goals:**
- Fabricating new recordings.
- Changing fixture contents, the production validators, the live path or the budget guard.
- Extending the existing DeepEval metrics.

## Decisions

### Replay the recording instead of re-implementing the rule

The hand-written subset check in `test_recorded_findings.py` duplicates a rule that already lives in `validate_finding`. Replaying removes the second definition, and a future change to the validator then moves the recordings with it, which is what a regression net is for. The alternative, keeping the local helper and adding a parallel assertion, leaves two definitions of the same rule free to drift apart.

### Prove the negative path on a mutated recording

`test_contract.py` already shows that a synthetic object is refused, and it stays. What it cannot show is that a reviewed recording sits close enough to the boundary for a small mutation to be caught, which is the failure mode that matters when someone edits a fixture. The mutation happens on an in-memory copy, never on the file. The alternative, building a fresh invalid object, would duplicate the contract test instead of tying the check to the corpus.

### Keep the strict domain model as the constraint boundary

`ConstraintAnalysisResult` is `extra="forbid"`, `strict=True`, requires five unique factors and ties the unknown verdict to `overall_score is None` with every factor unknown. Replaying the six recordings through it is the closest honest statement to "this answer would have been accepted" without a provider. The alternative, a local check of the score range, would miss both the undeclared-field rule and the factor rules.

### Guard the inventory

A corpus grows by adding files, and nothing currently fails when a recording is added and no test replays it. The check scans the fixtures folder and both test roots, because `local_retrieval.fr_en.json` is legitimately consumed by the unit suite rather than by the evals folder.

## Migration Plan

1. Add the replay tests, the negative checks and the inventory guard under `apps/api/tests/evals/`.
2. Run the suite. A failure here is a finding about a recording or about a boundary, to report rather than to work around.
3. Prove detection: the negative checks mutate a copy in memory, and the report adds a temporary file mutation that is restored straight after.
4. Run `uv run ruff check .`, `uv run ruff format --check .` and `uv run pytest -m 'not live'`.

Rollback: revert the commit. No data, contract or runtime state is involved.
