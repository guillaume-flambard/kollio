# identity/private-workspace-auth Specification

## Purpose
Defines how a Kollio member authenticates and gains access to ideas in a private workspace
without exposing tenant data or accepting unverifiable identities.

## Requirements

### Requirement: Browser authentication uses the configured identity tenant
The system SHALL provide sign-in, callback, session, and sign-out behavior for the configured
identity tenant. Authentication routes SHALL remain outside localized URL prefixes.

#### Scenario: Member signs in successfully
- **WHEN** a member completes authentication through a registered callback URL
- **THEN** the application SHALL establish a secure server-side session in the selected locale

#### Scenario: Identity service is not configured
- **WHEN** the application starts without complete identity configuration
- **THEN** authentication SHALL remain disabled and protected data SHALL remain inaccessible

### Requirement: API tokens are validated before authorization
The API MUST validate token signature, issuer, audience, expiry, and non-empty subject before
using the subject for an authorization decision.

#### Scenario: Token targets another API
- **WHEN** a request presents an otherwise valid token with a different audience
- **THEN** the API SHALL reject the request as unauthenticated

#### Scenario: Token is expired
- **WHEN** a request presents an expired token
- **THEN** the API SHALL reject the request as unauthenticated

### Requirement: Identity membership controls private workspace access
An authenticated identity SHALL access a private idea only when its subject is mapped to a user
who is a member of the idea's workspace.

#### Scenario: Imported workspace owner reads an idea
- **WHEN** the configured owner identity requests an imported private idea
- **THEN** the API SHALL return the idea

#### Scenario: Non-member requests a private idea
- **WHEN** an authenticated identity without workspace membership requests a private idea
- **THEN** the API SHALL return the same not-found response used for an unknown idea
