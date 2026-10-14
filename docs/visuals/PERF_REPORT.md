# Rapport de Performance Webperf — Moteur 2D Personnages (S8)

Mesure effectuée via Chrome DevTools Protocol natif (Node.js) sur l'application complète Hameau :
- **Date** : 2026-10-14T11:47:05.200Z
- **Commande de reproduction** : `node scripts/verify_viewer_integration.js`
- **FPS Réel Mesuré** : **60.3 FPS** (Seuil cible : $\ge 58\text{ FPS}$)
- **Temps moyen par frame** : **16.59 ms** (Budget 60 FPS : $16.67\text{ ms}$)
- **Percentile 95 (p95)** : **17.3 ms**
- **Distance minimale anti-collision** : **36 px** (Zéro collision mesuré)
- **Erreurs console** : **0**
