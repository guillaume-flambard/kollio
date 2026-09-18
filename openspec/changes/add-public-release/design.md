# Design - publish Kollio as an open source project

## Context

The repository has no `LICENSE`, no `CONTRIBUTING.md`, no `CODE_OF_CONDUCT.md` and no `SECURITY.md`, and `.github/` contains only the continuous integration workflow, so no issue or pull request template exists either. The root `README.md` is a documentation index in French whose status section still describes the pre-pivot backend (Python, Langfuse and SQLite on a Netcup server), which stopped being true when the product moved to the decision intelligence shape.

A handful of tracked files name the operator's infrastructure: `.env.example`, `docker-compose.yml`, `apps/api/src/platform/config.py`, `apps/web/nuxt.config.ts`, `apps/web/logto/sign-in-experience.css`, `apps/web/server/utils/kollio-api.ts`, `docs/11-bootstrap-status.md`, `docs/decisions/0002-branded-logto-sign-in-experience.md`, seven archived `acceptance.md` files, one archived `proposal.md` and the journey audit. The names are hosts (the product host and the identity provider host) plus the identity provider's application id in the example environment file.

Three of those values are coupled to the running deployment, which the deployment stack makes visible: the stack gives the web service its Logto endpoint, application identifiers and redirect base URL, but neither a Logto resource nor a public site URL, and it gives the API its audience. So `apps/web/nuxt.config.ts` (the Logto resource and the i18n base URL) and `apps/web/server/utils/kollio-api.ts` (the audience it asks a token for) read the operator's host in production, while `apps/api/src/platform/config.py` has its audience overridden by the environment and can take a generic default without any risk.

The audit of the history found no secret material: no blob was ever added with a sensitive suffix, and no credential-shaped value exists in the tree or in any reachable blob. The existing guard, `scripts/check_private_files.py`, runs on the tracked index in continuous integration and refuses sensitive paths and real credential values, but it knows nothing about infrastructure names.

## Goals / Non-Goals

**Goals:**
- The repository states its license, so a reader knows the terms, and a contributor knows how to run the stack, how to propose a change and how to report a vulnerability.
- Example configuration, development defaults, documents and archived evidence use placeholder hosts instead of the operator's own.
- The README orients a newcomer: product paragraph, quickstart, documentation order, license, and a status section that matches the product.
- The guards and the suites stay green, and the pilot keeps serving.

**Non-Goals:**
- Making the repository public, moving continuous integration to hosted runners and a public registry, or adding branch protection. Those belong to a follow-up change, since they touch the deployment path.
- Changing the three runtime-coupled values, or extending the private files guard to host names, which can only be green once the environment supplies those values.
- Rewriting git history. The audit found nothing to remove.

## Decisions

### Apache-2.0, with a developer certificate rather than a contributor agreement
The licence is permissive with an explicit patent grant, it is the most familiar choice for a young product that wants contributions, and it accepts the possibility that someone rehosts Kollio as a closed service. A contributor agreement would add a signature round trip for no benefit on a solo project, so the contributing guide asks for a `Signed-off-by` line instead, which records the origin of each contribution in the commit itself.

### Placeholders that keep each record readable
Hosts become `kollio.example.com` and `auth.example.com`, and the identity provider's application id becomes a placeholder. The archived acceptance files keep their commands, status codes and byte counts untouched, so the evidence still reads as evidence; only the name of the host changes. Replacing rather than deleting is deliberate: a deleted command would leave a record that no longer shows what was run.

### Keep the runtime coupling for its own change
The audience and the resource the web app asks for are part of the sign-in exchange, and the pilot is live. Changing them means adding the values to the deployment stack first, deploying, and proving that sign-in still works. Bundling that into a textual publication change would make a small change carry a production risk, and would blur which edit broke a login. The three values, and the guard extension that depends on them, are named in this change as its boundary and handled next.

### Replace only the stale parts of the README
The documentation order is the entry point agents and readers already follow, and it stays. What goes is the status paragraph that describes the pre-pivot backend and the framing that reads like an internal work log; what arrives is a product paragraph, a quickstart that mirrors the local foundations section, and the license line.

## Migration Plan

1. Copy the Apache-2.0 text and the Contributor Covenant into the repository, verbatim.
2. Write the contributing guide, the security policy, the code of conduct placement and the templates.
3. Rewrite the README.
4. Replace the hosts and the application id across the example configuration, the development compose defaults, the API settings default, the stylesheet asset URL, the deployment notes, the decision record, the archived evidence and the journey audit.
5. Run the guards and the suites, then read the tree once more for anything that still names the operator.

Rollback: revert the commit. The change is textual and additive, and no application behavior depends on it.
