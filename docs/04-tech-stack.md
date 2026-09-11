# 04 — Stack technique

## Front
| Brique | Choix | Pourquoi |
|---|---|---|
| Framework | **Nuxt (Vue 3)** | Choix produit ; SSR/SEO ; DX |
| UI | **Nuxt UI v3** (Reka UI + Tailwind v4) | Socle accessible + thémable ; le design system devient le thème |
| i18n | **@nuxtjs/i18n** (FR/EN) | Multilingue dès le départ (voir `07-i18n.md`) |
| Motion | **Motion for Vue** (ou @vueuse/motion) | Animations premium, maintenables (pas d'ad-hoc) |
| Client API | **généré depuis l'OpenAPI** | Typé ; partagé web + mobile plus tard |

**Règle UI :** widget interactif standard → Nuxt UI ; surface signature (hero, viz du tueur de contraintes, graphe d'élan, dépôt d'idée) → composant custom (généré par Astra) **consommant les mêmes tokens**. Ne pas tout générer from scratch (incohérent, non accessible, non maintenable).

## Back
| Brique | Choix | Pourquoi |
|---|---|---|
| Langage | **Python** | Les agents sont en Python |
| API | **FastAPI** | Async, Pydantic v2, OpenAPI auto → client typé |
| Agents | **LangGraph** | Graphes d'états, HITL, checkpointer Postgres |
| Validation | **Pydantic v2** | Structured outputs à la frontière LLM |
| Durabilité | **LangGraph checkpointer** (DBOS seulement si besoin au-delà du graphe) | Reprise/HITL sans infra en plus |
| File | **ARQ** | Async, Redis, match FastAPI |

## Données & LLM ops
| Brique | Choix |
|---|---|
| Base | **PostgreSQL** (+ **pgvector** / pgvectorscale) |
| Cache/broker/temps réel | **Redis** |
| Gateway LLM | **LiteLLM** (self-host) |
| Observabilité | **Langfuse** (instrumenté **OpenTelemetry**) |
| Eval | **DeepEval** (CI) + online evals Langfuse |
| Embeddings | **modèle multilingue** (cross-lingual) — non négociable |

## Infra
| Brique | Choix |
|---|---|
| Conteneurs | **Docker** (multi-stage) |
| Hébergement | **VPS Netcup** existant via **Make/Ansible + Compose/Traefik** |
| CI/CD | **GitHub Actions** (ruff, pytest, build, deploy) ; **Alembic** |
| Secrets | env plateforme → **Infisical** plus tard |
| Auth | managée pour aller vite (Clerk / Supabase Auth) ou FastAPI-Users |

## Monorepo & qualité
- **uv workspaces** (Python) + **pnpm workspaces** (JS). Pas de Nx/Turborepo (surdimensionné en polyglotte solo).
- **Modular monolith / tranches verticales**, couture hexagonale légère. DDD tactique au cœur seulement.
- **TDD** sur le domaine déterministe ; **eval-driven** sur les agents. Voir `08`.

## Ne PAS utiliser (over-engineering)
Kubernetes · Kafka/microservices (pré-échelle) · base vectorielle dédiée jour 1 · Celery+RabbitMQ · Temporal (solo) · framework mémoire prématuré · empiler LangSmith+Braintrust+Langfuse.
