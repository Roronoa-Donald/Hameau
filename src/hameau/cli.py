"""Command Line Interface for running HAMEAU simulation."""

import argparse
import os
import sys
import yaml
from pathlib import Path

from hameau.models.world import build_default_village
from hameau.simulation.distribution import build_canonical_agents
from hameau.simulation.scenario import ScenarioManager
from hameau.simulation.engine import SimulationEngine
from hameau.decisions import DeciderClient
from hameau.llm import BedrockClient
from patterns.memory_gate import MemoryGate


def main():
    parser = argparse.ArgumentParser(description="HAMEAU — Simulation multi-agents avec Strands Decider 2B et Amazon Nova Micro")
    parser.add_argument("--config", type=str, default="config.yaml", help="Chemin vers config.yaml")
    parser.add_argument("--days", type=int, default=None, help="Nombre de jours simulés")
    parser.add_argument("--ticks-per-day", type=int, default=None, help="Nombre de ticks par jour (défaut 192)")
    parser.add_argument("--mock-decider", action="store_true", help="Utiliser le mock déterministe au lieu du GPU local")
    parser.add_argument("--no-cassettes", action="store_true", help="Désactiver le cache des cassettes Bedrock")
    parser.add_argument("--serve", action="store_true", help="Lancer un serveur web local pour le visualiseur")
    parser.add_argument("--port", type=int, default=8000, help="Port pour le serveur web local (défaut 8000)")

    args = parser.parse_args()

    if args.serve:
        import http.server
        import socketserver
        import webbrowser
        os.chdir(Path(__file__).parent.parent.parent)
        handler = http.server.SimpleHTTPRequestHandler
        with socketserver.TCPServer(("", args.port), handler) as httpd:
            url = f"http://localhost:{args.port}/viewer/index.html"
            print(f"Serveur visualiseur HAMEAU démarré sur : {url}")
            try:
                httpd.serve_forever()
            except KeyboardInterrupt:
                print("\nArrêt du serveur.")
        return

    # Lecture de la configuration
    config_path = Path(args.config)
    if not config_path.exists():
        print(f"Erreur : fichier de configuration '{args.config}' introuvable.")
        sys.exit(1)

    with open(config_path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    days = args.days or cfg.get("simulation", {}).get("days", 1)
    ticks_per_day = args.ticks_per_day or cfg.get("simulation", {}).get("ticks_per_day", 192)

    use_mock = args.mock_decider
    use_cassettes = not args.no_cassettes

    print(f"===========================================================")
    print(f"   HAMEAU — Démarrage de la Simulation")
    print(f"   Jours : {days} | Ticks/jour : {ticks_per_day} (1 tick = 5 min)")
    print(f"   Decider 2B : {'Mock déterministe' if use_mock else 'GPU local (CUDA RTX 3050)'}")
    print(f"   Bedrock : {cfg['bedrock']['model_id']} ({cfg['bedrock']['region']})")
    print(f"   Cassettes : {'Activées (0$ au rejeu)' if use_cassettes else 'Désactivées'}")
    print(f"===========================================================\n")

    world = build_default_village()
    agents = build_canonical_agents()

    decider_cfg = cfg.get("decider", {})
    decider = DeciderClient(
        checkpoint=decider_cfg.get("checkpoint", DeciderClient.DEFAULT_CHECKPOINT),
        device=decider_cfg.get("device", "cuda"),
        mock=use_mock,
        seed=cfg.get("seed", 42),
    )

    bedrock_cfg = cfg.get("bedrock", {})
    bedrock = BedrockClient(
        model_id=bedrock_cfg.get("model_id", "amazon.nova-micro-v1:0"),
        region_name=bedrock_cfg.get("region", "us-east-1"),
        max_budget_usd=bedrock_cfg.get("max_budget_usd", 2.00),
        price_per_1m_input=bedrock_cfg.get("pricing_per_1m_tokens", {}).get("input", 0.035),
        price_per_1m_output=bedrock_cfg.get("pricing_per_1m_tokens", {}).get("output", 0.140),
        cassettes_dir=bedrock_cfg.get("cassettes_dir", "cassettes"),
        use_cassettes=use_cassettes,
        seed=cfg.get("seed", 42),
    )

    mg_cfg = cfg.get("memory_gate", {})
    memory_gate = MemoryGate(
        decider_client=decider,
        top_k=mg_cfg.get("top_k_injected", 3),
        max_candidates=mg_cfg.get("max_candidates", 12),
        half_life_ticks=mg_cfg.get("recency_half_life_hours", 24.0) * 12.0,  # 12 ticks/heure
        w_recency=mg_cfg.get("weights", {}).get("recency", 0.333),
        w_importance=mg_cfg.get("weights", {}).get("importance", 0.333),
        w_relevance=mg_cfg.get("weights", {}).get("relevance", 0.334),
        confidence_green=decider_cfg.get("thresholds", {}).get("D3", {}).get("green", 0.55),
        confidence_orange=decider_cfg.get("thresholds", {}).get("D3", {}).get("orange", 0.35),
    )

    scenario = ScenarioManager()

    engine = SimulationEngine(
        world=world,
        agents=agents,
        decider=decider,
        bedrock=bedrock,
        memory_gate=memory_gate,
        scenario=scenario,
        config=cfg,
    )

    summary = engine.run(days=days, ticks_per_day=ticks_per_day)
    print(f"\nJournal de simulation enregistré : {summary['log_file']}")
    print(f"Pour visualiser le résultat, ouvrez 'viewer/index.html' dans votre navigateur.")


if __name__ == "__main__":
    main()
