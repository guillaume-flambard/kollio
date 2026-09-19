# 09 — Roadmap

## Phase 0 — Fondations (livrée)

- Monorepo (uv + pnpm) ; Nuxt + Nuxt UI + **@nuxtjs/i18n (FR/EN)**, porté par le design system Living Canvas.
- **Postgres** (+ pgvector) et migrations Alembic ; plus de SQLite.
- FastAPI en tranches verticales, DDD tactique réservé aux itérations et au matching.
- Couche agents LangGraph (checkpointer Postgres, locale dans l'état du graphe) ; LiteLLM comme gateway ; traces Langfuse en OpenTelemetry.
- CI GitHub Actions (lint, types, tests, dérive de contrat, build) et déploiement Make/Ansible.

## Phase 1 — La boucle de décision (livrée, en validation)

Le produit tient en **trois moments visibles** : cadrer la décision, choisir avec ses raisons, enregistrer ce qui s'est passé.

- **Espaces de décision** : question, propriétaire, participants, statut, échéance ; cycle `OPEN → EXPLORING → CONVERGING → READY_TO_DECIDE → DECIDED → TESTING → LEARNED`, réouverture possible, historique versionné.
- **Explorer et converger** : branches d'exploration, promotion d'une contribution avec provenance, carte de convergence construite et corrigée à la main (accords, conflits, alternatives, inconnues, hypothèses fortes peu étayées, doublons).
- **Choisir** : options structurées (proposition, mécanisme, coût, risques, hypothèses critiques, preuves pour et contre), regard critique, décision enregistrée avec raisons, alternatives écartées et déclencheurs de réexamen.
- **Enregistrer** : expérience, résultat observé face à l'attendu, leçon confirmée par un humain, écran d'accueil qui dit ce qui demande attention.
- Cible d'attaque : équipes marketing, growth, produit, innovation et stratégie de 3 à 15 personnes qui utilisent déjà l'IA au quotidien, d'abord dans un espace privé (B2B-first en PLG).
- Capturer dès le départ le **flux du moat** : participation, contribution, décision, résultat (voir `02`).

**Jalon en cours, et le seul qui compte maintenant** : une vraie décision prise par deux personnes avec leurs propres mots, un résultat observé dans les jours qui suivent, puis un retour volontaire pour une seconde décision. Ce jalon ne demande aucune nouvelle intégration ni élargissement de fonctionnalités ; il demande que la boucle livrée soit utilisée sur un vrai cas et observée.

## Phase 2 — Expansion

- Couche **publique / B2C** une fois la boucle privée validée par un usage répété.
- **Récupération sémantique** à l'échelle (embeddings multilingues, faire remonter la leçon passée pertinente dans une nouvelle décision).
- Intégrations et exports (extension navigateur, Slack, Notion, Drive ; Decision Brief, Experiment Brief, Learning Memo).

## Phase 3 — Investisseurs (seulement avec cadre juridique)

- Financer une idée/équipe = **régulation financière** (AMF/SEC). Ne pas y toucher sans conseil juridique.
- Jusque-là : hors V1, et jamais présenté comme disponible.

## Fil rouge

Chaque phase : bâtir du solide sans sur-ingénierie ; ajouter une brique quand une métrique le réclame. Le nord = **accumuler le flux privé** (qui-résout-quoi-avec-qui + résultats) qui, seul, constitue le moat.
