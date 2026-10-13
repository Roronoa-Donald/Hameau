"""Benchmark Decider 2B environment (VRAM, CUDA, PyTorch, latency p50/p95).

Measures latency across 1, 4, and 8 grouped questions on a 300-word state.
Outputs results to results/decider_env.csv.
"""

import csv
import os
import sys
import time
import numpy as np
import torch

from strands_decider.infer import load_engine
from strands_decider.schema import ChoiceQuestion, NoulQuestion, ScoreQuestion


def check_module(name):
    try:
        __import__(name)
        return True
    except ImportError:
        return False


def make_300_word_state():
    words = [
        "Yao", "livreur", "du", "marché", "de", "Hameau", "est", "sur", "la", "place",
        "principale.", "Il", "observe", "les", "étals", "de", "légumes", "de", "Mariam",
        "et", "la", "boulangerie", "d'Awa", "qui", "embaume", "le", "pain", "chaud.",
        "Le", "maire", "Kofi", "discute", "devant", "la", "mairie", "avec", "Samuel",
        "le", "forgeron.", "Une", "inquiétude", "grandit", "au", "sujet", "d'une", "possible",
        "fermeture", "administrative", "du", "marché", "samedi", "matin.", "Les", "habitants",
        "s'interrogent", "sur", "les", "conséquences", "économiques", "et", "sociales", "pour",
        "le", "village.", "L'école", "est", "ouverte,", "Élise", "enseigne", "aux", "enfants,",
        "tandis", "que", "Nadia", "reçoit", "ses", "premiers", "patients", "au", "cabinet",
        "médical.", "Le", "café", "de", "la", "rivière", "accueille", "Paul", "qui", "lit",
        "les", "nouvelles", "avec", "attention.",
    ]
    # Multiply to reach ~300 words
    state = " ".join(words * 4)[:1800]
    return state


def build_questions_batch(count: int):
    qs = {}
    if count >= 1:
        qs["D1"] = ChoiceQuestion(
            instructions="Que doit faire Yao maintenant ?",
            criteria={"livrer": "Faire sa tournée", "parler": "Parler à Awa", "pause": "Faire une pause"}
        )
    if count >= 2:
        qs["D2"] = ScoreQuestion(
            instructions="Importance de la rumeur :",
            criteria=["1: insignifiant", "2: faible", "3: moyen", "4: important", "5: critique"]
        )
    if count >= 3:
        qs["D3"] = ScoreQuestion(
            instructions="Pertinence du souvenir :",
            criteria=["1: hors-sujet", "2: lointain", "3: utile", "4: déterminant"]
        )
    if count >= 4:
        qs["D4"] = NoulQuestion(
            instructions="Yao veut-il parler à Awa ?",
            criteria={"true": "engager la conversation", "false": "continuer son chemin"}
        )
    if count >= 5:
        qs["D5"] = ScoreQuestion(
            instructions="Intérêt de raconter la rumeur :",
            criteria=["1: nul", "2: anecdotique", "3: important", "4: urgent"]
        )
    if count >= 6:
        qs["D6"] = NoulQuestion(
            instructions="Est-ce le moment de réfléchir ?",
            criteria={"true": "oui", "false": "non"}
        )
    if count >= 7:
        qs["D7"] = NoulQuestion(
            instructions="Faut-il continuer à parler ?",
            criteria={"true": "continuer", "false": "conclure"}
        )
    if count >= 8:
        qs["D8"] = ScoreQuestion(
            instructions="Crédibilité du démenti :",
            criteria=["1: faux", "2: douteux", "3: plausible", "4: certain"]
        )
    return qs


def benchmark_model(checkpoint: str, model_label: str):
    print(f"\n--- Benchmarking {model_label} ({checkpoint}) on CUDA ---")
    t0 = time.time()
    try:
        engine = load_engine(checkpoint, device="cuda")
        load_time_s = round(time.time() - t0, 2)
        print(f"Loaded in {load_time_s}s")
    except Exception as e:
        print(f"Could not load {checkpoint}: {e}")
        return []

    state = make_300_word_state()
    results = []

    # Warmup
    _ = engine.ask(state, build_questions_batch(1))

    for num_q in [1, 4, 8]:
        qs = build_questions_batch(num_q)
        latencies = []
        for _ in range(5):
            t_start = time.perf_counter()
            _ = engine.ask(state, qs)
            t_end = time.perf_counter()
            latencies.append((t_end - t_start) * 1000.0)

        p50 = float(np.percentile(latencies, 50))
        p95 = float(np.percentile(latencies, 95))
        vram_mb = torch.cuda.max_memory_allocated() // (1024 * 1024)

        print(f"Batch {num_q} questions: p50={p50:.1f}ms, p95={p95:.1f}ms, VRAM={vram_mb}MB")
        results.append({
            "model": model_label,
            "checkpoint": checkpoint,
            "num_questions": num_q,
            "latency_p50_ms": round(p50, 1),
            "latency_p95_ms": round(p95, 1),
            "vram_used_mb": vram_mb,
            "vram_total_mb": torch.cuda.get_device_properties(0).total_memory // (1024 * 1024),
            "torch_version": torch.__version__,
            "cuda_available": torch.cuda.is_available(),
            "flash_linear_attention": check_module("flash_linear_attention"),
            "causal_conv1d": check_module("causal_conv1d"),
        })

    return results


def main():
    has_fla = check_module("flash_linear_attention")
    has_conv = check_module("causal_conv1d")
    print(f"PyTorch: {torch.__version__}, CUDA: {torch.cuda.is_available()}")
    print(f"flash-linear-attention: {has_fla}, causal-conv1d: {has_conv}")

    all_results = []

    # Model v21 (local)
    v21_res = benchmark_model("StrandsAgents/strands-decider-2B-hobson-v21", "hobson-v21")
    all_results.extend(v21_res)

    out_csv = "results/decider_env.csv"
    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        if all_results:
            writer = csv.DictWriter(f, fieldnames=list(all_results[0].keys()))
            writer.writeheader()
            writer.writerows(all_results)
    print(f"\nWritten {len(all_results)} benchmark rows to {out_csv}")


if __name__ == "__main__":
    main()
