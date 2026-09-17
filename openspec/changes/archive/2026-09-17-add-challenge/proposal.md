## Why

`docs/00-project-overview.md` §7 makes the Critic the last gate before a commitment: it checks unsupported assumptions, contradictory evidence, hidden dependencies, failure modes, causal claims and missing success criteria, under one question - what could make us regret this decision. §8 then commits a Decision with its rationale, uncertainty and revisit triggers.

Options now exist with their evidence linked, but nothing records what was challenged about them. Without that structure, the Critic has nowhere to write and a Decision Record (step 6) has nothing to cite.

This change builds the structure only: the six checks as a closed vocabulary, a challenge run per Option, findings as records, and a read that shows which checks are covered. Every finding is grounded in the same rule the rest of the graph uses - a machine proposal is not canonical until a human confirms it. The Critic itself, the first component that needs a model, lands in the next slice and writes into this structure.

## What Changes

- Add a challenge run per Option with a closed lifecycle: `OPEN`, `RUNNING`, `COMPLETED`, `FAILED`.
- Add findings bound to a run, each carrying one of the six §7 checks, a severity, a detail statement and an origin (human or critic).
- Let a human record a finding of any kind, confirmed by construction; let a machine proposal enter as `proposed` and stay out of the canonical picture until a human confirms or dismisses it.
- Let the owner and the participants run a challenge, record and resolve findings, and complete the run; let every workspace member read.
- Expose which of the six checks are covered for an Option, as information, gating nothing.
- Keep the Critic out: no model call, no agent, no dispatch. The port it will implement is declared, not implemented.

## Capabilities

### New Capabilities

- `challenge`: A workspace can challenge an Option against the six checks of §7, recording findings a human confirms, and read what has been challenged and what remains uncovered.

## Impact

Adds a `challenge` vertical module (domain, adapters, service, api), one PostgreSQL migration with two tables, six HTTP operations, regenerated OpenAPI types and a FR/EN error key. It changes no existing contract: six operations are added, none removed, and the Option and evidence shapes are untouched. Confirming and dismissing share one resolution operation, since both are the same transition to one of two closed values. Deterministic unit, PostgreSQL integration and acceptance evidence, with no model call anywhere in the slice.

Tickets: GitHub #113 (this slice); the Critic proposer is its own later slice.
