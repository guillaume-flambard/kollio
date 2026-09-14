# Context Map

Kollio is a multi-context repo. Each context owns its domain language in a `CONTEXT.md`; system-wide decisions live in `docs/decisions/`.

## Contexts

- [API](./apps/api/CONTEXT.md): the FastAPI backend; owns the domain model (ideas, iterations, constraint analyses, company context, teams, experiments) and the agent graphs.
- [Web](./apps/web/CONTEXT.md): the Nuxt application; the product surface where owners, contributors, and observers meet ideas.
- [API client](./packages/api-client/CONTEXT.md): the generated TypeScript client; the contract boundary between web and API.
- [UI](./packages/ui/CONTEXT.md): the shared design language (Living Canvas tokens and theme).

## Relationships

- **API → Web**: the API owns all domain state; the web app never invents domain concepts, it renders them.
- **API → API client**: the OpenAPI contract is generated from the API; the client package only republishes it.
- **UI → Web**: the web app consumes Living Canvas tokens and theme from the UI package; no raw values in screens.
- **API ↔ Web**: shared vocabulary for `Idea`, `Iteration`, `ConstraintAnalysis`, `CompanyContext`, and team roles; the API glossary is canonical when they disagree.
