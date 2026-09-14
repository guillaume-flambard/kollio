# Tasks

- [x] Backend: `running` reads expose a real `progress` (profile, active
  objective titles, constraint titles, reused-learning texts, evidence sources,
  area count) built from the frozen launch snapshot and effective evidence.
- [x] `AnalysisResponse.progress` + client regen.
- [x] `KollioAnalysisNarration` renders the real groups with count-aware,
  localized sentences, omits empty groups, caps long lists with "+N more", and
  settles all groups under reduced motion.
- [x] Wire `progress` from the deposit running state.
- [x] FR and EN catalogs.
- [x] Integration test for the running `progress`; DEPOSIT-03 asserts the real
  items, the "+N more" cap and no verdict while running, FR and EN.
- [x] `make verify` and browser suite green; #78 stays open (remaining items).
