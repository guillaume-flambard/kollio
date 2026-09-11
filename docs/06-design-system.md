# 06 — Design system

Inspiration : **Collective.work** (moderne, épuré, whitespace généreux, coins doux, tech-forward). Les tokens ci-dessous se mappent directement sur le thème **Nuxt UI v3** (`app.config.ts` + thème Tailwind v4).

## Maquettes de référence (artefacts publiés)
- Design system + écran principal en 2 directions (claire / sombre) : https://claude.ai/code/artifact/97f8a48d-e314-4342-aacb-5165b5147688
- Maquette concept initiale (GitHub des idées) : https://claude.ai/code/artifact/567235a8-2d00-420f-837b-2e5f05f51b1e

## Typographie
- **Titres/display : Bricolage Grotesque** (600/700/800) — du caractère.
- **Corps/UI : Geist** (400/500/600).
- **Mono : Geist Mono** (hash de commits, métadonnées, slugs).
- Toutes via Google Fonts. Prévoir des fallbacks proches (system-ui).

## Couleurs (light — thème par défaut)
| Rôle | Hex |
|---|---|
| Ink (texte) | `#141310` |
| Fond | `#f6f5f2` |
| Surface | `#ffffff` |
| Bordure | `#e7e4dd` |
| Accent | `#2f4bff` |
| Succès | `#1f9d5b` |
| Attention | `#e0912a` |
| Danger | `#d1495b` |

## Couleurs (dark — alternative dispo)
Fond `#100f0d` · surface `#191815` · bordure `#2a2823` · texte `#f2f0ea` · muted `#98948a` · **accent lime `#c5f24d`** · succès `#57d38a` · danger `#f2647a`.

> Deux directions ont été maquettées : **claire/éditoriale (accent bleu)** = défaut recommandé, et **sombre/tech (accent lime)** = alternative. À trancher ; le DS supporte les deux (tokens qui basculent).

## Primitives
- **Radius** : 8 / 10 / 14 / 20 (pills).
- **Espacement** : 4 · 8 · 14 · 22.
- **Ombre** : `0 1px 2px rgba(20,19,16,.05)`.
- **Statuts** (pills) : Équipe formée (vert), En itération (ambre), Graine (neutre), Cherche : <rôle> (accent).
- **Composants** : boutons (primary/secondary/ghost + tailles), badges/statuts, input/select, cards, avatars + avatar-stack, tabs, graphe de contribution (grille de cellules).

## Règle d'implémentation
Tokens → thème Nuxt UI. Textes = **clés i18n**, pas de texte en dur. Icônes = **SVG inline** stroke-based (jamais d'emoji). Le design system est la source unique ; les composants signature générés par Astra consomment ces tokens.
