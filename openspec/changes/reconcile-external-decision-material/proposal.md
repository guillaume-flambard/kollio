## Why

Teams already form decision material in ChatGPT, shared documents, and separate business units before it reaches Kollio. Rewriting a single latest document erases competing proposals, source context, and the human judgement that reconciled them, which prevents Kollio from becoming the durable memory of how a team decided.

## What Changes

- Add manually imported, immutable text material to a Decision Space, with its stated author, origin tool, original language, capture time, and ordered revisions.
- Let members select source excerpts and promote them into proposed or confirmed Contributions while preserving an addressable link to the exact source revision and excerpt.
- Add a reconciliation workspace where members compare material from several sources, see compatible and conflicting claims, and record whether a claim is combined, retained, rejected, or left open.
- Let the Companion propose a reconciliation brief only from selected source excerpts and confirmed Contributions. Every proposed statement SHALL cite its source material; a person decides what becomes shared reasoning or a Decision Record.
- Keep manual text import as the first boundary. Direct connectors to ChatGPT, Google Drive, Notion, Slack, file parsing, and automatic cross-workspace retrieval remain out of scope.
- Preserve all existing Branch, Contribution, Converge, Decision, workspace-isolation, and FR/EN behaviours.

## Capabilities

### New Capabilities

- `external-decision-reconciliation`: immutable source material, version lineage, excerpt-grounded reconciliation, and human-confirmed synthesis within one Decision Space.

### Modified Capabilities

- `branches`: a Contribution promoted from imported material retains a typed reference to its source revision and excerpt alongside the existing provenance fields.
- `explore-screens`: Explore lets members import material, inspect its provenance and revisions, and promote a selected excerpt without treating raw material as shared reasoning.
- `converge-screens`: the reasoning map renders source-backed Contributions with their source lineage and lets members reach the cited excerpt.

## Impact

Adds PostgreSQL tables and migrations, API schemas and routes, generated TypeScript client code, a LangGraph Companion workflow with Pydantic structured outputs, web screens and browser evidence. The capability is private to a workspace and a Decision Space. It introduces no connector credential, external data fetch, file upload, or change to existing permission rules. The visual shell change `redesign-decision-workspace` remains presentation-only and is intentionally independent.
