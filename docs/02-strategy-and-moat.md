# 02 — Stratégie & moat

## Le moat (défendabilité) — précis
Le moat n'est **PAS** le contenu des idées (commodité : les LLM génèrent des idées à volonté ; Reddit/LinkedIn/Product Hunt ont déjà le contenu public). Le moat est un **data network effect sur la MÉMOIRE ORGANISATIONNELLE** :
1. les **Learnings confirmés avec provenance** — la boucle Décision → Expérience → Outcome → Learning → Décision future ; chaque Learning réutilisé par un autre Decision Space rend le suivant meilleur ;
2. le **graphe de relations explicite** (SUPPORTS, CONTRADICTS, DUPLICATES, ALTERNATIVE_TO, DERIVED_FROM, SUPERSEDES, EVIDENCE_FOR, EVIDENCE_AGAINST) — stocké explicitement, pas seulement dans des embeddings ; les corrections humaines deviennent des données durables qui améliorent la convergence ;
3. la **boucle du Memory Retriever** — chaque nouvelle Décision fait remonter les leçons passées pertinentes en expliquant POURQUOI elles sont pertinentes, avec provenance.

## Les 4 conditions (sinon le moat est fictif)
1. C'est un **flux** généré par l'usage (Décisions, Outcomes, Learnings réels — pas un stock scrapé/acheté).
2. **Non observable ailleurs** (Decision Spaces privés, permissions first-class — pas du texte public).
3. L'usage **améliore structurellement** le produit (la récupération mémoire et la convergence s'améliorent avec les Learnings confirmés — pas un LLM générique qui donne déjà 80 % sans lui).
4. **Rattrapage impossible en un trimestre** par un concurrent bien financé (il démarre avec zéro Learning confirmé, zéro graphe de relations, zéro historique de corrections).

## L'insight qui décide de la faisabilité
La vitesse du moat = la vitesse à laquelle les **résultats reviennent**. Pas d'Outcome = pas de Learning = pas de réutilisation. Les paris à résultats de 2–5 ans ne produisent jamais de Learning réutilisable. **Donc cibler un domaine à boucle rapide** (décisions testées en jours : contenu/marketing/growth/features). C'est structurant pour le choix du premier segment.

## Go-to-market : B2B-first en PLG
- Le B2C pur (réseau d'idées grand public) : cold-start massif + monétisation faible + animation de communauté intensive → haute variance, long.
- **B2B en product-led growth** = la bonne entrée : un individu l'utilise seul (valeur single-player via l'IA), invite son équipe, l'équipe passe au payant. **Revenu jour 1, pas de cold-start (l'équipe est un groupe déjà constitué), moat qui s'accumule par organisation.** On vend par le produit, pas par du démarchage.
- Le B2C "cerveau collectif de l'humanité" = l'expansion, débloquée une fois le moteur rôdé.

## Tension à connaître
Les moats défendables demandent un minimum de go-to-market / distribution. Le PLG minimise le démarchage à froid mais ne l'annule pas. Option : un associé côté commercial pour la distribution pendant que la tech se construit.

## Anti-patterns (ce que Kollio n'est PAS)
- Pas un **réseau social d'idées** générique (cimetière : Quirky, CoFoundersLab, idea marketplaces) — la valeur est dans le flux privé + l'exécution, pas le partage.
- Pas un **validateur d'idées one-shot** (DimeADozen, ValidatorAI…) — sherlockable, sans rétention. La rétention vient de l'itération continue + l'équipe + la mémoire.
- Pas un **moteur de scoring** (scores universels, vanity metrics) — un score sans Outcome vérifiable n'est pas une donnée, c'est du décor. Les Outcomes priment sur les vanity scores.
- Pas la **couche investisseurs** en V1 (régulée).
