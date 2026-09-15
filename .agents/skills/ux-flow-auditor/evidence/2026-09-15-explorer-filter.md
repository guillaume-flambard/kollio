# Evidence record - Explorer filter toolbar audit (2026-09-15)

## Identifiers

- `Explorer.Filter.Toolbar.ApplyRole` - locales fr, en - scenarios EXPLORER-02
- `Explorer.Filter.Toolbar.ApplyRealism` - locales fr, en - scenarios EXPLORER-03, EXPLORER-05

## Scenario result

`apps/web/tests/browser/explorer.spec.ts`: **10 passed (57.1s)**, single clean
run, no concurrent runners. Covers EXPLORER-01/02/03/04/05 in fr + en.
Raw output: `evidence/2026-09-15-explorer-filter.spec-output.txt` (non-empty).

- EXPLORER-02: role select sets `sought_role=marketing` through the mocked API.
- EXPLORER-03: grounded button sets `realism_min=60` through the mocked API.

## Grounding checks

- **Tokens:** toolbar styles reference only `--ui-*` / `--kollio-*` semantic
  tokens (`apps/web/app/pages/workspace/index.vue`, lines ~237-238 and rail
  rules); `check_design_tokens.mjs` green, zero hex literals in the rail.
- **Locale:** role select aria-label resolves `ideas.detail.team.soughtTitle`
  ("Roles recherches" / "Sought roles"); grounded button resolves
  `ideas.explorer.realism.grounded` ("Initiatives ancrees" /
  "Grounded initiatives"). Both keys present in fr and en catalogs.
- **Vocabulary:** Explorer, role filter, realism band match
  `apps/web/CONTEXT.md` domain language. No invented synonyms.

## Findings

1. **Realism filter unreachable below 761px - FIXED same day.** The grounded
   button carried `class="domain-filter"` (`index.vue:157`), and the
   `@media (max-width: 760px)` block set
   `.ideas-filter-rail .domain-filter { display: none; }` with no mobile
   alternative. Fix: removed `.domain-filter` from the `display: none`
   selector and gave it an explicit visible chip style (`display: flex;
   min-height: 44px; margin-top: 8px`), so it survives as a tappable chip in
   the collapsed rail. Layout-only change, `check_design_tokens.mjs` still
   green. Regression test EXPLORER-05 (390px viewport, fr+en) failed before
   the fix, passes after. Tracked as issue #99, now closed.
2. **Role select survives small screens.** `.rail-select` is not in the hidden
   set; the rail nav collapses to `flex-wrap` and buttons keep
   `min-height: 44px` (touch target preserved).

## Verdict

Both flows AUDITED for desktop and mobile viewports (EXPLORER-05 covers the
390px case for the realism filter).
