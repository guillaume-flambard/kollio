# Narrated analysis loading

While a constraint analysis is running, the deposit screen SHALL narrate the
real inputs it is weighing - not generic stage labels - and the verdict that
replaces it is unchanged.

- **NL-01** When the analysis is running, the screen reads `analysis.progress`
  and shows the actual company name, the active objective titles, the active
  constraint titles, the reused learning texts and the evidence sources, each
  group headed by a localized, count-aware sentence.
- **NL-02** A group with no real data is omitted; a long list is capped and the
  overflow shown as "+N more", so the narration never overstates.
- **NL-03** The `running` read derives `progress` from the frozen launch
  snapshot and the effective evidence (which already carries the reused
  learnings), so nothing is invented.
- **NL-04** The verdict that replaces it is the same resolved/abstained state as
  before; the narration never blocks or fabricates it.
- **NL-05** `prefers-reduced-motion: reduce` renders every group settled at
  once; the real data, not the animation, is what shows.
- **NL-06** FR and EN show the same localized sentences over the same real
  data; no technical jargon; canonical tokens only.

