## Context

Decision #44 fixed the framing: the rename is UX and glossary only (code, database and API keep saying `Idea`), and a closed `InitiativeType` is set by the owner at deposit and editable after. The pilot's B2B perception depends on it: Kollio must not read as a startup-idea network.

## Goals / Non-Goals

**Goals:**

- One closed kind per initiative, from the ten decided values, defaulting to `idea`.
- The kind visible at deposit, in reads and in the list; the owner can re-classify.
- French/English B2B copy that never calls the object an idea.

**Non-Goals:**

- Renaming the database column, the API resource or the code identifiers (decision #44).
- Filtering or ranking by kind, per-kind templates, or kind-specific analysis prompts.
- Migrating historical wording of imported content.

## Decisions

### The closed list lives in the domain

`INITIATIVE_TYPES` in the ideas domain is the single source of truth, covered by strict Mypy and unit tests; the database check constraint and the Pydantic literal mirror it. A mismatch is a test failure, not a runtime surprise.

### Column default instead of a backfill

`initiative_type` is `NOT NULL DEFAULT 'idea'` with a check constraint, so existing rows need no data migration and old clients keep working.

### Owner-only re-classification

Changing the kind is an editorial act on the initiative, so it follows the same authorization as appending to the main line: the owner, and nobody else. Non-members get the not-found answer to avoid resource probing.

### The `idea` kind is labelled "Intuition" / "Hunch"

The kind list includes `idea`. Labelling it "Idée"/"Idea" would reintroduce the exact word the copy rule removes and confuse the kind with the object. "Intuition" (fr) and "Hunch" (en) read as a kind of initiative and keep the surface clean.

## Risks / Trade-offs

- **Copy churn**: 51 French and 46 English strings in the workspace namespaces changed. Tests read the catalogs, and a check asserts no forbidden word remains in those namespaces.
- **Kind semantics**: the ten values are a closed list; a new business kind needs a migration. Accepted while the pilot is small.
