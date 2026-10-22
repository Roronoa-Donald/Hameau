# Registre d'Honnêteté et des Allégations Chiffrées (CLAIMS_LEDGER.md)

Ce registre répertorie chaque chiffre public utilisé dans l'article AWS Builder Center, le README et la vidéo de démonstration.
Chaque ligne est vérifiée automatiquement par `scripts/check_claims.py` contre `results/summary.json`.

| Allégation | Chiffre Publié | Fichier Source | Commande de Reproduction | Statut |
| :--- | :--- | :--- | :--- | :--- |
| **Questions Decider réelles** | **13,351** | `runs/real_final_3j.jsonl` | `scripts/build_numbers.py` | **Vérifié (GPU réel)** |
| **Requêtes Decider (après batching)** | **8,122** | `runs/real_final_3j.jsonl` | `scripts/build_numbers.py` | **Vérifié (GPU réel)** |
| **Appels Amazon Bedrock réels** | **655** | `runs/real_final_3j.jsonl` | `scripts/build_numbers.py` | **Vérifié (100% direct)** |
| **Ratio Questions / LLM** | **20.38 : 1** | `results/summary.json` | `Q / L = 13351 / 655` | **Vérifié (> 20:1)** |
| **Ratio Requêtes / LLM** | **12.4 : 1** | `results/summary.json` | `R / L = 8122 / 655` | **Vérifié** |
| **Latence p50 Decider** | **124.31 ms** | `results/summary.json` | `Decider request latency p50` | **Vérifié (RTX 3050)** |
| **Latence p50 Bedrock** | **755.08 ms** | `results/summary.json` | `Bedrock latency_ms p50` | **Vérifié (Nova Micro)** |
| **Coût AWS total** | **0.01184 $** | `runs/real_final_3j.jsonl` | `Bedrock token accumulation` | **Vérifié (< 0.02 $)** |
| **Réduction de tokens MemoryGate** | **-22.99 %** | `results/summary.json` | `MemoryGate Top-3 gated vs raw candidates` | **Vérifié** |
| **Participation élection D9** | **40.0 % (8 / 20)** | `runs/real_final_3j.jsonl` | `election_result event at tick 516` | **Vérifié** |

### Allégations historiques corrigées / démenties
- *Ancien chiffre non qualifié « 10 816 décisions »* : Remplacé par **13,351 questions Decider typées (8,122 requêtes réseau)**, mesurées sur run GPU certifié.
- *Ancien indicateur « 0,0000 $ »* : Remplacé par le coût réseau réel mesuré **0.01184 $ USD**.
