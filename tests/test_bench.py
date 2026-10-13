"""Test benchmark suite execution and output consistency."""

from pathlib import Path
from bench.run_benchmark import run_strategy_a_heuristic, run_strategy_c_hybrid, run_strategy_ablation, run_strategy_b_all_llm


def test_benchmark_strategies():
    res_a = run_strategy_a_heuristic(days=1, ticks_per_day=12)
    assert res_a["decisions_count"] > 0
    assert res_a["bedrock_calls"] == 0

    res_c = run_strategy_c_hybrid(days=1, ticks_per_day=12)
    assert res_c["decisions_count"] > 0
    assert res_c["bedrock_calls"] >= 0

    res_abl = run_strategy_ablation(days=1, ticks_per_day=12)
    assert res_abl["decisions_count"] > 0

    res_b = run_strategy_b_all_llm(days=1, ticks_per_day=12)
    assert res_b["bedrock_calls"] > res_c["bedrock_calls"]
