# Design

## The seed is the only "setup", the path is all interface

`seed_faktus` creates exactly what an operator cannot click into existence
before they have data: the workspace, its members and the company context, plus
one initiative so there is something to open. It stops at the first iteration
(the deposit already happened); every step after that is done in the product,
which is the point ("no code or database intervention"). Fixed uuid5 ids and
upserts make it idempotent, so a failed demo run can be reseeded without
dropping anything, and `--reset` removes precisely its own rows (verified with
a scratch database).

The seeded content is reconstructed from what the repository already commits to
in its fixtures and docs: Faktus as a bootstrapped, founder-led B2B SaaS run by
a marketing leader; the objective "five paying pilots" and the constraint
"bootstrapped, no field hiring" from the reuse and contradiction eval fixtures;
an offline-first field-app initiative from the same fixtures. It is labelled as
reconstruction, not as the client's own words, so the §13 human-input work stays
visible.

## Why the path is a mapping, not one giant test

The loop spine is already integration- and browser-tested, each piece at its own
boundary. A single end-to-end Playwright test would need the live gateway and
real auth to be honest, which CI cannot run, or a full stateful fake backend that
re-implements every endpoint and mostly re-asserts the per-screen checks. So the
demo path is recorded as steps A–I, each tied to the concrete test that proves
it and the endpoint it exercises. The seed test is the one genuinely new
executable: it proves the starting state is deterministic and idempotent.

## What stays a human act

Two steps cannot be reduced to a green test without a live provider: producing a
real analysis verdict, and a real colleague logging in as the second person.
Both are named as operator actions in the acceptance, with the recorded eval and
the integration access-control test as the closest executable evidence.
