# Tasks - move-pipeline-to-hosted-runners

## 1. Move the verification jobs

- [x] 1.1 Run the `verify` job on a runner the platform provides instead of the self-hosted agent
- [x] 1.2 Run the optional live-evaluation job on a platform runner too

## 2. Publish on the platform registry

- [x] 2.1 Give the publishing job permission to write packages, and log in to the container registry with the workflow token
- [x] 2.2 Tag each image with the commit it was built from and keep a moving `latest`
- [x] 2.3 Take the machine-local registry out of the workflow

## 3. Keep the pattern scan without writing the patterns

- [x] 3.1 Read the rejected patterns from `KOLLIO_PRIVATE_PATTERNS` and announce the skip loudly when they are not configured
- [x] 3.2 Feed the repository secret into the verification step

## 4. Close with evidence

- [x] 4.1 Run the private-content check with the patterns configured and confirm the workflow file still parses
- [ ] 4.2 Confirm the first hosted run publishes images and that they pull without credentials
- [x] 4.3 Write `acceptance.md` with the scenario-to-evidence mapping
