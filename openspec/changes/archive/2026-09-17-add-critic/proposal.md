## Why

`docs/00-project-overview.md` §7 gives every Option a Critic that checks unsupported assumptions, contradictory evidence, hidden dependencies, failure modes, causal claims and missing success criteria, and asks one question: what could make us regret this decision? §13 makes that Critic a facilitator and a critic, never an oracle: it traces its structure to sources, exposes uncertainty, and never promotes anything to canonical on its own.

The Challenge structure shipped in `add-challenge` gave the Critic a place to write: runs, the six checks, severities, and the rule that a machine finding arrives as a proposal a human settles. Nothing writes into it yet. A run today completes holding whatever a person typed, which is the manual behaviour the product already had, and coverage stays empty because no machine ever looked.

## What Changes

- Implement the declared `ChallengeGateway`: one adapter that assembles a brief from the Option and its linked Evidence, calls the model once, and returns candidate findings.
- Assemble the brief from structured material only: the Option's own §7 fields and the confirmed Contributions linked as Evidence for or against. Raw Branch content is never sent.
- Execute a run: opening a challenge dispatches the run through the queue, the worker calls the Critic, validated findings are recorded with a `critic` origin and a `proposed` status, and the run completes.
- Validate every returned finding before it is stored: a known check, a known severity, a non-blank statement, and a citation that names a Contribution of the same Space. Nothing partial is stored.
- Record the model that produced the findings on the run, and the reason on a run that failed.
- A failed or refused run writes no findings, ends `FAILED`, and says why; a dispatch that cannot be queued fails the run rather than leaving it running forever.
- Keep the human half untouched: a machine finding is never confirmed on arrival, coverage stays informational and gates nothing, and nothing ranks or scores an Option.
- Ship no screen and no new HTTP operation: the run is triggered by the existing `open_challenge`.

## Capabilities

### Modified Capabilities

- `challenge`: the Critic half of the capability described in `openspec/specs/challenge/spec.md`. The structure, the six checks, the run lifecycle, the human resolution rules and coverage are unchanged; this adds who writes into that structure and under which constraints.

## Impact

Adds a Critic adapter, a queue adapter, one Taskiq task, one service execution path, and one nullable `failure_reason` column with the three adapter methods the worker path needs (`run_by_id`, `fail_run`, `set_run_model`). No HTTP operation is added, changed or removed. No migration of existing rows: runs recorded before this change keep a null model and a null reason, which reads as "no Critic looked at this run". Existing challenge tests gain a queue override so they do not reach Redis.

Tickets: GitHub #118 (step 8 of the Critic's own sequence in `docs/00` §7; follows #113).
