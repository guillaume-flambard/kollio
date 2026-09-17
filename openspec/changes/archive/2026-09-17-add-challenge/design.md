## Context

`docs/00-project-overview.md` §7 names six checks the Critic performs before a commitment, and §13 gives the Critic two concrete jobs (weak assumptions, failure modes) inside an assistant that structures and criticises but never decides. §8 commits a Decision that must still make sense six months later, which means the challenges raised have to be recorded rather than remembered.

This design settles the shape those challenges take, and nothing else. It ships no model call: the deterministic structure is what the Critic will later write into, and what a facilitator can already use by hand.

## Domain model

`ChallengeRun` is an Option-scoped aggregate: one attempt at challenging one Option.

| Field | Kind | Notes |
| --- | --- | --- |
| `id` | identity | server-generated |
| `space_id` | reference, required | the privacy boundary, carried so a run is never reachable outside its Space |
| `option_id` | reference, required | the Option being challenged |
| `status` | closed value | `OPEN`, `RUNNING`, `COMPLETED`, `FAILED` |
| `opened_by` | reference, required | a workspace member |
| `model` | text, optional | which model produced findings, null until the Critic runs |
| `lang` | code, required | the language of the last write, as everywhere else |
| `created_at`, `updated_at` | timestamps | platform convention |

`ChallengeFinding` is one recorded objection.

| Field | Kind | Notes |
| --- | --- | --- |
| `id` | identity | server-generated |
| `run_id` | reference, required | |
| `kind` | closed value | the six §7 checks |
| `severity` | closed value | `low`, `medium`, `high` |
| `detail` | text, required | what could make us regret this, stated plainly; trimmed, non-empty |
| `origin` | closed value | `human` or `critic` |
| `status` | closed value | `proposed`, `confirmed`, `dismissed` |
| `contribution_id` | reference, optional | the Contribution the finding is about, when it is about one |
| `lang` | code, required | |
| `created_at`, `updated_at` | timestamps | |

The six kinds are exactly `unsupported_assumption`, `contradictory_evidence`, `hidden_dependency`, `failure_mode`, `causal_claim`, `missing_success_criteria`. A seventh check is a change to §7, not a value someone adds at runtime.

## Rules

**Origins follow the same asymmetry as Contributions.** A finding a human records is `confirmed` on arrival: a person stating an objection is the canonical act. A finding the Critic proposes is `proposed` until a human confirms or dismisses it. Dismissal is a real outcome, not a deletion: "we looked at this and it does not hold" is durable convergence data, exactly like a corrected cluster.

**A rejected finding keeps its record.** Nothing is deleted, so a later reader sees that the challenge was considered and answered.

**The lifecycle is a closed set.** `OPEN` -> `RUNNING` -> `COMPLETED`, and `FAILED` from `RUNNING`. A `COMPLETED` or `FAILED` run is terminal. This slice opens runs directly in `RUNNING` (there is nothing to queue yet); the `OPEN` state exists so the Critic's future dispatch has a place to wait, and `FAILED` exists so a failed model call is recorded rather than lost.

**Coverage is information, not a gate.** The read reports which of the six checks carry at least one non-dismissed finding. It does not refuse a transition, does not block a Decision and produces no score - §7 forbids a fake universal score, and §21 puts outcomes over vanity metrics. Whether coverage should gate a commitment is a question for the Decision Record (step 6) and is answered there, not here.

## Permissions

- **Workspace = privacy boundary.** Any authenticated member of the owning workspace may read a run and its findings; everyone else receives the workspace-not-found treatment, so membership cannot be probed by identifier.
- **Write set = owner plus participants** of the parent Space, for opening a run, recording a finding, resolving one and completing a run.
- **A finding belongs to its Option.** A run for one Option never appears under another, even by supplying identifiers, because both the Space and the Option are checked against the path.

## Boundary

A new vertical module `apps/api/src/modules/challenge/` following the platform's lightweight hexagonal seam:

- `domain/` — the closed kinds, severities, statuses and origins; the finding-shape rule; the run lifecycle; the coverage computation; the access predicate. Pure, under strict Mypy, unit-tested with no database.
- `adapters/postgres.py` — the only place that touches the ORM or flushes.
- `service/challenge.py` — orchestration: open, read, record, confirm, dismiss, complete.
- `service/ports.py` — the `ChallengeGateway` protocol the Critic will implement, declared with no implementation, so the next slice adds an adapter rather than reshaping the module.
- `api/routes.py`, `api/schemas.py` — localized, authenticated endpoints; schemas are the request/response boundary.

Operation shapes follow the existing modules (`options`, `converge`) rather than being invented here: nesting under the workspace and the space, then the option, then the challenge.

## Persistence

One Alembic migration adding two tables:

- `challenge_runs` — required FKs to `decision_spaces` and `options` (both cascading), a closed status check, the platform's `lang` and timestamp columns.
- `challenge_findings` — required FK to `challenge_runs` (cascading), closed checks on `kind`, `severity`, `origin` and `status`, a non-blank `detail` check, an optional `contribution_id` FK, indexed by run.

Facts proved on a disposable PostgreSQL, not in the browser: cross-workspace isolation by identifier, the non-member refusal on every operation, and that a refused write stores nothing.

## Deliberately out of scope

- The Critic itself: no model call, no prompt, no agent graph, no queue dispatch. The gateway protocol is declared and unimplemented.
- Assumptions as their own entity (the Assumption half of §18) — a finding names what it is about in prose and, when it is about a Contribution, by reference. Assumptions arrive with Converge's AI slice.
- The Decision Record and any gating of a commitment (step 6).
- Anything about success metrics being recorded or tracked; §7 only requires that their absence is checkable.
- Any user interface.

## Open questions

- Should a run be reopenable after `COMPLETED`, or is challenging again always a new run? This slice chooses new runs, which keeps the existing run's findings frozen as the record of what was checked at that time.
- Should severity stay three-valued? It is deliberately coarse; if it turns out to drive nothing, it should be removed rather than extended.
