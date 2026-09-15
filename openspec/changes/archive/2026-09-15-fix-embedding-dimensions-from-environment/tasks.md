## 1. Boundary

- [x] 1.1 Add a failing settings test that supplies `EMBEDDING_MODEL` and `EMBEDDING_DIMENSIONS` through the environment, not as arguments, and asserts the settings load with the integer 1536.
- [x] 1.2 Add a validator on `embedding_dimensions` that runs before the membership rule and coerces the text form, then confirm the test passes.

## 2. Boundary held

- [x] 2.1 Confirm an unsupported dimension still fails closed, and that no argument path regressed.
- [x] 2.2 Run Ruff, the strict Mypy gate on the domain packages, and the API suite.

## 3. Delivery

- [x] 3.1 Regenerate the contract, confirm no drift, and build the production images.
- [x] 3.2 Ship the API image, then activate the 1536-dimension space in the deployment and confirm the stack starts and serves.
