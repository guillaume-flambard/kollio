# Evidence record - Responsive flow audit (2026-09-15)

## Identifiers

- `IdeaDetail.Experiments.Panel.HoldAtWidth` - locales fr - scenarios RESP-375, RESP-768
- `WorkspaceArea.Context.Settings.HoldAtWidth` - locales fr - scenarios RESP-375, RESP-768
- `Deposit.Submit.Form.HoldAtWidth` - locales fr - scenarios RESP-375, RESP-768
- `Deposit.Submit.Form.NarrateAtPhone` - locales fr - scenarios RESP-narration
- `WorkspaceArea.Navigation.TopBar.Open` - locales fr - scenarios NAV-mobile
- `Explorer.Filter.Rail.FitAtPhone` - locales fr - scenarios NAV-mobile
- `WorkspaceArea.Navigation.Rail.PersistDesktop` - locales fr - scenarios NAV-desktop

## Scenario result

`apps/web/tests/browser/responsive.spec.ts`: **10 passed (15.5s)**, single
clean run, one worker. Raw output:
`evidence/2026-09-15-responsive.spec-output.txt` (non-empty).

- RESP-375 / RESP-768: idea detail, onboarding wizard and deposit form hold with
  `scrollWidth - clientWidth <= 1`.
- RESP-narration: running narration fits 375px.
- NAV-mobile: the top-bar menu reveals every destination, exposes 5
  `aria-disabled` entries and holds width.
- NAV-desktop: the persistent rail returns at 1440px.

Locales: the spec asserts French UI strings only (`Expériences`, `Amorcer le
contexte de l'entreprise`, `Déposer l'initiative`, `Ouvrir la navigation`,
`Navigation principale`). English at these widths is not exercised, so the rows
are marked `fr` only.

## Grounding checks

- **Locale:** every asserted label resolves `ideas.experiments.title`,
  `workspace.settings.onboarding.title`, `ideas.deposit.title`,
  `navigation.label`, `ideas.explorer.forYou`.
- **Tokens:** layout uses `--kollio-display-hero`, `--kollio-radius-lg`,
  `--ui-border`, `--ui-bg-elevated`; no fixed widths overflow.

## Findings

1. **Contrast: disabled nav entries below AA.** The nine `aria-disabled`
   destination spans (`WorkspaceNav.vue:37,46`) use Tailwind `text-muted/75`,
   i.e. `--ui-text-muted` at 75% over `--ui-bg-elevated`. Measured that is
   3.14:1, under the 4.5:1 AA floor. NAV-mobile counts these five-plus entries
   as present but never checks their legibility.
2. **Invalid `aria-disabled` usage.** `aria-disabled="true"` sits on plain
   `<span>` elements (`WorkspaceNav.vue:37,46`) with no widget role. The
   attribute is not supported on a generic role, so assistive tech may ignore
   it and announce the upcoming destinations as ordinary reachable text, which
   contradicts the intent of the disabled state.
3. **WorkspaceArea nav has disabled destinations.** Five destinations render as
   non-interactive placeholders by design; NAV-mobile asserts exactly that, so
   coverage is honest, but there is no visible reason text or tooltip on them.

## Verdict

All seven responsive flows AUDITED for French. English string rendering at
375/768px remains unverified.
