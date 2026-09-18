# Publish Kollio as an open source project

## Why

Kollio is moving from a private pilot to a public repository, so the project can be read, discussed and contributed to, and so GitHub's free tier covers what the repository needs: hosted runners, a public container registry, and branch protection with required checks, which GitHub refuses on a private repository without a paid plan.

In its current state the repository cannot honestly call itself open source. It carries no license, so the default is all rights reserved, and a reader has no way to know how to run the stack, how to propose a change, or how to report a vulnerability. The tracked files also read like one person's machine: the example environment points at the operator's identity provider and site, the deployment notes quote the pilot's hosts, and the example environment file carries the identity provider's application id. Publishing in that state would expose the operator's infrastructure and still leave every question a newcomer asks unanswered.

## What Changes

- Add the Apache-2.0 license text at the root, so the repository states the terms a reader and a contributor operate under.
- Add the community files a public repository needs: a contributing guide that says how to run the stack and how to propose a change (one behavior per change, conventional single-line commits, DCO sign-off), a code of conduct, a security policy that points at private disclosure, and issue and pull request templates.
- Rewrite the root README so a newcomer finds the product pitch, the quickstart, the documentation order and the license, in place of the current status section that still describes the pre-pivot backend.
- Neutralise the operator's infrastructure wherever it is not coupled to the running deployment: the example environment file, the development compose defaults, the Logto audience default in the API settings, the sign-in stylesheet asset URL, the deployment notes, the architecture decision record, the archived acceptance evidence and the journey audit. Hosts become `kollio.example.com` and `auth.example.com`, and the identity provider's application id becomes a placeholder.
- Record the public repository contract in the specification, so a later change can hold the line rather than rediscovering it.

## Capabilities

### New Capabilities

- `operations/public-release`: define what a public Kollio repository carries and refuses, so publishing is a state the project keeps rather than a one-off action.

### Modified Capabilities

None.

## Impact

Adds `LICENSE`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md`, `.github/ISSUE_TEMPLATE/` and `.github/PULL_REQUEST_TEMPLATE.md`, rewrites `README.md`, and replaces placeholder values in `.env.example`, `docker-compose.yml`, `apps/api/src/platform/config.py`, `apps/web/logto/sign-in-experience.css`, `docs/11-bootstrap-status.md`, `docs/decisions/0002-branded-logto-sign-in-experience.md`, seven archived `acceptance.md` files, one archived `proposal.md` and the journey audit.

No application behavior changes. The three values the running web app needs at runtime, `apps/web/nuxt.config.ts` (the Logto resource and the site base URL) and `apps/web/server/utils/kollio-api.ts` (the API audience), keep the operator's host until the deployment environment supplies them, which is a separate change. No contract, migration, dependency or secret changes.

## Out of Scope

- Making the repository public, and the continuous integration move to hosted runners and a public registry with an autodeploy that pulls from it.
- Extending the private files check so it also fails on infrastructure hosts and personal paths. That guard can only be green once the deployment environment supplies the runtime values above, so it belongs to the same later change.
- The git history. The audit found no secret material in any reachable blob, so no history rewrite is planned.
