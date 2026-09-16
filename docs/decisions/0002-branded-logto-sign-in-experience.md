# ADR 0002: Brand Logto's hosted sign-in experience and serve it from a Kollio domain

Status: accepted
Date: 2026-09-16

## Context

Kollio delegates authentication to self-hosted Logto OSS 1.43.0 at
`kollio-auth.memolabs.dev`, reached through `@logto/nuxt` and Logto's hosted
sign-in experience. That experience was never customised, so users leaving the
product land on Logto's stock default skin on a different host. It reads as an
old, foreign login page. Logto officially supports two remedies: a custom UI
driven by the Experience API, and branding of the hosted page (app-level logo,
favicon, colours and custom CSS, with separate light and dark colours).

## Decision

Keep credentials entirely inside Logto and make the hosted experience read as
Kollio's: set app-level branding in the Logto Console and serve the experience
from a Kollio-owned domain through Traefik and Logto's custom-domain support.
Custom CSS is limited to Logto's own variables and documented hooks; nothing
bypasses the hosted interaction flow. Authorization decisions stay in Kollio,
per lab-infra's `self-host-kollio-identity` design.

## Alternatives

Bring-your-own-UI over the Experience API (`PUT /api/experience` with
`interactionEvent: 'SignIn'`, then `POST /api/experience/identification`)
would deliver genuinely Living Canvas markup, but it requires re-implementing
the interaction flow, captcha, error states and localized content, and its
exact email-and-password identification payload lives only in Logto's external
OpenAPI spec. The unique gain over branding is ours markup; the price is that
the product starts handling credentials. Not adopted unless branding proves
visually insufficient.

## Consequences

The branding CSS targets Logto's internal markup, so it can break on a Logto
upgrade and the sign-in page must be re-verified after each one. The
custom-domain route lives in lab-infra, not in this repo; this ADR records
only the product-side choice. The `prompt=consent` step on every sign-in is
out of scope here.
