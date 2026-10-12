# R1 — Direction visuelle et parité Web/Mac

## État : direction candidate, **non validée par rendu**

**Arbitrage ouvert :** [A (navigation structurée) vs B (canvas-first et contrôles contextuels)](05-design-arbitrations.md). Le wireframe ci-dessous est une hypothèse A, pas un contrat pour imposer des panneaux permanents. La direction B est prioritaire à tester à cause des documents Mac locaux plus récents.

Le Web dispose d'un design `Living Canvas` aubergine/porcelain et de visuels approuvés pour l'ancien produit. Le Mac a `Paper/Ink/Branch`, palette bleu/sauge et interactions spatiales documentées. Aucune identité V3 n'est encore approuvée.

### Direction A à maquetter d'abord

Combiner le calme éditorial de **Paper**, la lisibilité d'**Ink** et le changement explicable de **Branch**, avec la palette claire aubergine/porcelain de l'ancien Web **comme hypothèse**, pas décision irréversible.

Tokens sémantiques *candidats* : `canvas #F7F5F7`, `surface #FFFFFF`, `ink #252229`, `primary #493B57`, `selected #DDD3E8`, `question #D47A70`, `verified #899744`, `pending #A57932`. Le contraste, les états sombres et la compatibilité macOS restent à mesurer.

**Différence autorisée** : contrôles système, menus, raccourcis, scrollbar, typographie de remplacement, tailles tactiles et fenêtres, tant que structure, hiérarchie, contenus, statuts et actions principales concordent.

**Interdit** : deux palettes définies séparément, des badges d'IA décoratifs, des grilles génériques de cartes et des composants visuels qui masquent les permissions ou l'état d'une proposition.

## Cinq scènes à dessiner, côte à côte

| Scène | Contenu obligatoire | États à montrer |
|---|---|---|
| 01 Accueil | identité, reprendre, espaces, zone de création | vierge / récent / erreur |
| 02 Espace Document | navigation, objectif, texte, sources, barre d'intention | normal / sélection / source manquante |
| 03 Espace Canvas | mêmes objets, relations explicites, manipulation | normal / sélection / proposition en attente |
| 04 Comparaison + proposition | 2 options, différences, avant/après, accepter/refuser | non modifié / pending / stale / refus |
| 05 Décision + activité | choix, raison, preuves, événements et retour | décidé / à revoir / historique |

Les **cinq scènes doivent avoir un équivalent Web et Mac** ; une seule maquette V3 ne prouve pas la réconciliation.

## Architecture visible proposée

```text
┌────────────────────────────────────────────────────────────┐
│ Kollio / Mes espaces / Mon espace             Rechercher  │
├──────────────┬───────────────────────────────┬─────────────┤
│ Navigation   │ Document · Canvas · Comparer  │ Inspecteur  │
│ Espace       │                               │ Sources     │
│ Contenu      │     représentation active     │ Proposition │
│ Décisions    │                               │ Historique  │
│ Activité     │                               │             │
│              │ Demander une modification…    │             │
└──────────────┴───────────────────────────────┴─────────────┘
```

Ce wireframe indique la structure, **pas** les pixels finaux.

## Contrat composants

Chaque primitive possède : nom et rôles sémantiques, états (idle/hover/focus/disabled/busy/error), hiérarchie typographique, accessibilité, raccourci éventuel, modèle d'interaction clavier, comportement tactile si Web mobile, déclinaison SwiftUI et Vue.

Premières primitives : `AppShell`, `SpaceList`, `SpaceHeader`, `ViewSwitcher`, `ArtifactBlock`, `EvidenceRef`, `ProposalDiff`, `DecisionRecord`, `ActivityLine`, `IntentComposer`.

Ne pas forcer une bibliothèque de composants populaire. Le contrat et les tokens se partagent ; SwiftUI et Vue restent des rendus propres.

## Revue de parité et gate R1

- [ ] 5 maquettes Web + 5 maquettes Mac effectivement produites.
- [ ] Comparaison côte à côte avec les captures R0 authentiques.
- [ ] Deuxième passe : texte long, état vide, erreur et attente.
- [ ] Contrôle contraste, navigation clavier, accessibilité et tailles de texte.
- [ ] Validation humaine explicite du système visuel et du parcours.
- [ ] Seulement alors : codifier des tokens communs et autoriser la migration d'UI.

**Aucune maquette générée n'est une capture produit.**
