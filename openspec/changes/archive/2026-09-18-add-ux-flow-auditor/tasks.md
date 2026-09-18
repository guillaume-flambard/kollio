## 1. Tranche 0 - Tooling spike

- [x] 1.1 Run Playwright MCP against the Explorer filter flow and the Deposit
  submit flow with mocked API routes, and record setup cost, mock fidelity, and
  evidence quality.
- [x] 1.2 Run agent-browser against the same two flows and record the same
  three measures.
- [x] 1.3 Record the tooling decision and its rationale in `acceptance.md`
  before starting Tranche 2.

## 2. Tranche 1 - Minimal auditor skill

- [x] 2.1 Create `.agents/skills/ux-flow-auditor/SKILL.md` with identifier
  grammar, AUDITED-only-with-evidence rule, Living Canvas and i18n grounding,
  and the evidence record format.
- [x] 2.2 Verify the skill loads and its references (tokens path, CONTEXT.md
  path, example spec) resolve.

## 3. Tranche 2 - Scoped product-auditor agent

- [x] 3.1 Create the agent definition scoped to read-only audit plus
  evidence-file writes, bound to the Tranche 0 tooling decision.
- [x] 3.2 Run the agent once against the Explorer filter flow in FR and EN
  and verify the evidence record links a passing scenario and non-empty
  evidence.

## 4. Tranche 3 - Coverage registry and gate

- [x] 4.1 Create `.agents/skills/ux-flow-auditor/COVERAGE.md` seeded with the
  Explorer filter flow from the existing `EXPLORER-02`/`EXPLORER-03` scenarios.
- [x] 4.2 Add `scripts/check_ux_coverage.mjs` failing on AUDITED rows with
  missing or empty evidence, and verify it passes on the seed and fails on a
  deliberately broken row.
- [x] 4.3 Link every acceptance criterion in `acceptance.md` to its evidence.
