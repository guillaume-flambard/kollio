# operations/public-release Specification

## Purpose

A published project is built and shipped by people who do not own the operator's machine. The pipeline therefore has to run where anyone can read it, and it has to publish artifacts anyone can pull.

## ADDED Requirements

### Requirement: The pipeline builds and publishes on hosted runners (PR-06)

The pipeline SHALL run its verification and publication jobs on runners the platform provides rather than on the deployment host, and SHALL publish its images to a registry that any host may pull from, tagging each image with the commit it was built from and keeping a moving latest tag. A fork, a contributor or a second host SHALL be able to build and deploy the same code without access to the operator's machine.

#### Scenario: A push to main publishes images

- **WHEN** the main branch receives a commit
- **THEN** the pipeline verifies that commit
- **AND** it publishes an image tagged with that commit and moves `latest` in a registry that can be read without credentials

#### Scenario: Verification needs no operator machine

- **WHEN** the verification job runs
- **THEN** it runs on a runner the platform provides, with its own database and cache services
- **AND** it needs no self-hosted agent and no registry login

#### Scenario: The private-content scan still runs without naming what it rejects

- **WHEN** the scan runs with the rejected patterns configured in the environment
- **THEN** it fails on tracked content that matches them
- **AND** when the patterns are not configured it announces that it skipped that scan, and the other checks still run
