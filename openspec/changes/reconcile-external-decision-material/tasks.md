## 1. Source material domain and boundary

- [x] 1.1 Add immutable source material, revision, excerpt, and reconciliation-resolution persistence scoped to a Decision Space; verify targeted domain tests cover version retention, workspace isolation, and append-only resolution history.
- [ ] 1.2 Define Pydantic request and response schemas and FastAPI routes for manual text import, revision creation, excerpt promotion, source reads, and reconciliation resolution; verify `make contract` and generated API client output.
- [ ] 1.3 Extend Contributions with nullable typed source provenance without changing existing reads; verify existing Branch and Contribution integration tests remain green.

## 2. Grounded reconciliation workflow

- [ ] 2.1 Implement a LangGraph Companion reconciliation workflow with Pydantic structured outputs constrained to selected excerpts and confirmed Contributions; verify recorded evaluation fixtures reject missing or foreign citations.
- [ ] 2.2 Persist Companion proposals as non-canonical review material and require an explicit human resolution to affect shared reasoning; verify no tool call changes a Contribution, source revision, or Decision Record.

## 3. Reconciliation surfaces

- [ ] 3.1 Add Explore import, source revision, excerpt-selection, and promotion flows using FR/EN catalog keys; verify browser scenarios distinguish raw material from confirmed reasoning.
  - [ ] 3.1.1 Render a private source shelf that identifies author, originating tool, version, language and import time without representing raw material as shared reasoning.
  - [ ] 3.1.2 Let a participant create a revision and select bounded excerpts before any Companion action; preserve both source versions after reload.
  - [ ] 3.1.3 Let a participant promote a selected excerpt into a Contribution only through the existing human confirmation boundary.
- [ ] 3.2 Add a reconciliation view that compares selected source-backed Contributions and records combined, retained, rejected, or open outcomes with rationale; verify an open disagreement is not rendered as consensus.
  - [ ] 3.2.1 Make the Jean-Pierre and Corinne comparison legible as two cited source paths plus an explicit divergence, not as an automatically merged document.
  - [ ] 3.2.2 Let a member retain one view, combine compatible parts, reject a proposal, or leave the disagreement open, each with a human rationale.
  - [ ] 3.2.3 Render Companion output only as a review proposal with citations and confidence boundaries; it never changes shared reasoning by itself.
- [ ] 3.3 Add Converge source-lineage affordances that reach the cited excerpt without duplicating raw material on the map; verify browser coverage in French and English.
  - [ ] 3.3.1 Expose a compact lineage cue from a Contribution or finding to its source excerpt, with a keyboard-reachable inspection path.
  - [ ] 3.3.2 Keep the Converge map focused on confirmed reasoning, with one visible relationship treatment only where it explains a source or unresolved disagreement.

## 4. Evidence and delivery

- [ ] 4.1 Run domain, integration, browser, locale, type, and contract checks; verify results are recorded against every OpenSpec scenario in `acceptance.md` with simulated boundaries stated.
- [ ] 4.2 Exercise the Jean-Pierre and Corinne reconciliation journey with two source revisions and a human resolution; verify both original sources, the divergence, and the final rationale survive reload.
