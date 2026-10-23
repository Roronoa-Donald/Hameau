# HAMEAU — Cahier des charges et feuille de route

*Un village d'agents qui décident vite avec Strands Decider 2B et parlent avec Amazon Bedrock · Strands Decider Agent Hackathon (AWS Builder Center) · Version 1.0 · 13 octobre 2026*

## 0. Mode d'emploi du document

Ce document est la source de vérité du projet Hameau. Il fixe le but, le périmètre, le comportement exact du système, l'architecture, la méthode de mesure, les livrables du concours et la feuille de route jour par jour. Il est écrit pour qu'une personne qui n'a pas suivi les discussions puisse construire le projet.

Conventions : chaque exigence porte un identifiant (FR pour fonctionnelle, NFR pour non fonctionnelle) et une priorité MUST (indispensable), SHOULD (important) ou COULD (si le temps le permet). Les chiffres cibles sont des hypothèses à mesurer, jamais des promesses : l'article publiera ce que les tests donnent réellement, y compris les échecs. La mention « à vérifier » signale un détail tiré d'une source externe (documentation, dépôt, blog) à confirmer pendant la Phase 0 avant de s'y appuyer.

Sources : règlement du concours (mis à jour le 9 octobre 2026), page du hackathon sur AWS Builder Center, billet de présentation de Strands Decider 2B du 1er octobre 2026, dépôt strands-labs/strands-decider et son exemple examples/strands, articles Builder Center sur Decider, et l'article de recherche « Generative Agents » (Park et al., Stanford, 2023) qui sert d'inspiration.

## 1. Fiche d'identité du projet

- **Nom** : Hameau.
- **Promesse (à valider par la mesure)** : un village de 25 habitants qui vit plusieurs jours simulés, où Decider 2B prend la quasi-totalité des décisions rapides et où Bedrock n'écrit que les moments rares (dialogues, réflexions, journal du village).
- **Pattern déclaré** : Context and memory (scorer quels souvenirs sont pertinents avant de les injecter). Les autres décisions du système (choix d'action, déclencheurs de conversation) sont des décisions de soutien ; on ne déclare qu'un seul pattern.
- **Tags à ajouter avant l'échéance** : #strands-decider-2b et #context-memory.
- **Actif réutilisable principal** : MemoryGate, un module qui note l'importance des observations et la pertinence des souvenirs candidats avant injection dans le contexte d'un agent Strands.
- **Licence du dépôt** : Apache-2.0 (licence OSI ; c'est aussi celle de Decider d'après son dépôt et sa fiche Hugging Face).
- **Langue des livrables** : anglais pour l'article, la vidéo et le README (jury international) ; ce cahier des charges reste en français.
- **Équipe** : à confirmer (voir section 15, point 1 sur la règle « une entrée par personne »).
- **Fuseaux** : Lomé est à UTC+0 ; PT est à UTC-7 jusqu'au 1er novembre. 9h00 PT = 16h00 à Lomé.
- **Dates clés** : lancement le 16 octobre (le règlement donne 00h00 PT en tête et 9h00 PT dans le corps du texte : on retient la plus tardive par prudence, donc premier commit du projet le 16 octobre après 16h00 à Lomé) ; fin de la période de soumission le 23 octobre à 23h59 PT, soit le 24 octobre à 06h59 à Lomé ; **cible interne de soumission : le 23 octobre à midi (Lomé)**, soit 18 heures de marge ; Gate 1 la semaine du 26 octobre ; Gate 2 la semaine du 2 novembre ; annonce la semaine du 9 novembre.

## 2. Contexte, problème et objectifs

### 2.1 Rappel de l'épreuve

Il faut construire un agent fonctionnel sur AWS qui confie au moins une décision significative à Strands Decider 2B, associé à Amazon Bedrock pour la partie générative. Le modèle Decider ne génère pas de texte : il lit un état et une question typée, puis renvoie un choix, un oui/non ou un score, avec une confiance calibrée. C'est un modèle expérimental d'environ 2 milliards de paramètres, construit sur Qwen3.5-2B avec une tête qui note les options ; il répond en une centaine de millisecondes sur du matériel courant.

### 2.2 Le problème que Hameau met en scène

Les agents génératifs de Park et al. (2023) donnaient à 25 habitants virtuels une mémoire, des réflexions et des plans. Ce système faisait appel à un LLM pour presque tout : noter l'importance de chaque souvenir, décider quoi faire ensuite, décider de réfléchir, planifier. Le résultat est impressionnant mais coûteux et lent, ce qui explique que peu de gens le font tourner. Or la plupart de ces appels sont des décisions courtes et répétitives : choisir parmi quelques options, répondre par oui ou non, noter sur une échelle. C'est exactement la forme de décision que Decider traite.

### 2.3 Hypothèses à tester

- **H1** : Decider peut prendre les décisions rapides et fréquentes (choix d'action, importance, pertinence, déclencheurs) pendant que Bedrock ne produit que les textes rares, avec beaucoup moins d'appels LLM et une qualité acceptable.
- **H2** : la confiance calibrée de Decider permet de savoir quand ne pas décider seul : en zone de faible confiance, un repli (règle ou Bedrock) améliore le résultat.
- **H3** : le module MemoryGate est un pattern réutilisable par d'autres agents Strands qui ont un problème de contexte.

### 2.4 Objectifs mesurables (cibles, à confirmer par la mesure)

- **O1** : 12 agents pendant 3 jours simulés sans intervention (minimum) ; 25 agents (cible).
- **O2** : rapport décisions Decider / appels LLM d'au moins 20 pour 1 (cible ambitieuse : 50 pour 1), mesuré sur les journaux réels.
- **O3** : qualité des scores d'importance et de pertinence comparée à des étiquettes humaines et à un juge Bedrock ; l'écart est publié quel qu'il soit.
- **O4** : reproductibilité : tout run se rejoue à l'identique à partir d'une graine et de cassettes d'appels Bedrock enregistrés.
- **O5** : tous les livrables du concours prêts avant le 23 octobre à midi (Lomé).
- **O6** : une démonstration web rejouable accessible sans GPU ni compte AWS.

### 2.5 Non-objectifs

Hameau n'est pas un produit de production, ne prétend pas égaler la qualité de comportement d'un système entièrement piloté par LLM, ne traite aucune donnée de vraies personnes, et ne cherche pas à entraîner ou à affiner Decider.

## 3. Critères de réussite et traçabilité avec le barème

### 3.1 Barrière éliminatoire (réussite ou échec)

Une entrée à laquelle manque l'une de ces pièces n'est pas jugée, quelle que soit la qualité de l'idée. Chaque pièce a un responsable et une date de gel dans la feuille de route.

- Un article publié sur AWS Builder Center qui décrit l'agent, ce qu'il fait et la décision confiée à Decider 2B.
- Un dépôt public sous licence OSI avec le code de l'agent et au moins un pattern de décision réutilisable, clairement étiqueté : questions typées et options, câblage dans l'agent, courte note d'utilisation.
- Une vidéo de moins de trois minutes, publique sur YouTube, Vimeo, Facebook Video ou Youku, sans marque tierce ni musique protégée sans autorisation.
- Une utilisation de Decider 2B pour au moins une décision significative, avec Amazon Bedrock pour la partie générative.
- Les deux tags #strands-decider-2b et #context-memory.
- Un agent original, jamais publié avant, et une éligibilité valide : 18 ans ou plus, profil Builder Center, pays non exclu, pas d'employé Amazon ou AWS ni de proche, une seule entrée par personne.

### 3.2 Barème et preuves visées

- **Créativité et effet « wow » (30 %)** : un village qui vit, une rumeur qui se propage et change des comportements, un compteur en direct « décisions Decider contre appels LLM », une Gazette générée chaque soir. Preuves : vidéo, démonstration web rejouable, captures de l'inspecteur d'agent.
- **Utilisation efficace de Decider avec Bedrock (30 %)** : huit décisions typées à haute fréquence, usage de la confiance calibrée (zones et repli), MemoryGate packagé, comparaison de trois stratégies mesurée. Preuves : tableaux de l'article, scripts de benchmark, tests automatisés.
- **Qualité de communication (25 %)** : article structuré selon les quatre critères, vidéo en trois temps, README permettant de relancer le projet en moins de dix minutes. Preuve : relecture à froid par une personne extérieure au projet.
- **Originalité (15 %)** : à notre connaissance au 13 octobre 2026, les projets Decider publiés sont des garde-fous d'appels d'outils, des routeurs de modèles, un hébergement sur Lambda, un portage WebGPU et un juge d'épisodes pour robots ; nous n'avons pas trouvé de simulation multi-agents où Decider porte les décisions à haute fréquence. À reconfirmer le 16 octobre en relisant Builder Center.

### 3.3 Niveaux de réussite

- **Minimum honorable** : toutes les pièces éliminatoires ; 12 agents pendant 3 jours simulés ; trois stratégies comparées sur au moins une métrique de coût et une de qualité ; un article honnête avec ses limites.
- **Cible** : 25 agents ; calibration publiée ; démonstration web déployée sur AWS ; MemoryGate documenté avec tests.
- **Excellence** : ablations complètes ; question lab publié ; modèle de rumeur avec démenti ; vidéo soignée sous-titrée.

## 4. Vision produit et scénario de démonstration

### 4.1 L'histoire

Hameau est un petit village fictif de 25 habitants. Chaque jour simulé va de 6h à 22h ; un pas de simulation (tick) vaut 5 minutes. Chaque habitant a un métier, un caractère, des relations, une mémoire et des besoins. À 8h00 du premier jour, on glisse à un seul habitant (le livreur Yao) une rumeur fausse : « La mairie envisage de fermer le marché samedi. » On regarde ensuite le village la transmettre, la croire plus ou moins, et changer ses habitudes (courses plus tôt, stocks). Le lendemain matin, le maire publie un démenti qui entre en concurrence avec la rumeur. Le soir, la rédactrice du village raconte la journée dans la Gazette du Hameau.

### 4.2 Les moments « wow » à rendre visibles

1. **Le compteur** : en haut de l'écran, « décisions Decider : N · appels LLM : M · coût estimé ». Il grimpe en direct et montre l'écart.
2. **La rumeur** : un graphe qui s'allume habitant après habitant, avec le nombre de transmissions et le délai.
3. **L'inspecteur** : un clic sur un habitant affiche ses souvenirs avec leur importance, leur pertinence et la confiance de chaque décision récente.
4. **La preuve par l'ablation** : même village, même rumeur, mais sans MemoryGate (récupération par récence seule) : la rumeur ne change plus rien. C'est l'argument central de l'utilité de la décision.
5. **La Gazette** : un texte généré par Bedrock à partir des événements structurés, qui raconte le village et la rumeur.
6. **L'honnêteté** : un cas d'échec montré en clair (une décision à faible confiance qui bascule sur le repli).

### 4.3 La distribution

Douze habitants principaux, écrits à la main, forment le cœur de la démonstration. Les treize autres sont générés à partir de modèles de personnages puis relus.

- Awa, boulangère, matinale et bavarde.
- Kofi, maire, prudent, sensible à la réputation.
- Yao, livreur du marché, point d'entrée de la rumeur.
- Élise, institutrice, curieuse, aime vérifier.
- Samuel, forgeron, peu bavard, très écouté.
- Nadia, médecin, voit beaucoup de monde.
- Tom, étudiant, connecté, relaie vite.
- Mariam, marchande de légumes, première concernée par le marché.
- Paul, pêcheur retraité, habitué du café.
- Léa, bibliothécaire, archive les faits.
- Ibrahim, agriculteur, fournisseur du marché.
- Claire, rédactrice de la Gazette.

Dix lieux : place du marché, boulangerie, mairie, école, bibliothèque, atelier, cabinet médical, rivière, ferme, café. Chaque habitant a une maison (cinq nœuds de maisons partagés suffisent).

## 5. Périmètre

### 5.1 MVP (MUST)

- Monde en graphe de lieux, horloge, ordonnanceur par événements, graine aléatoire fixe.
- 12 agents avec persona, besoins, mémoire et routines.
- Décisions D1 (choix d'action), D2 (importance), D3 (pertinence), D4 (conversation) servies par Decider.
- Dialogues et réflexions via Bedrock avec Strands, plafonnés par un budget.
- Journal d'événements complet, compteurs, cassettes d'appels Bedrock.
- Viewer web de rejeu : carte, horloge, compteurs, inspecteur.
- Trois stratégies (A heuristique, B tout-LLM, C hybride) et un benchmark minimal.
- MemoryGate packagé avec README et tests.
- Article, vidéo, dépôt public, tags.

### 5.2 Cible (SHOULD)

- 25 agents ; décisions D5 à D8 ; zones de confiance calibrées ; ablations ; Gazette ; démonstration déployée sur S3 et CloudFront ; serveur GPU sur EC2.

### 5.3 Si le temps le permet (COULD)

- Mode direct (live) par WebSocket ; plans du matin écrits par Bedrock ; comparaison de v19 et v21 de Decider ; infrastructure décrite en CDK ; sous-titres multilingues.

### 5.4 Hors périmètre (WON'T)

Entraînement ou affinage du modèle ; pathfinding sur grille fine (on utilise un graphe de lieux) ; vraies personnes ou données réelles ; production ; son ou musique ; application mobile.

### 5.5 Ordre de coupe

Si le temps manque, on retire dans cet ordre : mode direct, infrastructure CDK, plans du matin Bedrock, D8, passage de 25 à 12 agents, ablations secondaires. On ne retire jamais : les pièces éliminatoires, MemoryGate, la comparaison A/B/C minimale et les limites honnêtes dans l'article.

## 6. Spécification fonctionnelle détaillée

### 6.1 Monde et temps

- **FR-01 (MUST)** : le monde est un graphe de 10 lieux et de quelques nœuds de maisons ; chaque arête a un coût de déplacement en ticks. Pas de grille ni de pathfinding : le viewer interpole les positions.
- **FR-02 (MUST)** : 1 tick = 5 minutes simulées ; journée de 6h00 à 22h00 soit 192 ticks ; la nuit est sautée (sommeil), avec consolidation des souvenirs à 22h00.
- **FR-03 (MUST)** : l'ordonnanceur est piloté par événements : un agent redécide lorsque son activité se termine ou qu'un événement l'interrompt, pas à chaque tick. Cela divise le nombre de décisions par trois à quatre.
- **FR-04 (MUST)** : tout le déterminisme vient d'une graine unique (ordre des agents, tirages aléatoires, bruit de départ).

### 6.2 Agents

- **FR-05 (MUST)** : chaque agent a un identifiant, un nom, un âge, un métier, trois traits, deux buts, une maison, un lieu de travail et des relations pondérées avec les autres.
- **FR-06 (MUST)** : état dynamique : lieu, activité, fin d'activité, besoins (énergie, faim, besoin social) entre 0 et 1.
- **FR-07 (SHOULD)** : agenda du jour : quatre à six intentions ; en MVP elles viennent de routines écrites, ensuite de Bedrock le matin.

### 6.3 Catalogue des décisions confiées à Decider

Chaque décision est une question typée avec ses options. Les textes exacts sont en annexe A ; ils seront testés dans le question lab (section 9), car la formulation et le seuil changent fortement les résultats.

**D1 — ActionPicker (choix)**

- Déclencheur : fin d'activité ou événement d'interruption.
- État fourni (150 à 300 mots) : identité en deux lignes, heure, lieu, besoins, intentions restantes, trois souvenirs choisis par MemoryGate, agents présents.
- Options (huit au plus, chacune décrite en une phrase) : continuer l'activité ; aller vers chacun des quatre lieux les plus plausibles ; faire la tâche de routine du lieu ; parler à l'agent le plus proche ; se reposer.
- Sortie : option choisie, probabilité de chaque option, confiance.
- Repli en zone rouge : la routine prévue à l'agenda.
- Fréquence estimée : 8 à 12 par agent et par jour.
- Qualité mesurée par : accord avec un juge Bedrock sur 60 situations, et part des décisions qui diffèrent de la routine (preuve que Decider décide réellement).

**D2 — ImportanceScorer (score 0 à 1)**

- Déclencheur : chaque nouvelle observation ou information reçue.
- Question : à quel point cet événement compte-t-il pour les buts, les relations et les inquiétudes de cette personne ?
- Sortie : score stocké avec la mémoire ; affiché de 1 à 10 dans le viewer.
- Fréquence estimée : 30 à 60 par agent et par jour.
- Qualité : corrélation de rang (Spearman) avec des étiquettes humaines et avec Bedrock (expérience E1).

**D3 — RelevanceScorer (score 0 à 1)**

- Déclencheur : avant D1, D4 et D5, pour chaque souvenir candidat (douze au plus).
- Question : ce souvenir est-il utile pour la situation actuelle ?
- Sortie : pertinence par candidat ; les trois meilleurs sont injectés.
- Qualité : précision@3 sur 60 situations étiquetées (E2).

**D4 — TalkGate (oui/non)**

- Déclencheur : deux agents au même endroit, disponibles.
- Question : cette personne veut-elle engager la conversation maintenant ?
- Repli : règle de proximité et de besoin social.
- Qualité : calibration (E3).

**D5 — ShareScorer (score 0 à 1)**

- Déclencheur : début d'une conversation.
- Question : ce souvenir vaut-il d'être raconté à cette personne ?
- Sortie : le ou les souvenirs les mieux notés guident le texte généré ; c'est le mécanisme de transmission de la rumeur.

**D6 — ReflectGate (oui/non)**

- Déclencheur : somme des importances depuis la dernière réflexion au-dessus d'un seuil, ou 21h30.
- Question : est-ce le moment de prendre du recul sur la journée ?
- Sortie : si oui, un appel Bedrock écrit la réflexion (au plus une par agent et par jour).

**D7 — ContinueGate (oui/non)**

- Déclencheur : après chaque réplique ; six répliques au plus par conversation.

**D8 — CredibilityGate (score 0 à 1)**

- Déclencheur : information reçue d'un autre agent.
- Question : cette information est-elle crédible compte tenu de sa source et de ce que la personne sait déjà ?
- Sortie : pondère l'influence de l'information sur les décisions ; permet au démenti de concurrencer la rumeur.

**Politique de confiance (FR-08, MUST).** Pour chaque type de décision, deux seuils (haut et bas) sont calibrés sur des cas étiquetés (E3), jamais choisis à la main. Zone verte (au-dessus du seuil haut) : la décision est appliquée. Zone orange : appliquée mais marquée dans le journal. Zone rouge (sous le seuil bas) : repli déterministe et, pour D1 et D5 seulement, escalade facultative vers Bedrock dans la limite d'un budget.

### 6.4 Modèle de mémoire et récupération

- **FR-09 (MUST)** : une mémoire est un enregistrement avec : identifiant, agent, tick, type (observation, dialogue, réflexion, plan, ouï-dire), texte d'une phrase, entités citées (agents, lieux), identifiant de fait (pour les rumeurs), agent source, nombre de transmissions (hop), importance et confiance associée, auteur de la décision (decider, règle ou Bedrock), dernier accès.
- **FR-10 (MUST)** : les événements sont produits par la simulation avec des champs structurés ; il n'y a donc aucune extraction de texte à faire pour savoir qui sait quoi.
- **FR-11 (MUST)** : récupération en trois temps. (1) Présélection déterministe : souvenirs partageant une entité avec la situation, plus les cinq plus récents et les cinq plus importants, plafonnés à douze. (2) Pertinence par D3. (3) Score final = récence + importance + pertinence, chacun normalisé entre 0 et 1, poids initiaux égaux, récence en décroissance exponentielle (demi-vie de départ de 24 heures simulées). Les poids et la demi-vie sont réglés sur E2. Les trois meilleurs sont injectés.

### 6.5 Conversations et rumeur

- **FR-12 (MUST)** : une conversation commence par D4, se déroule en six répliques au plus (D7 entre chaque), chaque réplique étant écrite par Bedrock avec les souvenirs choisis par MemoryGate et le sujet choisi par D5.
- **FR-13 (MUST)** : à la fin, la simulation écrit des mises à jour structurées : faits transmis (avec identifiants), nouvelle mémoire chez l'auditeur (type ouï-dire, source, hop), puis D2 et D8 pour noter importance et crédibilité.
- **FR-14 (MUST)** : scénario de référence : la rumeur R1 est injectée chez Yao à 8h00 le jour 1 ; le démenti R2 est publié par le maire à 10h00 le jour 2. Les deux faits circulent et concurrencent.
- **FR-15 (MUST)** : changement de comportement : un agent qui retient R1 avec une crédibilité suffisante peut choisir l'activité « faire des provisions au marché » le vendredi ; on mesure ces changements.
- **FR-16 (SHOULD)** : à la fin de chaque jour, le graphe de propagation (qui a appris quoi, de qui, à quel tick) est exporté.

### 6.6 Réflexion, plans, Gazette

- **FR-17 (SHOULD)** : quand D6 dit oui, Bedrock écrit une réflexion à partir des souvenirs récents les plus importants ; elle est stockée comme mémoire de haut niveau avec une importance élevée.
- **FR-18 (COULD)** : plan du matin écrit par Bedrock (un appel par agent et par jour) ; sinon routines.
- **FR-19 (SHOULD)** : chaque soir, Bedrock écrit la Gazette du Hameau (titre, trois brèves, histoire de la rumeur) à partir d'un résumé structuré du journal, sous la plume de Claire.

### 6.7 Usage de Bedrock et budgets

- **FR-20 (MUST)** : catalogue d'appels : B1 réplique de dialogue, B2 réflexion, B3 plan du matin (optionnel), B4 Gazette, B5 appels de la stratégie tout-LLM (benchmark uniquement).
- **FR-21 (MUST)** : plafond dur par jour simulé et par run (nombre d'appels et de jetons) avec arrêt propre ; compteur de coût estimé calculé depuis les jetons réellement consommés.
- **FR-22 (MUST)** : cassettes : chaque appel est enregistré avec une clé dérivée du modèle, du prompt, des paramètres et de la graine ; en mode rejeu, aucun appel réseau n'est fait.
- **FR-23 (SHOULD)** : un modèle rapide et peu coûteux pour B1 à B3, un modèle plus capable seulement pour B4 ; accès et région à confirmer en Phase 0.

### 6.8 Le viewer web

- **FR-24 (MUST)** : rejeu depuis un fichier de journal : lecture, pause, vitesse, saut dans le temps.
- **FR-25 (MUST)** : carte avec les lieux et les habitants en mouvement ; horloge et jour ; compteurs Decider et LLM ; coût estimé.
- **FR-26 (MUST)** : inspecteur d'agent : persona, activité, souvenirs récents avec importance et pertinence, dernières décisions avec options, probabilités, confiance et zone.
- **FR-27 (SHOULD)** : graphe de la rumeur, Gazette, onglet de comparaison A/B/C avec les graphiques du benchmark.
- **FR-28 (COULD)** : mode direct par WebSocket.
- **FR-29 (SHOULD)** : interface sobre, lisible au clavier, avec contrastes suffisants ; pas de bibliothèque lourde (JavaScript natif et canvas).

### 6.9 Journalisation

- **FR-30 (MUST)** : chaque décision, appel LLM, déplacement, écriture de mémoire, réplique, saut de rumeur et réflexion est écrit dans un journal JSONL horodaté (tick simulé et heure réelle). Les champs exacts sont décrits en section 7.6.

## 7. Spécification technique

### 7.1 Vue d'ensemble

Le système se compose de sept blocs.

- **Moteur de simulation** (Python) : horloge, ordonnanceur à événements, monde, agents, graine.
- **Cognition** : mémoire, récupération (MemoryGate), appels de décision.
- **Service Decider** : serveur local ou processus intégré, avec un faux backend pour les tests.
- **Couche Bedrock via Strands** : agents de dialogue, de réflexion et de Gazette ; cassettes d'appels ; compteur de coût.
- **Instrumentation** : journal JSONL, compteurs, latences, coût.
- **Viewer statique** : lit le journal et le rejoue dans le navigateur.
- **Harnais de benchmark** : lance les stratégies A, B et C, génère tableaux et graphiques.

Flux d'un décision typique : l'ordonnanceur signale qu'un agent doit décider ; MemoryGate présélectionne des souvenirs puis D3 les note ; D1 choisit l'action ; la simulation applique l'action et produit des observations ; D2 note leur importance et elles sont écrites en mémoire ; D4 peut déclencher une conversation (D5 choisit le sujet, Bedrock écrit les répliques, D7 décide de continuer) ; en fin de conversation, D8 et D2 mettent à jour les croyances ; le soir D6 déclenche une réflexion et Bedrock écrit la Gazette ; tout est journalisé.

### 7.2 Pile technique

- Python 3.11 ou plus récent ; environnement virtuel ; versions épinglées dans un fichier de verrouillage (le modèle est expérimental et son API peut évoluer).
- Paquets : strands-decider (installation par pip ; extras selon le matériel), strands-agents (SDK), boto3, pytest, ruff.
- Modèle Decider par défaut : StrandsAgents/strands-decider-2B-hobson-v19, la version publiée avec le billet de lancement. La v21 existe aussi sur Hugging Face et peut être comparée (COULD).
- Stockage : SQLite ou mémoire plus journal JSONL ; pas de base managée.
- Viewer : HTML, JavaScript natif et canvas ; aucun framework ; un seul dossier statique.
- Infrastructure : instance EC2 GPU, S3 et CloudFront pour le viewer, IAM pour Bedrock ; CDK ou Terraform en option (COULD).

### 7.3 Service Decider

- **NFR-T1 (MUST)** : deux modes d'accès : processus intégré (chargement du modèle en Python via le chargeur de la bibliothèque, à vérifier) ou serveur HTTP lancé par la commande strands-decider serve avec le nom du modèle et un port (documenté sur la page PyPI).
- **NFR-T2 (MUST)** : un client maison DeciderClient avec : requêtes groupées (plusieurs questions sur le même état, ce que le modèle fait efficacement), délais maximaux, nouvelles tentatives, cache par empreinte (état, question), journalisation de chaque appel (latence, taille de l'état, probabilités, confiance).
- **NFR-T3 (MUST)** : un faux backend déterministe qui permet de lancer les tests et l'intégration continue sans GPU.
- **NFR-T4 (MUST)** : une première mesure de débit en Phase 0 : requêtes par seconde selon la concurrence, la taille de l'état et le nombre d'options. Ce résultat fixe le nombre d'agents réaliste (voir risque R1).
- La latence augmente environ linéairement avec la taille de la tâche ; les états sont donc volontairement courts et les options bornées.

### 7.4 Hébergement sur AWS

- **Simulation et Decider** : une instance EC2 avec GPU NVIDIA (famille g5 par exemple). Sur un compte neuf, le quota de vCPU pour les instances G peut être à zéro : demander l'augmentation dès la Phase 0, car la validation peut prendre du temps.
- **Repli CPU** : Decider tourne aussi sans GPU (un test publié sur Builder Center l'a fait tourner sur Lambda en CPU), mais plus lentement ; ce repli sert à dépanner, pas à la démonstration finale.
- **Bedrock** : appel depuis la machine de simulation avec un rôle IAM limité à l'invocation des seuls modèles utilisés ; aucune clé dans le dépôt.
- **Viewer** : fichiers statiques et journaux de rejeu dans un bucket S3 derrière CloudFront ; c'est ce lien que les juges ouvrent sans GPU.
- **Contrôle des coûts** : alertes AWS Budgets, arrêt de l'instance quand elle ne sert pas, plafond d'appels Bedrock dans le code.

### 7.5 Intégration Strands

- Les agents génératifs (dialogue, réflexion, Gazette) sont des agents Strands avec un modèle Bedrock.
- MemoryGate s'insère dans le chemin de l'agent par un crochet avant l'appel du modèle (le billet de lancement indique qu'il existe des crochets autour de l'appel du modèle et de toute l'invocation) ou par un greffon d'injection de contexte ; les noms exacts des classes sont à vérifier dans la documentation (rubriques Hooks, Plugins et Context Injector).
- La boucle de simulation reste du Python ordinaire : Decider n'a pas besoin d'être un outil de l'agent pour décider.
- Le billet de lancement note que la bibliothèque officielle d'intégration est encore en préparation : le pattern publié ne doit pas en dépendre.

### 7.6 Schéma du journal d'événements (JSONL)

Chaque ligne contient : horodatage réel, tick simulé, jour, identifiant d'agent, type d'événement et charge utile. Types : decision, llm\_call, move, memory\_write, conversation\_turn, rumor\_hop, reflection, gazette, system.

- **decision** : question (D1 à D8), taille de l'état en jetons, options, option choisie, probabilité de chaque option, confiance, zone (verte, orange, rouge), latence en millisecondes, repli utilisé (oui ou non), stratégie.
- **llm\_call** : usage (B1 à B5), modèle, jetons entrants et sortants, latence, coût estimé, appel rejoué depuis une cassette (oui ou non).
- **memory\_write** : identifiant, type, texte, importance, confiance, identifiant de fait, source, hop.
- **rumor\_hop** : fait, émetteur, récepteur, tick, crédibilité donnée par D8.

Les cassettes sont stockées dans un dossier à part ; la clé d'un appel est l'empreinte du modèle, du prompt, des paramètres et de la graine.

### 7.7 Structure du dépôt

- README.md (installation en moins de dix minutes, démonstration, liens, tags) et LICENSE (Apache-2.0).
- src/hameau/world (monde, horloge, ordonnanceur), agents (persona, état), memory (flux de mémoire, récupération), decisions (client Decider, questions D1 à D8, zones de confiance), llm (agents Strands, cassettes, coûts), scenarios (rumeur, distribution), logging (journal, compteurs).
- patterns/memory\_gate (le pattern réutilisable, autonome, avec son README, ses exemples et ses tests).
- viewer (statique : index, scripts, styles, échantillon de journal).
- bench (stratégies A, B, C, jeux étiquetés, scripts d'évaluation, question lab, résultats en CSV).
- tests (faux Decider, cassettes de test).
- infra (scripts de déploiement, politique IAM d'exemple).
- docs (cahier des charges, notes d'architecture, résultats).

### 7.8 Configuration

Un fichier unique (YAML) décrit : graine, nombre d'agents, stratégie (heuristique, llm, hybride), seuils de confiance par décision, budgets Bedrock, modèles, chemins, mode (direct ou rejeu). Un run est entièrement défini par ce fichier plus la version du code.

## 8. Exigences non fonctionnelles

- **NFR-01 Performance (SHOULD)** : un jour simulé de 25 agents tourne en moins de 15 minutes réelles avec concurrence sur GPU ; à défaut, on réduit le nombre d'agents. Ordre de grandeur à mesurer : quelques milliers de questions Decider par jour simulé (jusqu'à une dizaine de milliers avec les scores de pertinence) contre environ 150 à 200 appels Bedrock (dialogues, réflexions, Gazette).
- **NFR-02 Reproductibilité (MUST)** : même configuration, même graine, mêmes cassettes : même journal, octet pour octet, hors horodatages réels.
- **NFR-03 Coûts (MUST)** : plafonds d'appels Bedrock par run, alertes de budget, instance arrêtée hors usage ; le coût affiché est calculé depuis les jetons réellement consommés avec la grille de prix du jour, jamais inventé.
- **NFR-04 Sécurité (MUST)** : aucun secret dans le dépôt ni dans l'historique ; analyse de secrets avant publication ; rôle IAM minimal ; seuls les fichiers du viewer sont publics.
- **NFR-05 Contenu et vie privée (MUST)** : personnages fictifs, aucune donnée personnelle réelle ; les prompts interdisent les contenus haineux ou dangereux ; garde-fous Bedrock en option ; relecture humaine de la Gazette avant la vidéo.
- **NFR-06 Licences (MUST)** : dépôt sous Apache-2.0 ; liste des dépendances et de leurs licences ; licence du modèle de base Qwen3.5-2B à vérifier ; polices et icônes sous licence permissive ; aucun logo de marque tierce ni musique protégée dans la vidéo.
- **NFR-07 Observabilité (SHOULD)** : compteurs et latences (p50, p95) visibles dans le viewer et exportés en CSV.
- **NFR-08 Maintenabilité (SHOULD)** : tests automatisés avec faux Decider ; revue croisée des modifications ; commits petits.
- **NFR-09 Accessibilité (SHOULD)** : navigation au clavier, contrastes suffisants, vidéo sous-titrée.
- **NFR-10 Honnêteté (MUST)** : aucune affirmation chiffrée dans l'article, la vidéo ou le README sans un fichier de résultats correspondant dans le dépôt.

## 9. Plan d'évaluation et benchmark

### 9.1 Principes

On mesure plutôt qu'on affirme. Chaque résultat est obtenu avec plusieurs graines et publié en médiane avec sa plage, pas en meilleur cas. Les jeux d'étiquettes sont écrits avant de voir les sorties des modèles, par deux personnes, pour éviter de juger les modèles avec leurs propres réponses. Le matériel, les versions et les paramètres sont listés avec chaque tableau. Les mauvais résultats sont publiés.

### 9.2 Les trois stratégies comparées

- **A, heuristique** : routine pour D1, importance par règles selon le type d'événement, pertinence par recouvrement d'entités et récence, pas d'appel LLM de décision.
- **B, tout-LLM** : chaque question que Decider reçoit dans C est posée à Bedrock avec la même information et une sortie contrainte. On teste un modèle rapide et peu coûteux et un modèle plus capable, pour que la comparaison reste équitable.
- **C, hybride (Hameau)** : D1 à D8 par Decider ; Bedrock seulement pour les textes (B1 à B4).

### 9.3 Expériences

- **E1 Importance** : 80 observations étiquetées faible, moyenne ou élevée par deux personnes. Métriques : accord entre étiqueteurs, corrélation de rang de Decider, de Bedrock et de l'heuristique avec les étiquettes.
- **E2 Récupération** : 60 situations avec jusqu'à douze souvenirs candidats ; les étiqueteurs désignent les trois plus pertinents. Métrique : précision@3 pour récence seule, recouvrement d'entités, Decider (D3) et Bedrock.
- **E3 Calibration** : au moins 60 cas étiquetés par question oui/non (D4, D6, D7) et pour D8. Métriques : exactitude par tranche de confiance (cinq tranches), erreur de calibration attendue, courbe couverture contre exactitude. Les seuils haut et bas sont choisis pour atteindre une exactitude cible en zone verte, en rapportant la part de décisions automatiques.
- **E4 Bout en bout (rumeur)** : dix graines pour A et C ; pour B, un village réduit (5 agents, 1 jour, 3 graines) à cause du coût, avec extrapolation déclarée comme telle. Métriques : part du village atteinte, délai, répartition des sauts, adoption du comportement (courses du vendredi), nombre d'appels LLM, jetons, coût, temps réel par jour simulé, latence de décision p50 et p95.
- **E5 Latence et débit** : latence de Decider selon la concurrence, la taille de l'état (jetons) et le nombre d'options (4, 8, 12), sur GPU et sur CPU.
- **E6 Ablations** : sans MemoryGate (récupération par récence seule) ; sans zones de confiance ; sans D3 (recouvrement seul) ; options de D1 à 4, 8 et 12 ; poids de récupération ; v19 contre v21 (COULD).

### 9.4 Le question lab

Un tutoriel publié sur Builder Center a observé que la formulation et la précision de la question changent fortement le résultat, et qu'un montage peut finir par ne rien décider du tout. Le question lab est donc un script qui évalue plusieurs variantes de chaque question sur les jeux étiquetés : formulations, ordre des options (permutations pour détecter un biais de position), longueur des descriptions, polarité de la question. On ajoute un test de retrait : on remplace Decider par la valeur par défaut et on mesure la perte, ainsi que la part des décisions qui diffèrent de la valeur par défaut. Ces deux chiffres répondent à la question qu'un juge posera : est-ce que Decider décide vraiment quelque chose d'utile ?

### 9.5 Cibles indicatives

Ce sont des hypothèses à ajuster après la première mesure, pas des promesses : rapport décisions Decider sur appels LLM d'au moins 20 pour 1 ; précision@3 de D3 à moins de dix points de Bedrock ; exactitude en zone verte d'au moins 90 % avec une couverture d'au moins 60 % sur D4, D6 et D7 ; une différence mesurable de diffusion de la rumeur entre C et l'ablation sans MemoryGate.

### 9.6 Rapport

Les scripts produisent des fichiers CSV et des graphiques. Chaque chiffre de l'article renvoie à un fichier de résultats du dépôt, avec l'identifiant du run, le matériel et les versions.

## 10. Le pattern réutilisable : MemoryGate

C'est l'actif que le règlement exige et qui pèse dans les 30 % d'utilisation efficace. Il doit être utilisable par quelqu'un qui n'a pas lu le reste du dépôt.

- **Emplacement** : dossier patterns/memory\_gate avec un fichier PATTERN.md en tête, clairement étiqueté comme le pattern de décision réutilisable de la soumission.
- **Contenu de PATTERN.md** : nom ; tag #context-memory ; problème résolu ; questions typées et options (importance et pertinence) ; câblage dans l'agent ; mode d'emploi en dix lignes ; seuils et zones de confiance ; limites connues.
- **Interface minimale** : une fonction qui note l'importance d'une observation pour une persona ou un rôle ; une fonction qui classe des souvenirs candidats pour une situation et renvoie les k meilleurs avec pertinence, confiance et zone ; une politique de repli quand la confiance est basse.
- **Câblage Strands** : un crochet (ou greffon) exécuté avant l'appel du modèle, qui lit la situation courante, récupère les candidats dans le magasin de souvenirs de l'agent, appelle Decider, puis injecte les meilleurs dans le contexte du modèle Bedrock. Les noms exacts des classes sont à vérifier en Phase 0.
- **Exemple autonome** : un petit agent Strands de conversation avec mémoire d'environ trente lignes, qui n'a pas besoin de la simulation.
- **Tests** : faux Decider déterministe pour vérifier le classement, les zones et le repli sans GPU.
- **Limites à écrire** : modèle expérimental, états courts, au plus douze candidats par appel, langue testée (anglais et français), seuils à recalibrer sur ses propres données.
- **Pattern secondaire (COULD)** : ActionPicker avec zones de confiance, proposé comme second exemple, sans changer le tag déclaré.

## 11. Livrables du concours

### 11.1 README

Titre et phrase d'accroche ; GIF ou capture ; ce que fait Hameau en cinq lignes ; installation et premier run en moins de dix minutes (rejeu sans GPU ni Bedrock grâce aux cassettes) ; lien vers la démo web ; lien vers MemoryGate ; résultats résumés avec renvoi aux CSV ; limites ; licence ; tags ; liens vers l'article et la vidéo.

### 11.2 Article Builder Center (en anglais, 1 500 à 2 200 mots)

Structure calquée sur le barème pour qu'un lecteur humain ou une IA retrouve chaque preuve.

1. Résumé en cinq lignes et lien vers la démo.
2. Le problème : le coût des agents génératifs quand tout passe par un LLM.
3. Ce qu'est Hameau (images, scénario de la rumeur).
4. Les décisions confiées à Decider : le tableau D1 à D8 avec leurs questions typées.
5. Le pattern MemoryGate : comment le réutiliser (extrait de code court).
6. Résultats : trois stratégies, appels, jetons, coût, latence, matériel ; ablation sans MemoryGate.
7. Qualité et calibration : E1 à E3, zones de confiance, part de décisions automatiques.
8. Quand ça échoue : cas d'échec, faux négatifs, limites du modèle expérimental.
9. Ce que nous avons appris.
10. Liens : dépôt, vidéo, démo. Tags #strands-decider-2b et #context-memory ajoutés.

### 11.3 Vidéo (objectif 2 min 40, jamais plus de 3 min)

- 0:00 à 0:15 — Accroche : le village qui vit, le compteur qui monte, une question : combien d'appels LLM faut-il pour faire vivre un village ?
- 0:15 à 0:40 — Le problème et l'idée : Decider décide vite, Bedrock raconte ; une animation simple en deux boîtes.
- 0:40 à 1:20 — La rumeur : on injecte R1, la carte s'allume, l'inspecteur montre les souvenirs notés et la confiance de chaque choix.
- 1:20 à 1:50 — MemoryGate : les candidats notés, les trois retenus ; écran partagé avec et sans MemoryGate.
- 1:50 à 2:20 — Les chiffres : trois stratégies, coût et appels ; une décision à faible confiance qui bascule sur le repli, montrée sans gêne.
- 2:20 à 2:40 — Réutilisation : le pattern, le dépôt, la démo en ligne, les tags.
- Production : capture d'écran 1080p, voix off en anglais, sous-titres, aucune musique protégée (aucune musique est plus sûr), aucun logo de marque tierce ; export MP4 ; mise en ligne publique sur YouTube ; vérification dans une fenêtre privée.

### 11.4 Liste de contrôle avant soumission

- Profil Builder Center complet ; inscription au hackathon faite ; éligibilité vérifiée (âge, pays, employeur).
- Dépôt public ; licence OSI visible à la racine ; aucun secret ; README à jour ; PATTERN.md présent ; installation testée par une personne extérieure.
- Article publié (pas en brouillon) sur Builder Center, avec les deux tags.
- Vidéo publique de moins de trois minutes, lien testé sans être connecté.
- Tous les liens (dépôt, vidéo, démo) fonctionnent dans une fenêtre privée.
- Chaque chiffre publié renvoie à un CSV du dépôt.
- Sauvegardes : dépôt, vidéo source, journaux et résultats.
- Soumission déposée avant le 23 octobre à midi (Lomé) ; capture d'écran de la confirmation.

## 12. Organisation

### 12.1 Rôles

- **Personne A — moteur, mesure, AWS** : monde, ordonnanceur, journal, benchmark, infrastructure, déploiement du viewer.
- **Personne B — cognition et génération** : mémoire, MemoryGate, questions typées et question lab, agents Strands et Bedrock, pattern réutilisable.
- **Partagé** : viewer (selon les compétences), article, vidéo, étiquetage des jeux de données (deux personnes obligatoires), relecture croisée.
- **Si une seule personne construit** : l'ordre de priorité est pièces éliminatoires, MemoryGate, D1 à D4, benchmark minimal, viewer de rejeu, puis tout le reste (section 5.5). Viser 12 agents.
- Les rôles peuvent être inversés ; l'essentiel est qu'une seule personne soit responsable de chaque pièce.

### 12.2 Rituels et règles de travail

- Point de quinze minutes chaque matin et chaque soir (heure de Lomé) : fait, bloqué, prochain jalon.
- Branche principale protégée, petites branches, revues croisées rapides ; une étiquette de version à la fin de chaque phase (v0.1 à v0.8).
- Une tâche est terminée quand elle a un test ou une mesure, une ligne dans le journal de projet et une trace dans le dépôt.
- **Gel des fonctionnalités le 21 octobre à 20h (Lomé)** : après cette heure, seulement des corrections, de la documentation, l'article et la vidéo.
- Ne pas travailler en continu : viser 8 à 10 heures de travail par jour et dormir ; les erreurs de la dernière nuit coûtent plus que les fonctionnalités qu'elle ajoute.

## 13. Feuille de route détaillée

Toutes les heures sont données à Lomé (UTC+0). Les durées sont des estimations de travail à deux personnes ; elles ne sont pas des garanties.

### Phase 0 — Préparation (13, 14 et 15 octobre)

Pas de code du projet : seulement de l'installation, de la lecture, des essais jetables non commités et de l'écriture de contenu.

1. Lire le règlement ensemble, s'inscrire au hackathon, vérifier profil Builder Center, âge, pays, employeur (30 min).
2. Poser la question de la règle équipe sur le Discord Strands ou la page du hackathon ; décider qui dépose la soumission (30 min).
3. Compte AWS : alerte AWS Budgets, utilisateur ou rôle IAM, région ; demande d'accès aux modèles Bedrock ; invocation de test (1 à 2 h).
4. **Demander l'augmentation de quota des instances GPU (famille G)** dès le premier jour (30 min de travail, puis attente).
5. Installer strands-decider ; lancer la commande d'exemple de choix ; essayer dix questions de type D1 à D3 à la main (2 h).
6. Lire l'exemple examples/strands du dépôt Decider et les rubriques Hooks, Plugins et Bedrock de la documentation Strands ; noter les noms exacts d'API (2 h).
7. Mesure jetable de débit : états de 300 mots, huit options, concurrence 1, 4 et 8, sur le matériel disponible ; déduire le nombre d'agents réaliste (2 h).
8. Écrire sans code les personas des douze habitants, les lieux, la rumeur R1 et le démenti R2 (2 à 3 h).
9. Relire Builder Center et le dépôt Decider pour reconfirmer l'originalité (30 min).
10. Choisir la région, les modèles Bedrock, le nom du dépôt, la licence ; préparer les outils de capture vidéo et un compte YouTube (1 h).

**Critères de sortie de la Phase 0** : Decider répond en local ; Bedrock répond ; le débit est connu ; le GPU est accessible ou un plan B est choisi ; la règle équipe est claire.

### Phase 1 — Vendredi 16 octobre (après 16h) : squelette et première décision

- 16h00 à 16h30 : créer le dépôt public (licence, README minimal, configuration de tests) ; premier commit.
- 16h30 à 19h00 : monde en graphe, horloge, ordonnanceur à événements, journal JSONL (A). En parallèle : DeciderClient, faux backend, décision D1 (B).
- 19h00 à 21h00 : trois agents qui se déplacent ; viewer minimal avec des points sur une carte qui rejoue le journal.
- 21h00 à 22h00 : démonstration interne.
- **Jalon M1** : trois agents bougent selon des choix réels de Decider, journalisés avec probabilités et confiance.
- **Porte G1** : si D1 est inutilisable (latence ou choix incohérents), on retravaille la formulation et réduit les options avant de continuer.

### Phase 2 — Samedi 17 octobre : mémoire et MemoryGate

- Matin : modèle de mémoire, écriture des observations, D2 pour l'importance.
- Midi : récupération en trois temps (présélection, D3, score final) ; injection des trois souvenirs dans D1.
- Après-midi : passage à 12 agents, routines, besoins ; viewer : horloge, compteurs et inspecteur v1.
- Soir : écriture des jeux étiquetés E1 et E2 (une moitié chacun).
- **Jalon M2** : douze agents vivent une journée complète sans aucun LLM de décision ; les compteurs montent.

### Phase 3 — Dimanche 18 octobre : Bedrock, conversations, rumeur

- Matin : couche Strands et Bedrock, cassettes, budgets, coût estimé.
- Midi : D4, D5 et D7 ; conversations de six répliques au plus ; mises à jour structurées ; rumeur R1 ; D8.
- Après-midi : D6 et réflexions ; Gazette.
- Soir : premier run de trois jours simulés avec 12 agents ; revue des journaux.
- **Jalon M3** : la rumeur se propage, la Gazette se génère, tout est rejouable.
- **Porte G2** : si la rumeur ne se propage pas ou ne change aucun comportement, on simplifie le mécanisme (plus de poids sur D5 et D8) avant la mise à l'échelle.

### Phase 4 — Lundi 19 octobre : échelle et lignes de base

- Matin : serveur Decider sur l'instance GPU, concurrence et requêtes groupées ; passage à 25 agents si le débit le permet.
- Après-midi : stratégies A et B ; squelette du harnais de benchmark.
- Soir : étiquetage terminé par les deux personnes pour E1, E2 et E3.
- **Jalon M4** : 25 agents sur 3 jours simulés en moins d'une heure ; les trois stratégies s'exécutent.
- **Porte G3** : si le débit est insuffisant, on reste à 12 agents et on le dit dans l'article.

### Phase 5 — Mardi 20 octobre : mesures

- Matin : E1, E2 et question lab ; ajustement des formulations.
- Midi : E3 (calibration), seuils et zones de confiance, repli.
- Après-midi : E4 avec plusieurs graines, E5, E6.
- Soir : fixer la configuration de référence et enregistrer le run officiel (journal et cassettes).
- **Jalon M5** : tous les chiffres existent en CSV.
- **Porte G4** : si les résultats sont faibles, on recentre l'article sur la méthode, les limites mesurées et le pattern ; on ne gonfle jamais un chiffre.

### Phase 6 — Mercredi 21 octobre : gel et packaging

- Matin : polissage du viewer (graphe de rumeur, comparaison, Gazette) ; déploiement sur S3 et CloudFront.
- Midi : MemoryGate packagé (PATTERN.md, exemple autonome, tests).
- Après-midi : README, nettoyage, analyse de secrets, licences ; relecture à froid : une personne extérieure installe et lance le projet en dix minutes.
- Soir : **gel des fonctionnalités à 20h** ; premier brouillon de l'article avec chiffres et figures.
- **Jalon M6** : dépôt propre et démonstration en ligne.

### Phase 7 — Jeudi 22 octobre : contenu

- Matin : article finalisé en anglais, figures, relecture croisée.
- Après-midi : enregistrement de la vidéo (deux ou trois prises), montage, sous-titres ; vérification de la durée, des logos et de la musique.
- Soir : mise en ligne publique de la vidéo ; article préparé sur Builder Center avec les deux tags ; test de tous les liens en fenêtre privée.
- **Jalon M7** : tous les livrables existent.

### Phase 8 — Vendredi 23 octobre : marge et soumission

- Matin : corrections finales ; liste de contrôle (section 11.4) ; **soumission avant midi (Lomé)** ; capture de la confirmation.
- Après-midi et soir : marge de sécurité (la limite est le 24 octobre à 06h59 à Lomé) ; aucune nouvelle fonctionnalité ; contrôle que tous les liens restent publics ; sauvegardes.

### Après la soumission

Surveiller l'adresse e-mail du profil Builder Center ; garder disponibles les justificatifs d'éligibilité (le règlement prévoit une vérification des finalistes) ; ne pas modifier le dépôt de manière qui change les résultats publiés pendant les phases de jugement ; arrêter l'instance GPU.

## 14. Registre des risques

Chaque risque a une probabilité (P) et un impact (I) évalués en faible, moyenne ou élevée, une parade et un plan B.

- **R1 — Débit insuffisant de Decider (P moyenne, I élevé)** : trop de décisions par jour simulé pour le matériel. Parade : ordonnancement par événements, états courts, options bornées à huit, requêtes groupées, concurrence, mesure dès la Phase 0. Plan B : 12 agents et moins de jours simulés, annoncés dans l'article.
- **R2 — Quota GPU non accordé (P moyenne, I élevé)** : Parade : demande le premier jour. Plan B : machine locale avec GPU, ou exécution CPU plus lente avec moins d'agents et un journal enregistré pour le rejeu.
- **R3 — Scores mal calibrés ou instables (P élevée, I moyen)** : le modèle est expérimental. Parade : question lab, permutations d'options, seuils calibrés sur données étiquetées, repli déterministe. Plan B : publier la limite et montrer le repli comme résultat.
- **R4 — Decider ne décide rien d'utile (P moyenne, I élevé)** : ses choix coïncident toujours avec la valeur par défaut. Parade : test de retrait et part de décisions différentes de la routine, mesurés dès la Phase 2. Plan B : durcir les situations où le choix compte (conflit entre routine et information reçue).
- **R5 — La rumeur ne se propage pas ou ne change rien (P moyenne, I élevé)** : Parade : mécanisme structuré de transmission, relations qui favorisent le bouche-à-oreille, réglage de D5 et D8. Plan B : scénario plus simple (information utile au lieu de rumeur) sans changer l'architecture.
- **R6 — Le viewer dévore le temps (P élevée, I moyen)** : Parade : JavaScript natif, graphe de lieux, pas d'animation coûteuse. Plan B : viewer minimal (carte, compteurs, inspecteur) et graphiques statiques exportés des CSV.
- **R7 — Coûts Bedrock et AWS (P moyenne, I moyen)** : Parade : plafonds dans le code, cassettes, alertes de budget, instance arrêtée hors usage. Plan B : modèle plus petit pour les textes.
- **R8 — Limitation de débit Bedrock (P moyenne, I moyen)** : Parade : file d'attente, nouvelles tentatives avec délai, cassettes. Plan B : réduire le nombre de dialogues.
- **R9 — API expérimentale qui change (P moyenne, I moyen)** : Parade : versions épinglées, couche d'abstraction DeciderClient. Plan B : figer la version du modèle et de la bibliothèque dès le 16 octobre.
- **R10 — Règle sur les équipes (P moyenne, I élevé)** : le règlement parle d'une entrée par personne et ne décrit pas les équipes. Parade : poser la question en Phase 0. Plan B : une personne dépose la soumission, les contributions de l'autre sont créditées dans le dépôt et l'article.
- **R11 — Fuseau horaire et échéance (P faible, I élevé)** : Parade : cible de soumission le 23 octobre à midi (Lomé) ; délai réel le 24 octobre à 06h59 (Lomé).
- **R12 — Vidéo trop longue ou problème de droits (P moyenne, I élevé)** : Parade : storyboard à 2 min 40, aucune musique, aucun logo tiers, vérification en fenêtre privée.
- **R13 — Une autre soumission ressemble à Hameau (P moyenne, I moyen)** : Parade : relire Builder Center le 16 octobre ; renforcer ce qui distingue Hameau (ablation, calibration, pattern réutilisable, démo en ligne).
- **R14 — Texte généré incohérent ou inapproprié (P moyenne, I moyen)** : Parade : faits structurés fournis au modèle, consignes de contenu, relecture humaine de la Gazette avant la vidéo, garde-fous Bedrock en option.
- **R15 — Fatigue et surcharge (P élevée, I moyen)** : Parade : gel des fonctionnalités, ordre de coupe, journées limitées, marge du 23 octobre.
- **R16 — Perte de données ou de liens (P faible, I élevé)** : Parade : dépôt distant, sauvegarde de la vidéo source, copie des résultats, test des liens en fenêtre privée.
- **R17 — Licence du modèle de base (P faible, I moyen)** : Parade : vérifier la licence de Qwen3.5-2B-Base en Phase 0 et la mentionner dans le dépôt.

## 15. Décisions ouvertes à trancher avant le 16 octobre

1. **Règle équipe** : qui dépose la soumission, et la participation à deux est-elle acceptée par l'organisateur ?
2. **Région AWS et modèles Bedrock** : lesquels, selon l'accès, les quotas et les prix du jour.
3. **Matériel de démonstration** : instance GPU EC2, machine locale avec GPU, ou repli CPU.
4. **Nombre d'agents final** : 12 ou 25, décidé après la mesure de débit (porte G3).
5. **Langue des livrables** : anglais recommandé pour l'article, la vidéo et le README ; version française du README en option.
6. **Modèle Decider** : v19 par défaut ; comparer ou non avec v21.
7. **Stratégie B** : quel modèle Bedrock sert de ligne de base équitable (un rapide et un plus capable).
8. **Infrastructure en code** : CDK ou scripts simples.
9. **Nom du dépôt et identité visuelle** : nom, palette, polices libres de droits.

## 16. Annexes

### Annexe A — Brouillons des questions typées (en anglais)

Les formulations ci-dessous sont des points de départ à passer au question lab. Le modèle lit un état en texte puis la question et ses options ; l'API exacte de déclaration des questions est à vérifier dans l'exemple officiel.

- **État type** : deux lignes de persona ; heure et lieu ; besoins ; intentions restantes ; trois souvenirs ; personnes présentes. Cent cinquante à trois cents mots au plus.
- **D1 (choix)** : What is the best next activity for this person right now ? Options : continue\_current (keep doing what they are doing) ; go\_to\_\<place> (walk to that place) ; do\_routine (do the usual task of this place) ; talk\_to\_\<name> (start a conversation with that person) ; rest (take a short break).
- **D2 (score)** : How much does this event matter to this person's goals, relationships or worries ? 0 means trivial, 1 means life-changing.
- **D3 (score)** : How useful is this memory for deciding what this person does or says right now ? 0 means useless, 1 means essential.
- **D4 (oui ou non)** : Does this person want to start a conversation with \<name> right now ? true : they want to talk ; false : they prefer to keep to themselves.
- **D5 (score)** : How worth telling \<name> is this memory ? 0 means not worth mentioning, 1 means they must hear it.
- **D6 (oui ou non)** : Is it time for this person to reflect on what happened recently ? true : yes, step back ; false : keep going.
- **D7 (oui ou non)** : Should the conversation continue after this last line ? true : there is more to say ; false : it has naturally ended.
- **D8 (score)** : How credible is this information, given who said it and what this person already knows ? 0 means not credible, 1 means fully credible.

### Annexe B — Modèles de prompts Bedrock

- **B1, réplique** : fournir la persona, le lieu, l'interlocuteur, les trois souvenirs retenus, le fait à transmettre (identifiant et phrase) et les répliques déjà dites ; imposer une réplique de quarante mots au plus, dans le caractère du personnage, sans inventer de nouveau fait.
- **B2, réflexion** : fournir les souvenirs récents les plus importants ; demander deux ou trois idées de haut niveau en une phrase chacune, fondées uniquement sur ces souvenirs.
- **B4, Gazette** : fournir un résumé structuré du jour (faits, transmissions, changements de comportement, chiffres) ; demander un titre, trois brèves et l'histoire de la rumeur, ton neutre et chaleureux, sans contenu offensant ni invention.
- **Paramètres** : température basse, longueur maximale stricte, graine enregistrée quand le service le permet, cassette systématique.

### Annexe C — Aide-mémoire de commandes (documentées publiquement)

- Installer : pip install strands-decider (extras selon le matériel, par exemple mlx pour un Mac ou vision pour les images, hors périmètre ici).
- Poser une question de choix en ligne de commande : strands-decider ask \<modèle> avec un état et une option de choix du type Question=a,b,c ; la sortie donne le choix, la confiance et la probabilité de chaque option.
- Lancer le serveur local : strands-decider serve \<modèle> avec un port.
- Modèle par défaut du projet : StrandsAgents/strands-decider-2B-hobson-v19.

### Annexe D — Modèles de jeux étiquetés

- **E1** : colonnes identifiant, persona, observation, étiquette 1 (faible, moyenne, élevée), étiquette 2, remarque.
- **E2** : colonnes identifiant de situation, texte de la situation, liste de douze souvenirs candidats, trois souvenirs les plus pertinents selon l'étiqueteur 1, selon l'étiqueteur 2.
- **E3** : colonnes identifiant, question (D4, D6, D7 ou D8), état, réponse attendue.
- Les deux étiqueteurs travaillent séparément ; les désaccords sont résolus ensemble et comptabilisés.

### Annexe E — Glossaire

- **Decider 2B** : petit modèle de décision (choix, oui ou non, score) avec confiance calibrée, sans génération de texte.
- **Système 1 et système 2** : décisions rapides et fréquentes (Decider) contre raisonnement ou texte rare et coûteux (Bedrock).
- **Tick** : pas de simulation, cinq minutes simulées.
- **Cassette** : enregistrement d'un appel Bedrock rejoué sans réseau.
- **Zone verte, orange, rouge** : niveaux de confiance qui déterminent si la décision est appliquée, signalée ou remplacée par un repli.
- **Ablation** : retirer un composant pour mesurer ce qu'il apporte.
- **MemoryGate** : pattern réutilisable qui note l'importance des observations et la pertinence des souvenirs.
- **Hop** : nombre de transmissions d'une information depuis sa source.

*Fin du document. Version 1.0 du 13 octobre 2026 : à relire à deux, à corriger après la Phase 0 et à figer le 16 octobre.*
