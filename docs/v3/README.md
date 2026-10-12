# Kollio V3 — Réconciliation produit, UX et technique

Statut : **proposition de référence en revue** (pas encore le produit implémenté). Date : 2026-10-12.

## Source unique de vérité — pendant la transition

Ce dossier contient **la vision produit et les critères de parité de Kollio V3** pour les deux clients :
- Web : [guillaume-flambard/kollio](https://github.com/guillaume-flambard/kollio)
- Mac : [guillaume-flambard/kollio-mac](https://github.com/guillaume-flambard/kollio-mac)

Hébergement temporaire dans le dépôt Web pour éviter la création d'un troisième repository. Cela ne signifie **pas** que la version Web est le produit maître, ni qu'une implémentation doit être portée à l'identique. Le contrat commun fait autorité *uniquement après validation de la vision et des maquettes*.

## Intention

> Un seul Kollio : un espace de travail vivant, où humains et IA construisent et transforment des objets durables ; des représentations interchangeables, des modifications visibles et contrôlées.

**Les données sont durables. Les vues sont adaptables. Les changements sont contrôlés.**

Ce que Kollio n'est pas : un clone de ChatGPT/Claude, un framework d'agents, un gestionnaire de projet générique, un simple tableau blanc, une interface destinée uniquement à surveiller Drop.

## Principes non négociables

1. **Une identité, deux clients** : vocabulaire, structure d'information, statuts, gestes critiques et design sémantique communs ; conventions d'OS natives permises.
2. **Une même expérience de base** : créer un espace, ajouter du contenu et des sources, examiner une proposition, choisir et revenir.
3. **État canonique indépendant des vues** : Document, Canvas, Comparer sont des projections sur les mêmes objets, jamais trois copies autonomes.
4. **IA propose ; utilisateur décide** : pas de mutation silencieuse, preview et validation des opérations ; le travail manuel reste disponible sans modèle.
5. **Aucune dépendance obligatoire à Drop, au harness ou à un fournisseur IA** ; ces systèmes peuvent enrichir les capacités plus tard.
6. **Pas de réécriture technique avant validation visuelle** : conserver les deux branches `main` stables.
7. **Pas de pseudo-preuves** : distinguer code présent, tests rapportés, essais relancés, capture d'écran réelle et usage humain.

## Livrables et ordre

- [01 — Inventaire R0](01-current-state.md) : écart Web/Mac, sources, preuves et captures manquantes.
- [02 — Contrat produit](02-product-contract.md) : modèle commun, navigation, parcours de référence.
- [03 — Parité visuelle](03-visual-parity.md) : design direction, écrans et scénarios à maquetter.
- [04 — Plan de migration](04-migration-plan.md) : phases, critères de sortie, risques et réutilisation.

## Règle de livraison

Toute demande de fonctionnalité V3 indique : modèle / surfaces Web et Mac / état de parité / migration de données / validation déterministe / validation visuelle / accessibilité. L'absence de l'un des clients doit être explicite dans la matrice, pas déguisée en parité.

## Baselines (branches main observées le 12/10/2026)

- Web `a45a5205ce56f4c663be890bd23ba36c978b7d0d` — 02/10/2026.
- Mac `536e7553a4eb6bc2fd3ec0d54102cf4c98ca4897` — 26/09/2026.

Ces SHA figent le diagnostic documentaire ; les futurs tests et captures devront préciser leur propre version.
