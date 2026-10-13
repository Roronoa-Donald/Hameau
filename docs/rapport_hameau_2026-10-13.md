# HAMEAU — Rapport d'audit et feuille de route « wow »

*13 octobre 2026 · sources : capture `test-jour1.png`, lecture du code, 3 mesures réelles, revue de code, audit sécurité, recherche web.*

> [!IMPORTANT]
> **Verdict** : l'architecture est saine et le squelette tourne, mais **le cœur de la promesse ne fonctionne pas encore**. Le jour 2 est gelé, la rumeur ne se propage pas, le ratio Decider/LLM est de 4:1 (cible 20:1), et le vrai Decider n'a jamais été validé dans la simulation. Rien d'irrattrapable : tout est corrigeable en 2 à 3 jours de travail ciblé.

---

## 1. Analyse de la capture `test-jour1.png`

| Constat visible | Diagnostic |
|---|---|
| Tick 192/192, 22:00, mais **Flux d'activité vide** | Le flux n'affiche que les événements du tick courant ; en fin de replay il est vide. Il faut un historique persistant. |
| Yao « Stocke des vivres » **alors que la rumeur n'est jamais passée par un autre agent** | Le badge se déclenche dès la crédibilité 85 % injectée à la main : aucun effet émergent. |
| « Action en cours : *commence sa journée* » figé | `currentAction` n'est jamais mis à jour par le viewer. |
| **Souvenirs notés (MemoryGate) : vide** | La section existe dans le HTML mais n'est jamais alimentée : l'argument central du projet est invisible. |
| Noms des agents qui se **chevauchent** (Ibrahim/Claire, Mariam/Samuel…) | Placement en cercle de 32 px, pas d'anti-collision ni de zoom. |
| Libellés de lieux surdimensionnés, flous | Polices en `var(--font-ui)` non résolues dans le canvas + mise à l'échelle `dpr` incohérente. |
| Mention « ~100 ms · Local GPU » | **Texte codé en dur**, faux (voir §2.3). |
| Ratio **3,4 : 1**, 103 décisions / 30 appels | Très loin du 20:1 promis ; les 103 ne sont que des D1. |
| Aucune carte « maison », ni sprites, ni jour/nuit | Esthétique « dashboard sombre » correcte mais générique : pas d'effet *wow*. |

---

## 2. Défauts mesurés (preuves exécutées)

### 2.1 🔴 Le jour 2 est entièrement gelé
Test : simulation 2 jours → **517 décisions D1 au jour 1, 0 au jour 2**.
Cause : `tick` repart à 0 chaque jour alors que `action_end_tick` est absolu (~190). → Le démenti R2 est injecté mais **personne n'agit ni ne parle**.
*Fix* : tick global (`day*192+tick`) partout, y compris MemoryGate (récence fausse aussi).

### 2.2 🔴 La rumeur ne se propage pas
Même test : **2 `rumor_hop` seulement (les 2 injections), 1 agent détient R1, 1 détient R2.**
Causes : aucune observation n'est écrite en mémoire (FR-10 absent), D5 n'est évalué que si l'orateur a des souvenirs, une seule paire par lieu et par tick, conversations de 2 répliques fixes, D7 jamais appelé.
Le scénario phare (« la rumeur change les comportements ») **n'existe donc pas** à ce stade.

### 2.3 🔴 Le vrai Decider n'est pas ce qu'on croyait
Mesure sur ta RTX 3050 (modèle v21, 3,9 Go VRAM) :
- **Latence : ≈ 2,9 s par lot** (pas ~100 ms) → `causal_conv1d` et `flash-linear-attention` absents ⇒ repli PyTorch lent (warnings transformers).
- **Scores hors échelle** : D2 = 1,70 (échelle 0–4), D3 = 1,20 (0–3). `read_score` renvoie un *indice de niveau attendu*, que le code traite comme un 0–1. En mode réel : crédibilité D8 presque toujours « ≥ 0,55 » ⇒ tout le monde croit tout, importance faussée dans MemoryGate.
- Estimation : 1 700 décisions / 2 jours ≈ des heures de calcul au rythme actuel.

*Fix* : normaliser `score/(L-1)`, installer `flash-linear-attention` (à tester), regrouper **toutes** les questions d'un agent en un seul `ask` (le modèle encode l'état une fois), cache par empreinte.

### 2.4 🟠 Intégrité du comptage (la métrique vedette)
- Seul D1 est journalisé ; D2/D3/D4/D5/D6/D8 sont **comptés mais invisibles** dans le JSONL. Le « ratio » n'est pas reproductible.
- `latency_p50` est en réalité une moyenne.
- `load()` retombe silencieusement sur le mock si le GPU échoue : un « vrai » run peut être un faux sans alerte.
- Mock non déterministe (`hash()` salé par processus) → viole NFR-02 (reproductibilité).
- Zones de confiance appliquées seulement à D1/D4 ; pour les questions oui/non le seuil 0,65 exige p > 0,825 : D4 n'est **jamais vert** en mock.

### 2.5 🟠 Réalisme de la simulation
Énergie/faim/besoin social ne varient jamais ; pas de sommeil ni de nuit ; durée d'action aléatoire indépendante de l'action ; mêmes agents peuvent parler à chaque tick ; Bedrock **invente des personnages** (« Monsieur Dupont » dans la Gazette) faute de liste d'entités fournie.

### 2.6 🟠 Écarts avec le cahier des charges
| Exigence | État |
|---|---|
| Intégration **Strands** (agents Bedrock + hook MemoryGate) | ❌ boto3 direct, aucun `strands.Agent` ni `HookProvider` |
| 25 agents (cible) / 12 (MVP) | 12 seulement |
| D5–D8 actifs, zones pour toutes les décisions | partiel (D7 jamais appelé) |
| Bench A/B/C, E1–E6, question lab, calibration | ❌ aucun dossier `bench/` |
| Ablation « sans MemoryGate » | ❌ |
| Cassettes de référence versionnées | ❌ (gitignorées) |
| Viewer : comparaison A/B/C, graphe de rumeur réel | graphe = simple liste |
| Déploiement S3/CloudFront, README <10 min, article, vidéo | ❌ |
| Tests multi-jours / déterminisme / complétude du journal | ❌ (tests actuels passent à côté de tous les bugs ci-dessus) |

---

## 3. Sécurité (audit dédié)

| Gravité | Constat | Correctif |
|---|---|---|
| 🔴 Haute | `--serve` lie `0.0.0.0` et sert **tout le dépôt** (`.git/config`, `config.yaml`, cassettes) | `127.0.0.1`, servir seulement `viewer/` |
| 🔴 Haute | **XSS** : `innerHTML` avec texte LLM/JSONL (`utterance`, `text`, `zone`…) dans `app.js:340,411,439` | `textContent`/échappement + liste blanche de `zone`, CSP |
| 🟠 Moy. | Cassettes non validées (empoisonnement → XSS + injection mémoire) | Valider schéma/longueurs, écriture atomique |
| 🟠 Moy. | Injection de prompt via mémoire d'agent | Délimiter « observations non fiables », plafonner les longueurs |
| 🟠 Moy. | Garde-fou budget : vérif. *avant* appel, par processus, pas de cap d'entrée, pas de retry/timeout | Estimation préalable, ledger persistant, `Config(retries, read_timeout)` |
| 🟡 Basse | Dépendances sans bornes hautes ; modèle HF non épinglé ; polices Google externes | `uv.lock` (déjà là), `revision=<sha>`, polices auto-hébergées |
| ✅ | **Aucun secret dans l'historique git** (vérifié), `yaml.safe_load`, pas d'outils côté Bedrock | — |

IAM recommandé (moindre privilège) : `bedrock:InvokeModel` sur `arn:aws:bedrock:us-east-1::foundation-model/amazon.nova-micro-v1:0` uniquement + AWS Budget à 5 $.

---

## 4. Recherches web — ce que font les meilleurs

> [!NOTE]
> Les recherches ont été menées par un sous-agent avec la seule recherche web : les points marqués *[à vérifier]* doivent être confirmés sur les pages officielles avant publication dans l'article.

**Simulations de référence**
- **Generative Agents / Smallville** (Park et al., 2023, arxiv 2304.03442) : mémoire + réflexion + replay scrubber ; la fête de la Saint-Valentin démontre la diffusion d'information.
- **AI Town** (a16z, github.com/a16z-infra/ai-town) : PixiJS, tilemap pixel-art, clic sur un agent → panneau mémoire/chat, sprites animés.
- **Project Sid / Altera** (arxiv 2411.00114) : architecture « modules rapides + LLM lent » = exactement notre Decider + Nova ; mesure spécialisation de rôles et transmission culturelle.
- **Concordia** (DeepMind) : *Game Master* arbitre → idée : un contrôle de plausibilité oui/non par Decider.
- **OASIS** (CAMEL-AI, arxiv 2411.11581) : diffusion de rumeurs à grande échelle, polarisation.

**Mesurer la diffusion (ce qui rend un projet « scientifique »)**
Courbe d'informés en S, **modèle SIR superposé** (S=n'a pas entendu, I=propage, R=a entendu et s'est tu), R0, arbre de cascade, **mutation de la rumeur par saut** (jeu du téléphone), centralité/ponts/super-propagateurs, moyenne ± IC sur N graines.

**Decider (README, à vérifier)** : calibration ECE ≈ 0,05 ; ~115 ms sur RTX 3090 *avec noyaux optimisés* ; seuils proposés : agir seul > ~0,95, repli/escalade < ~0,6 ; **plusieurs questions sur un même état ≈ coût marginal faible** ; questions courtes, fermées, options distinctes, tout le contexte dans l'état.

**Strands hooks** : `HookProvider` + `registry.add_callback(BeforeModelCallEvent, …)` (ou `BeforeInvocationEvent` pour une injection par tour), `event.agent.messages`/`system_prompt` modifiables. Option AgentCore Memory (`AgentCoreMemorySessionManager`) comme backend optionnel.

**Prix Bedrock (à vérifier)** : Nova Micro 0,035/0,14 $ par M tokens ; Nova Lite 0,06/0,24 ; batch ≈ −50 % ; Guardrails (`ApplyGuardrail`) ; Nova Canvas ≈ 0,04–0,08 $/image → **12 portraits ≈ 0,5–1 $ une fois**, servis en statique.

**Ce que montrent les projets gagnants de hackathons AWS** : hook de 15 s, démo en ligne sans installation, schéma d'architecture, **tableau coût/latence chiffré**, dépôt « une commande », section limites honnête, article de build.

---

## 5. Ce qui est banal aujourd'hui

1. Viewer = dashboard sombre à cercles et emojis, sans personnalité visuelle.
2. Dialogues LLM génériques sans mémoire visible, sans conséquence.
3. Le « wow » (compteur) affiche un ratio médiocre et un label « 100 ms » faux.
4. Aucune interaction du spectateur (on ne peut ni injecter une rumeur, ni la démentir).
5. Aucune expérience contrôlée : pas d'ablation, donc pas de preuve que Decider/MemoryGate servent à quelque chose.

---

## 6. Feuille de route priorisée

### Phase A — Rendre le projet **vrai** (indispensable, ~1,5 jour)
1. Tick global + reset des états de jour ; test 2 jours (« D1 jour 2 > 0 »).
2. `_format_answer` : normaliser les scores ; zones + repli pour **toutes** les décisions ; fin du fallback mock silencieux.
3. Journaliser **chaque** décision et appel LLM (`decision`, `llm_call`) ; ratio recalculé depuis le journal.
4. Observations écrites en mémoire (arrivée, vu, entendu) ; D5/D7 réels ; besoins qui évoluent + sommeil/nuit ; occupation après conversation.
5. Tester le Decider réel : installer `flash-linear-attention`, regrouper les questions par agent, mesurer p50/p95 réels (dire la vérité dans l'article).
6. Mock via `hashlib` (déterminisme, test avec deux `PYTHONHASHSEED`).
7. Fournir à Nova la **liste fermée des entités** (fin des « Monsieur Dupont »).

### Phase B — Rendre le projet **conforme et prouvé** (~1 jour)
8. `MemoryGate` en **vrai `HookProvider` Strands** + agents de dialogue/Gazette via `strands.Agent` (exigence du concours).
9. Dossier `bench/` : stratégies A (heuristique) / B (tout-LLM Nova) / C (hybride) ; **ablation sans MemoryGate** (récence seule) ; E3 calibration ; CSV + graphiques.
10. Corrections sécurité (serveur local, XSS, CSP, validation cassettes, budget pré-vol).
11. Passage à 25 agents (13 de plus générés depuis modèles) si le débit le permet.

### Phase C — Les fonctions **épatantes** (par rapport effet/coût)
| # | Fonction | Pourquoi ça claque | Coût |
|---|---|---|---|
| 1 | **Courbe SIR + graphe d'influence animé** (d3-force) : un lien clignote à chaque ragot, nœuds colorés S/I/R | Rend la diffusion *visible et scientifique* | faible |
| 2 | **Mode « Double-vue »** : même village, même graine, avec/sans MemoryGate côte à côte | La preuve par l'ablation en une image de vidéo | moyen |
| 3 | **Mutation de la rumeur** : diff de texte par saut (« fermer le marché » → « marché détruit ») + score Decider « déformation » | Effet « jeu du téléphone », très partageable | faible |
| 4 | **Hésitation visible** : bulle « … ? » + jauge de confiance ; zone rouge → l'agent « demande conseil » (escalade Nova) | Rend la confiance calibrée tangible (H2) | faible |
| 5 | **Intervention du spectateur** : bouton « Injecter une rumeur / Publier un démenti » en direct | Interactivité = mémorabilité | moyen |
| 6 | **Compteur coût/latence en temps réel** avec comparaison « si tout était LLM : N appels, X $ » | Chiffre-clé du barème (30 %) | faible |
| 7 | **Carte tilemap pixel-art** (Kenney CC0 / Tiled), sprites marchant en interpolation, cycle jour/nuit | Passage de « dashboard » à « petit monde » | moyen |
| 8 | **Portraits Nova Canvas** générés une fois (≈ 1 $) + **Gazette illustrée** | Humanise les 12 habitants | faible |
| 9 | **Guardrails Bedrock** : « rumeur toxique bloquée » | Démo sécurité à bas coût | faible |
| 10 | **Heatmap des lieux** (où se concentrent les ragots) + super-propagateurs | Insights de réseau | faible |
| 11 | **Replay partageable** (lien avec `#tick=…&agent=…`) hébergé S3/CloudFront | Les juges ouvrent sans GPU (O6) | faible |
| 12 | **Accessibilité** : légende `aria-live`, clavier complet, palette Okabe-Ito, `prefers-reduced-motion`, table de données alternative | Critère qualité + différenciant | faible |
| 13 | AgentCore Memory en backend optionnel | Coche l'écosystème AWS | moyen |
| 14 | Voix (Nova Sonic) pour la Gazette | Gadget ; **à écarter** (effort/valeur) | élevé |

**Slogan chiffré à viser (à n'écrire que si mesuré)** : « *X % des décisions prises localement en Y ms, Nova Micro seulement pour Z textes rares, coût total du run : 0,0N $* ».

---

## 7. Plan 3 jours recommandé

| Jour | Objectif | Livrable testable |
|---|---|---|
| **J1** | Phase A complète | `pytest` vert avec tests 2-jours, déterminisme, complétude du journal ; rumeur atteignant ≥ 8/12 agents ; vrai Decider chronométré |
| **J2** | Phase B + Phase C n°1, 2, 4, 6 | Bench A/B/C + ablation en CSV ; hook Strands ; viewer avec SIR + comparaison |
| **J3** | Phase C n°3, 7, 11, 12 + déploiement + README + article + vidéo | Lien public, vidéo < 3 min, dépôt propre, tags |

> [!WARNING]
> Ne publie **aucun chiffre** (« 100 ms », « 20:1 ») avant J1 : les valeurs actuelles sont fausses ou non mesurées (NFR-10 du cahier des charges).

## 8. Décision attendue
Je recommande de lancer **la Phase A immédiatement** (elle conditionne tout le reste). Dis-moi si je pars dessus, et si je dois viser **12 agents solides** ou **25 agents** (la latence réelle du Decider tranchera).
