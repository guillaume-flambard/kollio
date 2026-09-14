## Why

Kollio analyzes an Initiative from its title and pitch alone, so it cannot reason about the company behind it. The pilot's core proposition — a collective decision memory that knows the company's objectives and constraints — needs a persistent, workspace-scoped Company Context before any context-aware analysis can exist.

## What Changes

- Add a persistent Company Context per workspace: company profile, objectives and constraints.
- Let any workspace member read and edit it; deny everyone outside the workspace as if it did not exist.
- Give objectives an active/archived state and a priority flag; give constraints an active/archived state.
- Keep the context workspace-private by default, with FR/EN error localization inherited from the platform.
- Principles/strategy and key metrics are part of the capability but ship in a later slice (they do not block the analysis engine); the settings UI ships as its own ticket.

## Capabilities

### New Capabilities

- `company-context`: Workspace members can record and maintain their company profile, objectives and constraints as the durable context every analysis reads.

## Impact

Adds a `company_context` vertical module (domain, adapters, service, api), one PostgreSQL migration with three tables, generated OpenAPI types, and deterministic unit plus PostgreSQL integration tests. No agent call, no frontend change, no contract break.

Tickets: GitHub #53 (this slice), #52 (parent spec).
