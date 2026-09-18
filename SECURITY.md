# Security policy

## Supported versions

Kollio is pre release. Only the `main` branch is supported; there are no maintained release branches yet.

## Reporting a vulnerability

Please do not open a public issue. Use GitHub's private vulnerability reporting on this repository (the Security tab, then Report a vulnerability), which keeps the discussion private and gives a place to prepare a fix and a disclosure date. If you cannot use that form, write to g.flambard@gmail.com.

Useful in a first message: what you were doing, the exact request or click path, what you observed, and what you expected. A proof of concept helps, and a log excerpt or a screenshot is enough to start.

## What to expect

This is a solo maintained project without a paid on call rotation, so the honest promise is: an acknowledgement within a few days, an assessment of severity with you, a fix or a mitigation as fast as the severity warrants, and credit in the release note if you want it. Please allow a private window before publishing, and say so if a deadline matters to you.

## Scope

The pilot deployment runs the same code as this repository. In scope: anything that reaches production data, breaks the boundary between workspaces, escapes the least privilege given to agent tools, or leaks a provider credential. Out of scope: the configuration of the operator's own host, and findings that only apply to a locally modified build.
