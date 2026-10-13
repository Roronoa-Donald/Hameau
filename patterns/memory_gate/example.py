"""Standalone runnable example demonstrating MemoryGate pattern."""

from patterns.memory_gate import MemoryGate, MemoryCandidate
from hameau.decisions import DeciderClient


def run_example():
    print("=== Démonstration autonome de MemoryGate ===")
    decider = DeciderClient(mock=True, seed=42)
    gate = MemoryGate(decider_client=decider, top_k=2)

    memories = [
        MemoryCandidate("m1", "Awa a cuit 50 baguettes ce matin à l'aube.", tick=10, importance=0.2, entities=["boulangerie", "Awa"]),
        MemoryCandidate("m2", "Yao rapporte une rumeur : la mairie va fermer le marché samedi.", tick=24, importance=0.9, entities=["marche", "mairie", "Yao"], fact_id="R1"),
        MemoryCandidate("m3", "Kofi a signé les registres administratifs à la mairie.", tick=35, importance=0.3, entities=["mairie", "Kofi"]),
        MemoryCandidate("m4", "Il pleut doucement sur les berges de la rivière.", tick=48, importance=0.1, entities=["riviere"]),
    ]

    situation = "Kofi croise Yao devant la mairie. Yao aborde le sujet des commerces."
    situation_entities = ["mairie", "marche", "Yao"]
    current_tick = 50

    print(f"Situation : {situation}")
    print(f"Entités : {situation_entities}\n")

    candidates = gate.preselect(memories, current_tick, situation_entities)
    print(f"Candidats pré-sélectionnés ({len(candidates)} / {len(memories)}): {[c.id for c in candidates]}")

    top_memories = gate.score_and_rank(candidates, current_tick, situation)

    print("\nTop souvenirs retenus pour injection dans le contexte LLM :")
    for i, sm in enumerate(top_memories, 1):
        print(f"  {i}. [Zone: {sm.zone.upper()}] Score composite: {sm.composite_score} (Pertinence: {sm.relevance_score}, Importance: {sm.candidate.importance}, Récence: {sm.recency_score})")
        print(f"     -> « {sm.candidate.text} »\n")


if __name__ == "__main__":
    run_example()
