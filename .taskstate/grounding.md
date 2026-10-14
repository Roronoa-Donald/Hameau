# Grounding — Remplacement des Points par des Personnages 2D

## Données Réelles Disponibles (Source de Vérité)
- **Localisation des Données** :
  - `viewer/app.js` : état de simulation rejoué dans `this.agentsState` (12 agents canoniques).
  - Propriétés d'agent par tick :
    - `id`, `name`, `role`, `location`
    - `currentAction` (ex: "Effectuer sa tâche : se reposer chez soi", "Aller sur la place du marché")
    - `isTalking` (booléen)
    - `believedFacts` : dictionnaire des croyances (`R1_fermeture_marche`, `R2_dementi_maire`, `R3_ouverture_marche`)
    - `didStock` (booléen)
    - `energy`, `social`, `hunger` (nombres 0-100)
    - `lastReplica` (texte généré par Bedrock)
    - `confidenceZone` (vert / orange / rouge issu des décisions D1-D8)
  - Géométrie des lieux : `VILLAGE_LOCATIONS` (12 nœuds avec coordonnées normalisées `x, y` et icône).
  - Routes : `VILLAGE_ROADS` (arêtes du graphe).

## Chemins de Vérification par Critère DoD
1. **P0 Baseline** : Mesures réelles de FPS dans Chrome headless via CDP, captures d'écran avant (1x, 2x, 400%).
2. **P1 Art Bible & Contact Sheet** : `viewer/dev/characters.html` servi localement et inspecté dans le navigateur.
3. **P2/P3 Tranches S1-S9** : Tests unitaires de rendu procédural, placement déterministe, et tests visuels sans collision.
4. **P4 Vérification globale** : `scripts/verify.sh` doit sortir en code 0 à chaque jalon.
