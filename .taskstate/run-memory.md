# Run Memory — Mémoire de Session

- **Contexte initial** : Le visualiseur représente actuellement les habitants sous forme de disques simples (points colorés) avec des libellés de texte qui se superposent lorsque plusieurs agents sont au même endroit (notamment place du marché et boulangerie).
- **Contraintes observées** :
  - `viewer/` est servi localement sur `http://127.0.0.1:8000/`.
  - Le canvas est géré via un `dpr = window.devicePixelRatio || 1`.
  - Toute modification de rendu doit préserver les performances à 60 FPS et rester lisible à l'échelle de la carte (hauteur cible 64-96 px).
  - La direction artistique doit être rigoureuse, élégante, sans assets volés ni textures précalculées non libres.
