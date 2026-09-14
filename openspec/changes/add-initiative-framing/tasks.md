## 1. Deterministic domain

- [x] 1.1 Add failing unit tests for the closed list and its refusal rule.
- [x] 1.2 Implement `INITIATIVE_TYPES` and the validator under strict Mypy.

## 2. PostgreSQL persistence

- [x] 2.1 Add the `initiative_type` column with a check constraint and a `NOT NULL DEFAULT 'idea'` so existing rows keep working.
- [x] 2.2 Carry the kind through deposit and the owner-only update in the adapter.
- [x] 2.3 Verify no schema drift against the models.

## 3. HTTP contract

- [x] 3.1 Accept the kind on deposit (defaulting to `idea`), expose it in read and list, and add the owner-only update operation with the not-found/forbidden answers.
- [x] 3.2 Regenerate the contract and the TypeScript client; confirm one operation added and none removed.

## 4. B2B surface

- [x] 4.1 Switch the French and English workspace copy from idea to initiative with no forbidden word left in those namespaces.
- [x] 4.2 Add the kind selector at deposit and on the detail screen (read-only for non-owners).

## 5. Evidence

- [x] 5.1 Integration tests: deposit default, explicit kind, unknown refusal, owner update, non-owner refusal, non-member not-found, kind in read and list.
- [x] 5.2 Browser acceptance in FR and EN for the deposit selector, the owner edit and the non-owner read-only view.
- [x] 5.3 Record evidence and boundaries in `acceptance.md` and run the full verification.
