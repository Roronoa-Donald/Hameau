# Registre d'Honnêteté et des Allégations Chiffrées (CLAIMS_LEDGER.md)

Ce registre répertorie chaque chiffre public utilisé dans l'article AWS Builder Center, le README et la vidéo de démonstration.
Chaque ligne est vérifiée automatiquement par `scripts/check_claims.py` contre `results/summary.json`.

| Allégation | Chiffre Publié | Fichier Source | Commande de Reproduction | Statut |
| :--- | :--- | :--- | :--- | :--- |
| **Questions Decider réelles** | **13,467** | `runs/real_final_3j.jsonl` | `scripts/build_numbers.py` | **Vérifié (GPU réel)** |
| **Requêtes Decider (après batching)** | **8,206** | `runs/real_final_3j.jsonl` | `scripts/build_numbers.py` | **Vérifié (GPU réel)** |
| **Appels Amazon Bedrock réels** | **659** | `runs/real_final_3j.jsonl` | `scripts/build_numbers.py` | **Vérifié (100% direct)** |
| **Ratio Questions / LLM** | **20.44 : 1** | `results/summary.json` | `Q / L = 13467 / 659` | **Vérifié (> 20:1)** |
| **Ratio Requêtes / LLM** | **12.45 : 1** | `results/summary.json` | `R / L = 8206 / 659` | **Vérifié** |
| **Latence p50 Decider** | **1403.57 ms** | `results/summary.json` | `Decider request latency p50` | **Vérifié (RTX 3050)** |
| **Latence p50 Bedrock** | **746.02 ms** | `results/summary.json` | `Bedrock latency_ms p50` | **Vérifié (Nova Micro)** |
| **Coût AWS total** | **0.01194 $** | `runs/real_final_3j.jsonl` | `Bedrock token accumulation` | **Vérifié (< 0.02 $)** |
| **Réduction de tokens MemoryGate** | **-23.05 %** | `results/summary.json` | `MemoryGate Top-3 gated vs raw candidates` | **Vérifié** |
| **Participation élection D9** | **45.0 % (9 / 20)** | `runs/real_final_3j.jsonl` | `election_result event at tick 516` | **Vérifié** |

### Allégations historiques corrigées / démenties
- *Ancien chiffre non qualifié « 10 816 décisions »* : Remplacé par **13,467 questions Decider typées (8,206 requêtes réseau)**, mesurées sur run GPU certifié.
- *Ancien indicateur « 0,0000 $ »* : Remplacé par le coût réseau réel mesuré **0.01194 $ USD**.
