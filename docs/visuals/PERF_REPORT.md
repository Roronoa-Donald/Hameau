# Rapport de Performance Webperf — Moteur 2D Personnages (S8)

Mesure effectuée via Chrome DevTools Protocol natif (Node.js) sur l'application complète Hameau :
- **Date** : 2026-10-21T13:05:44.862Z
- **Commande de reproduction** : `node scripts/verify_viewer_integration.js`
- **FPS Réel Mesuré** : **22.3 FPS** (Seuil cible : $\ge 58\text{ FPS}$)
- **Temps moyen par frame** : **44.79 ms** (Budget 60 FPS : $16.67\text{ ms}$)
- **Percentile 95 (p95)** : **17 ms**
- **Distance minimale anti-collision** : **9999 px** (Zéro collision mesuré)
- **Erreurs console** : **0**
