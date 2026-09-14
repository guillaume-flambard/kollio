# 03 — Architecture back-end / agentique

## Point de départ (à migrer, pas jeter)
Existant : Python + Langfuse + SQLite, sur **VPS Netcup**. Bon réflexe : Langfuse. Fragilités à corriger : **SQLite** (un seul writer → `database is locked` en agentique), **pas de couche de durabilité**, instrumentation à basculer en **OpenTelemetry**.

## Schéma cible
```
Client ──SSE──> FastAPI (Docker)
   ├─ LangGraph            ← agents (graphes d'états, HITL) + checkpointer Postgres
   ├─ Postgres            ← relationnel + pgvector + mémoire agent (+ état LangGraph)
   ├─ Redis              ← cache + rate-limit + pub/sub + broker
   ├─ Taskiq worker       ← jobs LLM longs / RAG / outils (async, colle à FastAPI)
   └─ LiteLLM (gateway)   ← fallback multi-fournisseurs, budgets par clé, cache
Observabilité : Langfuse (garder, v4 = backend OTel-natif) — instrumenter en OpenTelemetry, PAS en API vendor
Eval : DeepEval en CI (gates de régression) + online evals Langfuse (LLM-as-judge CALIBRÉ)
Sécurité : validation Pydantic stricte · secrets env plateforme · plafonds $ par clé gateway · sandbox UNIQUEMENT si exécution de code
```

## Décisions clés
- **Framework d'agent : LangGraph** (choisi). Workflows = vrais graphes d'états avec human-in-the-loop (validation d'itérations). Persistance via **checkpointer Postgres** de LangGraph — commencer par là. **Ne PAS empiler DBOS** tant que la durabilité du graphe suffit ; ajouter DBOS seulement si besoin de durabilité au-delà du graphe (jobs métier non-agent).
- **Postgres** (une seule base) : relationnel + **pgvector** (matching sémantique = le moat) + mémoire agent + état LangGraph. Migration SQLite→Postgres = priorité 1 (`pgloader` + Alembic, ~½ journée).
- **pgvector** (avec pgvectorscale) tient jusqu'à ~50 M vecteurs. **Qdrant** seulement si scale/latence p99 critique plus tard. **Embeddings multilingues obligatoires** (voir `07-i18n.md`).
- **Mémoire agent = tables Postgres** (conversations, résumés glissants, faits en vecteurs). Mem0/Zep/Letta = seulement après un besoin mesuré.
- **File : Taskiq** (async natif, Redis, intégration FastAPI). Pas Celery. ARQ a été remplacé après son passage officiel en maintenance seule.
- **Streaming : SSE** (token-stream) ; WebSockets seulement pour le vrai bidirectionnel (interrompre un agent). Redis pub/sub découple worker↔endpoint.
- **Gateway : LiteLLM** self-host (1 conteneur sur le VPS, zéro markup, budgets par clé). OpenRouter acceptable pour un tout premier jet.
- **Routage par classe de tâche** (`src/platform/task_class.py`) : chaque appel passerelle déclare une `TaskClass` nommée ; la classe résout le modèle via la config (`LLM_MODEL` = intelligence marchandise : extraction, classification, résumé, embeddings, traduction, routage, petits contrôles ; `LLM_MODEL_VISIBLE` = intelligence visible, le raisonnement qu'un membre lit : challenge, contradiction, raisonnement sur les contraintes, comparaison, recommandation, apprentissage, explication). Le routage est un choix de configuration, pas des noms de modèle devinés aux points d'appel. `LLM_MODEL_VISIBLE` vide retombe sur `LLM_MODEL` : dev et CI font tourner tout le graphe sans credentials premium, et les fixtures enregistrées évitent les appels live. La classe et le modèle sont posés en attributs de span OTel (`kollio.task.class`, `gen_ai.request.model`) ; le coût par modèle reste porté par LiteLLM/Langfuse.
- **Observabilité : Langfuse**, instrumenté en **OpenTelemetry** (portabilité, pas de lock-in ; conventions GenAI encore expérimentales → pinner les versions, ne pas inventer d'attributs `gen_ai.*`).
- **Idempotence** : clés `(workflow_id, step_id)` sur tout tool-call à effet de bord.

## Déploiement (adapté au VPS Netcup)
- **Conteneuriser** (Dockerfile multi-stage). Tout tourne sur le **VPS Netcup existant** via **Make/Ansible + Compose/Traefik** (déploiement piloté par Make/Ansible, routage TLS via Traefik) → le plus économique et tu gardes le contrôle.
- Postgres + Redis : self-host sur le VPS via Make/Ansible (avec **backups + PITR** configurés) ; ou managés (Neon/Upstash) si tu préfères externaliser la sauvegarde.
- **CI : GitHub Actions** — ruff + pytest + build image + déploiement auto sur push `main` ; migrations Alembic dans le pipeline.
- **Démarrage sur sous-domaine** : Kollio est d'abord servi sur un **sous-domaine du domaine existant** (`kollio.<domaine>` ou `app.<domaine>`) — pas de nouveau domaine requis au départ ; bascule vers le domaine propre quand il sera acquis.

## Migration (ordre de ROI)
1. SQLite → Postgres + Alembic.
2. Enrober la logique d'agent existante en graphes LangGraph propres (+ checkpointer Postgres).
3. Basculer l'instrumentation en OTel ; durcir idempotence + structured outputs.
4. Ajouter gateway LiteLLM, worker Taskiq, DeepEval en CI, online evals Langfuse.

## À éviter (over-engineering solo)
Kubernetes · Kafka/microservices < ~50 req/min · base vectorielle dédiée jour 1 · framework mémoire prématuré · Celery+RabbitMQ · Temporal (piège d'ops solo — pas avant multi-service/fan-out massif) · sandbox microVM si pas d'exécution de code arbitraire.
