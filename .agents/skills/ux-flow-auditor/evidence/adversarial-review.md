# Adversarial review of the three verification reports

The frontend verification produced three reports: `i18n-report.md`, `a11y-report.md` and `journey-report.md`. This review attacks each one rather than restating it: which claims the evidence supports, which are over-claimed, and which parts of the product none of the three covers. It was written after the fixes landed, by reading the reports, the coverage register, the git history, re-running the gates, and re-measuring where a claim was cheap to check.

Status: complete.

## i18n report: holds, with one reproducibility weakness

What the evidence supports. The blocker was real and is closed. `apps/web/app/pages/workspace/people/[userId].vue` and `apps/web/app/pages/workspace/ideas/index.vue` resolved role labels through the pre-pivot family `ideas.role.*`, which holds seven keys while the API serves the thirteen craft roles of `User.roles` and the twelve functions of `BUSINESS_FUNCTIONS_SQL`, so any other value printed as a key path. The regression is now asserted on both screens, and replaying it against the old call sites fails four tests, which rules out a test that would pass either way. The commit `de8b913` is deployed, verified on the served build itself: `ideas.detail.roles` appears in two chunks and `ideas.role.` appears in none of the sixty-two.

The numbers reconcile. The report claims 472 web keys at parity; the gate today reports 1022 catalog keys with matching usages, and 1022 is twice 511, where 511 is 472 web keys plus the 39 keys of the API catalogues the gate also validates. Two passes, one count, no drift.

Over-claimed, and trimmed here. The report labels I18N-2 to I18N-5 by severity, and says none of them is a visible defect except through I18N-1, which is the correct reading. Read alone, however, "major" on I18N-2 (the locale gate checks one direction of usage) reads as a product risk rather than a tooling gap. It is a tooling gap: no user-facing string is wrong because of it today.

Unproven, and worth saying plainly. The report's clean axes rest partly on scanners that were never committed (`raw-strings.py` for untranslated literals, the placeholder and plural counters). No such script exists in the repository now, so a reader cannot reproduce those three claims; they rest on one pass, not on a gate. The claims about template-built keys are reproducible, because `scripts/check_locales.mjs` is committed and its one-direction limit is visible in its own source.

## a11y report: holds, with its severities re-labelled

What the evidence supports. A11Y-1 (explorer search box with no accessible name) and A11Y-2 (two `main` landmarks, one nested in the other) are confirmed by a rendered measurement and by source, and both are strict failures: 4.1.2 Name, Role, Value for the first, 1.3.1 Info and Relationships for the second, plus invalid nesting. A11Y-4 (the settings save confirmation is not in a live region, while four other screens do announce progress) is also strict, 4.1.3 Status Messages.

Corrected here. A11Y-3 (two navigation landmarks share the name "Navigation principale") and A11Y-5 (the profile has three `h2` sections and no `h1`) were filed as minor findings, which reads as conformance failures. They are not: no WCAG 2.2 success criterion requires unique landmark names or a level-1 heading. They are best-practice findings and are advisory. The report now says so in its result paragraph, and a reader may defer both without the project claiming non-conformance.

Unproven, and declared. English was measured on two screens of seven. The inbox was measured in its shell only. The decision space sections were not measured at all. Contrast was measured on the selectors the specs name, not on every text node. The resolved deposit verdict was never captured in a rendered read, so its score labelling rests on source. All of this is in the report's own limits section, and none of it is hidden, but it bounds what the report proves: it proves the explorer is broken for screen reader users and that five other screens are clean on the checks that were run, not that the product is accessible.

One editorial claim is not evidence: "the screen a contributor spends the most time in" is an assertion, not a measurement, and the review leaves it as prose.

## journey report: honest, and thinner than the label suggests

What the evidence supports. The public surface works: `/` serves the French landing (200, `lang="fr-FR"`, one `h1`) and `/en` the English one (200, `lang="en-GB"`), neither carries a raw translation key, and no forbidden term from the vocabulary rule appears in the visible French prose. The authentication gate holds: every `/workspace*` path redirects 302 to `/sign-in`, which redirects to Logto with `response_type=code` and PKCE `S256`, and `/sign-out` ends the session at the provider. No credential was requested, guessed or bypassed, which is the rule.

What it does not prove. Nine steps of the golden path are `NOT VERIFIED`, and those nine are the product: the explorer, the deposit and its analysis, the idea detail, the person profile, the decision inbox, the decision space sections and the settings. The report says this and cites the gate it met, so it does not lie, but the honest summary of this audit is "the door is locked and holds", not "the journey works". Anyone who reads only the file name would overestimate it; the coverage row added for it is deliberately scoped to the public journey.

JOURNEY-1 (an unknown path returns a JSON 404 body from the server rather than a localized not-found page) is a real observation and a fair minor finding, but it is the framework's default error response rather than a screen defect. It belongs to a small hardening ticket, not to the journey's risk list.

## What none of the three covers

- The authenticated product, end to end: no pass has signed in, so nothing here proves that a member can deposit, analyse, iterate, form a team or read the inbox.
- Agent output quality. The annex bundle names an evaluation corpus that does not exist yet, so nothing here judges what the agents produce.
- Participation values. The i18n report recorded that `owner`, `decision_maker`, `contributor` and `observer` have no label family; it is latent today and still latent.
- The stray spec. `apps/web/tests/browser/a11y-audit-tmp.spec.ts` is committed, writes its evidence into `apps/web/.agents/...` rather than the path it declares, overwrites its own measurements, and reads the deposit verdict without waiting. It is a finding about the audit tooling, not about the product.

## Verdict

The i18n blocker was real, is fixed, and its fix is proven. The accessibility audit is sound and its two strict findings are worth fixing; its two advisory findings should not be sold as conformance failures. The journey audit proves the public surface and the gate, and nothing beyond them. The verification is therefore complete in the sense that all three audits exist with evidence, and incomplete in the sense that the authenticated journey remains unverified.
