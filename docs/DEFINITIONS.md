# Définitions Canoniques des Métriques — Projet HAMEAU

Ce document fixe les définitions strictes et univoques des termes et métriques utilisés dans l'ensemble des expériences, du visualiseur, du README et de l'article Builder Center.

---

## 1. Décisions et Inférences Strands Decider 2B

* **Question Decider ($Q$)** :
  Une question élémentaire typée posée au modèle System One (Strands Decider 2B). Chaque question correspond à un gabarit formel parmi D1 à D9 :
  * **D1 — ActionPicker** (`ChoiceQuestion`) : choix de l'action ou destination parmi un ensemble discret.
  * **D2 — ImportanceScorer** (`ScoreQuestion`) : évaluation de l'importance intrinsèque d'une observation sur une échelle discrète de 1 à 5.
  * **D3 — RelevanceScorer** (`ScoreQuestion`) : évaluation de la pertinence d'un souvenir candidat dans un contexte donné (échelle 1 à 4) au sein du composant MemoryGate.
  * **D4 — TalkGate** (`NoulQuestion` / binaire) : décision d'engager ou non la conversation avec un agent co-localisé.
  * **D5 — ShareScorer** (`ScoreQuestion`) : sélection des souvenirs à partager lors d'un échange (échelle 1 à 4).
  * **D6 — ReflectGate** (`NoulQuestion` / binaire) : décision de déclencher une introspection synthétique du soir.
  * **D7 — ContinueGate** (`NoulQuestion` / binaire) : décision de poursuivre ou clore un échange verbal.
  * **D8 — CredibilityGate** (`ScoreQuestion`) : évaluation de la crédibilité accordée à une information reçue (échelle 1 à 5).
  * **D9 — VoteChoice** (`ChoiceQuestion`) : vote individuel lors du scrutin municipal du Jour 3 à 17h00 (`kofi`, `victor` ou `abstention`), conditionné par le top-3 des souvenirs sélectionnés par MemoryGate.

* **Requête Decider ($R$)** :
  Un appel unique d'inférence (local ou via HTTP `/v1/systemone`). Une requête Decider comprend un état contextuel unique (`state`) et un dictionnaire d'une ou plusieurs questions Decider typées ($\ge 1$). Par exemple, l'évaluation de 4 souvenirs dans MemoryGate peut être groupée en 1 seule requête Decider portant 4 questions D3.

---

## 2. Générations et Appels Amazon Bedrock

* **Appel LLM ($L$)** :
  Une invocation effective de l'API Amazon Bedrock (`amazon.nova-micro-v1:0` via Converse API). Les appels LLM sont strictement réservés aux tâches de génération ouverte :
  * **B1** : Réplique de conversation naturelle entre deux villageois.
  * **B2** : Réflexion synthétique introspective de fin de journée.
  * **B4** : Rédaction quotidienne de « La Gazette du Hameau ».
  *(Note : Toute décision de contrôle, de filtrage ou de routage est interdite au LLM et réservée au Decider 2B ou à des règles déterministes).*

---

## 3. Ratios Hybrides (Double Métrique Obligatoire)

Pour éviter toute ambiguïté ou gonflement artificiel des ratios, deux métriques distinctes doivent être systématiquement publiées côte à côte :

1. **Ratio Questions / Appel LLM ($Q / L$)** :
   $$\text{Ratio}_{Q/L} = \frac{\text{Nombre total de questions Decider typées } (D_1 \dots D_8)}{\max(1, \text{Nombre total d'appels Bedrock LLM})}$$
   *Représente le nombre d'arbitrages cognitifs pris par le modèle 2B pour chaque réplique ou texte généré par le LLM.*

2. **Ratio Requêtes / Appel LLM ($R / L$)** :
   $$\text{Ratio}_{R/L} = \frac{\text{Nombre total de requêtes réseau/inférence Decider}}{\max(1, \text{Nombre total d'appels Bedrock LLM})}$$
   *Représente le nombre d'appels réseau Decider effectifs par appel LLM (reflète l'impact du batching de questions).*

---

## 4. Métriques de Latence

* **Latence Serveur GPU ($\text{lat}_{\text{server}}$ en ms)** :
  Temps de calcul brut mesuré sur le worker GPU (durée d'exécution de `engine.ask` ou forward pass du modèle), hors transfert réseau. Enregistré dans le journal sous `payload.latency_ms` par le worker.

* **Latence Aller-Retour Client ($\text{lat}_{\text{client}}$ en ms)** :
  Temps total écoulé du point de vue du moteur de simulation client entre l'envoi de la requête et la réception complète de la réponse (incluant la sérialisation JSON, le transport TCP/TLS Cloudflare et le calcul GPU).

---

## 5. Règle d'Attribution Matérielle et d'Honnêteté

* **Machine hôte locale** : `NVIDIA GeForce RTX 3050 6GB Laptop GPU` (Driver 615.71.09, CUDA 13.4, VRAM 6,14 Go).
* **Machine distante** : `Google Colab GPU Tesla T4 / L4 (16 Go VRAM)` via Cloudflare Quick Tunnel.
* **Interdiction de mélange** : Les mesures de latence ou de débit d'un worker distant ne doivent jamais être présentées comme des mesures locales du portable. Chaque mesure est explicitement étiquetée avec son environnement matériel d'origine (`hardware: local_rtx3050` ou `hardware: colab_t4`).
* **Runs mock** : Les exécutions sous `--mock-decider` ne comptent en aucun cas comme mesures de latence ou de performance GPU. Elles ne servent qu'à valider la logique d'état et le déterminisme algorithmique.
