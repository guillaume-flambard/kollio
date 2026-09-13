## Implementation

- [x] Document the workflow, ADR, agent handoff and PR evidence expectations.
- [x] Connect the private browsing pilot to explicit acceptance checks.
- [x] Add isolated Playwright coverage and include both UI suites in CI and Make.
- [x] Extend anonymous request checks to workspace endpoints.
- [x] Complete local verification and record actual results.
- [x] Fix the pagination regression exposed by BROWSE-02 in both locales.

## External limitation

- [ ] Enforce required merge checks with GitHub branch protection (HTTP 403:
  current private repository requires a different GitHub plan or visibility).
