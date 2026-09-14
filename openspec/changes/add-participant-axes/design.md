## Context

Decision #48 fixed the shape: two axes, both closed lists, the owner adds members directly, the application flow survives, and existing craft roles migrate onto the function axis. The pilot needs the vocabulary to read as business, not product.

## Goals / Non-Goals

**Goals:**

- Participation and business function as two closed lists, validated at the boundary and in the domain.
- Owner-only direct addition that is effective immediately; self-nomination unchanged.
- A single, lossless migration of existing roles, applications and sought values.

**Non-Goals:**

- Granting `owner` to anyone but the initiative owner.
- Per-function permissions, function-specific templates, or ranking by function.
- The member-picker UI: it needs a workspace-members endpoint and ships in its own slice.

## Decisions

### Two columns instead of one free role

`idea_memberships` gains `participation` (default `contributor`) and `business_function`; the legacy `role` column is dropped after the values are mapped. Keeping one column would force every read to guess which axis it holds.

### The mapping lives in the domain and is imported by the migration

`LEGACY_ROLE_TO_FUNCTION` is the single source; the migration imports it so the historical mapping cannot drift from the documented one, and a unit test pins its content.

### `owner` stays reserved

The owner is implicit on the initiative; `decide_addition` refuses the `owner` participation, so the loop keeps exactly one owner and the membership rows stay about participants.

### The sought values change vocabulary, not column name

`ideas.sought_roles` keeps its name (the explorer filter and API parameter are unchanged) while its values move to the function axis in the same migration. Renaming the column would ripple through the contract for no pilot value; the glossary records the vocabulary.

## Risks / Trade-offs

- **Filter semantics change silently** for existing clients sending a craft value: the value is now invalid, and the list simply returns nothing rather than failing. Accepted: the field is a filter, and the vocabulary is documented.
- **Migration depends on app code** (the mapping constant). Accepted for a pure historical map, guarded by a unit test.
