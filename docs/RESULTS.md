# Résultats Expérimentaux Officiels — Projet HAMEAU

> **Source de vérité unique** : [`results/summary.json`](../results/summary.json)  
> **Fichier journal source** : [`runs/real_final_3j.jsonl`](../runs/real_final_3j.jsonl)  
> **Généré le** : 2026-10-22T12:09:29.223438+00:00  
> **Backend Décisions** : `StrandsAgents/strands-decider-2B-hobson-v21` (local_gpu)  
> **Backend Générations** : `amazon.nova-micro-v1:0` (live_network, 655 appels réels)  
> **Matériel** : NVIDIA GeForce RTX 3050 6GB Laptop GPU (6144 Mo VRAM)

---

## 1. Synthèse Globale (Run Réel 3 Jours — E1)

| Métrique | Valeur Mesurée | Définition / Source |
| :--- | :--- | :--- |
| **Population** | **20 habitants** | Village canonique (20 agents) |
| **Durée simulée** | **3 jours (576 ticks)** | 1 tick = 5 min (6h00 à 22h00) |
| **Durée réelle (wall-clock)** | **1965.4 s (32.8 min)** | 655.1 s / jour simulé |
| **Questions Decider ($Q$)** | **13,351** | D1 à D9 évaluées sur GPU local |
| **Requêtes Decider ($R$)** | **8,122** | Inférences après batching prefix |
| **Appels Amazon Bedrock ($L$)** | **655** | 100% réseau direct (638 conv., 14 réfl., 3 gazettes) |
| **Ratio Questions / LLM ($Q / L$)** | **20.38 : 1** | Arbitrages 2B par génération LLM (Cible > 20:1) |
| **Ratio Requêtes / LLM ($R / L$)** | **12.4 : 1** | Appels inférence par génération LLM |
| **Latence Decider Questions** | **p50 = 249.56 ms**, p95 = 417.6 ms | Inférence System One locale GPU |
| **Latence Decider Requêtes** | **p50 = 124.31 ms**, p95 = 411.59 ms | Durée brute par appel ask() |
| **Latence Bedrock Nova Micro** | **p50 = 755.08 ms**, p95 = 1041.8 ms | Appel API AWS us-east-1 |
| **Zones de confiance** | **Vert: 13.19 %**, Orange: 73.11 %, Rouge: 13.7 % | Seuils calibrés D1 à D9 |
| **Replis en zone rouge** | **1829 (13.7 %)** | Routine/Abstention déterministe |
| **Tokens Bedrock consommés** | **275,632 tokens** (254,664 in / 20,968 out) | Nova Micro API |
| **Coût réel AWS Bedrock** | **0.01184 $ USD** | 0.035 $/1M in, 0.140 $/1M out |

---

## 2. Répartition des Décisions par Gabarit ($Q = 13,351$)

| Gabarit | Type | Description | Nombre ($Q$) | Replis |
| :--- | :--- | :--- | :--- | :--- |
| **D1** | `choice` | ActionPicker (déplacements & routines) | 2,570 | 850 |
| **D2** | `score` | ImportanceScorer (importance d'un fait) | 249 | 0 |
| **D3** | `score` | RelevanceScorer (pertinence MemoryGate) | 7,986 | 1 |
| **D4** | `noul` | TalkGate (engager la conversation) | 1,433 | 935 |
| **D5** | `score` | ShareScorer (souvenir à partager) | 486 | 0 |
| **D6** | `noul` | ReflectGate (introspection du soir) | 41 | 31 |
| **D7** | `noul` | ContinueGate (poursuivre l'échange) | 319 | 0 |
| **D8** | `score` | CredibilityGate (crédibilité d'un ouï-dire) | 249 | 0 |
| **D9** | `choice` | VoteChoice (scrutin municipal Jour 3) | 18 | 12 |

---

## 3. Scrutin Municipal (D9) — Jour 3, 17h00

* **Participation** : 8 votes exprimés sur 20 habitants (40.0 %).
* **Résultat du dépouillement** :
  * **Kofi** : 4 voix
  * **Victor** : 4 voix
  * **Abstention** : 12 voix (dont 6 replis en zone rouge)
* **Vainqueur proclamé** : **Kofi** (incumbent_keeps_office).
* **Annonce Gazette** : Publiée dans l'édition du soir J3 rédigée par Amazon Nova Micro.

---

## 4. Filtrage de Contexte MemoryGate (E3)

* **Évaluations D3 totales** : 1893 contextes évalués.
* **Évaluations avec > 3 candidats** : 1145.
* **Volume brut estimé sans MemoryGate** : 745,167 tokens.
* **Volume injecté avec MemoryGate (Top-3)** : 573,854 tokens.
* **Réduction de tokens mesurée** : **-22.99 %**.

---

## 5. Calibration D8 sur Faits Objectifs (E5)

* **Échantillon évalué ($N$)** : 249 décisions D8 associées à une vérité terrain connue.
* **Exactitude globale** : **34.9 %**.
* **Erreur de calibration (ECE)** : 0.113.
* **Décisions D2, D3, D4, D6** : **Non mesurées** (étiquettes humaines non renseignées dans `results/labels/`).
