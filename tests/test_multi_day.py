"""Tests for multi-day simulation and global tick mechanics (A1)."""

import json
from pathlib import Path
import pytest
import yaml

from hameau.decisions import DeciderClient
from hameau.models.world import build_default_village
from hameau.simulation import build_canonical_agents, ScenarioManager, SimulationEngine
from hameau.llm import BedrockClient
from patterns.memory_gate import MemoryGate, MemoryCandidate


def test_multi_day_activity_not_frozen(tmp_path):
    """Verify that Day 2 does not freeze and has active decisions comparable to Day 1."""
    cfg = yaml.safe_load(open("config.yaml"))
    cfg["logging"]["runs_dir"] = str(tmp_path)
    cfg["logging"]["log_filename"] = "multi_day_test.jsonl"

    dec = DeciderClient(mock=True, seed=42)
    br = BedrockClient(cassettes_dir="cassettes", use_cassettes=True, seed=42)
    engine = SimulationEngine(
        build_default_village(),
        build_canonical_agents(),
        dec,
        br,
        MemoryGate(dec),
        ScenarioManager(),
        cfg,
    )

    summary = engine.run(days=2, ticks_per_day=192)

    log_file = tmp_path / "multi_day_test.jsonl"
    lines = [json.loads(l) for l in log_file.read_text().splitlines() if l.strip()]

    d1_day1 = [l for l in lines if l.get("event_type") == "decision" and l.get("day") == 1]
    d1_day2 = [l for l in lines if l.get("event_type") == "decision" and l.get("day") == 2]

    assert len(d1_day1) >= 100, f"Expected >=100 Day 1 decisions, got {len(d1_day1)}"
    assert len(d1_day2) >= 100, f"Expected >=100 Day 2 decisions (not frozen), got {len(d1_day2)}"

    # Day 2 activity should be in the same order of magnitude as Day 1 (at least 50%)
    ratio = len(d1_day2) / len(d1_day1)
    assert ratio >= 0.50, f"Day 2 / Day 1 activity ratio too low: {ratio:.2f}"


def test_memory_gate_recency_across_days():
    """Verify that MemoryGate recency decays properly across day boundaries using global tick."""
    dec = DeciderClient(mock=True, seed=42)
    gate = MemoryGate(dec, half_life_ticks=192)

    # Candidate memory created on Day 1 at tick 10 (global tick 10)
    c1 = MemoryCandidate(
        id="mem1",
        text="Yao a mentionné la fermeture du marché",
        tick=10,  # global tick 10
        importance=0.8,
        entities=["yao", "marche"],
    )

    # Retrieval on Day 2 at tick 10 (global tick: 192 + 10 = 202)
    # delta_ticks = 202 - 10 = 192 ticks = exactly one half-life -> recency should be ~0.50
    scored = gate.score_candidates(
        candidates=[c1],
        context_text="Yao discute avec Élise au marché",
        current_tick=202,  # global tick
    )

    assert len(scored) == 1
    recency = scored[0].recency_score
    # exp(-ln(2) * 192 / 192) = 0.50
    assert 0.45 <= recency <= 0.55, f"Expected recency ~0.50 after 1 half-life, got {recency}"
