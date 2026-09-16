# Kollio web app — inventory: done vs remaining (2026-09-16)

Method: read-only audit of the six routes + chrome, crossed with
`.agents/skills/ux-flow-auditor/COVERAGE.md` (51 AUDITED rows), GitHub issues
#100–105 (all OPEN, no comments), and `git log -30`. No code changed.

## 0. Coverage state

51 AUDITED rows. Covered: Explorer filter toolbar + rail, Deposit entry/submit/
verdict + initiative-type select, Settings context + onboarding, People open
from team/explorer, IdeaDetail experiments/team/timeline/type, NAV mobile +
desktop rail.

**Zero flow rows**: landing (`pages/index.vue`), auth sign-in/out, WorkspaceNav
utilities + upcoming entries, CommentComposer, real questions/evidence data,
matching/benchmark/pilot/outcome-reuse APIs.

## 1. Landing `/` (`pages/index.vue`) — no coverage

Done: hero + CTA (:21-40), initiative-flow preview (:42-44),
outcomes/method/trust/final-CTA (:47-80), session fetch (:5).
Missing:
- Signed-in CTAs only route to `/workspace` (:7,28) — no deposit/explorer entry.
- Nav anchor `#product` matches NO section id (`layouts/default.vue:12`,
  `components/kollio/SiteFooter.vue:10`) — dead link.

## 2. Explorer (`workspace/index.vue`)

Done: search + filters rail (:123-157), results + sort (:160-163), skeleton
(:164-166), error + retry (:167), empty (:184), pagination (:185-188),
preview panel (:191-203). Coverage: Explorer.*, Deposit.Entry.
Partial: sort is a static label, no control (:162); filter icon inside search
does nothing (:126); realism filter is only a ≥60 toggle (:154).
Missing: domain chips (intentional per flow); no matching surface at all.

## 3. Deposit (`workspace/deposit.vue`)

Done: title/pitch/lang/type form (:116-138), disabled submit (:140), submit
error (:139), narration while running (:146), timeout + retry (:147-153),
abstain/resolved verdict (:154-161), constraints/contradictions (:162-183),
open-idea link (:184-186). Coverage: Deposit.*, TYPE-01.
Missing: basis/gap copy keys may fall back to the raw key (:164,167).

## 4. Settings (`workspace/settings.vue`)

Done: 7-step wizard (:426-501), detailed editor behind toggle (:503-515),
profile/objectives/constraints/principles/metrics CRUD + archive (:516-731),
load/action errors (:418-423), per-list empty notes (:563,607,650,701).
Coverage: SETTINGS-*, ONBOARD-*.
Missing: no delete anywhere, archive only (:586,629,672,724); metrics unit
shown read-only (:720); wizard metrics lose value/unit/source — name only
(seedList :353-367).

## 5. Idea detail (`workspace/ideas/[ideaId].vue`)

Done: skeleton/error (:432-442), breadcrumb + advance + more (:455-465),
owner-only initiative-type select (:471-480), timeline propose + accept /
reject / rollback (:530-573), experiment loop (:575-578), team members +
sought + join-requests + add/apply/leave/remove (:580-667). Coverage: TEAM,
TIMELINE, OWNER, PROPOSE, EXPERIMENT, TYPE-02/03.
Partial: questions/evidence counts hardcoded 0 (:502,504,
`IdeaCompanion.vue:17`); more-actions `...` dead (:462-464); topic `+`
just switches panel (:488); `writeToEnrich`/comment composer only switches
panel (:527,670).

## 6. People (`workspace/people/[userId].vue`)

Done: back link (:27), 404 vs generic error (:29-36), header + bio + roles
(:39-45), owned/teams/acts lists + empty states (:47-80), idea links (:20-22).
Coverage: PROFILE-01/02.
Missing: no loading skeleton, no pagination; membership rows link only via
the arrow icon (:64).

## 7. Chrome

`layouts/workspace.vue`: rail + drawer + locale + sign-out (:10-78) done.
`layouts/default.vue`: header/drawer/footer + skip link (:23,56,90) done;
dead `#product` anchor (:12).
`components/kollio/WorkspaceNav.vue:37,46`: workshops / community /
resources + search / notifications — all `disabled`.
`components/kollio/SiteFooter.vue:26-32`: anchors + locale + workspace only;
no trust links (blocked: no legal pages or contact exist).

## 8. Top 10 load-bearing gaps

1. Landing has zero flow coverage + dead `#product` anchor.
2. Questions/evidence panels are empty shells (counts hardcoded 0).
3. Explorer sort is a label, not a control.
4. Decorative filter icon in the explorer search bar.
5. IdeaDetail `...` more-actions dead; 3 competing advance paths.
6. Comment composer flips panel, never posts.
7. Nav promises 5 features that are dead (`disabled`).
8. Matching/benchmark/pilot APIs have no screen (#105).
9. Settings wizard drops metric value/unit/source.
10. Archive-only everywhere (no delete); member leave/remove asymmetric.

## 9. Tracker state

#100–105 ALL OPEN, no comments. #100 is the wayfinder parent ("redo the
screens with OpenDesign, then fill the missing capabilities"); #101 asks
spec-vs-mockup-vs-code for the OD artefact; #102 redo order + done criteria;
#103 explorer target structure; #104 idea-detail target structure; #105
missing-capability placement. **#100–104 prescribe the OpenDesign-redo path,
which is rejected — re-point or close before reuse. #105 (capability
placement) is still live and valuable.**

## 10. Proposed phased plan (repo-native wayfinder flow, not BMAD)

- Phase 0 — close/re-point: close #100–104 as superseded (OD redo rejected),
  keep #105; add dead-`#product` fix + questions/evidence-shell decision.
- Phase 1 — dead controls: explorer sort control, filter icon, `...` menu,
  composer post path, advance-path unification (gaps 3–6).
- Phase 2 — data completeness: questions/evidence real data, wizard metric
  value/unit/source, delete vs archive policy (gaps 2, 9, 10).
- Phase 3 — capabilities: matching/benchmark/pilot placement per #105 +
  the 5 disabled nav entries — product decisions first (gaps 7–8).
- Phase 4 — landing coverage: first Landing.* flows + signed-in CTA routing
  (gap 1).
Each phase: `/to-spec` → `/to-tickets` → `/implement` per ticket with the
existing gates (tokens, locales, UX coverage, 122 browser specs).
