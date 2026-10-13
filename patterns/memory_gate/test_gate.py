"""Unit tests for MemoryGate reusable pattern and Strands HookProvider integration."""

import pytest
from patterns.memory_gate import MemoryGate, MemoryCandidate, ScoredMemory
from hameau.decisions.client import DeciderClient
from strands.hooks import HookRegistry
from strands.hooks.events import BeforeModelCallEvent


@pytest.fixture
def mock_decider():
    return DeciderClient(mock=True, seed=42)


@pytest.fixture
def sample_candidates():
    return [
        MemoryCandidate(id="m1", text="Le maire a convoqué une réunion urgente.", tick=50, importance=0.9, entities=["maire", "mairie"]),
        MemoryCandidate(id="m2", text="Il fait beau aujourd'hui.", tick=180, importance=0.1, entities=[]),
        MemoryCandidate(id="m3", text="La farine va manquer à la boulangerie.", tick=100, importance=0.8, entities=["boulangerie", "marche"]),
        MemoryCandidate(id="m4", text="Awa a nettoyé son four ce matin.", tick=170, importance=0.3, entities=["boulangerie"]),
    ]


def test_memory_gate_preselect(mock_decider, sample_candidates):
    gate = MemoryGate(decider_client=mock_decider, max_candidates=2)
    selected = gate.preselect(sample_candidates, current_tick=190, situation_entities=["maire"])
    assert len(selected) <= 2
    # m1 shares entity "maire", so it must be selected
    assert any(c.id == "m1" for c in selected)


def test_memory_gate_score_and_rank(mock_decider, sample_candidates):
    gate = MemoryGate(
        decider_client=mock_decider,
        top_k=2,
        half_life_ticks=192.0,
        confidence_green=0.55,
        confidence_orange=0.35,
    )
    ranked = gate.score_and_rank(
        candidates=sample_candidates,
        current_tick=190,
        situation_context="Awa cherche des informations sur la livraison de farine.",
    )
    assert len(ranked) == 2
    assert isinstance(ranked[0], ScoredMemory)
    assert ranked[0].composite_score >= ranked[1].composite_score
    for item in ranked:
        assert 0.0 <= item.composite_score <= 1.0
        assert 0.0 <= item.relevance_score <= 1.0
        assert item.zone in ("green", "orange", "red")


def test_memory_gate_strands_hook_registration(mock_decider):
    gate = MemoryGate(decider_client=mock_decider)
    registry = HookRegistry()
    gate.register_hooks(registry)
    assert registry.has_callbacks()
    callbacks = list(registry.get_callbacks_for(BeforeModelCallEvent(agent=None)))
    assert len(callbacks) == 1


def test_memory_gate_hook_invocation(mock_decider, sample_candidates):
    gate = MemoryGate(decider_client=mock_decider, top_k=2)
    registry = HookRegistry()
    gate.register_hooks(registry)

    # Simulation d'un événement BeforeModelCallEvent
    class FakeAgent:
        def __init__(self):
            self.memory_candidates = sample_candidates
            self.current_tick = 190
            self.messages = ["Awa s'inquiète du manque de farine."]

    agent = FakeAgent()
    state = {
        "memory_candidates": sample_candidates,
        "current_tick": 190,
        "context_text": "Awa s'inquiète du manque de farine.",
    }
    event = BeforeModelCallEvent(agent=agent, invocation_state=state)

    registry.invoke_callbacks(event)

    assert "selected_memories" in state
    assert len(state["selected_memories"]) == 2
    assert "memory_gate_injected_text" in state
    assert "Score:" in state["memory_gate_injected_text"]
