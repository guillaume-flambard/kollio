# Route task classes to models

## Why

The pilot runs a cheap model behind LiteLLM. Members judge the product through
the text they read, so putting a cheap model on the reasoning step risks a
"Claude thinks better" verdict no matter how good the memory and context are.
Right now every gateway call hardcodes the single configured model, so there is
no seam to send reasoning to a premium model and cheap work to a cheap one.

## What changes

- A named `TaskClass` (extraction, classification, summarisation, embedding,
  translation, routing, small_check; challenge, reasoning, contradiction,
  comparison, recommendation, learning, explanation) split into a commodity
  tier and a visible tier.
- Each gateway call declares its task class; `resolve_model` maps the class to
  a configured model. Premium routing is a configuration choice, not call-site
  model names.
- The constraint-analysis and competition gateways are visible-tier; the stored
  analysis model and the OTel span carry the resolved model and the task class.

## Out of scope

- Registering an actual premium deployment in the LiteLLM config: that is an
  operator configuration when they have a key. Leaving `LLM_MODEL_VISIBLE`
  unset keeps dev and CI on the cheap model with no premium credentials.
- Adversarial multi-step reasoning (#76) and the comparative benchmark (#77),
  which consume this routing but are separate slices.
