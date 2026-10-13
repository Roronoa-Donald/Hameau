"""Unit tests for MemoryGate pattern."""

from patterns.memory_gate import MemoryGate, MemoryCandidate
from hameau.decisions import DeciderClient


def test_memory_gate_preselect_and_scoring():
    decider = DeciderClient(mock=True, seed=42)
    gate = MemoryGate(decider_client=decider, top_k=2, max_candidates=5)

    memories = [
        MemoryCandidate(f"m_{i}", f"Souvenir banal {i}", tick=i * 5, importance=0.2, entities=["autre"])
        for i in range(10)
    ]
    # Ajouter un souvenir critique lié à la situation
    critical_mem = MemoryCandidate(
        "m_crit",
        "Rumeur de fermeture du marché",
        tick=40,
        importance=0.95,
        entities=["marche", "mairie"],
        fact_id="R1",
    )
    memories.append(critical_mem)

    # Pré-sélection
    candidates = gate.preselect(memories, current_tick=50, situation_entities=["marche"])
    assert len(candidates) <= 5
    # Le souvenir critique doit faire partie des présélectionnés
    candidate_ids = [c.id for c in candidates]
    assert "m_crit" in candidate_ids

    # Ranking
    top_scored = gate.score_and_rank(candidates, current_tick=50, situation_context="Rencontre sur la place du marché.")
    assert len(top_scored) == 2
    assert all(0.0 <= s.composite_score <= 1.0 for s in top_scored)
    assert all(s.zone in ["green", "orange", "red"] for s in top_scored)
