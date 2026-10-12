/* GENERATED — scripts/generate-spatial.mjs. Do not edit by hand. */
export interface SpatialV3Node {
  id: string
  kind: "mission" | "idea" | "goal" | "source" | "proposal" | "question" | "decision"
  label: string
  eyebrow: string
  detail: string
  status: string
  depth: 1 | 2
  x: number
  y: number
}
export interface SpatialV3Edge {
  id: string
  source: string
  target: string
  type: string
  label: string
  depth: 1 | 2
}
export interface SpatialV3Fixture {
  schemaVersion: 1
  id: string
  title: string
  subtitle: string
  description: string
  nodes: SpatialV3Node[]
  edges: SpatialV3Edge[]
}
export const spatialV3Fixture: SpatialV3Fixture = {
  "schemaVersion": 1,
  "id": "kollio-spatial-intro-v1",
  "title": "Lancement produit",
  "subtitle": "Explorer les options avant de décider",
  "description": "Préparer le lancement sans perdre les décisions ni les preuves.",
  "nodes": [
    {
      "id": "mission",
      "kind": "mission",
      "label": "Lancement produit",
      "eyebrow": "CONTEXTE CENTRAL",
      "detail": "Notre intention durable et le point de départ du raisonnement.",
      "status": "saved",
      "depth": 1,
      "x": 0.5,
      "y": 0.54
    },
    {
      "id": "context",
      "kind": "idea",
      "label": "Comprendre le besoin",
      "eyebrow": "CONTEXTE",
      "detail": "Les hypothèses et deux références associées à la situation.",
      "status": "saved",
      "depth": 1,
      "x": 0.22,
      "y": 0.25
    },
    {
      "id": "goal",
      "kind": "goal",
      "label": "Choisir une direction claire",
      "eyebrow": "OBJECTIF",
      "detail": "Définir le résultat souhaité sans créer une action exécutable.",
      "status": "saved",
      "depth": 1,
      "x": 0.78,
      "y": 0.25
    },
    {
      "id": "evidence",
      "kind": "source",
      "label": "Étude de marché",
      "eyebrow": "SOURCE",
      "detail": "Référence présente mais non vérifiée par un humain.",
      "status": "unverified",
      "depth": 2,
      "x": 0.2,
      "y": 0.77
    },
    {
      "id": "proposal",
      "kind": "proposal",
      "label": "Lancement progressif",
      "eyebrow": "PROPOSITION",
      "detail": "Modification proposée, sans application automatique.",
      "status": "pending",
      "depth": 2,
      "x": 0.78,
      "y": 0.77
    },
    {
      "id": "question",
      "kind": "question",
      "label": "Que manque-t-il ?",
      "eyebrow": "QUESTION",
      "detail": "Point encore ouvert qui nécessite une exploration.",
      "status": "open",
      "depth": 2,
      "x": 0.84,
      "y": 0.49
    }
  ],
  "edges": [
    {
      "id": "rel-context",
      "source": "mission",
      "target": "context",
      "type": "relates",
      "label": "contexte",
      "depth": 1
    },
    {
      "id": "rel-goal",
      "source": "mission",
      "target": "goal",
      "type": "supports",
      "label": "oriente",
      "depth": 1
    },
    {
      "id": "rel-evidence",
      "source": "mission",
      "target": "evidence",
      "type": "evidence",
      "label": "documente",
      "depth": 2
    },
    {
      "id": "rel-proposal",
      "source": "mission",
      "target": "proposal",
      "type": "proposes",
      "label": "propose",
      "depth": 2
    },
    {
      "id": "rel-question",
      "source": "goal",
      "target": "question",
      "type": "questions",
      "label": "interroge",
      "depth": 2
    }
  ]
}
