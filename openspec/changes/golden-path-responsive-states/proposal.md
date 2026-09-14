# Golden-path responsive and states guard

## Why

The last item of #78. A member must be able to walk the golden path on the phone
and tablet widths they actually use, and every screen must handle empty, loading
and error rather than a blank frame. The empty/loading/error handling already
exists per screen (empty states, skeletons, the error surface, the running
narration); what was missing was a standing check that the newest golden-path
screens do not break at narrow widths.

## What changes

- A responsive browser guard: the onboarding wizard, the deposit form and its
  running narration, and the initiative detail with its experiments loop render
  at 375 and 768 with no horizontal overflow and the primary control reachable.
- It caught one real defect: the settings enrichment forms (objectives,
  constraints, non-negotiables) overflowed at phone width because their
  two-column inputs could not shrink. Inputs now take `min-width: 0` and the
  inline and metric forms stack to one column under 640px.

## Out of scope

- A pixel-by-pixel redesign of each screen; this is the overflow and reachability
  floor, not a visual-approval sweep. The "would this screenshot go on the
  homepage" judgement stays a human, eyes-on pass.
