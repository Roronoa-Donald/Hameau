"""Tests for Decider score normalization, confidence zones, and error handling (A2)."""

import pytest
from strands_decider.schema import ScoreAnswer, ChoiceAnswer, NoulAnswer
from hameau.decisions.client import DeciderClient
from hameau.decisions.confidence import ConfidenceThresholds, classify_zone, ZoneType


def test_score_normalization_5_levels():
    """Verify that a 5-level rubric (index 0..4) is strictly normalized to [0.0, 1.0]."""
    client = DeciderClient(mock=True)
    raw_answer = ScoreAnswer(
        score=2.85,  # expected level index in [0, 4]
        legend={"0": "1: trivial", "1": "2: low", "2": "3: mid", "3": "4: high", "4": "5: extreme"},
        probabilities={"0": 0.05, "1": 0.15, "2": 0.35, "3": 0.35, "4": 0.10},
        confidence=0.72,
    )
    formatted = client._format_answer(raw_answer)

    assert formatted["type"] == "score"
    # 2.85 / (5 - 1) = 2.85 / 4 = 0.7125
    assert formatted["value"] == pytest.approx(0.7125, rel=1e-3)
    assert formatted["raw_score"] == pytest.approx(2.85, rel=1e-3)
    assert 0.0 <= formatted["value"] <= 1.0


def test_score_normalization_4_levels():
    """Verify that a 4-level rubric (index 0..3, e.g. D8/D5) is strictly normalized to [0.0, 1.0]."""
    client = DeciderClient(mock=True)
    raw_answer = ScoreAnswer(
        score=1.5,
        legend={"0": "1: fausse", "1": "2: douteux", "2": "3: plausible", "3": "4: certain"},
        probabilities={"0": 0.1, "1": 0.4, "2": 0.4, "3": 0.1},
        confidence=0.60,
    )
    formatted = client._format_answer(raw_answer)

    # 1.5 / (4 - 1) = 1.5 / 3 = 0.50
    assert formatted["value"] == pytest.approx(0.50, rel=1e-3)
    assert formatted["raw_score"] == pytest.approx(1.5, rel=1e-3)


def test_confidence_zones_all_types():
    """Verify confidence classification for green, orange, and red zones."""
    th = ConfidenceThresholds(green=0.60, orange=0.40)
    assert classify_zone(0.75, th) == "green"
    assert classify_zone(0.50, th) == "orange"
    assert classify_zone(0.30, th) == "red"


def test_no_silent_mock_fallback_on_real_mode():
    """Verify that if real Decider engine fails to load and mock=False, an explicit error is raised."""
    # Pointing to an invalid checkpoint must raise an error, never fall back silently to mock
    client = DeciderClient(checkpoint="nonexistent/fake-model-checkpoint-1234", mock=False)
    with pytest.raises(Exception):
        client.load()
