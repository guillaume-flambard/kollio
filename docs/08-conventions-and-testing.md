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
  - **Evals comparatives** (`python -m src.platform.benchmark`, #77) : trois bras sur ~10 initiatives réelles — A modèle nu (prompt seul), B modèle visible sans mémoire d'entreprise, C Kollio complet (mémoire + Known/Assumed/Unknown + contradictions). Feuille de notation **aveugle** (positions mélangées par graine, clé séparée), notation sur 7 dimensions (dont `company_knowledge`, `willingness_to_challenge`, `trust` = les différenciateurs). Les appels live sont **opt-in** et gardés par `LiveEvaluationGuard` ; hors flag on rejoue depuis des **sorties enregistrées**, donc la comparaison est reproductible sans fournisseur. Le score final reste humain ; si C ne bat pas clairement A, c'est traité comme un problème produit, pas un accident de notation.
- **Idempotence** : clés `(workflow_id, step_id)` sur tout tool-call à effet de bord (testées).

## Qualité / CI
- **ruff** (lint+format), **pytest**, **mypy** (au moins sur `domain/`).
- **GitHub Actions** : lint → tests → build image → deploy (Make/Ansible sur Netcup) ; migrations Alembic dans le déploiement.
- Commits conventionnels ; PR petites ; specs OpenSpec tenues à jour.

## Frontière LLM (rappel non négociable)
Tout ce que renvoie un LLM passe par un schéma Pydantic avant exécution. Locale toujours dans l'état du graphe. Secrets jamais dans le contexte d'un agent (moindre privilège des outils = 1re défense anti-injection).

## Automated guards

`make verify` (and Foundations CI) run four checks beyond the test suites:

- `node scripts/check_locales.mjs` — the FR and EN catalogs expose the same keys, and every static key used by `apps/web/app` exists in them. A template or concatenated key only needs one catalog entry starting with its static prefix, which proves the family exists without enumerating runtime values.
- `node scripts/check_design_tokens.mjs` — `apps/web/app` contains no literal colour and no `--kollio-*` name absent from `packages/ui/src/tokens.css`. A typo there is invisible in review because the hardcoded fallback wins at runtime, so the check is the only reliable guard. Run it with `--self-test` to prove it still fails on a fixture. `--ui-*` names come from Nuxt UI and are exempt; a variable declared in the same file is treated as local.
- the migration drift check, `uv run alembic check` from `apps/api`.
- `node scripts/check_web_performance_budgets.mjs`: gzips every `.js` and `.css` file emitted under `apps/web/.output/public/_nuxt` and compares the totals and the largest single file against `performance-budgets.json`; images are measured raw. The totals cover every chunk the build emits, lazy route chunks included, so they grow with each new surface and are not a load-time measure; the per-file caps are that guard. Refresh a total only with a measured build and a dated reason, and leave the largest-file caps alone unless the entry payload really moved.
