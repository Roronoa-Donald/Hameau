# HAMEAU — Baseline Measurement (Étape 0)

*Date : 2026-10-13 · Configuration : 12 agents, 2 jours (384 ticks simulés), mock Decider, Bedrock Nova Micro avec cassettes.*

## 1. Métriques du Run Initial (runs/hameau_run.jsonl)

| Métrique | Valeur mesurée | Observation |
|---|---|---|
| **Événements totaux** | 1 079 | 510 décisions, 482 répliques dialogue, 60 déplacements, 22 rumor_hop, 2 réflexions, 2 gazettes |
| **Décisions D1 (Jour 1)** | **510** | Actif |
| **Décisions D1 (Jour 2)** | **0** | **DÉFAUT 2.1 CONFIRMÉ** : Jour 2 entièrement gelé |
| **Rapport affiché vs réel** | 2 700 annoncés / 510 journalisés | **DÉFAUT 2.5 CONFIRMÉ** : Décisions D2-D8 non journalisées |
| **Propagation de la Rumeur R1** | 2 agents (Yao, Élise) | **DÉFAUT 2.2 CONFIRMÉ** : Rumeur répétée 20 fois au même agent |
| **Propagation du Démenti R2** | 1 agent (Kofi) | Injecté mais jamais transmis (jour 2 gelé) |
| **Coût AWS total** | 0,000217 $ | 486 appels dont 472 en cassette |

## 2. Défauts Reproduits par Tests Automatisés (`tests/audit_repro/test_defects.py`)

- `test_repro_2_1_day_2_freeze` : **REPRODUIT** (`d1_day2 == 0`).
- `test_repro_2_2_rumor_does_not_spread` : **REPRODUIT** (`len(r1_holders) == 1`).
- `test_repro_2_3_score_not_normalized` : **REPRODUIT** (`raw_score == 2.85 > 1.0`).
- `test_repro_2_4_mock_pythonhashseed_variance` : **REPRODUIT** (`hash()` utilisé dans client.py).
- `test_repro_2_5_unlogged_decisions` : **REPRODUIT** (`total_decisions (163) > logged (35)`).
