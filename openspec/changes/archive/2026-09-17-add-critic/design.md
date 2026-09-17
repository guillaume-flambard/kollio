## Context

`add-challenge` shipped the structure and declared two ports it did not implement: `ChallengeGateway` (the Critic) and `ChallengeQueue` (dispatch). This slice implements both, keeping every rule the `challenge` capability already states. The model call is the only new non-determinism; everything around it stays testable without a model.

## The brief

The Critic receives a structured brief, never raw Branch material:

| Part | Source | Notes |
| --- | --- | --- |
| `question` | the Decision Space | the one question being converged on |
| `option.title`, `option.proposal` | the Option | required fields |
| `mechanism`, `upside`, `cost`, `risks`, `critical_assumptions`, `success_metrics` | the Option | optional; absent fields are omitted rather than sent as empty strings |
| `evidence_for`, `evidence_against` | confirmed Contributions linked through `OptionEvidence` | each carries its id, title and body |

A `suggested` Contribution is never sent as evidence: the brief may only cite material the Space already treats as canonical, which is the same rule the manual link operation enforces.

The brief carries Contribution ids so the Critic can cite its sources, and every returned citation is checked against the ids actually sent. A finding citing anything else is refused, because an unverifiable citation is how a critic invents support.

## Trust rules (§13)

- The Critic proposes; it never promotes. Findings arrive with origin `critic` and status `proposed`.
- No finding is confirmed on arrival, and a confirm or dismiss remains a human write through the existing resolution operation.
- A dismissed finding keeps its row: a wrong challenge is convergence data too.
- No consensus is fabricated: the Critic returns findings, never a verdict about the Option as a whole.
- Uncertainty is expressed as severity (`low`/`medium`/`high`) and as an honest `unknown` where the brief does not say. Nothing in the response is presented as a probability.
- The model that produced the findings is recorded on the run, so a finding can always be traced to the model and moment that raised it.

## Execution

Opening a challenge creates the run (`RUNNING`) and dispatches it, exactly as the constraint analysis dispatches a workflow from its route. The worker:

1. loads the run by id and its Option, space and linked evidence;
2. assembles the brief;
3. calls `ChallengeGateway.challenge(brief, locale)`;
4. validates every returned finding against the closed vocabularies and the sent citations;
5. writes them through the existing `create_finding` path with origin `critic` and status `proposed`, and records the model on the run;
6. completes the run.

Steps 1, 4, 5 and 6 are deterministic and proved with a fake gateway. Step 3 is the declared model boundary.

**Failure semantics.** Validation happens before any write, so a run whose findings are partly invalid stores nothing rather than a partial set. A gateway error, an empty result or an unparseable response ends the run `FAILED` with a reason and writes no findings. A dispatch that cannot be queued fails the run for the same reason, so no run is left `RUNNING` forever. A failed run can be retried by opening a new one; the failed row is kept.

## Routing and cost (§19)

The Critic is a high-value moment, so it runs on the visible tier: `TaskClass.CHALLENGE` for the call, `resolve_model` for the model, and a single request per run. Findings are bounded by a maximum count so one run cannot flood the Space.

## Boundary

- `challenge/domain/critic.py` — the pure validation of a candidate finding: kind, severity, non-blank statement, citation membership. No I/O, under strict Mypy.
- `challenge/adapters/critic.py` — `LLMChallengeGateway` implementing the declared `ChallengeGateway`, mirroring `constraint_analysis/adapters/litellm.py` (prompt composed with the untrusted-content and locale clauses, JSON-schema response format, OTel span, `resolve_model`).
- `challenge/adapters/taskiq.py` — `TaskiqChallengeQueue` implementing the declared `ChallengeQueue`.
- `challenge/service/challenge.py` — `execute_run(repository, gateway, run_id, locale)`, taking the gateway as a parameter so a fake drives it.
- `platform/worker.py` — one `@broker.task`, mirroring `constraint-analysis.execute`.
- One nullable `failure_reason` column on `challenge_runs`.

## Deliberately out of scope

- The Memory Retriever (§11): the Critic does not yet read prior Learnings. That is the next slice and the reason the brief is assembled in one place.
- Scenario variables in the brief (§9): a sensitivity read is not evidence about an Option's assumptions.
- Any screen, and any new HTTP operation.
- A recorded critic fixture under `tests/evals/fixtures/`: recording one needs a live model call, which is guarded, budgeted and never part of CI. Declared as an eval debt rather than hand-authored, because a hand-written "recording" would not be a recording.

## Open questions

- Should a run be retried automatically on a transient gateway failure, or is a new run the honest retry? Today: a new run, because a retry would need the run's brief to be reproducible from stored state, which it is, but it would also hide how many attempts a person triggered.
- Should the Critic receive the Option's previously dismissed findings, so it stops re-raising what a human already settled? That belongs with the Memory Retriever's slice, which has the retrieval machinery.
