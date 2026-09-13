# 08 — Conventions, monorepo & tests

## Monorepo
```
workshop/
  apps/
    api/                     # FastAPI — couche HTTP mince
      src/
        modules/             # TRANCHES VERTICALES (un module par domaine)
          ideas/
            domain/          # logique pure, sans framework — TDD ici
            service/         # cas d'usage (application)
            adapters/        # repo Postgres, etc. (couture hexagonale)
            api/             # routes FastAPI du module
          iterations/  matching/  teams/  users/
        agents/              # graphes LangGraph + tools — EVAL ici (locale en param)
        platform/            # gateway LLM (LiteLLM), langfuse/OTel, redis, config, db
      tests/
      alembic/
    web/                     # Nuxt + Nuxt UI + @nuxtjs/i18n
    # mobile/                # plus tard (Capacitor/Ionic Vue ou natif)
  packages/
    api-client/              # généré depuis l'OpenAPI → web (+ mobile)
    ui/                      # thème/design system Nuxt UI
  contracts/                 # schémas partagés / OpenAPI
  openspec/                  # spécifications OpenSpec
```
Outils : **uv workspaces** (Python) + **pnpm workspaces** (JS). Pas de Nx/Turborepo.

## Architecture (rappel)
- **Modular monolith en tranches verticales.** Un module = un domaine, autonome.
- **Couture hexagonale légère** seulement autour de l'externe qui bouge : DB, gateway LLM, agents (interfaces + implémentations → mockables en test, swappables).
- **DDD tactique (agrégats, value objects) uniquement au cœur** : `iterations` (commit/branch/rollback) et `matching`. Modules CRUD = simples, pas de cérémonie.
- **PAS** de clean-archi 4 couches partout, **PAS** de mappers systématiques.

## Tests
- **TDD sur le domaine déterministe** : modèle d'itérations (commit/branch/rollback), permissions, règles de scoring, logique de matching. C'est là que le TDD paie.
- **Eval-driven sur les agents** (pas de unit-test de sortie LLM) :
  - **DeepEval** en CI (`assert_test`, gates de régression sur PR) ;
  - **fixtures enregistrées** (style VCR) pour les appels LLM déterministes en test ;
  - **structured outputs Pydantic** validés à la frontière → le bord agent devient testable ;
  - **online evals** Langfuse (LLM-as-judge **calibré** vs 30–50 annotations humaines, mesurer FP/FN) sur échantillon de trafic ; boucle traces bas-score → dataset.
- **Idempotence** : clés `(workflow_id, step_id)` sur tout tool-call à effet de bord (testées).

## Qualité / CI
- **ruff** (lint+format), **pytest**, **mypy** (au moins sur `domain/`).
- **GitHub Actions** : lint → tests → build image → deploy (Make/Ansible sur Netcup) ; migrations Alembic dans le déploiement.
- Commits conventionnels ; PR petites ; specs OpenSpec tenues à jour.

## Frontière LLM (rappel non négociable)
Tout ce que renvoie un LLM passe par un schéma Pydantic avant exécution. Locale toujours dans l'état du graphe. Secrets jamais dans le contexte d'un agent (moindre privilège des outils = 1re défense anti-injection).

## Delivery and browser acceptance

Use [the delivery workflow](12-delivery-workflow.md) to connect these conventions
to OpenSpec scenarios, acceptance evidence and ADRs. `pnpm test:ui` runs component
tests; `pnpm test:browser` runs the browser acceptance suite. Both are required by
`make verify` and CI. The initial browser fixture simulates API responses and is
not evidence of real authentication or backend isolation.
