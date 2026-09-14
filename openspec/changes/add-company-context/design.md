## Context

Every analysis currently reads only an idea's title and pitch. Making Kollio a company decision memory requires a durable, workspace-scoped context before the analysis engine can use it. Decision #45 fixed the seam: a dedicated `company_context` module, slice 1 limited to profile, objectives and constraints, editable by any workspace member.

## Goals / Non-Goals

**Goals:**

- Persist one Company Context per workspace, isolated like every other workspace resource.
- Keep the module a simple vertical slice: domain access rule, adapter, service, api.
- Store user-written text with its origin language, so translation-on-read can arrive later.
- Expose the context through the generated contract and a French/English settings screen.

**Non-Goals:**

- Principles/strategy and key metrics (later slice; they do not block the analysis).
- Any agent call, retrieval or prompt change — those belong to the context-aware analysis ticket.
- Translations of context text, history/versioning of the context, or per-item permissions.

## Decisions

### A dedicated module, not an extension of `workspaces`

`workspaces` is a thin listing seam. Company Context is a distinct bounded context (company facts versus membership and routing), so it gets its own module and tables keyed by `workspace_id`, following the profiles module shape.

### One access rule, duplicated on purpose

`can_access_context` is two lines and mirrors `can_read_idea`/`can_read_profile`. A shared kernel would couple modules to save two lines; module autonomy wins, consistent with the existing adapters that each read membership.

### Language recorded on write

`lang` (fr|en) is stored on all three tables and set from the request locale on every create or update, recording the language of the last write, like `Idea` and `Iteration`. The non-negotiable requires storing origin language; translating on read is out of scope.

### Errors say workspace, not idea

Non-members receive 404 with a dedicated `not_found_workspace` message rather than the idea message, so the surface never leaks which resource type was probed.

### The settings screen stays one page

Profile, objectives and constraints are three independent editors on one page: "keep simple CRUD simple" (docs/08) and existing pages already mix domains. Split into components if a fourth editor appears.

## Risks / Trade-offs

- **Context drift**: the profile is replaced wholesale on each save; a partial client payload clears omitted fields. Accepted (true PUT semantics) and covered by a test.
- **Language semantics**: an edit in another language flips the row's `lang`; acceptable because the field records last-write language, and history is not part of this slice.
- **Browser evidence**: Playwright runs locally only (CI runs Vitest); recorded as a limitation in `acceptance.md`.
