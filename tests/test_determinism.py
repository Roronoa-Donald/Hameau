"""Tests for Decider mock determinism across PYTHONHASHSEED (A6)."""

import os
import subprocess
import pytest


def test_mock_determinism_across_pythonhashseed():
    """Verify that MockDecider gives identical outputs regardless of PYTHONHASHSEED."""
    code = """
import os
from hameau.decisions import DeciderClient, build_d1_action_picker, build_d2_importance_scorer, build_d6_reflect_gate
c = DeciderClient(mock=True, seed=42)
res = c.ask("state_agent_test", {
    "D1": build_d1_action_picker({"a": "alpha", "b": "beta", "c": "gamma"}),
    "D2": build_d2_importance_scorer("nouvelle information reçue"),
    "D6": build_d6_reflect_gate(),
})
print(res["D1"]["value"], res["D1"]["confidence"])
print(res["D2"]["value"], res["D2"]["confidence"])
print(res["D6"]["value"], res["D6"]["confidence"])
"""
    out1 = subprocess.check_output(
        ["uv", "run", "python", "-c", code],
        env=dict(os.environ, PYTHONHASHSEED="1111"),
    ).decode().strip()

    out2 = subprocess.check_output(
        ["uv", "run", "python", "-c", code],
        env=dict(os.environ, PYTHONHASHSEED="9999"),
    ).decode().strip()

    assert out1 == out2, f"Outputs differ across PYTHONHASHSEED!\nHash 1111:\n{out1}\nHash 9999:\n{out2}"
