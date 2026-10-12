# R0–R1 — Workspace local unifié et prototype visuel

**État : structure locale mise en place, prototype visuel de test, PAS monorepo unique ni UI V3 intégrée.**

## Agencement

```text
kollio-v3/
  apps/web/     Git worktree du dépôt kollio (branche feat/kollio-v3-web)
  apps/mac/     Git worktree du dépôt kollio-mac (branche feat/kollio-v3-mac)
  shared/
    tokens.json
    generated/tokens.css
    generated/KollioTokens.swift
  design/prototype/
    index.html  — aperçu conceptuel interactif Web/Mac
    styles.css
    app.js
  docs/
    VISION.md
    COMPONENTS.md
    DELIVERY.md
  scripts/
    generate-tokens.mjs
    check-v3.mjs
```

Ce workspace constitue une **troisième racine Git locale pour les assets de conception uniquement**, excluant `apps/` de son suivi Git. Commit de bootstrap local `62d50ae`. Aucune création de dépôt GitHub supplémentaire, aucun déplacement/destruction des repos existants.

Les deux worktrees disposent d'histoires séparées :
- Web : point de départ du travail local `d7ea2ef9cbe0`.
- Mac : point de départ du travail local `e8d24c976605`, plus récent que `main` GitHub.

La copie Mac originale présente des modifications non commitées et un HEAD détaché : elle a été laissée intacte. Ces modifications **ne figurent pas** dans le worktree V3.

## Aperçu visuel

Le prototype V3 est un fichier HTML local consultable dans Safari, sans dépendance à un framework de composants. Il propose cinq scènes avec **une même donnée simulée** : création, document, canvas, comparaison, décisions/historique. Un contrôle bascule Web ↔ Mac ; les différences restent limitées aux indices de plateforme. Des actions d'acceptation/rejet simulées font évoluer l'état en mémoire.

### Qualité et limites

- `node --check design/prototype/app.js` : réussi.
- `node scripts/generate-tokens.mjs --check` : réussi.
- `node scripts/check-v3.mjs` : réussi.
- **Ni UI test navigateur, ni vraie synchronisation, ni backend agentique n'ont été validés.**
- Les fichiers Swift/CSS générés ne sont pas encore importés par les applications réelles.
- Les cinq maquettes validées Web/Mac et les vraies captures runtime R0 sont encore à faire.

## Décisions demandées pour R1

1. Valider / modifier **document-first avec contrôles contextuels**, plutôt que des panneaux permanents.
2. Choisir les états et comportements canoniques de `AppFrame`, `HomeStart`, `ViewSwitcher`, `ProposalPreview`, `DecisionRecord`, etc.
3. Confirmer le principe : **un espace/état canonique et trois vues (Document/Canvas/Comparer)**.
4. Choisir, après validation, si la V3 doit être hébergée dans un seul monorepo Git ou garder temporairement ce workspace de worktrees.

Le dossier de design existe sur le Mac ; il n'est pas encore publié sur une branche GitHub commune. Il serait incorrect de prétendre que les deux applications implémentent le nouveau shell.
