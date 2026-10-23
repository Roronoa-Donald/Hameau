"""Command Line Interface for running HAMEAU simulation."""

import argparse
import os
os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")
import sys
import yaml
from pathlib import Path
from typing import Optional

from hameau.models.world import build_default_village
from hameau.simulation.distribution import build_canonical_agents
from hameau.simulation.scenario import ScenarioManager
from hameau.simulation.engine import SimulationEngine
from hameau.decisions import DeciderClient
from hameau.llm import BedrockClient
from patterns.memory_gate import MemoryGate


import functools
import http.server
import socketserver
import urllib.parse


class RestrictedViewerHandler(http.server.SimpleHTTPRequestHandler):
    """Serveur web strictement restreint au dossier viewer/ et aux fichiers de runs/."""

    def __init__(self, *args, repo_root: Optional[Path] = None, **kwargs):
        self.repo_root = repo_root or Path(__file__).resolve().parent.parent.parent
        self.viewer_dir = (self.repo_root / "viewer").resolve()
        self.runs_dir = (self.repo_root / "runs").resolve()
        super().__init__(*args, directory=str(self.viewer_dir), **kwargs)

    def translate_path(self, path: str) -> str:
        clean_path = urllib.parse.urlsplit(path).path
        clean_path = urllib.parse.unquote(clean_path).lstrip("/")

        # Route /runs/ autorisée pour charger les logs de simulation
        if clean_path.startswith("runs/"):
            sub_path = clean_path[len("runs/"):]
            target = (self.runs_dir / sub_path).resolve()
            if target.is_relative_to(self.runs_dir) and target.is_file():
                return str(target)
            return str(self.viewer_dir / "__not_found__")

        target = (self.viewer_dir / clean_path).resolve()
        if target.is_relative_to(self.viewer_dir):
            return str(target)
        return str(self.viewer_dir / "__not_found__")


def create_viewer_server(port: int = 8000, repo_root: Optional[Path] = None):
    """Crée un serveur HTTP lié exclusivement à 127.0.0.1 (localhost)."""
    root = repo_root or Path(__file__).resolve().parent.parent.parent
    handler_factory = functools.partial(RestrictedViewerHandler, repo_root=root)
    server = socketserver.TCPServer(("127.0.0.1", port), handler_factory)
    assigned_port = server.server_address[1]
    return server, assigned_port


def main():
    parser = argparse.ArgumentParser(description="HAMEAU — Multi-agent simulation with Strands Decider 2B and Amazon Nova Micro")
    parser.add_argument("--config", type=str, default="config.yaml", help="Path to config.yaml")
    parser.add_argument("--days", type=int, default=None, help="Number of simulated days")
    parser.add_argument("--ticks-per-day", type=int, default=None, help="Number of ticks per day (default 192)")
    parser.add_argument("--mock-decider", action="store_true", help="Use deterministic mock instead of local GPU")
    parser.add_argument("--decider-urls", type=str, default=None, help="Remote GPU worker URLs (comma-separated). Read from .env if omitted.")
    parser.add_argument("--no-cassettes", action="store_true", help="Disable Bedrock cassette cache")
    parser.add_argument("--output", type=str, default=None, help="JSONL log output file path (e.g. runs/real_gpu_run.jsonl)")
    parser.add_argument("--serve", action="store_true", help="Launch local web server for the viewer")
    parser.add_argument("--port", type=int, default=8000, help="Port for local web server (default 8000)")

    args = parser.parse_args()

    if args.serve:
        server, port = create_viewer_server(args.port)
        url = f"http://127.0.0.1:{port}/index.html"
        print(f"HAMEAU secure viewer server started at: {url}")
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")
        finally:
            server.server_close()
        return

    # Chargement éventuel de .env (URLs éphémères de Colab)
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass

    # Détermination des URLs distantes (CLI > .env > None)
    decider_urls_str = args.decider_urls or os.environ.get("DECIDER_URLS")

    # Lecture de la configuration
    config_path = Path(args.config)
    if not config_path.exists():
        print(f"Error: configuration file '{args.config}' not found.")
        sys.exit(1)

    with open(config_path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    if args.output:
        cfg.setdefault("logging", {})["log_filename"] = args.output

    days = args.days or cfg.get("simulation", {}).get("days", 1)
    ticks_per_day = args.ticks_per_day or cfg.get("simulation", {}).get("ticks_per_day", 192)

    use_mock = args.mock_decider
    use_cassettes = not args.no_cassettes

    if use_mock:
        decider_mode_str = "Deterministic Mock (no GPU)"
    elif decider_urls_str:
        decider_mode_str = f"Distributed GPU Colab ({decider_urls_str})"
    else:
        decider_mode_str = "Local GPU (CUDA RTX 3050)"

    print(f"===========================================================")
    print(f"   HAMEAU — Simulation Starting")
    print(f"   Days: {days} | Ticks/day: {ticks_per_day} (1 tick = 5 min)")
    print(f"   Decider 2B: {decider_mode_str}")
    print(f"   Bedrock: {cfg['bedrock']['model_id']} ({cfg['bedrock']['region']})")
    print(f"   Cassettes: {'Enabled ($0 on replay)' if use_cassettes else 'Disabled'}")
    print(f"===========================================================\n")

    world = build_default_village()
    agents = build_canonical_agents()

    decider_cfg = cfg.get("decider", {})
    decider = DeciderClient(
        checkpoint=decider_cfg.get("checkpoint", DeciderClient.DEFAULT_CHECKPOINT),
        device=decider_cfg.get("device", "cuda"),
        mock=use_mock,
        seed=cfg.get("seed", 42),
        server_urls=decider_urls_str if not use_mock else None,
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
        confidence_green=decider_cfg.get("thresholds", {}).get("D3", {}).get("green", 0.40),
        confidence_orange=decider_cfg.get("thresholds", {}).get("D3", {}).get("orange", 0.25),
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
    print(f"\nSimulation log saved to: {summary['log_file']}")
    print(f"To visualize the results, open 'viewer/index.html' in your browser.")


if __name__ == "__main__":
    main()
