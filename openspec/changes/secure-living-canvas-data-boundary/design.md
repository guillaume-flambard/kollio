## Context

Manual document import is the V1 boundary. Kollio stores the memory users deliberately import; it must not claim zero storage. Security is a product behaviour and a sales claim only when backed by controls.

## Decisions

### Default deny model egress

Each workspace has an approved-provider policy. An invocation is refused unless the provider is approved, the actor is entitled, and the exact excerpts have been selected. A provider record carries processor name, region, retention/training terms, contract status, and approval state. A model from any geography, including China, is blocked unless a workspace administrator explicitly approves it after the policy is documented.

This policy applies to every existing and future workflow immediately. A workspace with no approved provider has no model access; there is no system-provider fallback or grandfathered path.

### Minimise and disclose

The gateway receives excerpts, never implicit full-space memory. The audit record stores actor, provider, model, excerpt ids, time, outcome, and workflow id, never a duplicate prompt body. Provider policy, transmission detail and prototype status are administrator-only controls; ordinary members see neither a model choice nor a transmission confirmation in the decision flow.

### Customer controls

Administrators can export source material and decision records, configure retention, request deletion, and read an immutable security activity log. Deletion has a documented backup-expiry window. DPA, subprocessor list, incident process and EU hosting facts are published only after they are true operationally.

### Living Canvas is the product-wide constraint

Every authenticated surface uses `packages/ui/src/tokens.css`, the shared theme, Kollio-owned SVG icons and the canonical Aubergine mark. Security is not a generic admin dashboard: it uses the same airy canvas, semantic felt-tip wash, readable relationship lines and motion rules. No raw visual values, third-party icon packs, gradients, or separate design system are allowed.

## Risks

- [Provider marketing claim outruns contract] -> display verified policy facts, never infer zero retention.
- [Sensitive material reaches a provider unexpectedly] -> selected-excerpt allowlist at UI, API and gateway.
- [Security controls interrupt the decision flow] -> keep policy and audit in administrator-only settings, while the runtime guard stays invisible to ordinary members.
