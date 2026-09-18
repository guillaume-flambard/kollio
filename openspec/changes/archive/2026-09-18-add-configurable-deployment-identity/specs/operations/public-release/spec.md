# operations/public-release Specification

## Purpose

A published project has to be runnable by someone who is not its author, which means the identity of the deployment belongs to the deployment and not to the repository. This capability states what the repository may assume about the environment it runs in.

## ADDED Requirements

### Requirement: The deployment identity comes from the environment (PR-05)

The web application SHALL read its identity-provider resource and its public site URL from the environment rather than from values committed in the repository, and it SHALL fail with a message that names the missing configuration when the resource is absent. The resource requested from the identity provider and the audience used for the API SHALL come from one configured value, so they cannot diverge. Tracked content SHALL NOT name the operator's host or home directory, and a check SHALL fail when it does.

#### Scenario: A clone runs without the operator's host

- **WHEN** someone clones the repository and runs the web application with their own identity provider configuration
- **THEN** no file in the repository names the operator's host or home directory
- **AND** the application reads the resource and the site URL from the environment

#### Scenario: The resource and the audience agree

- **WHEN** the server asks the identity provider for an access token
- **THEN** the resource indicator it requests and the audience it presents to the API come from the same configured value

#### Scenario: The resource is missing

- **WHEN** no resource is configured in the environment
- **THEN** the server fails with an error that names the missing configuration instead of requesting a token with an empty audience

#### Scenario: The guard catches a quoted host

- **WHEN** tracked or staged content contains the operator's host or home directory
- **THEN** the private file check fails and names the file
