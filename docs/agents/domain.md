# Domain Docs

Kollio uses a multi-context domain documentation layout.

## Before exploring

1. Read the root `CONTEXT-MAP.md`. It lists the contexts and how they relate.
2. Read the `CONTEXT.md` for each context relevant to the task.
3. Read applicable system decisions in `docs/decisions/`.
4. Read context-specific decisions next to the relevant context when they exist.

If a context document does not exist yet, proceed silently. Domain-modeling workflows create it when terminology or decisions are resolved.

## Context layout

| Context | Domain document |
| --- | --- |
| FastAPI backend | `apps/api/CONTEXT.md` |
| Nuxt application | `apps/web/CONTEXT.md` |
| Generated API client | `packages/api-client/CONTEXT.md` |
| Shared UI package | `packages/ui/CONTEXT.md` |

System-wide decisions remain in `docs/decisions/`. Context-specific ADRs may live under the corresponding context's `docs/decisions/` directory.

Use terms defined in the relevant `CONTEXT.md`. Surface any conflict with an existing decision explicitly.
