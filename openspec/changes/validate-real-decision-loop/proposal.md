## Why

Kollio's delivered loop is evidenced by simulated browser responses, integration tests, and bounded provider evaluations, but it has not yet demonstrated the product milestone that matters: two people making a real decision in their own words, observing an outcome, and voluntarily returning for another decision. The existing seeded pilot proves a demonstrable path; this change defines a distinct, privacy-preserving validation of repeated real use.

## What Changes

- Define a real-use validation protocol for one private Decision Space with two distinct participants, a recorded decision, an observed experiment outcome, and a confirmed learning.
- Require evidence of an unprompted second Decision Space created by a pilot participant after the first loop has reached an observed outcome.
- Record only the minimum pseudonymized operational evidence needed to distinguish product use from a scripted demonstration: timestamps, lifecycle transitions, participant roles, completion state, and voluntary-return evidence.
- Require a concise debrief that separates discovered product friction from feature requests and turns each material friction into a follow-up OpenSpec change or an explicitly deferred decision.
- Preserve the existing `pilot-path` seeded demonstration as a prerequisite and state its simulated-boundary limits rather than treating it as proof of real adoption.

## Capabilities

### New Capabilities

- `real-decision-loop-validation`: evidence and acceptance criteria for validating repeated, real collaborative use of the private decision loop without retaining pilot decision content.

### Modified Capabilities

- `pilot-path`: distinguish the seeded interface demonstration from real-use validation and make their evidence boundaries explicit.

## Impact

This change creates pilot-run evidence and a small, privacy-preserving validation record. It does not add product features, connectors, analytics tracking, public sharing, or new model-provider access. Implementation may use the existing authenticated product, its operational logs, and a manually maintained acceptance record; any friction that requires product behavior changes is deferred to its own change.
