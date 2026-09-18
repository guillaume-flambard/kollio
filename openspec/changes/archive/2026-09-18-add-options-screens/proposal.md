# Add the Options screens

## Why

`docs/00-project-overview.md` section 7 makes the Option the object a team compares and
later decides between: each one carries a proposal, a mechanism, an upside, a cost, its
risks, its critical assumptions, its success metrics and the evidence for and against it.
Section 20 step 5 puts Options right after Converge, and the API slice (#112) already
stores them, links confirmed Contributions to them and refuses to score them.

Nothing in the product reaches that API. The Options section of a Decision Space renders a
placeholder, so a team that converged on its reasoning still has no way to write down the
paths it might take, to attach the Contributions that argue for or against each one, or to
read a trade-off instead of a summary.

## What Changes

The `options` section of a Decision Space becomes real, at
`/workspace/decision-spaces/[spaceId]/options`:

- The section lists the Options the Space holds, each with its title, its proposal and
  whether it carries evidence.
- A member writes an Option from a form. Title and proposal are required. The six
  narrative fields §7 names (mechanism, upside, cost, risks, critical assumptions,
  success metrics) are optional, and a field left out stays out rather than arriving as
  an empty answer.
- A member edits an Option, and the change survives a reload.
- A member links a confirmed Contribution of the same Space as evidence `for` or
  `against`, and unlinks it. A Contribution that is not confirmed is not offered.
- A member deletes an Option; it leaves the list and the Space still reads.
- Nothing on the screen scores, ranks or rates one Option against another.

Seven Nitro proxies carry the seven `options` operations to the browser. The API contract
is unchanged, so `make contract` is a no-op for this slice.

## Capabilities

### New Capabilities

- `options-screens` — the browser surface of the Options section: listing, writing,
  editing, deleting and linking evidence, with the fields §7 declares and no scoring.

### Modified Capabilities

None.

## Impact

Adds the body of the Options section, seven Nitro proxies, the Options keys in both locale
catalogs, vocabulary in `apps/web/CONTEXT.md` and browser evidence at the mocked-API
pattern.

No API change, no migration, no agent call. Two honest boundaries: the list operation
carries no evidence, so the screen reads each Option in detail to say whether it carries
any; and a Contribution that is not confirmed is refused by the API, so the "not offered"
case is proved in the browser spec with a mocked unconfirmed Contribution rather than in
production.

Tickets: GitHub #122 (migration step 5 of `docs/00-project-overview.md` §20, screen half;
follows the API slice #112).
