# Narrated analysis loading

While a constraint analysis is running, the deposit screen SHALL narrate the
stages Kollio performs instead of showing a bare wait, and the real result SHALL
replace the narration unchanged.

- **NL-01** When the analysis is running, the five narration steps are shown
  (company context, objectives and constraints, reused learnings, the five
  constraint areas, the decision and its disagreements) and one is marked
  current.
- **NL-02** The verdict that replaces it is the same resolved/abstained state as
  before; the narration never blocks or fabricates it.
- **NL-03** `prefers-reduced-motion: reduce` renders all steps settled at once.
- **NL-04** FR and EN show the same five localized steps; no technical jargon.
- **NL-05** No literal colours; only canonical tokens, under the guard.
