# Plan d'Expériences Pré-Enregistré (Pre-Registration) — HAMEAU

*Date de pré-enregistrement : 22 octobre 2026*  
*Auteur de l'évaluation : Antigravity Test Engine*  
*Engagement : Ce protocole est gravé avant l'exécution des mesures. Aucune condition, métrique ou prédiction ne sera rétroactivement modifiée. Les résultats seront ajoutés sous chaque section sans masquer les échecs.*

---

## Protocole Général & Séparation des Graines
* **Graines de réglage (Tuning / Exploration)** : Graines 100 à 104. Servent exclusivement aux vérifications d'ingénierie et calibration des hyperparamètres préliminaires.
* **Graines de test (Evaluation / Benchmark)** : Graines 1 à 5. Strictement isolées, utilisées pour produire les chiffres finaux sans réajustement post-hoc.
* **Budget Bedrock** : Plafond strict de 3,00 $ USD. Interruption immédiate si projection > 2,70 $ USD.
* **Environnements matériels distincts** :
  * `local_rtx3050` : Ordinateur portable, GPU NVIDIA GeForce RTX 3050 6GB Laptop GPU.
  * `colab_t4` : Instance distante Google Colab Tesla T4 16GB VRAM.

---

## E0 — Environnement et Vitesse Réelle du Decider (Micro-Benchmark)

* **Hypothèse** : Le modèle Strands Decider 2B s'exécute sur le GPU local RTX 3050 (6 Go VRAM) en moins de 800 ms par requête unitaire sans `flash-linear-attention`, et le groupement de questions (batching 4, 8, 16) amortit la latence par question de plus de 50 %.
* **Matériel testé** : `local_rtx3050` (RTX 3050 6 Go).
* **Configurations testées** :
  * Longueurs de contexte d'état : 150, 300, 600 tokens.
  * Questions groupées : 1, 4, 8, 16 questions par requête.
  * Régimes : À froid (1er appel) vs À chaud (moyenne 5 répétitions).
* **Métriques mesurées** : VRAM allouée/réservée (Go), latence p50, p95, max (ms), débit (questions / seconde), présence de `flash-linear-attention` et `causal_conv1d`.
* **Fichier produit** : `results/decider_latency.csv`.
* **Prédiction chiffrée** :
  * VRAM totale chargée $\le 4,2$ Go.
  * Latence 1 question (état 150 tokens, chaud) : $400 \pm 150$ ms.
  * Présence de `flash-linear-attention` : ABSENT (fallback PyTorch de référence).
* **Condition d'échec** : VRAM > 5,5 Go (OOM), ou latence unitaire > 1 500 ms empêchant la faisabilité des runs longs locaux.

---

## E1 — Run Réel de Référence (12 Habitants, 3 Jours)

* **Hypothèse** : Une simulation complète de 3 jours (576 ticks) à 12 habitants produit plus de 3 000 décisions Decider réelles avec un ratio questions Decider / appel LLM supérieur à 15:1 et un coût Bedrock inférieur à 0,20 $ par run.
* **Conditions** : 12 villageois canoniques, 3 jours (576 ticks), Decider réel, Bedrock réel (réseau avec cache cassette).
* **Graines de test** : Graines 1 à 3 (élargi à 5 si le débit mesuré en E0 le permet dans le budget temps).
* **Métriques mesurées** :
  * Questions Decider ventilées par gabarit (D1 à D8).
  * Requêtes Decider totales.
  * Appels LLM par usage (B1 dialogue, B2 réflexion, B4 gazette).
  * Jetons d'entrée et de sortie (Decider et Bedrock).
  * Latences serveur et client (p50, p95).
  * Temps réel par jour simulé (minutes).
  * Répartition des zones de confiance (Verte $\ge$ seuil vert, Orange, Rouge < seuil orange).
  * Taux de replis heuristiques (zone rouge).
* **Prédiction chiffrée** :
  * Ratio questions/LLM $> 15:1$.
  * Décisions en zone verte $> 55\,\%$, zone rouge $< 15\,\%$.
  * Coût Bedrock $< 0,15\,\$$ par run avec Nova Micro.
* **Condition d'échec** : Ratio questions/LLM $< 10:1$, ou zone rouge $> 30\,\%$ (indiquant un modèle inopérant nécessitant un repli constant).

---

## E2 — Diffusion de la Rumeur et Run Témoin

* **Hypothèse** : La rumeur R1 se propage par contact social à plus de 50 % du village en moins de 36 heures simulées, et induit un changement causal de comportement chez au moins 3 agents (approvisionnement / évitement du marché), vérifié par contraste strict avec un run témoin sans rumeur.
* **Conditions** : Pour chaque graine de test $g \in \{1, 2, 3\}$ :
  * Condition A (Rumeur) : Injection standard de R1 au Jour 1 à 08h00.
  * Condition B (Témoin) : AUCUNE injection de R1 (scénario neutre).
* **Métriques mesurées** :
  * Taux maximal de pénétration du fait (% d'habitants croyant R1).
  * Délai pour atteindre 50 % du village (ticks).
  * Nombre total de sauts de transmission (`rumor_hop`).
  * Nombre d'agents dont l'action ou les croyances divergent au Jour 2 et 3 entre Condition A et Condition B.
* **Prédiction chiffrée** :
  * Pénétration maximale de R1 : $60\,\% \pm 15\,\%$.
  * Divergence causale comportementale : $\ge 3$ agents modifiant leur routine de marché le vendredi/samedi par rapport au témoin.
* **Condition d'échec** : Aucune différence mesurable entre le run rumeur et le run témoin (absence d'impact causal du modèle), ou diffusion nulle ($< 2$ villageois atteints).

---

## E3 — Ablation MemoryGate

* **Hypothèse** : Le filtrage par pertinence sémantique du MemoryGate (D3) réduit la taille du prompt injecté aux agents d'au moins 40 % par rapport à la récence brute, tout en maintenant un taux d'utilisation des souvenirs pertinents équivalent ou supérieur.
* **Conditions** : Même scénario, même graine de test ($g=1, 2$), 3 conditions d'ablation :
  * (a) **MemoryGate complet** (Recency + Importance D2 + Relevance D3).
  * (b) **Récence seule** (les $K$ souvenirs les plus récents sans filtrage D3).
  * (c) **Heuristique par entités** (simple correspondance exacte de mots-clés d'entités).
* **Métriques mesurées** :
  * Nombre moyen de tokens de souvenirs injectés dans le contexte D1 / B1.
  * Nombre d'appels LLM et décisions induites.
  * Pénétration de la rumeur et délai de transmission.
  * Intervalle de confiance bootstrap apparié sur les différences.
* **Prédiction chiffrée** :
  * Réduction des tokens injectés $\ge 40\,\%$ pour la condition (a) vs (b).
* **Condition d'échec** : Condition (a) augmente la consommation de tokens ou dégrade la cohérence comportementale par rapport à (b) et (c).

---

## E4 — Comparaison de Stratégies Architecturales

* **Hypothèse** : L'architecture hybride (Decider 2B local pour le contrôle + Nova Micro pour le texte) présente un coût au moins 10x inférieur à une architecture Tout-LLM et une latence de décision unitaire inférieure à 800 ms.
* **Conditions** : Village réduit (5 habitants, 1 jour, graines 1 et 2) pour respecter le budget Bedrock ($< 3\,\$$) :
  * Stratégie A : **Heuristique sans IA** (règles statiques, arbres de décision purs).
  * Stratégie B : **Tout-LLM** (Nova Micro pour D1 à D8 et les dialogues).
  * Stratégie C : **Hybride HAMEAU** (Decider 2B pour D1-D8, Nova Micro pour B1-B4).
* **Métriques mesurées** :
  * Coût financier réel observé ($/jour simulé).
  * Latence médiane par décision (ms).
  * Nombre d'appels réseau LLM.
* **Prédiction chiffrée** :
  * Coût C $< 0,05 \times$ Coût B.
  * Latence C $< 0,5 \times$ Latence B.
* **Condition d'échec** : La stratégie hybride C est plus coûteuse ou plus lente que le Tout-LLM B.

---

## E5 — Calibration avec Vérité Objective

* **Hypothèse** : Le modèle Strands Decider 2B est calibré sur les évaluations de véracité : les scores de confiance élevés reflètent une probabilité empirique d'exactitude significativement supérieure aux scores faibles.
* **Conditions** : Analyse des décisions D8 (crédibilité accordée aux rumeurs) face à la vérité fondamentale des faits du monde :
  * R1 (fermeture du marché) : FAUX (ground truth = 0).
  * R2 (démenti officiel du maire) : VRAI (ground truth = 1).
  * R3 (ouverture effective du marché) : VRAI (ground truth = 1).
* **Métriques mesurées** :
  * Exactitude empirique découpée en 5 tranches de confiance ([0-0.2], [0.2-0.4], [0.4-0.6], [0.6-0.8], [0.8-1.0]).
  * Erreur d'étalonnage attendue (ECE - Expected Calibration Error).
  * Nombre de cas par tranche. Si $N < 30$, la métrique sera explicitement signalée comme « indicative ».
* **Prédiction chiffrée** :
  * Exactitude tranche [0.8-1.0] $> 70\,\%$.
  * ECE $< 0,25$.
* **Condition d'échec** : Corrélation nulle ou négative entre score de confiance affiché et vérité du fait (modèle surconfiant sur les fausses rumeurs).

---

## E6 — Stabilité et Déterminisme

* **Hypothèse** : Le moteur HAMEAU est strictement déterministe en mode mock (invariance sous `PYTHONHASHSEED`), et le Decider réel sur GPU présente un taux de reproductibilité supérieur à 98 % sur inférence répétée avec température nulle / greedy.
* **Conditions** :
  * Test (a) Mock : Exécution du même run (graine 1, 1 jour) avec `PYTHONHASHSEED=0` et `PYTHONHASHSEED=42`. Diff binaire sur le log JSONL.
  * Test (b) Decider réel : Deux exécutions séquentielles de 50 décisions D1 sur le GPU avec les mêmes états.
  * Test (c) Biais de position : 100 requêtes D1 dont l'ordre des options dans le gabarit est permuté circulairement.
* **Métriques mesurées** :
  * Taux de divergence textuelle (0 requis en mock).
  * Taux d'accord de décision (% de choix identiques).
  * Taux de biais de position (% de choix corrélés avec l'indice 0).
* **Prédiction chiffrée** :
  * Test (a) : 0 divergence.
  * Test (b) : Accord $\ge 98\,\%$.
  * Test (c) : Biais de premier choix $< 35\,\%$ (sur 4 options).
* **Condition d'échec** : Test (a) diverge (déterminisme brisé), ou Test (c) présente un biais premier choix $> 60\,\%$.

---

## E7 — Passage à l'Échelle (Scaling Population)

* **Hypothèse** : Le temps de simulation par jour et la VRAM GPU évoluent de manière quasi-linéaire avec le nombre d'habitants pour le calcul individuel, et quadratique pour les rencontres de proximité.
* **Conditions** : Tailles de village : 6, 12, 18, 24 habitants, sur 1 jour (192 ticks), graine 1.
* **Métriques mesurées** :
  * Durée réelle du run (secondes).
  * Nombre total de décisions générées.
  * Débit moyen (décisions / seconde).
  * VRAM pic consommée (Go).
* **Prédiction chiffrée** :
  * 6 agents : $< 5$ min.
  * 12 agents : $< 12$ min.
  * 18 agents : $< 25$ min.
  * 24 agents : $< 45$ min.
  * VRAM pic $\le 4,5$ Go pour toutes les tailles (maintien du modèle en mémoire).
* **Condition d'échec** : OOM VRAM (> 5,8 Go) ou explosion exponentielle du temps de simulation ($> 90$ min pour 24 agents).

---

## E8 — Analyse de Coût Réel et Extrapolations

* **Hypothèse** : Le coût financier d'une simulation HAMEAU de 3 jours à 12 habitants reste inférieur à 0,25 $ en réseau réel et strictement égal à 0,0000 $ en mode rejeu cassette.
* **Grille tarifaire de référence (Amazon Nova Micro us-east-1)** :
  * Entrée (Input tokens) : 0,035 $ / 1M tokens.
  * Sortie (Output tokens) : 0,140 $ / 1M tokens.
* **Métriques mesurées** :
  * Jetons réels consommés par type d'appel (B1, B2, B4).
  * Coût calculé exact selon le barème officiel.
  * Économie comparée à un modèle frontière (ex : Claude 3.5 Sonnet ou GPT-4o).
* **Prédiction chiffrée** : Coût total réel par run 3J $< 0,10\,\$$.
* **Condition d'échec** : Dépassement du coût de 0,50 $ par run.

---

## E9 — Performance du Visualiseur Web

* **Hypothèse** : Le visualiseur Web Canvas 2D maintient un taux de rafraîchissement $\ge 50$ FPS et charge un journal de simulation complet ($> 6\,000$ événements) en moins de 1,5 seconde sans aucune erreur console.
* **Conditions** : Mesure sur Google Chrome headless via Chrome DevTools Protocol (CDP) sur un journal réel de plus de 6 000 événements.
* **Métriques mesurées** :
  * Temps de chargement et parsing du JSONL (ms).
  * FPS moyen et temps de rendu par frame (ms, p95).
  * Nombre d'erreurs console levées.
* **Prédiction chiffrée** :
  * Temps de chargement $< 1\,200$ ms.
  * FPS moyen $\ge 55$ FPS.
  * Erreurs console : strictement 0.
* **Condition d'échec** : FPS $< 30$ FPS, temps de chargement $> 3\,000$ ms, ou $\ge 1$ erreur console non gérée.

---

## E10 — Catalogue des Échecs et Limitations

* **Hypothèse** : L'inspection systématique des décisions révèle des cas limites documentables : replis fréquents en zone rouge, hésitations comportementales ou contradictions entre souvenirs et actions.
* **Conditions** : Extraction automatique depuis les logs réels :
  * Les 10 pires décisions en score de confiance le plus faible (zone rouge).
  * Cas d'incohérence observable (ex: décision contraire à un souvenir fort).
* **Livrable** : Tableau factuel documentant l'état d'entrée, les options, le choix du modèle, la raison de l'échec et la mitigation système mise en œuvre.
