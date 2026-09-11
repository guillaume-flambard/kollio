# 09 — Roadmap

## Phase 0 — Fondations (solidifier, ne pas repartir de zéro)
- Monorepo (uv + pnpm) ; scaffold Nuxt + Nuxt UI + **@nuxtjs/i18n (FR/EN)**.
- **Migrer SQLite → Postgres** (+ pgvector, Alembic).
- Auth managée ; squelette FastAPI en tranches verticales ; module `ideas` en DDD-lite + tests.
- Couche `agents` LangGraph (+ checkpointer Postgres, locale en param) ; Langfuse en OTel ; LiteLLM gateway.
- Design system → thème Nuxt UI. CI GitHub Actions → déploiement Make/Ansible sur Netcup.

## Phase 1 — V1 (B2B-first, PLG)
Le produit minimal qui a de la valeur seul et démarre le flux :
- **Déposer une idée** + **tueur de contraintes** en direct (valeur single-player IA).
- **Itérer façon GitHub** (commits/branches/propositions/rollback).
- **Formation d'équipe** (rejoindre la boucle, rôles).
- **Explorer** (feed filtrable) — d'abord dans un **workspace privé** (B2B).
- Modèle **par siège**, self-serve (un user seul → invite son équipe → payant).
- **Cibler un segment à boucle rapide** (marketing/growth/contenu/produit) pour que le flux/outcomes se remplissent vite.
- Capturer dès le départ le **flux du moat** : IdeaMembership, Contribution, Outcome (voir `05`).

## Phase 2 — Expansion
- Couche **publique / B2C** (cerveau collectif ouvert) une fois le moteur rôdé.
- **Matching** à l'échelle (embeddings multilingues, recommandation idées↔personnes qui s'améliore avec le flux).
- Visibilité/distribution des idées.

## Phase 3 — Investisseurs (seulement avec cadre juridique)
- Financer une idée/équipe = **régulation financière** (AMF/SEC). Ne pas y toucher sans conseil juridique.
- Jusque-là : montré **verrouillé** ("plus tard") dans l'UI.

## Fil rouge
Chaque phase : bâtir du solide sans sur-ingénierie ; ajouter une brique quand une métrique le réclame. Le nord = **accumuler le flux privé** (qui-résout-quoi-avec-qui + résultats) qui, seul, constitue le moat.
