## Why

Existing component tests are omitted from CI, browser acceptance is manual, and
agents have no shared scenario-to-evidence delivery contract.

## What Changes

Document a single workflow and ADR, link private browsing scenarios to evidence,
run component and browser checks in CI and local verification, and cover anonymous
workspace requests. Fix the page-two Previous link retaining page=2, exposed by
the new FR/EN browser scenarios. Keep browser simulation separate from backend security proof.

## Capabilities

### New Capabilities
- `delivery-verification`: scenario-led delivery with mandatory verification.

## Impact

Agent instructions, docs, Makefile, package scripts, CI and test fixtures change.
No new dependency or production authentication bypass is introduced. Repository
branch protection is unavailable under the current GitHub plan.
