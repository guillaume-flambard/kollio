# add-decision-screens

## Why

`docs/00-project-overview.md` §20 steps 5 and 6 close the reasoning phase: an Option is
challenged before it is chosen, and the choice is committed as a versioned record. The API
already holds both — the `challenge` module runs the Critic and stores its findings, and the
`decisions` module commits versioned records — but no screen reaches them. The Decision
section is still a placeholder that says what will live there, so a Space can be explored,
converged and filled with Options and still cannot be challenged or decided.

## What Changes

The `decision` section of a Decision Space becomes real:

- A member picks one of the Space's Options and opens a challenge on it. The section reads
  that Option's runs, shows the run status and the model that answered, and lists the
  findings the Critic proposed with their kind, their severity and their status. A member
  confirms or dismisses each proposed finding; nothing is settled automatically.
- A run that failed shows its stored reason, no findings, and the action that opens a new run
  on the same Option.
- The section states that the Critic proposes and a person decides, and it carries no
  verdict, no score, no ranking and no prediction about the Option.
- A member commits the Decision Record from `READY_TO_DECIDE`: the selected Option, the
  rationale, the rejected alternatives, the arguments for and against (confirmed
  Contributions of the Space), the critical assumptions, the unresolved uncertainty, the
  success criteria and the revisit triggers.
- Every committed version is listed and readable; an earlier version is never overwritten.

Six Nitro proxies carry the operations; the API contract is unchanged.

## Capabilities

### New Capabilities

- `decision-screens`

### Modified Capabilities

- None

## Impact

- Adds the body of the Decision section, six proxies (`list_challenges`, `open_challenge`,
  `resolve_challenge_finding`, `get_decision_record`, `list_decision_versions`,
  `commit_decision`), the Decision keys in both locales, and Playwright evidence on mocked
  routes.
- No API change, no migration, no agent call.
- Boundaries recorded in `acceptance.md`: `record_challenge_finding`, `complete_challenge`
  and `get_challenge` stay unsurfaced (the Critic records findings and completes runs, and a
  reader is served by `list_challenges`), and the record read answers `null` rather than an
  error when the Space has never been decided.

Tickets: GitHub #123 (migration steps 5 and 6 of `docs/00-project-overview.md` §20, screen
half; follows the API slices #113 and #114).
