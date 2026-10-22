"""Micro-benchmark for Strands Decider 2B real latency and throughput (Experiment E0)."""

import csv
import json
import os
import platform
import subprocess
import sys
import time
from pathlib import Path
import numpy as np
import torch

from strands_decider.infer import load_engine
from strands_decider.schema import ChoiceQuestion, ScoreQuestion

def get_git_commit():
    try:
        p = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True)
        return p.stdout.strip()
    except Exception:
        return "unknown"

def get_git_dirty():
    try:
        p = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True, check=True)
        return len(p.stdout.strip()) > 0
    except Exception:
        return False

def check_kernels():
    fla_present = False
    causal_present = False
    try:
        import flash_linear_attention
        fla_present = True
    except ImportError:
        fla_present = False

    try:
        import causal_conv1d
        causal_present = True
    except ImportError:
        causal_present = False

    return fla_present, causal_present

def build_state(token_count: int) -> str:
    # Build text approximately token_count words
    base_sentence = (
        "Yao le livreur du marche de Hameau se deplace sur la place centrale vers la boulangerie d Awa "
        "en observant les passants sous le ciel couvert d un matin d automne avec son chargement de sacs. "
    )
    words = base_sentence.split()
    repeated = (words * ((token_count // len(words)) + 2))[:token_count]
    return " ".join(repeated)

def build_questions(count: int):
    questions = {}
    for i in range(count):
        if i % 2 == 0:
            questions[f"q_{i}"] = ChoiceQuestion(
                instructions=f"Que doit faire l habitant a ce moment précis (arbitrage {i}) ?",
                criteria={
                    "routine": "Poursuivre sa tâche habituelle sans interruption",
                    "pause": "Faire une pause et regarder autour de soi",
                    "marche": "Se diriger vers les étals du marché",
                    "rentrer": "Rentrer à sa maison pour se reposer"
                }
            )
        else:
            questions[f"q_{i}"] = ScoreQuestion(
                instructions=f"Évaluer l importance de cet événement pour l habitant {i}",
                criteria=[
                    "1: Insignifiant ou bruit de fond",
                    "2: Anecdotique ou routine banale",
                    "3: Notable pour le quotidien",
                    "4: Important pour ses objectifs",
                    "5: Critique ou alerte majeure"
                ]
            )
    return questions

def run_benchmark():
    print("=" * 60)
    print("   HAMEAU — Micro-Benchmark Strands Decider 2B (E0)")
    print("=" * 60)

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Target Device: {device}")
    if device == "cuda":
        gpu_name = torch.cuda.get_device_name(0)
        gpu_vram = torch.cuda.get_device_properties(0).total_memory / 1e9
        print(f"GPU: {gpu_name} ({gpu_vram:.2f} GB total)")
    else:
        gpu_name = platform.processor()
        gpu_vram = 0.0

    fla_present, causal_present = check_kernels()
    print(f"Kernel flash-linear-attention: {'PRESENT' if fla_present else 'ABSENT (PyTorch ref fallback)'}")
    print(f"Kernel causal_conv1d: {'PRESENT' if causal_present else 'ABSENT (PyTorch ref fallback)'}")

    checkpoint = "StrandsAgents/strands-decider-2B-hobson-v21"
    print(f"\nLoading model {checkpoint} on {device}...")
    t_load_start = time.perf_counter()
    engine = load_engine(checkpoint, device=device)
    t_load_end = time.perf_counter()
    load_time = t_load_end - t_load_start
    print(f"Loaded in {load_time:.2f}s")

    vram_alloc = torch.cuda.memory_allocated() / 1e6 if device == "cuda" else 0.0
    vram_res = torch.cuda.memory_reserved() / 1e6 if device == "cuda" else 0.0
    print(f"Initial VRAM allocated: {vram_alloc:.1f} MB, reserved: {vram_res:.1f} MB")

    state_token_lengths = [150, 300, 600]
    question_counts = [1, 4, 8, 16]
    warm_reps = 5

    out_csv = Path("results/decider_latency.csv")
    out_csv.parent.mkdir(parents=True, exist_ok=True)

    rows = []

    print("\nRunning matrix benchmark (State tokens x Grouped questions)...")
    for tokens in state_token_lengths:
        state_text = build_state(tokens)
        for q_count in question_counts:
            questions = build_questions(q_count)

            # 1. COLD RUN
            if device == "cuda":
                torch.cuda.synchronize()
            t0 = time.perf_counter()
            res_cold = engine.ask(state_text, questions)
            if device == "cuda":
                torch.cuda.synchronize()
            lat_cold_ms = (time.perf_counter() - t0) * 1000.0

            cur_alloc = torch.cuda.memory_allocated() / 1e6 if device == "cuda" else 0.0
            cur_res = torch.cuda.memory_reserved() / 1e6 if device == "cuda" else 0.0

            rows.append({
                "device": gpu_name,
                "state_tokens": tokens,
                "num_questions": q_count,
                "regime": "cold",
                "latency_p50_ms": round(lat_cold_ms, 2),
                "latency_p95_ms": round(lat_cold_ms, 2),
                "latency_max_ms": round(lat_cold_ms, 2),
                "throughput_qps": round(q_count / (lat_cold_ms / 1000.0), 2),
                "vram_alloc_mb": round(cur_alloc, 1),
                "vram_reserved_mb": round(cur_res, 1),
                "fla_present": fla_present
            })

            # 2. WARM RUNS
            warm_lats = []
            for _ in range(warm_reps):
                if device == "cuda":
                    torch.cuda.synchronize()
                t0 = time.perf_counter()
                res_warm = engine.ask(state_text, questions)
                if device == "cuda":
                    torch.cuda.synchronize()
                warm_lats.append((time.perf_counter() - t0) * 1000.0)

            p50 = float(np.percentile(warm_lats, 50))
            p95 = float(np.percentile(warm_lats, 95))
            mx = float(np.max(warm_lats))
            qps = q_count / (p50 / 1000.0)

            cur_alloc = torch.cuda.memory_allocated() / 1e6 if device == "cuda" else 0.0
            cur_res = torch.cuda.memory_reserved() / 1e6 if device == "cuda" else 0.0

            rows.append({
                "device": gpu_name,
                "state_tokens": tokens,
                "num_questions": q_count,
                "regime": "warm",
                "latency_p50_ms": round(p50, 2),
                "latency_p95_ms": round(p95, 2),
                "latency_max_ms": round(mx, 2),
                "throughput_qps": round(qps, 2),
                "vram_alloc_mb": round(cur_alloc, 1),
                "vram_reserved_mb": round(cur_res, 1),
                "fla_present": fla_present
            })

            print(
                f"State {tokens:3d} toks | Questions: {q_count:2d} | "
                f"Cold: {lat_cold_ms:6.1f} ms | Warm p50: {p50:6.1f} ms (p95: {p95:6.1f} ms) | "
                f"Throughput: {qps:5.2f} Q/s | VRAM: {cur_alloc:.0f} MB"
            )

    with open(out_csv, "w", encoding="utf-8", newline="") as f:
        fieldnames = [
            "device", "state_tokens", "num_questions", "regime",
            "latency_p50_ms", "latency_p95_ms", "latency_max_ms",
            "throughput_qps", "vram_alloc_mb", "vram_reserved_mb", "fla_present"
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)

    print(f"\nWritten benchmark results to {out_csv}")

    # Generate Manifest E0
    manifest = {
        "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "experiment": "E0_decider_latency",
        "git_commit": get_git_commit(),
        "git_dirty": get_git_dirty(),
        "hardware": {
            "device_type": device,
            "device_name": gpu_name,
            "total_vram_gb": round(gpu_vram, 2)
        },
        "environment": {
            "python_version": sys.version.split()[0],
            "torch_version": torch.__version__,
            "cuda_available": torch.cuda.is_available(),
            "flash_linear_attention_installed": fla_present,
            "causal_conv1d_installed": causal_present
        },
        "model": {
            "checkpoint": checkpoint,
            "load_time_seconds": round(load_time, 2),
            "vram_allocated_mb_post_load": round(vram_alloc, 1)
        }
    }

    manifest_path = Path("results/manifest_e0.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    print(f"Written manifest to {manifest_path}")

if __name__ == "__main__":
    run_benchmark()
