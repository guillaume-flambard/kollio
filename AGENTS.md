# AGENTS.md — instructions pour les agents de code

Tu construis **Kollio**. Lis les docs dans `docs/` (ordre dans `README.md`) et traite-les comme la source de vérité. En cas de contradiction avec une habitude par défaut, ce sont ces docs qui gagnent.

## En une phrase
Un "GitHub des idées" collaboratif : dépôt d'idée → tueur de contraintes (IA) → itérations façon commits → l'équipe se forme. Le moat = le **flux privé** (qui-résout-quoi-avec-qui + résultats), pas le contenu des idées.

## Non-négociables (à respecter dès la première ligne)
1. **Multilingue FR/EN dès le départ.** `@nuxtjs/i18n` côté front, tout texte en clé de traduction. **Embeddings multilingues** pour le matching (une idée FR doit matcher un profil EN). Contenu utilisateur stocké avec sa langue d'origine, traduit à la lecture. Agents répondent dans la locale de l'utilisateur. Voir `docs/07-i18n.md`.
2. **Agents : LangGraph** (graphes d'états, HITL). Persistance via checkpointer Postgres. Voir `docs/03-architecture.md`.
3. **Modular monolith en tranches verticales** (un module par domaine), **couture hexagonale légère** autour de la DB / la gateway LLM / les agents. **PAS** de clean-archi 4 couches partout, **PAS** de mappers partout. DDD tactique réservé au cœur (itérations, matching). Voir `docs/08-conventions-and-testing.md`.
4. **TDD sur le domaine déterministe** (itérations/commits, permissions, scoring, matching). **Eval-driven** (DeepEval + fixtures enregistrées + structured outputs Pydantic) sur la couche agent — on ne unit-teste pas la sortie LLM.
5. **Postgres, pas SQLite.** Une base : relationnel + pgvector + mémoire agent. Migrer l'existant.
6. **Structured outputs Pydantic** partout à la frontière LLM ; **idempotence** (`workflow_id + step_id`) sur tout tool-call à effet de bord.
7. **Observabilité dès le jour 1** : Langfuse (garder), instrumenter en **OpenTelemetry** (pas en API vendor).

## Initialisation — scaffolder, ne PAS réinventer (IMPÉRATIF)
- **Initialise le projet avec les CLIs officiels au terminal** (`npx nuxi@latest init`, `nuxi module add`, `uv init`, `uv add`, `alembic init`). **Ne génère PAS de squelettes de fichiers à la main / de mémoire.** N'invente pas la roue : lance les générateurs officiels, PUIS réorganise le résultat dans la structure définie (`docs/08`).
- **Toujours les DERNIÈRES versions stables.** Utilise `@latest` / laisse les CLIs résoudre ; ne hardcode pas de numéros de version (ils seront périmés). Après install, **relève les versions résolues** (lockfiles) et consigne-les.
- Commandes détaillées et ordre exact : **`docs/10-project-init.md`** — à suivre avant d'écrire du code.

## À NE PAS faire (over-engineering)
Remplacer ou réinterpréter la direction visuelle **Living Canvas** (`docs/06-design-system.md`) : on l'étend, on ne la remplace pas. Tokens canoniques de `packages/ui/src/tokens.css` uniquement, aucun hex littéral, aucun nom de variable inexistant dans les pages.
Kubernetes · Kafka/microservices tant que < ~50 req/min · base vectorielle dédiée jour 1 (pgvector d'abord) · framework de mémoire (Mem0/Zep) prématuré · Celery+RabbitMQ (utiliser Taskiq avec Redis) · empiler plusieurs frameworks d'agents · sandbox microVM si les agents n'exécutent pas de code arbitraire · la couche investisseurs (régulée — hors V1).

## Périmètre V1
Dépôt d'idée · tueur de contraintes · itération façon GitHub · formation d'équipe · explorer. **Hors V1 :** couche investisseurs. Cible d'attaque : **B2B-first en PLG** (espace d'équipe privé), le public/B2C étant l'expansion. Voir `docs/02-strategy-and-moat.md` et `docs/09-roadmap.md`.

## Implementation language
All code, identifiers, comments and docstrings must be in English. Localized user-facing text belongs in FR/EN translation catalogs. Preserve original field names only at legacy data boundaries.


## Delivery contract

Follow `docs/12-delivery-workflow.md` for every product change. Start with observable
OpenSpec scenarios, define boundary contracts, and deliver one complete behavior
per slice. Link scenarios to evidence in the change's `acceptance.md`. Read relevant
ADRs in `docs/decisions/`. Run the applicable checks before claiming completion;
record simulated boundaries and unfinished acceptance criteria explicitly.

## Agent skills

### Issue tracker

Issues and specs are tracked in GitHub Issues for `guillaume-flambard/kollio`. See `docs/agents/issue-tracker.md`.

### Triage labels

Use the default Matt Pocock triage labels. See `docs/agents/triage-labels.md`.

### Domain docs

Use a multi-context layout for the API, web app, API client, and UI package. See `docs/agents/domain.md`.
