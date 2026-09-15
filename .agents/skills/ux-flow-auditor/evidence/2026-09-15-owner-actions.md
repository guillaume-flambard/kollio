# Evidence record - Owner actions flow audit (2026-09-15)

## Identifiers

- `Timeline.Owner.IdeaDetail.Accept` - locales fr, en - scenarios OWNER-01
- `Timeline.Owner.IdeaDetail.Reject` - locales fr, en - scenarios OWNER-02
- `Timeline.Owner.IdeaDetail.Rollback` - locales fr, en - scenarios OWNER-03
- `Timeline.Owner.IdeaDetail.HideFromMember` - locales fr - scenarios MEMBER-04

## Scenario result

`apps/web/tests/browser/owner-actions.spec.ts`: **7 passed (20.3s)**, single
clean run, one worker. OWNER-01, OWNER-02 and OWNER-03 in fr + en, plus the
locale-independent MEMBER-04. Raw output:
`evidence/2026-09-15-owner-actions.spec-output.txt` (non-empty).

- OWNER-01: accept splices the proposal onto main and marks it accepted.
- OWNER-02: reject posts the rationale and shows it.
- OWNER-03: rollback appends the rollback message with the source hash.
- MEMBER-04: a member sees zero `[data-accept]` and `[data-rollback]` controls.

## Grounding checks

- **Locale:** `ideas.iterations.accepted`, `.rejected`,
  `.rollbackMessage` (`{hash}` interpolated), `.rationalePlaceholder`.
- **Tokens:** `--kollio-active-ink`, `--kollio-question`,
  `--kollio-radius-pill`, `--ui-border`, `--ui-text-muted`.

## Findings

1. **MEMBER-04 is locale-independent and runs once.** The single test at
   `owner-actions.spec.ts:106` sits outside the per-locale loop and loads the
   unprefixed route, so the permission-hiding guarantee is only proven against
   the default locale (fr). Given the audit rule that FR and EN are checked
   separately, the hidden-owner-action state in EN is not re-run per locale.
2. **No token or locale defect observed** on the tested paths.

## Verdict

OWNER-01/02/03 AUDITED for fr and en. MEMBER-04 AUDITED for fr only.
