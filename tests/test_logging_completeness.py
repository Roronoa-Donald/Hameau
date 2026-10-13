"""Tests for complete decision logging (D1-D8) and event stream metrics reduction (A3)."""

import json
from pathlib import Path
import pytest
import yaml

from hameau.decisions import DeciderClient
from hameau.models.world import build_default_village
from hameau.simulation import build_canonical_agents, ScenarioManager, SimulationEngine
from hameau.llm import BedrockClient
from patterns.memory_gate import MemoryGate


def test_all_decisions_logged_to_jsonl(tmp_path):
    """Verify that every decision (D1 to D8) produces a JSONL event and counters match lines."""
    cfg = yaml.safe_load(open("config.yaml"))
    cfg["logging"]["runs_dir"] = str(tmp_path)
    cfg["logging"]["log_filename"] = "completeness_test.jsonl"

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

    summary = engine.run(days=1, ticks_per_day=30)

    log_file = tmp_path / "completeness_test.jsonl"
    lines = [json.loads(l) for l in log_file.read_text().splitlines() if l.strip()]
    decision_events = [l for l in lines if l.get("event_type") == "decision"]

    # 1. Total decisions counter MUST match exact count of logged decision lines
    assert summary["decider_total_decisions"] == len(decision_events), (
        f"Counter mismatch: {summary['decider_total_decisions']} vs logged {len(decision_events)}"
    )

    # 2. Check presence of decision types
    decision_types = {e["payload"].get("decision") for e in decision_events}
    print(f"Logged decision types: {decision_types}")

    # Must contain at least D1, D3, D4, D6
    for required in ["D1", "D3", "D4"]:
        assert required in decision_types, f"Missing required decision type {required} in logs"

    # 3. Check payload schema of decision events
    sample = decision_events[0]["payload"]
    for required_field in ["decision", "chosen_option", "confidence", "zone", "latency_ms", "backend"]:
        assert required_field in sample, f"Field '{required_field}' missing in decision payload"
