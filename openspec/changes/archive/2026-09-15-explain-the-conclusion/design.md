# Design

- The explanation renders where the analysis detail already renders: the
  deposit verdict panel. The idea detail shows a single label, so there is
  nothing to extend without inventing a new panel.
- Basis and contradiction labels are translation keys
  (`ideas.analysis.basis.*`, `ideas.analysis.contradictionTarget.*`), not
  literals; the engine's `gap` and `detail` are user-facing prose and stay
  as the model wrote them, in the requested locale.
- The styles use canonical tokens (`--ui-text-muted`), consistent with #69.
