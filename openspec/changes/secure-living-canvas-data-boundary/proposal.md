## Why

Kollio asks teams to preserve sensitive decision memory, but its current product contract does not make data transmission, model-provider risk, retention, or visual consistency explicit. Faktus needs an honest, auditable boundary before importing company material.

## What Changes

- Establish a default-deny data-egress policy: only explicitly selected excerpts may reach an approved model provider.
- Make provider, region, retention policy, and transmitted excerpts visible before an AI invocation and in its audit trail.
- Add workspace retention, export, deletion, and security-audit controls.
- Establish Living Canvas/Aubergine as a product-wide invariant, including settings and security surfaces.
- **BREAKING**: no unapproved provider, including a Chinese model, may receive workspace material merely because it is configured.

## Capabilities

### New Capabilities
- `decision-data-boundary`: customer-controlled data egress, approved providers, audit, retention, export and deletion.
- `living-canvas-governance`: enforce the canonical Living Canvas system across every authenticated product surface.

### Modified Capabilities
- `model-routing`: resolve only an approved provider for the workspace and make the resolution auditable.
- `explore-screens`: disclose the model transmission boundary while importing or invoking reconciliation.

## Impact

FastAPI authorization and gateway policy, LiteLLM configuration, Postgres audit and retention records, generated API client, all authenticated Nuxt screens, FR/EN catalogues, operations documentation, DPA and subprocessors register.
