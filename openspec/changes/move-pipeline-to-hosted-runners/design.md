# Design - build and publish on hosted runners

## Context

`.github/workflows/ci.yml` runs three jobs, all on `runs-on: [self-hosted, Linux, X64]`: the verification job that lints, migrates and tests, the opt-in live evaluation job, and the publish job that builds four images (api, worker, web, litellm) and pushes them to a registry reachable only as `127.0.0.1:5000`. The publish job carries a comment explaining why: the repository was private, so its package was private too and the deployment host could not pull it, which is why the image was built where it is served.

That arrangement tied the pipeline to one machine. It also meant the project could not require status checks on `main`, because GitHub offers required checks on private repositories only with a paid plan, so an unverified push could land. The repository now carries a licence, a contributor guide and a code of conduct, so the pipeline has to run where a contributor can watch it and publish images a stranger can pull.

Two details make the move simple. The web behaviour script in `apps/web` runs `vitest run`, so that step needs no browser download and works anywhere. And the private-content check `scripts/check_private_files.py` carried the rejected patterns as a literal, which cannot be published; it now reads them from the environment variable `KOLLIO_PRIVATE_PATTERNS`.

## Goals / Non-Goals

**Goals:**

- Verification and publication run on runners the platform provides, with no agent installed on the deployment host.
- Images are published to a registry any host may pull, tagged by the commit and by a moving `latest`.
- The private-content scan still rejects the operator's infrastructure without naming it in the repository.
- The pipeline keeps its behaviour otherwise: the same checks, the same four images, `max-parallel: 2`, the same build arguments and the same OCI labels.

**Non-Goals:**

- Making the repository public, which is its own change.
- Requiring status checks on `main`, which only becomes possible once the repository is public.
- Rewriting git history.
- Moving the pipelines of other repositories.

## Decisions

### Hosted runners for every job

The three jobs move from `[self-hosted, Linux, X64]` to `ubuntu-latest`. The verification job brings its own Postgres and Redis service containers and the web behaviour step is a unit test run, so nothing there needs the deployment host. The live evaluation job runs compose, which hosted runners provide, and it stays opt-in behind a manual dispatch.

### The registry is the platform's, tagged by commit plus a moving latest

The publish job logs in with `docker/login-action` using the workflow token and pushes `ghcr.io/guillaume-flambard/kollio-<image>:<commit>`, then retags and pushes `:latest`. Nothing pulls anonymously until the packages are public, which follows with the repository's visibility; until then the deployment stack keeps pointing at its machine-local registry, so the switch lands on the deployment side and not here.

### Patterns by secret, with a loud skip

The private-content check no longer writes the patterns it rejects: it reads `KOLLIO_PRIVATE_PATTERNS` from the environment and, when the variable is absent, prints one line saying so and skips that single scan. In continuous integration the variable comes from a repository secret, so the scan runs. On a contributor's machine and on a pull request from a fork it announces the skip instead of pretending it checked.

### Keep the publishing shape

`max-parallel: 2` and the prune step stay as they are. They were tuned for a small machine and they cost nothing on a hosted runner, and changing them would mix a registry move with a performance decision.

## Migration Plan

1. Move the three jobs to platform runners and publish to the platform registry.
2. Give the private-content check its patterns through the environment.
3. Make the repository public, which also allows required checks on `main`.
4. Confirm that the published images pull without credentials, then point the deployment stack of the private infrastructure repository at the new registry.

Rolling back is reverting this commit: the old pipeline keeps working for as long as the self-hosted agent and the machine-local registry exist.
