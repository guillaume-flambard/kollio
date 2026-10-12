# R1 — Arbitrages de design à résoudre, pas à masquer

**Statut : ouvert, arbitrage humain indispensable avant changement de composants.**

## Découverte pendant R0

La copie locale Mac, à `/Users/memo/projects/kollio-mac`, est en HEAD détachée `e8d24c9` avec des modifications de travail. Elle possède un `docs/product-pack/P13_VISUAL_LANGUAGE_V3.md` **plus récent que le `main` distant**. Ce document n'a **pas** été publié dans le dépôt GitHub que cette PR référence ; ne pas écraser, citer comme source distante ou importer silencieusement ce travail local.

Le document local approfondit le principe **Paper / Ink / Branch / Glass** : canvas comme application, très peu de chrome à l'état de repos, contrôles éphémères, gestes près de l'objet. Il entre en tension avec le modèle de navigation Web à sections fixes et avec le wireframe initial à sidebar/inspecteur permanents.

**Conséquence :** le board visuel initial produit pendant le cadrage est une *hypothèse A*, pas une maquette V3 approuvée. Ce n'est ni une capture ni une décision d'abandonner l'UX Mac.

## Deux directions à tester côte à côte

| Décision | A — Shell structuré | B — Document-first, chrome contextuel |
|---|---|---|
| Accueil | zones de navigation toujours visibles | page d'entrée structurée puis espace épuré |
| Dans un espace | sidebar, modes et inspecteur visibles | surface pleine, commandes/panneaux sur demande |
| Forces | découverte, collaboration, familiarité Web | attention sur le travail, cohérence du Mac existant |
| Risques | interface générique qui écrase le canvas | fonctions difficiles à découvrir |
| Mac | risque de renier Paper/Ink/Branch/Glass | proche du concept local actuel |
| Web | proche de la structure actuelle | refonte plus profonde, besoin de repères clairs |

**Hypothèse préférée pour expérimentation : B**, avec raccourcis et navigation explicitement accessibles, et un accueil structuré commun. Pas de sidebar permanente imposée au canvas Mac ou Web.

## Invariants à valider dans les deux directions

- La même information est lisible sous les vues Document / Canvas / Comparer.
- Les objets sélectionnés, preuves, propositions et décisions ont les mêmes statuts visibles.
- Les actions importantes ont un chemin clavier, souris et accès assistif, sans dépendre du survol.
- Un nouvel utilisateur trouve comment revenir à ses espaces sans deviner un geste caché.
- Réduire le chrome ne supprime pas le contexte des erreurs, des sources ou des permissions.
- Le même écran au repos ne doit pas afficher deux produits visuellement opposés.

## Protocole de décision R1

1. Capturer les deux runtimes actuels ; préserver provenance et SHA.
2. Maquetter **la même scène** en A et B, sur Web et Mac, au moins pour un espace ouvert et une proposition en attente.
3. Tester : créer, retrouver un objet, changer de vue, consulter une preuve, refuser une proposition, revenir aux espaces.
4. Comparer réussite/erreurs et préférence esthétique séparément.
5. Choisir une direction et **modifier alors seulement** les tokens et le shell des deux applications.

## État des captures historiques Mac retrouvées (12/10/2026)

Trois exemples ont été ouverts/inspectés par accès read-only via SentinelX :
- `build/kollio-presentation.png` : document spatial avec branches et mode de lecture ;
- `build/kollio-comparison.png` : deux directions contenues dans un cadre de comparaison ;
- `build/inspect-2-new.png` : fenêtre d'entrée Kollio devant un environnement de développement.

Ce sont des captures **historiques présentes sur disque**, pas des captures de l'application réexécutée aujourd'hui ; certaines montrent d'autres fenêtres. Ne pas les publier telles quelles dans une PR publique. Elles sont absentes des assets versionnés du dépôt distant.

Aucun service Web n'écoute actuellement sur les ports de développement locaux 3000 et 8000 de ce Mac selon les vérifications effectuées. Cela ne préjuge pas d'un déploiement distant.

Les tests applicatifs n'ont pas été relancés dans ce chantier. La CI de documentation Web est passée ; aucun workflow CI n'a été trouvé pour la branche compagnon Mac.

## Risques hors champ pour le moment

- Nommage `V3` déjà utilisé par un document local Mac : réserver le terme **Unified Kollio V3** au contrat multi-plateforme une fois son adoption décidée.
- Travail Mac local non fusionné : aucune commande de reset/checkout sur cette copie.
- Une capture historique ou un rendu génératif ne démontre pas la parité d'une fonctionnalité.
