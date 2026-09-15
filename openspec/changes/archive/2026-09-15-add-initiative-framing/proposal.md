## Why

Kollio presents every deposit as an "idea", which reads as a startup-idea network rather than the B2B decision memory the pilot tests. Owners also cannot say what kind of initiative they are depositing, so the company's campaigns, pricing changes, partnerships and internal improvements are indistinguishable in the record.

## What Changes

- Give every idea a closed initiative type (idea, hypothesis, campaign, opportunity, decision, experiment, pricing, market, partnership, internal improvement), set at deposit and editable afterwards by the owner.
- Default to the `idea` kind so existing rows and clients keep working unchanged.
- Refuse unknown kinds at the boundary.
- Speak of Initiatives in the French and English B2B surfaces; code, database and API keep saying Idea (decision #44).

## Capabilities

### New Capabilities

- `initiative-framing`: an initiative carries its kind, and the B2B surface calls it an Initiative.

## Impact

Adds an `initiative_type` column with a closed check constraint and one migration, one domain rule with unit tests, the field in deposit/read/list responses, an owner-only update operation, a type selector at deposit and on the detail screen, and the French/English copy switch for the workspace surfaces. No breaking change: the field defaults to `idea`, and contract regeneration adds one operation without removing any.

Tickets: GitHub #56 (this slice), #52 (parent spec).
