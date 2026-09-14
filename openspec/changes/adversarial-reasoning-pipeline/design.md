# Design

## Where the pipeline lives

The orchestration is `agent/pipeline.py::run_constraint_pipeline`, a plain
async function the graph's single analyze node calls. It is deliberately not
five graph nodes: the graph, the HITL review interrupt, the worker and the
member-facing `ConstraintAnalysisResult` response all stay exactly as they were.
The pipeline is one cohesive step that happens to spend five model calls, so
the checkpoint still pauses once, at review, on the same state key.

## Order, tiers and routing

`STEP_ORDER` fixes analyst, challenger, evidence_critic, company_fit,
synthesizer. `STEP_TASK_CLASS` maps each to a `TaskClass` (#75); the tier comes
from `intelligence_tier` and the model from `gateway.model_commodity` /
`model_visible`. So analyst runs cheap and the rest run premium, with no
call-site model names.

## Enforcement

`require_synthesis_inputs` runs after the critic and before the synthesizer and
raises `PipelineIncompleteError` if the challenger or the evidence critic
produced nothing. The worker treats that as a non-retryable failure (alongside
the unsupported-locale guard) so a soft conclusion is never published. The
synthesizer prompt states it must reflect the challenger and the critic and not
soften; the enforcement is structural, not a suggestion.

## Persistence and the brief

`build_decision_brief` assembles a compact dict (title, pitch, profile, active
objectives and constraints, evidence capped at 8). The synthesizer validates its
output with the existing `validate_analysis_result` against the brief's evidence
and context ids, so the K/A/U and contradiction invariants from #58 are
unchanged. Each step's `PipelineStep` (name, tier, model, output) is written to
`constraint_analyses.steps` and, before review, to `analysis_workflows.draft_steps`.

## Testing without a live provider

The order, tiers, the one-result contract and the skip-enforcement are unit-
tested with a scripted reasoning gateway. The routing (analyst cheap, rest
premium) is captured through a queued fake HTTP client. The agentic E2E drives
the real worker and the real gateway against a fake OpenAI server that answers
by requested schema name, asserting the five calls in order. No live provider in
CI.
