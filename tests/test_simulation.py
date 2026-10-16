"""Unit test for SimulationEngine."""

import yaml
from pathlib import Path
from hameau.models.world import build_default_village
from hameau.simulation.distribution import build_canonical_agents
from hameau.simulation.scenario import ScenarioManager
from hameau.simulation.engine import SimulationEngine
from hameau.decisions import DeciderClient
from hameau.llm import BedrockClient
from patterns.memory_gate import MemoryGate


def test_simulation_short_run(tmp_path):
    with open("config.yaml", "r") as f:
        cfg = yaml.safe_load(f)

    # Paramètres temporaires de test
    cfg["logging"]["runs_dir"] = str(tmp_path)
    cfg["logging"]["log_filename"] = "test_run.jsonl"
    cfg["bedrock"]["cassettes_dir"] = "cassettes"

    world = build_default_village()
    agents = build_canonical_agents()
    decider = DeciderClient(mock=True, seed=42)
    bedrock = BedrockClient(
        model_id=cfg["bedrock"]["model_id"],
        region_name=cfg["bedrock"]["region"],
        cassettes_dir="cassettes",
        use_cassettes=True,
    )
    mg = MemoryGate(decider_client=decider, top_k=3)
    scenario = ScenarioManager()

    engine = SimulationEngine(
        world=world,
        agents=agents,
        decider=decider,
        bedrock=bedrock,
        memory_gate=mg,
        scenario=scenario,
        config=cfg,
    )

    # Exécution sur 30 ticks pour vérifier l'injection de R1 (tick 24)
    summary = engine.run(days=1, ticks_per_day=30)

    assert summary["decider_total_decisions"] > 0
    assert summary["ratio_decider_to_llm"] > 0
    assert Path(summary["log_file"]).exists()

    # Vérification que le log contient des événements
    with open(summary["log_file"], "r", encoding="utf-8") as f:
        lines = f.readlines()
    assert len(lines) > 5

    # Vérification que l'injection R1 a bien eu lieu
    assert any("R1_fermeture_marche" in line for line in lines)
