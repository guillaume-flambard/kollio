# Roadmap de réconciliation — R0 à R5

## Cadence

Une seule roadmap produit, deux plans d'implémentation et des revues visuelles simultanées. Ne jamais considérer « présent en code » comme « parité démontrée ».

| Phase | Livrables | Sortie mesurable |
|---|---|---|
| R0 — Baseline | inventaire des deux repos, scripts de capture fiables, 5 scènes par client | captures runtime authentiques annotées |
| R1 — Vision visible | north star, tokens candidats, 5 scènes × 2 clients | comparaison approuvée après revue humaine |
| R2 — Contrats | `Space`, `Artifact`, `View`, `Proposal`, `Evidence`, codec et fixtures | round-trip Web ⇄ Mac et refus des versions inconnues |
| R3 — Parcours commun | accueil + création + inspecteur + validation sur les deux clients | scénario identique testé sur données partagées |
| R4 — Vues adaptatives | Document / Canvas / Comparer sur les mêmes ids | pas de perte ou duplication au changement de vue |
| R5 — Capacités externes | import résultats harness et raccord Drop optionnel | permissions, preuve et dégradation sans connexion |

## Réutilisation différenciée

**Mac — garder** : `KollioCore` (objets, commandes, transactions), `DocumentCodec`, `ProposalValidator`, `SourceLedger`, canvas et adaptateurs d'inférence. **Revoir** : shell/navigation, découpage `KollioModel.swift`, accessibilité clavier, performance, capture fiable. **Geler** : collaboration/commerce/public SDK/Apple system integration hors tranche R3.

**Web — garder** : modèles de décisions, convergence, expériences/outcomes/learnings, workspace/auth, API et couche de provenance. **Revoir** : home, six sections obligatoires, composants de navigation, contrat des vues, UI kits selon la direction retenue. **Geler** : réseau public d'idées, fonctionnalités investisseurs et orchestration dupliquée.

## Actions P0 (sans toucher aux fonctionnalités)

1. Accepter la vision et fixer les SHA de base.
2. Recueillir 5 vraies captures Web et Mac ; corriger la capture Mac au niveau de fenêtre.
3. Répertorier les objets et migrations réelles avant création d'un schéma commun.
4. Dessiner le même scénario sur les deux plateformes ; tenir un registre `identique / équivalent natif / spécifique`.
5. Faire valider visuellement R1 avant de porter les tokens dans les codes existants.

## Risques à contrôler

- **Big bang** : ne pas réécrire les deux clients en parallèle avant une verticale validée.
- **Perte de données** : migrateurs testés sur copies ; jamais de remplacement silencieux.
- **Divergence silencieuse** : checks de tokens, fixtures partagées, revue de capture par PR.
- **Faux dynamisme** : vues déclaratives d'abord ; pas de code généré arbitraire.
- **Confusion runtime** : simulation, tests mockés, inférence locale réelle et modèle distant sont étiquetés.
- **Couplage d'écosystème** : Kollio doit fonctionner sans Drop ni harness.

## Tableau de pilotage initial

| Scène / capacité | Web actuel | Mac actuel | V3 |
|---|---|---|---|
| Créer depuis du texte | Parcours différent | Présent | À concevoir |
| Ouvrir un espace | Decision Space | Document local | À concevoir |
| Sources et preuves | Dans contributions | SourceLedger | À unifier |
| Examiner proposition | Workflow métier | Diff/ghost branch | À unifier |
| Décider | Decision Record | Décision document | À unifier |
| Changer Document/Canvas/Comparer | Non unifié | Canvas dominant | À construire |
| Reprise durable | Backend Postgres | Fichier `.kollio` | Contrat à définir |
| Interopérabilité | API HTTP | JSON `.kollio` | Non prouvée |

Ce tableau constitue une baseline de travail et non une validation finale des capacités.
