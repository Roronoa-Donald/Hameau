#!/usr/bin/env python3
"""Strands Decider 2B Calibration and Evaluation Suite for HAMEAU (B3).

Measures:
- E1: Importance scoring Mean Absolute Error (MAE) and Spearman rank correlation.
- E2: Relevance scoring MAE and Top-k alignment.
- E3: Binary classification Brier Score and Expected Calibration Error (ECE).
Outputs: results/calibration.csv and prints markdown summary table.
"""

import argparse
import csv
import json
import math
from pathlib import Path
from typing import Any, Dict, List, Tuple

from hameau.decisions import DeciderClient
from hameau.decisions.questions import (
    build_d2_importance_scorer,
    build_d3_relevance_scorer,
)
from strands_decider.schema import NoulQuestion


def compute_spearman(x: List[float], y: List[float]) -> float:
    """Computes Spearman rank correlation coefficient."""
    n = len(x)
    if n <= 1:
        return 1.0

    def rank(values: List[float]) -> List[float]:
        sorted_indices = sorted(range(n), key=lambda i: values[i])
        ranks = [0.0] * n
        i = 0
        while i < n:
            j = i
            while j < n - 1 and values[sorted_indices[j]] == values[sorted_indices[j + 1]]:
                j += 1
            avg_rank = (i + j) / 2.0 + 1.0
            for k in range(i, j + 1):
                ranks[sorted_indices[k]] = avg_rank
            i = j + 1
        return ranks

    rx = rank(x)
    ry = rank(y)
    d_sq = sum((rx[i] - ry[i]) ** 2 for i in range(n))
    return 1.0 - (6.0 * d_sq) / (n * (n**2 - 1))


def compute_ece(probs: List[float], labels: List[int], n_bins: int = 5) -> Tuple[float, List[Dict[str, Any]]]:
    """Computes Expected Calibration Error (ECE) and bin details."""
    n = len(probs)
    bin_size = 1.0 / n_bins
    bins_data = []
    total_ece = 0.0

    for b in range(n_bins):
        bin_lower = b * bin_size
        bin_upper = (b + 1) * bin_size
        # Filter items in bin
        items = [
            (p, y) for p, y in zip(probs, labels)
            if (bin_lower <= p < bin_upper) or (b == n_bins - 1 and bin_lower <= p <= bin_upper)
        ]
        count = len(items)
        if count > 0:
            avg_conf = sum(p for p, _ in items) / count
            avg_acc = sum(y for _, y in items) / count
            gap = abs(avg_acc - avg_conf)
            weighted_gap = (count / n) * gap
            total_ece += weighted_gap
        else:
            avg_conf = (bin_lower + bin_upper) / 2.0
            avg_acc = 0.0
            gap = 0.0

        bins_data.append({
            "bin": f"[{bin_lower:.1f}, {bin_upper:.1f}]",
            "count": count,
            "avg_conf": round(avg_conf, 3),
            "avg_acc": round(avg_acc, 3),
            "gap": round(gap, 3),
        })

    return round(total_ece, 4), bins_data


def evaluate_e1(client: DeciderClient, filepath: Path) -> Dict[str, Any]:
    """Evaluates E1 (Importance Scorer D2)."""
    samples = [json.loads(line) for line in filepath.read_text(encoding="utf-8").strip().splitlines() if line]
    preds = []
    targets = []
    latencies = []

    for item in samples:
        state = item["situation"]
        q = build_d2_importance_scorer(item["observation"])
        res = client.ask(state, {"d2": q})
        ans = res.get("d2", {})
        preds.append(ans.get("value", 0.5))
        targets.append(item["expected_score"])
        if "latency_ms" in ans:
            latencies.append(ans["latency_ms"])

    mae = sum(abs(p - t) for p, t in zip(preds, targets)) / len(samples)
    spearman = compute_spearman(preds, targets)
    avg_latency = sum(latencies) / len(latencies) if latencies else 0.0

    return {
        "dataset": "E1_Importance",
        "sample_count": len(samples),
        "mae": round(mae, 4),
        "spearman_rank_corr": round(spearman, 4),
        "avg_latency_ms": round(avg_latency, 2),
    }


def evaluate_e2(client: DeciderClient, filepath: Path) -> Dict[str, Any]:
    """Evaluates E2 (Relevance Scorer D3)."""
    samples = [json.loads(line) for line in filepath.read_text(encoding="utf-8").strip().splitlines() if line]
    preds = []
    targets = []
    latencies = []

    for item in samples:
        state = item["situation"]
        q = build_d3_relevance_scorer(item["memory"])
        res = client.ask(state, {"d3": q})
        ans = res.get("d3", {})
        preds.append(ans.get("value", 0.5))
        targets.append(item["expected_score"])
        if "latency_ms" in ans:
            latencies.append(ans["latency_ms"])

    mae = sum(abs(p - t) for p, t in zip(preds, targets)) / len(samples)
    spearman = compute_spearman(preds, targets)
    # Binary classification accuracy for relevant (> 0.5)
    binary_preds = [1 if p >= 0.5 else 0 for p in preds]
    binary_targets = [1 if t >= 0.5 else 0 for t in targets]
    acc = sum(1 for p, t in zip(binary_preds, binary_targets) if p == t) / len(samples)

    avg_latency = sum(latencies) / len(latencies) if latencies else 0.0

    return {
        "dataset": "E2_Relevance",
        "sample_count": len(samples),
        "mae": round(mae, 4),
        "spearman_rank_corr": round(spearman, 4),
        "binary_accuracy": round(acc, 4),
        "avg_latency_ms": round(avg_latency, 2),
    }


def evaluate_e3(client: DeciderClient, filepath: Path) -> Dict[str, Any]:
    """Evaluates E3 (Calibration, Brier Score, and ECE)."""
    samples = [json.loads(line) for line in filepath.read_text(encoding="utf-8").strip().splitlines() if line]
    probs = []
    labels = []
    latencies = []

    for item in samples:
        state = item["state"]
        q = NoulQuestion(instructions=item["question"])
        res = client.ask(state, {"noul": q})
        ans = res.get("noul", {})
        # Probability of True
        p = ans.get("probability", 0.5)
        probs.append(p)
        labels.append(item["true_label"])
        if "latency_ms" in ans:
            latencies.append(ans["latency_ms"])

    # Brier Score = 1/N sum (p - y)^2
    brier_score = sum((p - y) ** 2 for p, y in zip(probs, labels)) / len(samples)
    ece, bins_data = compute_ece(probs, labels, n_bins=5)
    acc = sum(1 for p, y in zip(probs, labels) if (p >= 0.5 and y == 1) or (p < 0.5 and y == 0)) / len(samples)
    avg_latency = sum(latencies) / len(latencies) if latencies else 0.0

    return {
        "dataset": "E3_Calibration",
        "sample_count": len(samples),
        "brier_score": round(brier_score, 4),
        "ece": round(ece, 4),
        "accuracy": round(acc, 4),
        "avg_latency_ms": round(avg_latency, 2),
        "bins_data": bins_data,
    }


def main():
    parser = argparse.ArgumentParser(description="Strands Decider 2B Calibration Suite (E1, E2, E3)")
    parser.add_argument("--mock", action="store_true", default=True, help="Use deterministic mock decider")
    parser.add_argument("--device", type=str, default="cuda", help="Device for real model (cuda/cpu)")
    parser.add_argument("--checkpoint", type=str, default="StrandsAgents/strands-decider-2B-hobson-v21")
    parser.add_argument("--output-csv", type=str, default="results/calibration.csv", help="Path to write CSV")
    args = parser.parse_args()

    eval_dir = Path("eval")
    e1_file = eval_dir / "e1_importance.jsonl"
    e2_file = eval_dir / "e2_relevance.jsonl"
    e3_file = eval_dir / "e3_calibration.jsonl"

    for f in [e1_file, e2_file, e3_file]:
        if not f.exists():
            raise FileNotFoundError(f"Evaluation file '{f}' not found.")

    client = DeciderClient(
        checkpoint=args.checkpoint,
        device=args.device,
        mock=args.mock,
        seed=42,
    )
    client.load()

    print("==========================================================")
    print("   HAMEAU Strands Decider Calibration & Benchmark")
    print(f"   Backend: {'Mock' if args.mock else args.checkpoint}")
    print("==========================================================")

    res_e1 = evaluate_e1(client, e1_file)
    print(f"[E1] Importance Scoring : MAE={res_e1['mae']} | Spearman r={res_e1['spearman_rank_corr']}")

    res_e2 = evaluate_e2(client, e2_file)
    print(f"[E2] Relevance Scoring  : MAE={res_e2['mae']} | Spearman r={res_e2['spearman_rank_corr']} | Acc={res_e2['binary_accuracy']}")

    res_e3 = evaluate_e3(client, e3_file)
    print(f"[E3] Confidence Calib.  : Brier Score={res_e3['brier_score']} | ECE={res_e3['ece']} | Acc={res_e3['accuracy']}")

    # Write CSV
    out_path = Path(args.output_csv)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["dataset", "sample_count", "metric_primary", "value_primary", "metric_secondary", "value_secondary", "backend"])
        writer.writerow(["E1_Importance", res_e1["sample_count"], "MAE", res_e1["mae"], "Spearman_r", res_e1["spearman_rank_corr"], "mock" if args.mock else "gpu"])
        writer.writerow(["E2_Relevance", res_e2["sample_count"], "MAE", res_e2["mae"], "Spearman_r", res_e2["spearman_rank_corr"], "mock" if args.mock else "gpu"])
        writer.writerow(["E3_Calibration", res_e3["sample_count"], "Brier_Score", res_e3["brier_score"], "ECE", res_e3["ece"], "mock" if args.mock else "gpu"])

    print(f"\nCalibration metrics successfully recorded in: {out_path}")
    print("==========================================================")


if __name__ == "__main__":
    main()
