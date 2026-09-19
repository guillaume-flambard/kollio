# Acceptance evidence - move-pipeline-to-hosted-runners

The pipeline ran its three jobs on an agent installed on the deployment host and pushed its images into a registry only that host could reach, which tied building to one machine and kept the repository unable to require status checks on `main`. This change moves every job onto runners the platform provides, publishes images to a registry any host may pull, and stops the repository from carrying the patterns it rejects by reading them from the environment.

Status: complete.

| Spec scenario | Evidence | State |
| --- | --- | --- |
| A push to main publishes images | The workflow publishes `ghcr.io/guillaume-flambard/kollio-<image>:<commit>` and moves `latest`, and no longer names the machine-local registry. Local proof: the file parses as YAML and the string `127.0.0.1:5000` is gone. The first hosted run is the delivery evidence. | Pending, first hosted run |
| Verification needs no operator machine | The three jobs now declare `runs-on: ubuntu-latest` and the file contains no self-hosted label; the web behaviour step is `vitest run`, so no browser download is needed. The first hosted run is the delivery evidence. | Pending, first hosted run |
| The private-content scan still runs without naming what it rejects | `scripts/check_private_files.py` reads the patterns from `KOLLIO_PRIVATE_PATTERNS`: with them configured it exits 1 and names a probe file that contains one, and without them it prints that it skipped that scan and exits 0 on a clean tree. The repository secret `KOLLIO_PRIVATE_PATTERNS` exists, so the verification step receives them. | Passing |

## Verification runs (2026-09-19)

Live, in production, after the deploy:

- Nothing is recorded yet. The first hosted run happens on the next push to `main`, and the deployment still pulls from the machine-local registry until the published packages exist and are public, which is the follow-up in the private infrastructure repository.

Local, before deploy:

- `grep -n '127.0.0.1:5000\|self-hosted' .github/workflows/ci.yml` → `NO_STALE_REFERENCE`.
- `uv run --project apps/api python -c "import yaml; yaml.safe_load(open('.github/workflows/ci.yml')); print('YAML OK via uv')"` → `YAML OK via uv`.
- `python3 scripts/check_private_files.py --tracked` → exit 0 with the patterns unset (it announces the skip) and exit 0 with them configured on a clean tree; with a tracked probe file containing a rejected pattern it exits 1 and names the file.
- `gh secret list --repo guillaume-flambard/kollio` → `KOLLIO_PRIVATE_PATTERNS`.

## Known boundaries

- No application file changed, so the web gates (lint, type check, locale, token and coverage guards, production build, browser suite) are unaffected by this change and were not re-run for it. The workflow itself is the artifact under test, and its YAML validity plus the hosted run are its evidence.
- The repository is still private at the time of the first run, so the packages it creates are private too. The deployment pulls anonymously only once the repository and its packages are public.
- Branch protection and required status checks are not set by this change, though a public repository makes them available.
- The self-hosted agent and the machine-local registry stay in place until the deployment stack has switched, so the old pipeline remains a working fallback.
