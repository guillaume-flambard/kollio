# 10 — Initialisation du projet (bootstrap)

## Principe (IMPÉRATIF — lire avant d'écrire du code)
- **Scaffolder avec les CLIs officiels au terminal.** L'agent (Astra/Codex) **exécute les commandes**, il ne génère PAS de squelettes de fichiers à la main ni de mémoire. On n'invente pas la roue : les générateurs officiels produisent la base, puis on **réorganise** dans la structure de `docs/08`.
- **Dernières versions stables, toujours.** `@latest` / laisser les CLIs résoudre. **Ne pas hardcoder de numéros de version** (périmés par définition). Après chaque install, relever les versions résolues (`package.json`, `pnpm-lock.yaml`, `pyproject.toml`, `uv.lock`) et les consigner.
- Prérequis machine : Node LTS, **pnpm**, **Python 3.12+**, **uv**, Docker.

> Les commandes ci-dessous sont canoniques ; si une commande exacte a changé, **se référer à la doc officielle courante** du CLI concerné plutôt que d'inventer.

## 0. Monorepo
```bash
mkdir kollio && cd kollio && git init
pnpm init
# pnpm-workspace.yaml :
#   packages:
#     - "apps/*"
#     - "packages/*"
# (Python : uv workspace au niveau apps/api, voir §2)
```

## 1. Front — Nuxt + Nuxt UI + i18n
```bash
pnpm dlx nuxi@latest init apps/web
cd apps/web
pnpm dlx nuxi@latest module add ui      # Nuxt UI (dernière majeure) — amène Tailwind
pnpm dlx nuxi@latest module add i18n     # @nuxtjs/i18n
pnpm add motion-v                        # ou @vueuse/motion — la lib motion recommandée à jour
cd ../..
```
- Configurer i18n **FR/EN dès maintenant** (voir `07`). Mapper les tokens du design system dans `app.config.ts` (voir `06`).

## 2. Back — Python + FastAPI + LangGraph
```bash
mkdir -p apps/api && cd apps/api
uv init
uv add "fastapi[standard]" pydantic pydantic-settings sqlalchemy alembic asyncpg redis arq langgraph langfuse litellm
uv add --dev pytest pytest-asyncio ruff mypy deepeval
uv run alembic init alembic
cd ../..
```
- `uv` résout les dernières versions ; consigner `uv.lock`. Instrumentation Langfuse **en OpenTelemetry** (voir `03`).

## 3. Base de données (local puis prod)
- Local : `docker-compose.yml` avec **Postgres (+ extension `vector`)** et **Redis**.
- `CREATE EXTENSION IF NOT EXISTS vector;` dans la 1re migration Alembic.
- Prod : mêmes services via **Make/Ansible** sur le VPS Netcup (voir `03`).

## 4. Réorganiser selon la clean archi (doc 08) — NE PAS laisser la structure par défaut
Après le scaffold officiel, réarranger en **tranches verticales** :
```
apps/api/src/
  modules/<domaine>/{domain,service,adapters,api}   # ideas, iterations, matching, teams, users
  agents/                                            # graphes LangGraph (+ locale en param)
  platform/                                          # litellm, langfuse/otel, redis, db, config
packages/
  api-client/   # généré depuis l'OpenAPI de FastAPI → consommé par web (+ mobile plus tard)
  ui/           # thème / design system Nuxt UI
contracts/      # OpenAPI / schémas partagés
openspec/       # spécifications OpenSpec
```

## 5. Qualité dès le départ
- `ruff` (lint+format), `mypy` (au moins sur `domain/`), `pytest` configurés.
- Hooks pre-commit ; **GitHub Actions** : lint → test → build image → deploy (Make/Ansible sur Netcup) ; migrations Alembic dans le pipeline.

## Règle d'or pour l'agent
Terminal + CLIs officiels pour tout ce qui a un générateur (Nuxt, modules Nuxt, uv, alembic, OpenAPI client). Écrire à la main **uniquement** : le code métier (modules domaine, agents, adapters) et la **réorganisation** vers la structure ci-dessus. Dernières versions, toujours ; versions résolues consignées. Jamais de squelette réinventé de mémoire.
