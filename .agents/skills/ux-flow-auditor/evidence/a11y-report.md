# Accessibility audit

Scope: the six screens the frontend verification brief names (landing, /workspace/ideas, /workspace/deposit, /workspace/ideas/[ideaId], /workspace/people/[userId], /workspace) plus /workspace/settings, in French and English.

Method: Chromium against the Nuxt app served by the repository Playwright webServer, with API responses simulated. Two disposable specs produced the rendered evidence (`apps/web/tests/browser/a11y-audit-tmp.spec.ts`, pre-existing, and `apps/web/tests/browser/a11y-probe-tmp.spec.ts`, written for this audit and deleted before the change landed). Raw measurements were written to a JSON file, one record per test, kept at `.agents/skills/ux-flow-auditor/evidence/2026-09-18-a11y-probe.json`; the rendered values quoted below come from it. Contrast was computed by compositing translucent backgrounds and applying the WCAG ratio. Claims that do not come from a rendered measurement are marked source-only and cite `file:line`.

Result: 5 findings (0 blocker, 2 major, 3 minor), and 10 checks verified clean across the same screens. The two major findings are on the explorer, the screen a contributor spends the most time in.

Three of the five map onto a WCAG 2.2 success criterion: A11Y-1 to 4.1.2 Name, Role, Value (A), A11Y-2 to 1.3.1 Info and Relationships (A) plus invalid HTML nesting, A11Y-4 to 4.1.3 Status Messages (AA). A11Y-3 and A11Y-5 are best-practice findings (unique landmark names, a level-1 heading above the sections) rather than conformance failures: no success criterion requires them, so they are advisory and can be deferred without claiming non-conformance. The adversarial review of this report (`evidence/adversarial-review.md`) records the same reading.

## Findings

### A11Y-1 (major) The explorer search field has no accessible name

Screen: WorkspaceArea.Ideas.Explorer, fr and en.
Where: `apps/web/app/pages/workspace/ideas/index.vue:118-122`.
Expected: the search input announces what it searches for. A placeholder is not a name: it disappears as soon as the field has content and screen readers do not treat it as a label.
Observed: the input is `type="search"` with `placeholder="Rechercher une initiative, un domaine ou un besoin"`, no `aria-label`, no `aria-labelledby`, and it is wrapped in a `<label class="ideas-search">` whose text content is empty (only an `aria-hidden` icon and the input itself live inside). The accessible name is therefore empty.
Rendered evidence: `search.ariaLabel: null`, `search.ariaLabelledby: null`, `search.labelTag: "LABEL"`, `search.labelText: ""`, `accName.closestLabelText: ""`.
Repro: open `/workspace/ideas`, query the search box, read its computed accessible name. The repository already has the string to reuse (`ideas.explorer.search`).

### A11Y-2 (major) The explorer renders two `main` landmarks, one nested in the other

Screen: WorkspaceArea.Ideas.Explorer, fr and en.
Where: `apps/web/app/layouts/workspace.vue:80` (`<main id="main" class="workspace-main min-w-0">`) and `apps/web/app/pages/workspace/ideas/index.vue:150` (`<main class="ideas-results">`).
Expected: one `main` landmark per page, holding the page content. A second `main` nested inside the first gives screen reader users two "main" entries in the landmark list and an invalid nesting.
Observed: exactly two `main` elements, the second one nested in the first.
Rendered evidence: `mains: [{ id: "main", cls: "workspace-main min-w-0", nested: false }, { id: "", cls: "ideas-results", nested: true }]`.
Repro: open `/workspace/ideas`, list all `main` elements and check each one's nearest `main` ancestor. The workspace layout already owns the `main` element, so the page-level `<main>` should be a `<section>` (or carry no landmark role).

### A11Y-3 (minor) Two navigation landmarks share the same name on the landing

Screen: landing, fr and en.
Where: `apps/web/app/layouts/default.vue:29` (`nav.site-header__nav`) and `apps/web/app/components/kollio/SiteFooter.vue:25` (`nav.site-footer__nav`), both named with the same key `t('navigation.label')` ("Navigation principale" in French, "Main navigation" in English). The workspace sidebar (`apps/web/app/components/kollio/WorkspaceNav.vue:21`) uses the same key, so the ambiguity reappears on any page that renders the footer next to the sidebar.
Expected: each navigation landmark carries a name that says which navigation it is, so a landmark list can tell them apart.
Observed: two visible `nav` elements on the landing both expose the name "Navigation principale".
Rendered evidence: `navs: [{ name: "Navigation principale", hidden: false, cls: "site-header__nav" }, { name: "Navigation principale", hidden: false, cls: "site-footer__nav" }]`.
Repro: open `/` with the `kollio_locale=fr` cookie, list the `nav` elements and read their names.

### A11Y-4 (minor) The settings save confirmation is not announced

Screen: WorkspaceArea.Settings, fr (the component is the same in en).
Where: `apps/web/app/pages/workspace/settings.vue` contains no `aria-live` at all, while the other screens that report progress do have one (`app/pages/workspace/ideas/index.vue:155`, `app/pages/workspace/deposit.vue:145`, `app/pages/workspace/decision-spaces/index.vue:151`, `app/components/kollio/IdeaDetailSkeleton.vue:8`).
Expected: after saving, a screen reader user learns that the save happened without moving focus back to the region.
Observed: the confirmation text exists in the document (measured `savedNoteLive.text` = "Les membres de l'espace de travail, et l...") but it is not inside a live region, so nothing is announced.
Rendered evidence: `savedNoteLive: { text: "Les membres de l'espace de travail, et l", live: null }`.
Repro: open `/workspace/settings`, save, and inspect the confirmation element for `aria-live` or `role="status"`.

### A11Y-5 (minor) The person profile has no level-1 heading

Screen: WorkspaceArea.People.Profile, fr (same component in en).
Where: `apps/web/app/pages/workspace/people/[userId].vue` renders the person through `KollioPersonRow` (`app/components/kollio/PersonRow.vue:22-31`), which marks the name as a link or a `<strong>`, never as a heading, and then opens three `<h2>` sections.
Expected: the page names its subject with a level-1 heading before the section headings, so heading navigation lands somewhere meaningful.
Observed: the only headings on the page are three level-2 headings (`INITIATIVES DÉPOSÉES`, `ÉQUIPES`, `ACTES ENREGISTRÉS`), with no level-1 heading above them. The person name is exposed as link text, which is announced, but it is not reachable through heading navigation.
Rendered evidence: `headings: ["H2:INITIATIVES DÉPOSÉES", "H2:ÉQUIPES", "H2:ACTES ENREGISTRÉS"]`.
Repro: open `/workspace/people/owner-one`, list every `h1` and `h2`.

## Checked and clean

These were measured in the rendered build and did not reveal a defect. They are recorded so the next audit does not redo them.

1. Document language: with the `kollio_locale=fr` cookie the root serves `lang="fr-FR"` and French content; with no cookie an English browser is redirected to `/en` with `lang="en-GB"`. The redirect is the configured `detectBrowserLanguage.redirectOn: 'root'` behaviour, not a defect. The earlier i18n pass reported `htmlLang: "en-GB"` on its "landing fr" row, which was the English page: that row was mislabelled, the product is correct.
2. Decorative avatars: `app/components/kollio/PersonRow.vue` wraps the avatar in `aria-hidden="true"` and gives any `<img>` an empty `alt`, so no accessible name is lost; no `<img>` without an `alt` attribute was found on the profile or the idea detail.
3. Preview close button: measured at 0 by 0 pixels on the desktop explorer because `app/components/kollio/IdeaPreviewPanel.vue:78` hides it above 1181px, where the preview is permanent. By design.
4. Explorer pagination: not rendered with the fixture (two ideas, `limit` 5), because `app/pages/workspace/ideas/index.vue:175` guards it with `totalPages > 1`. Not exercised rather than defective.
5. Navigation entries: `app/components/kollio/WorkspaceNav.vue` renders four `NuxtLink` entries (Inbox, Decision Spaces, Ideas, Settings) with `min-h-11` (44px) and `aria-hidden` icons. No `aria-disabled` entry exists anywhere in `apps/web/app`, so the five disabled entries the earlier pass recorded are gone.
6. Contrast: worst measured ratios per screen were landing 10.09, explorer 4.77, deposit 14.26, idea detail 10.26, settings 4.77, all at or above the 4.5 requirement for their text size.
7. Form labels: every field carries a name, deposit 4 of 4 and settings 35 of 35, with `required` on title and pitch and the submit button disabled until the form is valid.
8. Idea detail context tabs: the tab list is labelled ("Contexte de l'initiative"), each tab controls a labelled panel, and `ArrowRight` moves the selection to the next tab.
9. Mobile drawer: it traps focus while open (`role="dialog"`, `aria-modal="true"`, focus inside) and Escape removes it from the document entirely, with none of twelve successive `Tab` presses landing inside it.
10. Deposit verdict: the verdict container carries `aria-live="polite"` (`app/pages/workspace/deposit.vue:145`) and the submit error carries `role="alert"`. Each constraint score is a `<dd>` under a labelled `<dt>` in a `<dl>`, so the score is semantically tied to its dimension (source-only, the resolved state was not captured in a rendered read).

## Scenario grid

| Screen | fr | en | Evidence |
| --- | --- | --- | --- |
| Landing (`/`) | PASS, with A11Y-3 | PASS, with A11Y-3 | rendered measurement of landmarks, headings, names, contrast, `lang` |
| Explorer (`/workspace/ideas`) | FAIL, A11Y-1 and A11Y-2 | FAIL, A11Y-1 and A11Y-2 | rendered measurement of landmarks, nav names, search name, boxes, contrast, focus ring |
| Deposit (`/workspace/deposit`) | PASS, with A11Y-4 elsewhere | not measured | rendered measurement of labels, live region, contrast, 44px floor |
| Idea detail (`/workspace/ideas/[ideaId]`) | PASS | not measured | rendered measurement of icon button names, tabs, keyboard, contrast |
| Person profile (`/workspace/people/[userId]`) | FAIL, A11Y-5 | not measured | rendered measurement of landmarks, headings, names |
| Decision inbox (`/workspace`) | PASS on the shell | not measured | rendered measurement of the page shell only, see limits |
| Settings (`/workspace/settings`) | FAIL on the save announcement | not measured | rendered measurement of labels, fieldsets, contrast, 44px floor |

## Known limits

- The English locale was only measured on the landing and the explorer. The other screens are rendered by the same components with the same attributes, so the checks that passed in French are expected to pass in English, but that was not measured and this report does not claim it.
- Every API response is simulated. This proves what the browser is given, not what the API returns, and not authentication or persistence.
- The inbox was audited in its page shell only: the inbox endpoints were not simulated, so the four sections were not exercised. The shell has one non-nested `main`, one named navigation and a level-1 heading.
- The decision space sections (Explore, Converge, Options, Decision, Experiment, Learning) are outside this audit and stay unaudited for accessibility.
- The profile roles list was empty in the fixture, so its rendering was not exercised here. It is covered by the i18n pass under `WorkspaceArea.People.Profile.RoleLabels`.
- The resolved deposit verdict was not captured in a rendered read (the read landed on the running narration), so the score labelling claim is source-only.
- Contrast was measured on the selectors each spec names, not on every text node in the document.
