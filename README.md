# HAMEAU

**Un village d'agents qui décident vite avec Strands Decider 2B et parlent avec Amazon Bedrock (Nova Micro)**  
*Strands Decider Agent Hackathon · AWS Builder Center*

Tags: `#strands-decider-2b` `#context-memory`

## Vue d'ensemble

HAMEAU démontre comment découpler les décisions à haute fréquence (prises en ~100ms par Strands Decider 2B sur GPU local) de la génération narrative et des dialogues rares (confiés à Amazon Bedrock via Amazon Nova Micro).

- **Decider 2B (Local GPU RTX 3050)** : Gère D1 (actions), D2 (importance), D3 (pertinence des souvenirs via MemoryGate), D4 (volonté de parler), D5 (sujet), D6 (réflexion), D7 (poursuite du dialogue), D8 (crédibilité de la rumeur).
- **Amazon Bedrock (Nova Micro)** : Génère B1 (répliques de conversation), B2 (réflexions profondes), B4 (Gazette du village).
- **Pattern réutilisable** : `MemoryGate` (`patterns/memory_gate/`) pour le scoring et l'injection ciblée de souvenirs dans le contexte LLM.
