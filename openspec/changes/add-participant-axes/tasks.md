## 1. Deterministic domain

- [x] 1.1 Add failing unit tests for both closed lists, the reserved owner participation, the application and the addition rules.
- [x] 1.2 Implement the two axes, the legacy mapping and the validators under strict Mypy.

## 2. PostgreSQL persistence

- [x] 2.1 Add participation and business function with check constraints; map memberships, applications and sought values; drop the legacy role column.
- [x] 2.2 Carry both axes through the adapter, the reads and the owner-only addition.
- [x] 2.3 Verify no schema drift.

## 3. HTTP contract

- [x] 3.1 Expose both axes on collaborators, accept the function on applications, add the owner-only add operation with its refusals, and keep the acceptance optional.
- [x] 3.2 Regenerate the contract and the client.

## 4. Surface

- [x] 4.1 Show both axes on the team panel, apply with a function, and label both axes in French and English.
- [x] 4.2 Filter the explorer on functions.

## 5. Evidence

- [x] 5.1 Integration tests: owner add, unknown function refused, non-owner refused, application and acceptance end to end, legacy values mapped.
- [x] 5.2 Update the browser mocks to the new shapes and keep the suites green.
- [x] 5.3 Record evidence and boundaries in `acceptance.md` and run the full verification.
