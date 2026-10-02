# Inert control inventory — Kollio web app (source audit, 2026-09-16)

Scope: six screens (`apps/web/app/pages/index.vue`, `apps/web/app/pages/workspace/index.vue`,
`apps/web/app/pages/workspace/deposit.vue`, `apps/web/app/pages/workspace/ideas/[ideaId].vue`,
`apps/web/app/pages/workspace/people/[userId].vue`, `apps/web/app/pages/workspace/settings.vue`),
layout `apps/web/app/layouts/workspace.vue`, shared components `apps/web/app/components/kollio/`.
Method: for every `button`, `NuxtLink`, `a[href]`, `select`, `input`, `textarea` in the
templates, traced whether it has a click/submit handler, a real router target or href,
or a v-model/state change. No product file edited.

## Ranked inert controls (user-impact order)

### 1. Sort label imitating a control — explorer (DEAD, known issue)
- Screen: explorer. File: `apps/web/app/pages/workspace/index.vue:162`
- Rendered: `<span>{{ t('ideas.explorer.sortBy') }} <b>{{ t('ideas.explorer.activity') }}</b></span>`
- Visible FR: "Trier par : Activité récente" / EN: "Sort by: Recent activity"
- Keys: `ideas.explorer.sortBy`, `ideas.explorer.activity`
- Expected: clicking opens sort options (activity, realism, newest…). Actual: plain
  `<span>`, no handler, no focus, results always API default order. Dead: remove until a
  real sort exists (or wire `?sort=` to the ideas query).

### 2. "More actions" button with no handler — idea detail (DEAD)
- Screen: idea detail. File: `apps/web/app/pages/workspace/ideas/[ideaId].vue:462-464`
- Rendered: `<button type="button" class="idea-more-action" :aria-label="t('ideas.detail.moreActions')">` (three-dot icon), no `@click`.
- Visible: icon-only button. FR: "Plus d'actions" (aria-label) / EN: "More actions"
- Key: `ideas.detail.moreActions`
- Expected: menu (edit, share, archive…). Actual: nothing happens on click or keyboard.
  Dead: remove or disable with explanation until the menu exists.

### 3. Comment composer that only switches a tab — idea detail (INCOMPLETE)
- Screen: idea detail. Files: `apps/web/app/pages/workspace/ideas/[ideaId].vue:670`
  (`<KollioCommentComposer :label="t('ideas.detail.comment')" @activate="selectPanel('team')" />`)
  + `apps/web/app/components/kollio/CommentComposer.vue:12` (button emits `activate`).
- Visible FR: "Voir qui contribue à cette initiative" / EN: "See who contributes to this initiative"
- Key: `ideas.detail.comment`
- Expected: the pill with message icon + submit arrow opens a comment input and posts.
  Actual: click only sets `activePanel = 'team'`; no input opens, no POST exists anywhere
  for comments. Incomplete: no comment API is exposed on this screen; either build the
  composer or relabel as a "see contributors" link.

### 4. "Write to enrich" prompt that only switches a tab — idea detail (INCOMPLETE)
- Screen: idea detail. File: `apps/web/app/pages/workspace/ideas/[ideaId].vue:527`
- Rendered: `<button … @click="selectPanel('questions')">{{ t('ideas.detail.writeToEnrich') }}</button>`
- Visible FR: "Écrire pour enrichir cette initiative, ou saisir / pour plus d'options…"
  / EN: "Write to enrich this initiative, or type / for more options..."
- Key: `ideas.detail.writeToEnrich`
- Expected: a writing surface (or slash-command menu). Actual: jumps to the questions
  tab, which is always an empty state (finding 6). Typing `/` does nothing.
  Incomplete: the questions/answer flow has no screen; relabel as navigation or remove
  the `/` promise.

### 5-9. Disabled nav items with no availability explanation — workspace nav (DEAD, ×5)
- Screen: all workspace screens (shared). File: `apps/web/app/components/kollio/WorkspaceNav.vue:37` (×3) and `:46` (×2)
- Rendered: `<button type="button" disabled aria-disabled="true">` with icons.
- Labels/keys: `navigation.workshops` (FR "Ateliers"/EN "Workshops"),
  `navigation.community` ("Communauté"/"Community"), `navigation.resources`
  ("Ressources"/"Resources"), `navigation.search` ("Recherche"/"Search"),
  `navigation.notifications` ("Notifications"/"Notifications"). Group label
  `navigation.upcoming` ("Fonctionnalités à venir"/"Upcoming features").
- Expected: navigation or search/notifications panels. Actual: permanently disabled,
  no tooltip/date/roadmap link explaining when they arrive. The `upcoming` group label
  partly explains the first three but nothing explains search/notifications.
  Dead: hide until implemented (keeping five dead rows in the primary nav teaches users
  the nav cannot be trusted).

### 10. Stats buttons with hardcoded zero counts — idea detail (INCOMPLETE)
- Screen: idea detail. File: `apps/web/app/pages/workspace/ideas/[ideaId].vue:502` and `:504`
- Rendered: buttons switching to `questions`/`evidence` panels (the switch works), but
  labels are `t('ideas.detail.stats.questions', { count: 0 })` and
  `t('ideas.detail.stats.evidence', { count: 0 })` — count literal `0`, never wired.
- Visible FR: "0 question ouverte" / "0 preuve" (always) / EN: "0 open questions" / "0 pieces of evidence"
- Keys: `ideas.detail.stats.questions`, `ideas.detail.stats.evidence`
- Expected: live counts. Actual: always zero even when evidence/questions exist.
  Incomplete: counters need a backing source or should be removed from the labels.

### 11. "See all" button leading to a permanent empty state — companion (INCOMPLETE)
- Screen: idea detail companion. File: `apps/web/app/components/kollio/IdeaCompanion.vue:89`
  (`<button … @click="selectPanel('questions')">{{ t('ideas.detail.companion.seeAll') }}</button>`)
- Visible FR: "Tout voir" / EN: "See all". Key: `ideas.detail.companion.seeAll`
- Expected: a questions list. Actual: lands on the questions tab whose content is always
  `KollioEmptyState` with `ideas.detail.companion.questions.empty` (lines 91-95;
  `panelCounts = { questions: 0, evidence: 0 }` hardcoded, line 17). Button functions
  but its destination can never show anything. Incomplete: questions have no data
  source on any screen.

## Verified FUNCTIONAL (spot-check, not inert)
Landing: brand link, 4 anchor nav links (`#product` target exists in
  `LandingInitiativeFlow.vue:6`, `#teams`/`#method`/`#trust` exist in `index.vue`),
  language switch, sign-in/out link, 3× `KollioPrimaryAction` (render `NuxtLink` or
  `<a href="/sign-in">` depending on auth state), hero `#method` secondary action,
  decision-card `#method` link. All resolve.
Explorer: create-idea `NuxtLink`, search input (v-model + debounced `replaceFilters`),
  4 stage filter buttons, sought-role `<select>`, realism toggle button, row buttons
  (`@select`), preview close/backdrop, pagination `NuxtLink`s, error retry button.
Deposit: all inputs/selects bound, submit POSTs + polls analysis, retry-analysis
  button, open-idea `NuxtLink`.
Idea detail: breadcrumb, advance/topic-add/stats/writing buttons (all switch panels —
  real state change), disclosure toggle, initiative-type select (PATCH), propose form,
  iteration accept/reject/rollback, experiment loop (full CRUD), team apply/accept/
  reject/leave/remove/add forms, tabs, provenance highlight button (switches panel).
Profile: back link, idea/membership links. Settings: wizard + all profile/objective/
  constraint/principle/metric create+patch forms, advanced toggle. Layout: menu
  open/close, drawer focus trap, locale + sign-out links. `PrimaryAction` with only
  `@click` renders a working `<button>` (explorer retry, detail error retry).
No `href="#"`, no no-op handlers, no other disabled-without-cause controls found
(`deposit-submit` disabled state is explained by `required` + empty fields).

## Could not determine from source alone
- Whether the explorer realism toggle (`realism_min=60`) and role/stage filters return
  correct server results (needs live API check; wiring exists).
- Whether sign-in/out round-trips work (auth is config-gated; links are well-formed).
- Whether experiment/outcome/learning POSTs succeed end to end (handlers + endpoints
  exist; server validation untested here).
- Visual affordance questions (does the sort `<span>` *look* clickable in the running
  CSS; are disabled nav rows visibly distinct) — needs the browser-owning teammate.
- Note (not a control, hence unranked): companion collaborator names
  (`IdeaCompanion.vue:69-77`) render via `KollioPersonRow` *without* `to`, so unlike
  the team-section rows (`[ideaId].vue:588`) they are plain text, not profile links.
  Inconsistent but not inert since they never present as actionable.
