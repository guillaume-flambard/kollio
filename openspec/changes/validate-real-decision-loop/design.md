## Context

The shipped product and the archived `verify-pilot-journey` change demonstrate a seeded, test-backed path. They do not establish that people use the product for a real decision or return after seeing an outcome. This change adds an evidence protocol only; it does not alter the product or collect decision content.

## Goals / Non-Goals

**Goals:**

- Create a repeatable, falsifiable way to validate the current product with two real participants.
- Preserve pilot confidentiality while retaining enough evidence to audit each milestone.
- Turn observed friction into explicit product decisions rather than an unprioritized feature list.

**Non-Goals:**

- Add analytics, telemetry, connectors, CRM records, or a participant recruiting workflow.
- Automate evaluation of decision quality or infer adoption from page views.
- Change the behavior covered by the existing seeded pilot or active feature changes.

## Decisions

### Use a private acceptance record rather than product analytics

The validation record will contain only pseudonymized roles, timestamps or ordered milestone references, completion states, and links to existing operational evidence. This preserves the product's private-memory promise and is sufficient for a small pilot. Product analytics would add data collection and consent work without proving the required behavioral milestones.

### Treat voluntary return as a separately evidenced event

The first decision may be facilitated to ensure that the pilot can reach the loop. A second Space only counts when the participant acts without an immediate facilitator prompt. This separates willingness to try the product from evidence of retained value.

### Keep product fixes in independent OpenSpec changes

The pilot records friction and its impact, but does not embed speculative fixes in this validation change. A fix with externally visible behavior gets its own proposal, delta specification, contract and evidence. This keeps the pilot evidence stable while implementation proceeds in small slices.

### Use existing evidence boundaries explicitly

Browser tests remain interface evidence under simulated API responses; integration tests remain persistence and authorization evidence. Pilot observations supplement these sources and do not replace them.

## Risks / Trade-offs

- [A short pilot window may not permit an observed outcome] → Record the uncompleted milestone and extend only the observation window, not the interpretation of evidence.
- [Facilitator involvement can be mistaken for adoption] → Record whether each milestone was guided and require an unprompted second-space event for voluntary return.
- [A small sample cannot prove broad PMF] → Report it as a narrow repeat-use signal and keep the conclusion bounded to the participants and decision context.
- [Pilot evidence could expose sensitive content] → Store pseudonymized roles and evidence references only; do not copy source text or decision rationale into the acceptance record.

## Migration Plan

1. Confirm the archived seeded-pilot evidence remains reproducible on the current revision.
2. Prepare one private Decision Space and two participant roles using the existing product.
3. Run the real loop and maintain `acceptance.md` as milestones occur.
4. Hold a short debrief, record friction dispositions, and create follow-up changes only for confirmed product needs.
5. Archive the change only after its acceptance record names every scenario as passed, incomplete, or deliberately not met.
