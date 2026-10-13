"""Test calibration suite execution and metrics sanity."""

from pathlib import Path
from scripts.calibrate import evaluate_e1, evaluate_e2, evaluate_e3, compute_ece, compute_spearman
from hameau.decisions import DeciderClient


def test_spearman_computation():
    x = [1.0, 2.0, 3.0, 4.0, 5.0]
    y = [1.0, 2.0, 3.0, 4.0, 5.0]
    assert compute_spearman(x, y) == 1.0


def test_ece_computation():
    probs = [0.9, 0.8, 0.7, 0.6, 0.5]
    labels = [1, 1, 1, 0, 0]
    ece, bins = compute_ece(probs, labels, n_bins=5)
    assert 0.0 <= ece <= 1.0
    assert len(bins) == 5


def test_calibration_eval_datasets():
    client = DeciderClient(mock=True, seed=42)
    eval_dir = Path(__file__).resolve().parent.parent / "eval"

    res_e1 = evaluate_e1(client, eval_dir / "e1_importance.jsonl")
    assert res_e1["sample_count"] == 20
    assert 0.0 <= res_e1["mae"] <= 1.0

    res_e2 = evaluate_e2(client, eval_dir / "e2_relevance.jsonl")
    assert res_e2["sample_count"] == 20
    assert 0.0 <= res_e2["binary_accuracy"] <= 1.0

    res_e3 = evaluate_e3(client, eval_dir / "e3_calibration.jsonl")
    assert res_e3["sample_count"] == 20
    assert 0.0 <= res_e3["brier_score"] <= 1.0
    assert 0.0 <= res_e3["ece"] <= 1.0
