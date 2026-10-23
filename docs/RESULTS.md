# Résultats Expérimentaux Officiels — Projet HAMEAU

> **Source de vérité unique** : [`results/summary.json`](../results/summary.json)  
> **Fichier journal source** : [`runs/run_real_3j.jsonl`](../runs/run_real_3j.jsonl)  
> **Généré le** : 2026-10-23T02:44:14.627918+00:00  
> **Backend Décisions** : `StrandsAgents/strands-decider-2B-hobson-v21` (local_gpu)  
> **Backend Générations** : `amazon.nova-micro-v1:0` (live_network, 659 appels réels)  
> **Matériel** : NVIDIA GeForce RTX 3050 6GB Laptop GPU (6144 Mo VRAM)

---

## 1. Synthèse Globale (Run Réel 3 Jours — E1)

| Métrique | Valeur Mesurée | Définition / Source |
| :--- | :--- | :--- |
| **Population** | **20 habitants** | Village canonique (20 agents) |
| **Durée simulée** | **3 jours (576 ticks)** | 1 tick = 5 min (6h00 à 22h00) |
| **Durée réelle (wall-clock)** | **16616.0 s (276.9 min)** | 5538.7 s / jour simulé |
| **Questions Decider ($Q$)** | **13,467** | D1 à D9 évaluées sur GPU local |
| **Requêtes Decider ($R$)** | **8,206** | Inférences après batching prefix |
| **Appels Amazon Bedrock ($L$)** | **659** | 100% réseau direct (642 conv., 14 réfl., 3 gazettes) |
| **Ratio Questions / LLM ($Q / L$)** | **20.44 : 1** | Arbitrages 2B par génération LLM (Cible > 20:1) |
| **Ratio Requêtes / LLM ($R / L$)** | **12.45 : 1** | Appels inférence par génération LLM |
| **Latence Decider Questions** | **p50 = 2606.09 ms**, p95 = 4530.08 ms | Inférence System One locale GPU |
| **Latence Decider Requêtes** | **p50 = 1403.57 ms**, p95 = 4348.15 ms | Durée brute par appel ask() |
| **Latence Bedrock Nova Micro** | **p50 = 746.02 ms**, p95 = 1224.4 ms | Appel API AWS us-east-1 |
| **Zones de confiance** | **Vert: 13.2 %**, Orange: 73.12 %, Rouge: 13.69 % | Seuils calibrés D1 à D9 |
| **Replis en zone rouge** | **1843 (13.69 %)** | Routine/Abstention déterministe |
| **Tokens Bedrock consommés** | **278,661 tokens** (257,802 in / 20,859 out) | Nova Micro API |
| **Coût réel AWS Bedrock** | **0.01194 $ USD** | 0.035 $/1M in, 0.140 $/1M out |

---

## 2. Répartition des Décisions par Gabarit ($Q = 13,467$)

| Gabarit | Type | Description | Nombre ($Q$) | Replis |
| :--- | :--- | :--- | :--- | :--- |
| **D1** | `choice` | ActionPicker (déplacements & routines) | 2,588 | 854 |
| **D2** | `score` | ImportanceScorer (importance d'un fait) | 255 | 0 |
| **D3** | `score` | RelevanceScorer (pertinence MemoryGate) | 8,046 | 1 |
| **D4** | `noul` | TalkGate (engager la conversation) | 1,432 | 946 |
| **D5** | `score` | ShareScorer (souvenir à partager) | 511 | 0 |
| **D6** | `noul` | ReflectGate (introspection du soir) | 41 | 31 |
| **D7** | `noul` | ContinueGate (poursuivre l'échange) | 321 | 0 |
| **D8** | `score` | CredibilityGate (crédibilité d'un ouï-dire) | 255 | 0 |
| **D9** | `choice` | VoteChoice (scrutin municipal Jour 3) | 18 | 11 |

---

## 3. Scrutin Municipal (D9) — Jour 3, 17h00

* **Participation** : 9 votes exprimés sur 20 habitants (45.0 %).
* **Résultat du dépouillement** :
  * **Kofi** : 5 voix
  * **Victor** : 4 voix
  * **Abstention** : 11 voix (dont 5 replis en zone rouge)
* **Vainqueur proclamé** : **Kofi** (incumbent_keeps_office).
* **Annonce Gazette** : Publiée dans l'édition du soir J3 rédigée par Amazon Nova Micro.

---

## 4. Filtrage de Contexte MemoryGate (E3)

* **Évaluations D3 totales** : 1917 contextes évalués.
* **Évaluations avec > 3 candidats** : 1155.
* **Volume brut estimé sans MemoryGate** : 753,965 tokens.
* **Volume injecté avec MemoryGate (Top-3)** : 580,162 tokens.
* **Réduction de tokens mesurée** : **-23.05 %**.

---

## 5. Calibration D8 sur Faits Objectifs (E5)

* **Échantillon évalué ($N$)** : 255 décisions D8 associées à une vérité terrain connue.
* **Exactitude globale** : **34.5 %**.
* **Erreur de calibration (ECE)** : 0.1181.
* **Décisions D2, D3, D4, D6** : **Non mesurées** (étiquettes humaines non renseignées dans `results/labels/`).
