# Rapport Baseline — État Initial du Rendu Visuel des Habitants

Ce document dresse l'état des lieux rigoureux du visualiseur HAMEAU avant la refonte visuelle des personnages 2D, avec mesures réelles, analyse du code source et captures d'écran à l'appui.

---

## 1. Localisation du Rendu Actuel dans le Code Source

Dans [`viewer/app.js`](file:///home/rd/hackaton-aws-2/viewer/app.js), le dessin des agents est localisé dans la méthode `renderMap(w, h, ctx)` (lignes 979 à 1026) :

```javascript
// Dessin actuel : simple cercle plein (point coloré)
ctx.beginPath();
ctx.arc(ax, ay, (isSelected ? 14 : 10) * this.dpr, 0, Math.PI * 2);
ctx.fillStyle = hasOpen ? "#10b981" : hasDebunk ? "#06b6d4" : hasRumor ? "#f43f5e" : "#38bdf8";
ctx.fill();

// Bulle d'expression emoji au-dessus
if (a.isTalking) {
  ctx.font = `${14 * this.dpr}px sans-serif`;
  ctx.fillText("💬", ax, ay - 14 * this.dpr);
}

// Nom de l'agent
ctx.font = `700 ${9 * this.dpr}px var(--font-ui)`;
ctx.fillStyle = isSelected ? "#ffffff" : "#94a3b8";
ctx.fillText(a.name, ax, ay - 12 * this.dpr);
```

### Données Disponibles par Agent et par Tick :
- `a.id` : Identifiant canonique (ex: `awa`, `kofi`, `yao`, `claire`).
- `a.name` : Nom complet affiché.
- `a.role` : Métier ou statut civil (ex: `Boulangère`, `Maire du Hameau`).
- `a.location` : Clé du lieu actuel parmi `VILLAGE_LOCATIONS` (ex: `marche`, `boulangerie`).
- `a.currentAction` : Intention en cours issue de D1 (ex: *« Se rendre à son travail »*, *« Faire une pause »*).
- `a.isTalking` : Booléen indiquant si l'agent dialogue à ce tick.
- `a.believedFacts` : Dictionnaire des faits connus et niveau de croyance (`R1_fermeture_marche`, `R2_dementi_maire`, `R3_ouverture_marche`).
- `a.didStock` : Booléen indiquant si l'agent est en comportement de stockage/panique.
- `a.energy`, `a.social`, `a.hunger` : Jauges internes de besoin (0 à 100).
- `a.lastReplica` : Texte de réplique ou dialogue généré en direct par Bedrock.
- `a.confidenceZone` : Zone de confiance Decider (`green`, `orange`, `red`).

---

## 2. Défauts Visuels et Ergonomiques Observés (Preuve par l'Image)

L'inspection de la capture [`docs/visuals/screenshots/before_market_crop_400.png`](file:///home/rd/hackaton-aws-2/docs/visuals/screenshots/before_market_crop_400.png) révèle les défauts critiques suivants :

1. **Représentation schématique par points déshumanisés** : Les habitants sont de simples disques bleus de 10-14 px de rayon, sans corps, sans posture, sans visage, ni silhouette reconnaissable.
2. **Collisions sévères d'étiquettes textuelles** :
   - Le libellé du nom `Mariam` est dessiné directement sur l'icône du nœud `Place du Marché`.
   - Le nom `Yao` et son point chevauchent le libellé textuel `Place du Marché`.
   - À gauche, `Tom` entre en collision avec le nœud `Maisons Centre`.
3. **Absence totale de direction artistique et de volume** : Aucune ombre portée au sol, aucun dégradé de matière ou de lumière, ambiance visuelle plate et générique.
4. **Non-respect de l'accessibilité cognitive (WCAG)** : L'état d'un agent (rumeur R1, démenti R2, normal) est uniquement communiqué par la couleur du point (rouge vs bleu), ce qui exclut les personnes daltoniennes et empêche la lisibilité rapide de la scène.
5. **Absence d'animation vivante** : Pas de respiration, pas de clignement, pas de démarche, aucun signe d'activité organique.

---

## 3. Mesures Réelles de Performance Baseline

Mesure exécutée via Chrome DevTools Protocol (`node scripts/measure_baseline.js`) sur 120 frames consécutives de rendu Canvas au Tick 24 (12 agents actifs) :

| Métrique | Valeur Mesurée | Commande de Reproduction |
| :--- | :--- | :--- |
| **Temps moyen par frame Canvas** | **0,14 ms** | `node scripts/measure_baseline.js` |
| **Médiane (p50) durée frame** | **0,10 ms** | `node scripts/measure_baseline.js` |
| **Percentile 95 (p95) durée frame** | **0,30 ms** | `node scripts/measure_baseline.js` |
| **FPS mesuré** | **60,2 FPS** | `node scripts/measure_baseline.js` |

> **Constat technique** : Le coût JS du dessin primitif actuel est négligeable (< 0,3 ms). Notre cible pour les personnages 2D animés avec OffscreenCanvas précalculé est de rester sous les **2,5 ms par frame**, garantissant un maintien stable à **60 FPS** même avec 25 agents simultanés.

---

## 4. Fichiers et Captures Associés
- Vue d'ensemble 1x : [`docs/visuals/screenshots/before_1x.png`](file:///home/rd/hackaton-aws-2/docs/visuals/screenshots/before_1x.png)
- Vue d'ensemble 2x (Retina) : [`docs/visuals/screenshots/before_2x.png`](file:///home/rd/hackaton-aws-2/docs/visuals/screenshots/before_2x.png)
- Zoom 400% Zone du Marché : [`docs/visuals/screenshots/before_market_crop_400.png`](file:///home/rd/hackaton-aws-2/docs/visuals/screenshots/before_market_crop_400.png)
- Données brutes de métrique : [`docs/visuals/screenshots/baseline_metrics.json`](file:///home/rd/hackaton-aws-2/docs/visuals/screenshots/baseline_metrics.json)
