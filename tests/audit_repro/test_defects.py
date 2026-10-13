"""Regression tests verifying all audit defects (2.1 to 2.5) are resolved."""

import os
import subprocess
import tempfile
import yaml
import pytest
from pathlib import Path

from hameau.decisions import DeciderClient
from hameau.models.world import build_default_village
from hameau.simulation import build_canonical_agents, ScenarioManager, SimulationEngine
from hameau.llm import BedrockClient
from patterns.memory_gate import MemoryGate


def test_fix_2_1_day_2_not_frozen(tmp_path):
    """Verify defect 2.1 is fixed: Day 2 has active decisions comparable to Day 1."""
    cfg = yaml.safe_load(open("config.yaml"))
    cfg["logging"]["runs_dir"] = str(tmp_path)
    cfg["logging"]["log_filename"] = "freeze_fixed_test.jsonl"
    
    dec = DeciderClient(mock=True, seed=42)
    br = BedrockClient(cassettes_dir="cassettes", use_cassettes=True, seed=42)
    engine = SimulationEngine(build_default_village(), build_canonical_agents(), dec, br, MemoryGate(dec), ScenarioManager(), cfg)
    
    engine.run(days=2, ticks_per_day=192)
    
    import json
    lines = [json.loads(l) for l in (tmp_path / "freeze_fixed_test.jsonl").read_text().splitlines() if l.strip()]
    d1_day1 = [l for l in lines if l.get("event_type") == "decision" and l.get("day") == 1]
    d1_day2 = [l for l in lines if l.get("event_type") == "decision" and l.get("day") == 2]
    
    assert len(d1_day1) > 100, f"Expected Day 1 decisions, got {len(d1_day1)}"
    assert len(d1_day2) > 100, f"Expected Day 2 active decisions, got {len(d1_day2)}"


def test_fix_2_2_rumor_spreads(tmp_path):
    """Verify defect 2.2 is fixed: Rumor R1 spreads through social interactions."""
    cfg = yaml.safe_load(open("config.yaml"))
    cfg["logging"]["runs_dir"] = str(tmp_path)
    cfg["logging"]["log_filename"] = "rumor_fixed_test.jsonl"
    
    dec = DeciderClient(mock=True, seed=42)
    br = BedrockClient(cassettes_dir="cassettes", use_cassettes=True, seed=42)
    engine = SimulationEngine(build_default_village(), build_canonical_agents(), dec, br, MemoryGate(dec), ScenarioManager(), cfg)
    
    engine.run(days=2, ticks_per_day=192)
    
    r1_holders = [a for a in engine.agents.values() if "R1_fermeture_marche" in a.persona.believed_facts]
    assert len(r1_holders) >= 8, f"Expected at least 8 agents holding R1, got {len(r1_holders)}"


def test_fix_2_3_score_normalized():
    """Verify defect 2.3 is fixed: ScoreAnswer is strictly normalized to [0, 1]."""
    from strands_decider.schema import ScoreAnswer
    client = DeciderClient(mock=True)
    raw_answer = ScoreAnswer(
        score=2.85,  # level index between 0 and 4
        legend={"0": "1: trivial", "1": "2: low", "2": "3: mid", "3": "4: high", "4": "5: extreme"},
        probabilities={"0": 0.05, "1": 0.15, "2": 0.35, "3": 0.35, "4": 0.10},
        confidence=0.72,
    )
    formatted = client._format_answer(raw_answer)
    assert 0.0 <= formatted["value"] <= 1.0
    assert formatted["value"] == pytest.approx(0.7125, rel=1e-3)
    assert formatted["raw_score"] == pytest.approx(2.85, rel=1e-3)


def test_fix_2_4_mock_deterministic():
    """Verify defect 2.4 is fixed: Mock uses deterministic hash independent of PYTHONHASHSEED."""
    import inspect
    from hameau.decisions import client
    src = inspect.getsource(client.DeciderClient._mock_ask)
    assert "abs(hash(" not in src, "Expected builtin hash() to not be used in mock code"
    assert "_deterministic_hash" in src, "Expected _deterministic_hash to be used in mock code"


def test_fix_2_5_logged_equals_counted(tmp_path):
    """Verify defect 2.5 is fixed: logged decision events strictly equal total_decisions."""
    cfg = yaml.safe_load(open("config.yaml"))
    cfg["logging"]["runs_dir"] = str(tmp_path)
    cfg["logging"]["log_filename"] = "logged_fixed_test.jsonl"
    
    dec = DeciderClient(mock=True, seed=42)
    br = BedrockClient(cassettes_dir="cassettes", use_cassettes=True, seed=42)
    engine = SimulationEngine(build_default_village(), build_canonical_agents(), dec, br, MemoryGate(dec), ScenarioManager(), cfg)
    
    summary = engine.run(days=1, ticks_per_day=30)
    
    import json
    lines = [json.loads(l) for l in (tmp_path / "logged_fixed_test.jsonl").read_text().splitlines() if l.strip()]
    logged_decisions = [l for l in lines if l.get("event_type") == "decision"]
    
    assert summary["decider_total_decisions"] == len(logged_decisions), (
        f"Expected exact match: counted {summary['decider_total_decisions']} vs logged {len(logged_decisions)}"
    )
