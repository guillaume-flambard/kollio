# Task-class model routing

The gateway SHALL route by named task class, not by call-site model names.

- **RT-01** Every LLM gateway call declares a `TaskClass`; each class maps to a
  configured model through `resolve_model`.
- **RT-02** The constraint analysis is a visible-intelligence class and requests
  the visible model; a commodity class such as extraction does not.
- **RT-03** Local development and CI run the full loop without premium
  credentials: an unset `LLM_MODEL_VISIBLE` falls back to `LLM_MODEL`, and no
  live provider call is made in CI (recorded fixtures).
- **RT-04** The task class and the resolved model are visible per run in the
  existing OpenTelemetry attributes; no vendor pricing API is called in code.
