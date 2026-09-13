# Kollio — documents de projet

**Kollio** — un "GitHub des idées" : une plateforme collaborative où l'on dépose une idée, où l'IA la pressure-teste (le tueur de contraintes), où l'on itère façon commits/branches, et où une équipe se forme autour d'elle.

Ces documents sont la **source de vérité** du projet. Ils sont destinés à être lus par des agents de code (Astra, Claude Code) et par OpenSpec. Déposer le contenu à la **racine du dépôt**.

## Ordre de lecture
1. `AGENTS.md` — instructions pour les agents de code (à lire en premier)
2. `docs/00-project-overview.md` — ce qu'est Kollio, la vision
3. `docs/01-product-spec.md` — le produit, les concepts, le périmètre V1
4. `docs/02-strategy-and-moat.md` — la défendabilité (le moat) et la stratégie B2B-first
5. `docs/03-architecture.md` — l'architecture back-end / agentique
6. `docs/04-tech-stack.md` — la stack et les décisions
7. `docs/05-data-model.md` — le modèle de données
8. `docs/06-design-system.md` — le design system
9. `docs/07-i18n.md` — le multilingue FR/EN (dès le départ)
10. `docs/08-conventions-and-testing.md` — conventions, monorepo, tests
11. `docs/09-roadmap.md` — les phases
12. `docs/10-project-init.md` — **bootstrap** : commandes d'initialisation (CLIs officiels, dernières versions) — à lire avant d'écrire du code

## Statut
Pré-PMF. Un back-end existe déjà (Python + Langfuse + SQLite sur VPS Netcup) et sera solidifié/migré selon `docs/03-architecture.md`. Ne pas partir de zéro : migrer.

## Principe directeur
Bâtir du **solide sans sur-ingénierie**. Chaque brique se remplace individuellement quand une métrique le réclame — jamais "au cas où".

## Local foundations

Use the runtimes recorded in `.nvmrc` and `.python-version`. Copy `.env.example`
to `.env`, generate a local Postgres password and LiteLLM master key, and set the
local database URL. Provider credentials remain outside Git.

```bash
make install
make services
make migrate
make build
make up
make verify
```

Integration tests require `TEST_DATABASE_URL` pointing to a separate Postgres
database with the Alembic migrations applied. Never point tests at imported data.
Provider calls require `KOLLIO_RUN_LIVE_EVALS=1`; ordinary checks use recordings.

See `docs/11-bootstrap-status.md` for resolved versions, evidence and unfinished
Phase 0 acceptance criteria. The current implementation is a foundation, not the
complete V1 product.

## Delivery workflow

Read [the delivery workflow](docs/12-delivery-workflow.md) before starting a product
change. It defines scenario evidence, agent handoffs, contracts, tests, evaluations
and the merge criteria. Durable decisions live in [ADRs](docs/decisions/).
