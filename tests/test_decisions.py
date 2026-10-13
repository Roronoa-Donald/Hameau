"""Unit tests for Decider questions, confidence, and client."""

from hameau.decisions import (
    DeciderClient,
    ConfidenceThresholds,
    classify_zone,
    build_d1_action_picker,
    build_d2_importance_scorer,
    build_d3_relevance_scorer,
    build_d4_talk_gate,
)


def test_confidence_zones():
    thresholds = ConfidenceThresholds(green=0.65, orange=0.40)
    assert classify_zone(0.85, thresholds) == "green"
    assert classify_zone(0.65, thresholds) == "green"
    assert classify_zone(0.50, thresholds) == "orange"
    assert classify_zone(0.40, thresholds) == "orange"
    assert classify_zone(0.39, thresholds) == "red"
    assert classify_zone(0.10, thresholds) == "red"


def test_decider_mock_client():
    client = DeciderClient(mock=True, seed=42)
    state = "Yao est sur la place du marché à 08h00. Il a reçu une rumeur."

    questions = {
        "D1": build_d1_action_picker({
            "livrer": "Effectuer sa tournée de livraison",
            "parler": "Parler à Awa devant la boulangerie",
            "pause": "Faire une pause",
        }),
        "D2": build_d2_importance_scorer("La mairie envisage de fermer le marché samedi."),
        "D3": build_d3_relevance_scorer("Yao se souvient que le marché est vital pour son travail."),
        "D4": build_d4_talk_gate("Awa"),
    }

    results = client.ask(state, questions)

    assert "D1" in results
    assert results["D1"]["type"] == "choice"
    assert results["D1"]["value"] in ["livrer", "parler", "pause"]
    assert "confidence" in results["D1"]

    assert "D2" in results
    assert results["D2"]["type"] == "score"
    assert 0.0 <= results["D2"]["value"] <= 1.0

    assert "D3" in results
    assert results["D3"]["type"] == "score"

    assert "D4" in results
    assert results["D4"]["type"] == "noul"
    assert isinstance(results["D4"]["value"], bool)

    assert client.total_decisions == 4
    assert client.total_tokens > 0
