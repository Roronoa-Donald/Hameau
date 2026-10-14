# Plan d'Implémentation par Tranches Verticales (PLAN.md)

Ce plan découpe l'implémentation complète du moteur visuel 2D dans le visualiseur Hameau en 9 tranches verticales fines (**S1 à S9**) selon la méthode `incremental-implementation` et les exigences des six skills. Chaque tranche est auto-contenue, immédiatement testable dans le navigateur et validée par une preuve objective avant de passer à la suivante.

---

## Matrice des Tranches Verticales (S1 – S9)

| Tranche | Intitulé | Portée & Fichiers Touchés | Critère d'Acceptation (DoD) | Preuve de Validation |
| :--- | :--- | :--- | :--- | :--- |
| **S1** | **Intégration du module & Bascule de vue** | `viewer/character_renderer.js`<br>`viewer/index.html`<br>`viewer/app.js` | Import propre de `CharacterRenderer2D` dans l'application principale. Ajout d'un bouton de bascule « 🎭 Personnages / ⚪ Points » dans la barre d'outils. Le mode points initial reste opérationnel à 100%. | CDP: Bascule vérifiée par script headless, 0 erreur console. |
| **S2** | **Remplacement des points par personnages idle** | `viewer/app.js` | En mode personnages, les points sont remplacés par les personnages en pied à l'échelle adaptée (56-64px), avec ombre portée au sol et respiration animée. | Capture 1x/2x plein village avec les 12 habitants en place. |
| **S3** | **Anti-collision et agencement d'arêtes** | `viewer/app.js` | Quand $K \ge 2$ agents sont sur le même lieu, ils se déploient en arc étagé. Les noms des lieux sont surélevés au-dessus du nœud, les noms d'agents sont placés sous leurs pieds. Aucun texte ne se chevauche. | Capture gros plan sur la Place du Marché avec 4+ agents sans collision. |
| **S4** | **Interpolation spatiale de marche continue** | `viewer/app.js` | Lors d'un changement de lieu d'un agent, transition spatiale fluide (lerp avec easing cubique) entre $P_{\text{from}}$ et $P_{\text{to}}$. Activation de la cinématique de foulée (`walk`) et retournement du regard dans le sens de marche. | CDP: Mesure de déplacement continu entre 2 ticks. |
| **S5** | **Bulles de dialogue éditoriales** | `viewer/character_renderer.js`<br>`viewer/app.js` | Quand `a.isTalking === true`, affichage d'une bulle de texte stylisée avec ancre triangulaire, texte tronqué proprement avec points de suspension, et cinématique oratoire de parole. | Capture d'écran lors d'une réplique de dialogue entre deux agents. |
| **S6** | **Badges visuels croyances & stockage** | `viewer/app.js` | Halo discret et élégant pour R1 (rose-rouge `#f43f5e`), R2 (cyan `#06b6d4`), stockage (panier ou charge lourde). La posture de l'habitant reflète la rumeur ou le soulagement. | Capture comparative : habitant serein vs porteur R1 vs démenti R2. |
| **S7** | **Portraits en buste dans l'Inspecteur & Gazette** | `viewer/index.html`<br>`viewer/app.js`<br>`viewer/styles.css` | Remplacement du cercle d'avatar dans l'Inspecteur d'Agent par un canvas du buste animé haute définition. Affichage du portrait de Claire dans La Gazette. | Capture de l'Inspecteur d'Agent avec portrait expressif vivant. |
| **S8** | **Optimisation & Benchmark Webperf** | `scripts/measure_characters_perf.js` | Profilage réel en direct via Chrome CDP avec 12 agents animés en continu, interpolation et dialogue : garantie $\ge 58 \text{ FPS}$ et temps de frame $< 3 \text{ ms}$. | Rapport chiffré dans `docs/visuals/PERF_REPORT.md` avec commande. |
| **S9** | **Responsive, Finitions & Non-régression** | `viewer/styles.css`<br>`scripts/verify.sh` | Validation du rendu sur différentes densités d'écran (DPR 1x et 2x), vérification du contraste WCAG, exécution finale de `scripts/verify.sh`. | Rapport final et captures `after_1x.png`, `after_2x.png`. |

---

## Protocole d'Exécution Rigoureux

Pour chaque tranche $S_i$ :
1. **Écriture du code ciblé** (aucune modification hors périmètre).
2. **Vérification automatique** : Test unitaire ou script de mesure Chrome CDP.
3. **Capture d'écran de preuve** datée dans `docs/visuals/screenshots/`.
4. **Mise à jour du registre de preuves** dans `.taskstate/evidence.md` et `docs/visuals/SKILLS_LOG.md`.
5. **Validation de non-régression** avec `bash scripts/verify.sh`.
