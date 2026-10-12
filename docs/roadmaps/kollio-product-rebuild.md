# Kollio product rebuild

## Product invariant

Kollio has one visual language: **Living Canvas / Aubergine**. It is light-first, calm, airy and relational. Every authenticated screen extends the same canonical tokens, Geist typography, Kollio-owned SVG icon system, felt-tip selection wash and relationship line treatment. No route may introduce a generic SaaS card grid, an alternate palette, a third-party icon set, raw visual values or a separate design system.

The approved reference is the custom reconciliation direction: a quiet left rail, source material treated as paper, selected excerpts in restrained lavender/coral wash, one visible curved relationship at a time, and a living brief that preserves uncertainty instead of manufacturing consensus. It is a direction, not an image to copy literally.

## Observed baseline

- `apps/web/app/pages/workspace/decision-spaces/[spaceId].vue` and every major decision section own large page-local style blocks.
- Those blocks contain raw spacing, sizing, timing, radius and shadow values, so the canonical token system cannot govern the product consistently.
- Explore, Converge, Options, Experiment and Learning have independently evolved dense form-and-card layouts. This is the source of the visual incoherence, not a single route-level defect.
- The new reconciliation persistence is isolated and version-safe, but it has no end-to-end contract, Companion workflow or user surface yet.
- The security policy is partially modelled. It must be completed before sensitive source material can be sent to a model. Prototype routing is never a Faktus security promise.

## Delivery order

### Chassis: one product, not route-by-route styling

1. Record desktop and phone visual acceptance references for Inbox, Space shell, Explore import and reconciliation.
2. Inventory every authenticated route and identify its local visual literals.
3. Extend only `packages/ui/src/tokens.css` for durable needs, then enforce a failing guard for undeclared literals, token names and non-Kollio icons.
4. Build shared primitives: app frame, page header, moment navigation, primary action, paper/source block, reasoning block, empty/error state, status and relationship connector.
5. Migrate Workspace Inbox and the Decision Space shell to those primitives first. Their screenshots become the reference evidence.

### Security: invisible for members, controlled by administrators

6. Finish provider policy persistence, audit, retention and authorization tests.
7. Carry workspace, actor and selected source-excerpt ids through every model gateway call. Refuse by default. There is no system-provider fallback.
8. Seed the prototype provider explicitly as `b.ai / qwen3.8-flash` only after its configured route is verified. Mark it prototype and prevent sensitive material from reaching it.
9. Add administrator-only provider, audit, retention, export and deletion surfaces. Members never choose a model, see a provider modal or confirm an invocation.
10. Publish no Faktus security claim until hosting, encryption, backups, subprocessor terms, deletion window and DPA are verified operationally.

### Reconciliation: the distinctive Kollio loop

11. Deliver manual text import with stated author, origin, language, visibility and immutable version timeline.
12. Let a member select stable source excerpts, promote an excerpt to a proposed Contribution and retain its lineage.
13. Build the Companion as a LangGraph review workflow. It can compare selected excerpts and propose cited alternatives, but never changes reasoning or decides.
14. Build the reconciliation view in Living Canvas: source sheets on the left, one inspected relationship in the centre, living brief on the right. A human explicitly retains, combines, rejects or leaves an item open with a rationale.
15. Carry provenance into Converge without copying raw documents into the map.

### Product inheritance: every screen earns the same language

16. Rebuild Options and Decision using shared paper, reasoning and relationship primitives.
17. Rebuild Experiment and Learning using the same three-moment narrative, rather than dashboard cards.
18. Rebuild administrator settings with the same calm Living Canvas grammar, while keeping security detail out of ordinary member flows.
19. Retire or quarantine legacy Initiative navigation after its destination is covered by the shared chassis. Preserve URLs until a separate migration decision.

## Evidence gates

- API boundary: Postgres integration tests for workspace isolation, provider denial, audit immutability and source lineage.
- Agent boundary: recorded Pydantic fixtures that reject missing, foreign or uncited excerpts. No live provider is needed for CI.
- Visual boundary: FR and EN Playwright scenarios at desktop, 768px and 375px, with non-empty screenshot evidence recorded through `ux-flow-auditor`.
- Design boundary: token and icon guard passes for every authenticated route; a known invalid fixture fails.
- Delivery boundary: generated API client, locale parity, typecheck, production build and a migrated disposable database all pass before a slice is claimed complete.

## Explicit exclusions

- No SaaS connector, file parser or automatic Drive/Slack/Notion ingestion in V1.
- No autonomous reconciliation, automatic consensus, opaque AI memory or per-member model selection.
- No claim that a free prototype model is suitable for Faktus confidential data.
