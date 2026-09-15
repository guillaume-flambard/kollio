# Evidence record - Initiative type flow audit (2026-09-15)

## Identifiers

- `Initiative.Type.Deposit.Select` - locales fr, en - scenarios TYPE-01
- `Initiative.Type.IdeaDetail.Change` - locales fr, en - scenarios TYPE-02
- `Initiative.Type.IdeaDetail.HideFromNonOwner` - locales fr, en - scenarios TYPE-03

## Scenario result

`apps/web/tests/browser/initiative-type.spec.ts`: **6 passed (11.6s)**, single
clean run, one worker. TYPE-01, TYPE-02 and TYPE-03 in fr + en. Raw output:
`evidence/2026-09-15-initiative-type.spec-output.txt` (non-empty).

- TYPE-01: the deposit POST carries `initiative_type: 'campaign'`.
- TYPE-02: the owner PATCH changes the type to `pricing` and the selector holds
  the new value.
- TYPE-03: a non-owner sees the localised type label and no selector.

## Grounding checks

- **Locale:** `ideas.initiativeType.*` and `ideas.initiativeTypeLabel` resolve in
  fr and en; the deposit title and pitch keys resolve too.
- **Tokens:** the selector inherits the deposit field styling
  (`--ui-border`, `--ui-bg-elevated`, `--ui-text`).

## Findings

1. **Vocabulary check passes.** The user-facing field uses
   `ideas.initiativeTypeLabel` and the Initiative wording required by
   `apps/web/CONTEXT.md`; no second meaning for "Idea" is introduced.
2. **No token or locale defect observed** on the tested paths.

## Verdict

All three initiative-type flows AUDITED for fr and en.
