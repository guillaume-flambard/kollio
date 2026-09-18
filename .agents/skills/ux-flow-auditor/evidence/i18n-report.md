# i18n verification report — kollio web app (FR / EN)

- **Scope**: every rendered page of `apps/web` (landing, explorer, deposit, idea detail,
  person profile, company context / settings), both locales, catalogs, placeholder
  interpolation, date and number formatting, and the forbidden raw-vocabulary class.
- **Date**: 2026-09-17
- **Auditor**: session audit, hand-run (no teammate produced anything; see "Method" below).
- **Locales audited**: `fr` (default, unprefixed) and `en` (`/en` prefix,
  `strategy: prefix_except_default`).
- **Verdict**: the translation *plumbing* is in good shape (FR/EN key parity green, zero
  hardcoded strings, zero raw enum leak into the DOM by accidental interpolation), but
  there is **one user-visible blocker** on the person profile: role labels are looked up
  with a vocabulary that the API does not produce, so the page prints raw i18n key paths
  for real data. Four further findings are tooling / dead-config hygiene.

## Method

Static analysis first (a gate run plus three purpose-built scanners), then one browser
run to confirm the top finding in a real render. Scripts live in
`/var/folders/.../T/opencode/kollio-i18n/` and are throwaway; their output is quoted
inline below. No teammate ever wrote a file: `find .agents -type f -newermt '-90 minutes'`
returned nothing across the whole wait, and `git worktree list` showed a single worktree,
so nothing was produced in isolation either.

## Evidence files

| Path | What it holds |
|------|---------------|
| `.agents/skills/ux-flow-auditor/evidence/2026-09-17-i18n-profile-role-render.txt` | Playwright console capture: the role list rendered in FR and in EN |
| `.agents/skills/ux-flow-auditor/evidence/2026-09-17-prod-90-profile-roles-raw-keys-fr.png` | FR person profile, raw key paths visible |
| `.agents/skills/ux-flow-auditor/evidence/2026-09-17-prod-90-profile-roles-raw-keys-en.png` | EN person profile, raw key paths visible |
| `apps/web/tests/browser/profiles.spec.ts` | the existing PROFILE-01 / PROFILE-02 spec, whose fixture hides the blocker |

---

## Finding I18N-1 — BLOCKER — the person profile prints raw key paths for real role values

**Class**: missing translation key (dynamic key built from a value that has no key).
**Verified**: `verified-rendered` — reproduced in Chromium, FR and EN.

`apps/web/app/pages/workspace/people/[userId].vue:43` renders the profile's own role list:

```vue
<li v-for="role in profile.roles" :key="role">{{ t(`ideas.role.${role}`) }}</li>
```

and `[.../people/[userId].vue:62]` renders each team membership:

```vue
<strong>{{ t(`ideas.role.${membership.role}`) }}</strong>
```

Both look the value up under `ideas.role.*`. That branch of the catalog holds exactly
**seven legacy keys** in each locale:

```
ideas.role -> commercial, data, designer, dev, growth, owner, product
```

But neither value the API returns comes from that vocabulary:

- `profile.roles` is `User.roles` — a JSONB column with **no CheckConstraint**
  (`apps/api/src/modules/ideas/adapters/postgres.py:41`). The values actually seeded by
  `apps/api/src/platform/seed_demo.py:28-68` are
  `['product','strategy']`, `['design','research']`, `['engineering','platform']`,
  `['ai','data']`, `['growth','sales']`, `['operations','finance']`.
  Only `data`, `growth` and `product` have a key.
- `membership.role` is `IdeaMembership.business_function` renamed on the way out
  (`apps/api/src/modules/profiles/adapters/postgres.py:92`, typed `MembershipResponse.role`
  in `apps/api/src/modules/profiles/api/schemas.py`). That column is constrained to twelve
  values by `BUSINESS_FUNCTIONS_SQL` (`apps/api/src/modules/ideas/adapters/postgres.py:61`):
  `marketing, sales, finance, product, engineering, customer_success, operations, legal,
  hr, data, direction, other`. `seed_demo.py:31-71` writes `product`, `product`,
  `engineering`, `data`, `marketing`, `operations`, so **three seeded values have no key**
  and `legal`, `hr`, `customer_success`, `direction`, `sales`, `finance` would have none
  either.

`apps/web/nuxt.config.ts:27-34` sets no `fallbackLocale` and no `missingWarn`, so vue-i18n
falls back to the key path itself: the user reads `ideas.role.engineering`.

### Render proof

Two role values the API really produces (`engineering`, `platform`) were mocked into the
profile response and the page was loaded at `/workspace/people/owner-one` (FR) and
`/en/workspace/people/owner-one` (EN):

```
[fr] profile-roles text = "ideas.role.engineering\nideas.role.platform"
[fr] memberships text = "ÉQUIPES\nideas.role.engineering\ndans Deuxième idée\n→"
[en] profile-roles text = "ideas.role.engineering\nideas.role.platform"
[en] memberships text = "TEAMS\nideas.role.engineering\nin Deuxième idée\n→"
```

Note that everything surrounding the broken label resolves correctly (`ÉQUIPES` / `TEAMS`,
`dans {idea}` / `in {idea}`), so this is a vocabulary mismatch, not an i18n wiring failure.

### Why the existing test does not catch it

`apps/web/tests/browser/profiles.spec.ts:10` mocks `roles: ['dev']` and `:14` mocks
`memberships: [{ …, role: 'dev' }]`. `dev` is one of the seven legacy keys, so the fixture
passes by coincidence. The spec also asserts the *wrapper* (`p.roleIn`) but never the role
label itself, so a raw key path on the label is invisible to it.

### The correct vocabulary already exists in both catalogs

| API value | Correct key family | Size | Match |
|-----------|--------------------|------|-------|
| `IdeaMembership.business_function` (12 SQL values) | `ideas.function.*` | 12 | exact |
| `User.roles` (13 seeded values) | `ideas.detail.roles.*` | 13 | exact (`ai`, `ai_data`, `data`, `design`, `engineering`, `finance`, `growth`, `operations`, `platform`, `product`, `research`, `sales`, `strategy`) |

So the fix is a vocabulary swap on the profile page, not new translations.

---

## Finding I18N-2 — MAJOR — the locale gate checks one direction and its message claims both

**Verified**: `source-only` (`scripts/check_locales.mjs` read in full).

```
$ node scripts/check_locales.mjs
FR/EN translation keys match, and all 472 catalog keys cover their usages.
```

The second half of that sentence is not implemented. The script:

1. asserts FR and EN have identical key sets (`assert.deepEqual(keys(french), keys(english))`) — **real, and green**;
2. walks `apps/web/app` for `t()` / `$t()` / `$te()` call sites and throws when a called key is
   absent from the catalog — a **used → exists** check only.

There is no **exists → used** pass, so a catalog key with no call site is reported as
"covering its usages". Running that reverse check by hand
(`unused-keys.py`, exact literal match plus template-literal and concatenation prefixes):

```
catalog keys: 472
literal call sites cover: 326
dynamic prefixes: 19
UNUSED candidates: 36
```

The 36 include two whole generations of superseded keys:

- `hero.eyebrow`, `hero.title`, `hero.description`, `hero.action`,
  `meta.title`, `meta.description`,
  `principles.label`, `principles.idea.*`, `principles.challenge.*`, `principles.team.*`
  — ten keys replaced by `landing.hero.*`, `landing.meta.*` and `landing.*`
  (both generations are present in `fr.json`; `rg -F hero.title apps/web packages` outside the
  catalogs only matches `landing.hero.title`).
- plus `ideas.collectionTitle`, `ideas.eyebrow`, `ideas.page`, `ideas.explorer.results`,
  `ideas.explorer.all|domain|language|recent|updated`, `ideas.detail.back|eyebrow|inspectSource`,
  `ideas.detail.team.send`, `ideas.deposit.metaTitle`, `ideas.deposit.narration.more`,
  `ideas.empty.description`, `ideas.profile.metaTitle`, `navigation.workspace`,
  `workspace.description`, `workspace.ideaLabel`, `workspace.role.admin`,
  `workspace.role.member`, `auth.pending`.

Impact: dead keys are translated, reviewed and kept in sync in two files for nothing, and the
gate actively tells a reviewer the opposite. Either add the reverse check or correct the
message to state the one direction it does verify.

---

## Finding I18N-3 — MAJOR — the configured date and number formats are dead, and formatting is duplicated per page

**Verified**: `source-only`.

`apps/web/i18n/i18n.config.ts` declares:

```ts
datetimeFormats: { fr: { short: { year: 'numeric', month: 'short', day: 'numeric' } },
                   en: { short: { … same … } } },
numberFormats:   { fr: { decimal: { style: 'decimal' } }, en: { decimal: { … } } }
```

No `$d`, `$n`, `d()` or `n()` call exists anywhere in `app/` — the configured formats are
never used. (`numberFormats.*.decimal` with `style: 'decimal'` is the runtime default anyway.)
Pages instead build their own formatter, three times over:

- `apps/web/app/pages/workspace/ideas/[ideaId].vue:30` and `:234`:
  `new Intl.DateTimeFormat(locale.value, { day: 'numeric', month: 'long', year: 'numeric' })`,
  exposed as `formatDate: iso => dateFormatter.value.format(new Date(iso))`.
- `apps/web/app/pages/workspace/people/[userId].vue:13`: the same formatter, repeated.
- `apps/web/app/pages/workspace/index.vue:57`:
  `new Intl.RelativeTimeFormat(locale.value, { numeric: 'auto' })`.

`apps/web/app/utils/timeline.ts` already takes `formatDate` through `TimelineFormatters`,
so the seam for one shared formatter exists; nothing centralises it today. Two consequences:
the catalog-level format config is untested and can drift, and a locale-format change has to
be made in three places to take effect.

---

## Finding I18N-4 — MINOR — dynamically built keys are invisible to the gate (root cause of I18N-1)

**Verified**: `source-only`.

Keys assembled at render time, prefix by prefix:

| Site | Key family | Values resolve? |
|------|-----------|-----------------|
| `people/[userId].vue:43,62` | `ideas.role.${role}` | **no** — see I18N-1 |
| `IdeaPreviewPanel.vue:47` | `ideas.detail.roles.${role}` | yes (13 keys = seeded values) |
| `workspace/index.vue:146` (+ `teamRoles` at `:58`) | `ideas.function.${role}` | yes (12 = `BUSINESS_FUNCTIONS_SQL`) |
| `[ideaId].vue:458,468`, `people/[userId].vue:52` | `ideas.stage.${stage}` | yes (3 = stage constraint) |
| `[ideaId].vue:235` | `ideas.iterations.${status}` | yes (3 = proposal status) |
| `ExperimentLoop.vue:240` | `ideas.experiments.status.${status}` | yes (4 = `STATUS_CHECK`) |
| `ExperimentLoop.vue:356` | `ideas.experiments.learning.${status}` | yes (2 = `LEARNING_STATUS_CHECK`) |
| `settings.vue:582,625,668,721` | `workspace.settings.state.${state}` | yes (2 = `STATE_CHECK`) |

`check_locales.mjs` deliberately handles template literals and `'prefix.' +` concatenation,
but only to test that the *prefix* exists in the catalog. It cannot tell whether a concrete
value has a key, which is exactly how I18N-1 survives a green gate. A value-level check (the
API's closed vocabularies vs the key families) would close this class.

---

## Finding I18N-5 — MINOR — latent: participation roles have no labels at all

**Verified**: `source-only`.

`apps/api/src/modules/ideas/adapters/postgres.py:61` also defines
`PARTICIPATION_ROLES_SQL = "'owner', 'decision_maker', 'contributor', 'observer'"`
(the `participation` field, distinct from `business_function`). The catalog has
`ideas.role.owner` but no `decision_maker`, `contributor` or `observer` key. No screen
renders `participation` through `t()` today, so nothing is broken now; this is recorded
because I18N-1 is the same mistake already realised once, and the profile page is one
rendering decision away from repeating it.

---

## Axes verified clean (no finding)

1. **FR/EN key parity** — `scripts/check_locales.mjs` green (also validates
   `apps/api/src/locales`). 472 web keys identical in both catalogs.
2. **No untranslated literal in markup** — `raw-strings.py` walked all 38 `<template>`
   blocks in `app/`: **1052 text nodes, every one free of a literal** (the single candidate,
   `IdeaPreviewPanel.vue:47`, is a multi-line moustache extraction artefact), and **zero**
   user-facing static attributes (`label`, `title`, `placeholder`, `aria-label`, `alt`,
   `description`, `summary`) — all are bound.
3. **No hardcoded French outside the catalog** — `rg '[À-ÿ]' app/` (excluding
   `i18n/locales/**`) matches only a regex character class at
   `app/pages/workspace/ideas/[ideaId].vue:189`.
4. **Placeholder interpolation** — `pa2.py` over 472 keys / 24 with placeholders / 327 literal
   call sites produced exactly two candidates, both disproved by hand: the concatenated
   `ideas.function.` prefix (`[ideaId].vue:610`, all twelve values keyed) and
   `t('ideas.iterations.branch', { name })` (`[ideaId].vue:536`, a shorthand object the
   scanner's named-argument regex cannot see).
5. **Plurals** — `plural-audit.py` found 10 plural keys; every one is called with a numeric
   or `{ count }` argument except `ideas.explorer.results`, which has no call site at all
   (dead key, counted in I18N-2).
6. **No raw enum leaking into the DOM** — all 22 moustache interpolations carrying a
   suspected enum field name go through `t()` with a built key
   (`ExperimentLoop.vue:240,356`, `IdeaPreviewPanel.vue:47`, `IterationTimeline.vue:80`,
   `LandingInitiativeFlow.vue:55`, `[ideaId].vue:458,468`, `workspace/index.vue:134,140,146`,
   `people/[userId].vue:43,52,62`, `settings.vue:582,588,625,631,668,674,721,727`).

---

## Scenario map

| Scenario | What was exercised | Result |
|----------|--------------------|--------|
| PROFILE-01 (profile from the idea team panel), FR | role list + membership label with real API role values | **FAIL** — raw keys (I18N-1) |
| PROFILE-01, EN | same, `/en` prefix | **FAIL** — raw keys (I18N-1) |
| PROFILE-02 (profile from an explorer collaborator), FR/EN | same component, same lookup | **FAIL** — same root cause |
| All other pages, FR/EN | literal-string scan, static-attribute scan, catalog parity, plural arity, enum-leak scan | PASS |

## Known limits of this pass

- The rendering proof for I18N-1 used a mocked profile response (the API's own seeded values),
  not production data and not a logged-in session. The source chain
  (seed → column → adapter → `.vue:43,62` → catalog) is complete and consistent with the
  render, so the finding stands; the screenshots are from the browser fixture, named
  `2026-09-17-prod-90-…` only to sit with the other dated captures.
- Findings I18N-2 through I18N-5 were established from source and static analysis, not from a
  render. They are marked `source-only` and none of them is a user-visible defect except
  through I18N-1.
- `check_locales.mjs`, the scanners and the Playwright spec were all run on the working tree
  at `a4d7b2f` (unmodified product code); the temporary audit spec was deleted after the
  capture so the tree holds only evidence.
