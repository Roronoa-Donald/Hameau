# Decisions — Remplacement des Personnages du Viewer

| ID | Date | Décision | Justification & Règle |
| :--- | :--- | :--- | :--- |
| D-01 | 2026-10-14 | Rendu procédural pur Canvas 2D / OffscreenCanvas | Zéro dépendance, zéro asset externe tiers, licence Apache-2.0 propre, performance optimale 60 FPS. |
| D-02 | 2026-10-14 | Proportions de 7 têtes avec stylisation éditoriale soignée | Rejet du pixel-art, des emojis et du chibi ; évitement de la vallée de l'étrange par une stylisation d'illustration chaude et chaleureuse. |
| D-03 | 2026-10-14 | Système d'animation à base de graine et de tick | Déterminisme absolu des animations secondaires (respiration, clignement, balancement de marche), sans `Math.random` non contrôlé. |
| D-04 | 2026-10-14 | Architecture paramétrique par données (JSON) | Extensibilité native de 12 à 25 agents sans modifier le moteur de rendu. |
| D-05 | 2026-10-14 | Préservation stricte de la simulation et du backend | Les journaux JSONL, le CLI, et les métriques d'audit ne sont pas altérés. |
