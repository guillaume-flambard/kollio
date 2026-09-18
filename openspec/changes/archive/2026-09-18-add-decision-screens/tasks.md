## 1. Vocabulary and routes

- [x] 1.1 Add the Decision keys to both locale catalogs and record the section's vocabulary in `apps/web/CONTEXT.md`.
- [x] 1.2 Add the six Nitro proxies the section needs, refusing a missing identifier before the API is reached.

## 2. The challenge half

- [x] 2.1 Let a member choose one of the Space's Options and open a challenge on it.
- [x] 2.2 Read that Option's runs: the run status, the model that answered and the stored reason of a run that failed.
- [x] 2.3 List the findings of the current run with their kind, their severity and their status, and let a member confirm or dismiss a proposed finding.
- [x] 2.4 Say plainly that the Critic proposes and a person decides, show the coverage the read carries, and offer the action that opens a new run after a failure.

## 3. The record half

- [x] 3.1 Read the current record and every committed version, and say the Space has not been decided yet rather than rendering nothing.
- [x] 3.2 Commit a record from `READY_TO_DECIDE`: the selected Option, a required rationale, the rejected alternatives, the arguments for and against, the critical assumptions, the uncertainty, the success criteria and the revisit triggers.
- [x] 3.3 Keep every version readable after a new commit, and refuse the commit form when the Space is not ready rather than letting the API refuse it.
- [x] 3.4 Refuse honestly: a member who is not a participant is told so, and a failed read says it could not be read.

## 4. Browser evidence

- [x] 4.1 Add failing browser specs for the whole section: no Option, opening a challenge, findings with their kind, severity and status, settling findings, a failed run and its retry, committing a record, a second version, the absence of any verdict, the refusal of a non-participant and a failed read.
- [x] 4.2 Carry them to green, keeping the two `decision-spaces.spec.ts` scenarios that assert the section's heading intact.

## 5. Documentation and verification

- [x] 5.1 Write the `decision-screens` spec delta with its observable scenarios.
- [x] 5.2 Record the scenario-to-test table, the boundaries and the deferred work in `acceptance.md`.
- [x] 5.3 Run lint, typecheck, the locale gate, the design-token gate, the UX coverage gate, the browser suite and the production build.
- [x] 5.4 Validate the change with OpenSpec.
