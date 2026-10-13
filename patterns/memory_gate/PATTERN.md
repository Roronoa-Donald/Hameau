# Pattern : MemoryGate (Context & Memory Scoring)

**Hackathon Tags** : `#strands-decider-2b` `#context-memory`  
**License** : Apache-2.0  
**Author** : Équipe HAMEAU (Strands Decider Agent Hackathon - AWS Builder Center)

---

## 1. Problème résolu

Les architectures d'agents autonomes à mémoire persistante (type Generative Agents, Park et al., 2023) souffrent d'un goulet d'étranglement majeur :
- Récupérer tous les souvenirs ou faire appel à un grand modèle génératif (LLM) pour noter la pertinence de chaque souvenir candidat sature le contexte, explose la latence (> 2-5 secondes) et multiplie les coûts par 100.
- La récupération naïve par seule récence temporelle ou similarité vectorielle brute échoue à discerner si une information lointaine mais critique (ex: une rumeur ou un événement clé) doit primer sur une observation triviale récente.

**MemoryGate** résout ce problème en déléguant le filtrage et la notation de pertinence à **Strands Decider 2B** en ~100 ms sur GPU local (ou instance modeste), avant d'injecter uniquement les 3 souvenirs les plus décisifs dans le prompt d'Amazon Bedrock.

---

## 2. Fonctionnement en 3 Étapes

```
[Magasin de souvenirs] 
          │
          ▼
1. Présélection déterministe (Entités communes + 5 récents + 5 importants <= 12)
          │
          ▼
2. Évaluation de pertinence (D3) par Strands Decider 2B
   - Shared-prefix KV cache : 12 candidats évalués en un seul forward
   - Confiance calibrée : Zones Verte, Orange, Rouge avec repli automatique
          │
          ▼
3. Tri par Score Composite :
   Score = (w_r * Récence_Exp) + (w_i * Importance) + (w_p * Pertinence_Decider)
          │
          ▼
[Top-3 souvenirs injectés dans le contexte de Bedrock]
```

---

## 3. Formule du Score Composite

Le score final $S \in [0, 1]$ pour chaque souvenir $m$ est calculé par :

$$S(m) = w_r \cdot e^{-\lambda \Delta t} + w_i \cdot \text{Importance}(m) + w_p \cdot \text{Pertinence}(m)$$

Où :
- $\Delta t$ est l'âge du souvenir en pas de simulation.
- $\lambda = \frac{\ln(2)}{T_{1/2}}$ correspond à une demi-vie paramétrable (ex: 24h).
- $w_r, w_i, w_p \approx 0.33$ sont les pondérations normalisées.

---

## 4. Politique de Confiance Calibrée (Zones)

Pour chaque évaluation de pertinence (D3) :
- **Zone Verte ($\ge 0.55$)** : Score appliqué directement.
- **Zone Orange ($[0.35, 0.55[$)** : Score appliqué, noté dans les logs d'observabilité.
- **Zone Rouge ($< 0.35$)** : Repli déterministe automatique ($(\text{Importance} + 0.5) / 2$) pour éviter toute hallucination de scoring.

---

## 5. Exemple d'utilisation minimal autonome (30 lignes)

```python
from patterns.memory_gate import MemoryGate, MemoryCandidate
from hameau.decisions import DeciderClient

# Initialisation
client = DeciderClient(mock=True) # ou checkpoint local GPU
gate = MemoryGate(decider_client=client, top_k=3)

# Magasin de souvenirs
memories = [
    MemoryCandidate("m1", "Awa a cuit 50 baguettes ce matin", tick=10, importance=0.2, entities=["boulangerie", "Awa"]),
    MemoryCandidate("m2", "Yao dit que la mairie va fermer le marché samedi", tick=24, importance=0.9, entities=["marche", "mairie"]),
    MemoryCandidate("m3", "Kofi est en réunion à la mairie", tick=40, importance=0.4, entities=["mairie", "Kofi"]),
]

# Situation courante
situation = "Kofi croise Yao devant la mairie à 10h00. Yao s'inquiète du marché."
situation_entities = ["mairie", "marche", "Yao"]

# 1. Présélection
candidates = gate.preselect(memories, current_tick=50, situation_entities=situation_entities)

# 2. Scoring et classement
top_memories = gate.score_and_rank(candidates, current_tick=50, situation_context=situation)

for m in top_memories:
    print(f"[{m.zone.upper()}] Score={m.composite_score} : {m.candidate.text}")
```
