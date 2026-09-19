# Build and publish on hosted runners

## Why

The pipeline ran on a self-hosted agent installed on the deployment host and pushed its images into a registry that only that host could reach. That was a consequence of the repository being private: the private package could only be pulled by the machine that built it, and a private repository cannot require status checks on `main` without a paid plan, so nothing stopped an unverified push from landing.

The repository now carries a licence and a path for contributors. The same pipeline therefore has to build where anyone can read it and publish images anyone can pull, so a fork, a contributor or a second host can run and deploy the same code without an account on the operator's machine.

## What Changes

- Run the verification and live-evaluation jobs on runners provided by the platform.
- Publish on those runners too, with the workflow token, into `ghcr.io` instead of the machine-local registry: one image per commit, tagged with the commit and with a moving `latest`.
- Read the forbidden patterns of the private-content check from the environment instead of carrying them in the repository, and announce the skip when they are not configured.
- The deployment stack still points at the machine-local registry until the packages exist and are public, which is a separate repository.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `operations/public-release`: add a requirement that the pipeline builds and publishes on runners the platform provides, into a registry any host may pull, so the project can be built and deployed without the operator's machine.

## Impact

Touches `.github/workflows/ci.yml` and `scripts/check_private_files.py`. The deployment stack of the private infrastructure repository follows once the published packages are public. No application, contract, migration or database change. The workflow needs one GitHub secret holding the patterns the private-content check rejects; without it that single scan prints a line and skips, and every other check still runs.

## Out of Scope

- Making the repository public, and the branch protection rules that become available with it.
- Rewriting the git history.
- Moving the pipelines of the other repositories.
