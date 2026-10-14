# Backlog — Éléments et Défauts Hors Périmètre Visuel

Ce fichier répertorie les défauts et améliorations identifiés mais situés hors du périmètre strict de la mission visuelle des personnages 2D, conformément aux règles du projet.

| ID | Domaine | Description du Défaut / Amélioration | Raison de Non-Traitement dans cette Mission |
| :--- | :--- | :--- | :--- |
| BL-01 | Métriques UI | Compteur de latence affichant parfois `~0 ms moy.` lors des exécutions ultra-rapides ou mocks. | Hors périmètre : les compteurs et métriques réelles de simulation ne doivent pas être altérés. |
| BL-02 | Métriques UI | Affichage de coût `0,0000 $` lorsque les cassettes de test sont actives. | Conforme au comportement nominal (0$ pour les rejeux cassettes), mais pourrait afficher explicitement `(Cassette)` au lieu de 0$. |
| BL-03 | Rendu Gazette | Affichage du Markdown brut dans certains paragraphes de la Gazette au lieu d'un parseur typographique complet. | Hors périmètre : concerne le formatage textuel du journal du soir et non le rendu 2D des personnages sur la carte. |
