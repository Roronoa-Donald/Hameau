"""Unit tests for BedrockClient with Amazon Nova Micro."""

import os
import pytest
from hameau.llm import BedrockClient, BudgetExceededError


def test_bedrock_nova_micro_invocation(tmp_path):
    cassettes_dir = tmp_path / "test_cassettes"
    client = BedrockClient(
        model_id="amazon.nova-micro-v1:0",
        region_name="us-east-1",
        max_budget_usd=0.50,
        cassettes_dir=str(cassettes_dir),
        use_cassettes=True,
    )

    messages = [{"role": "user", "content": [{"text": "Dis 'Bonjour Hameau' en 2 mots."}]}]

    # Premier appel (réseau vers Bedrock ou mock offline si absent)
    try:
        res1 = client.generate(messages, max_tokens=10)
    except Exception:
        from unittest.mock import MagicMock
        mock_client = MagicMock()
        mock_client.converse.return_value = {
            "output": {"message": {"content": [{"text": "Bonjour Hameau"}]}},
            "usage": {"inputTokens": 10, "outputTokens": 2},
        }
        client._client = mock_client
        res1 = client.generate(messages, max_tokens=10)

    assert len(res1["text"]) > 0
    assert res1["from_cassette"] is False
    assert client.total_calls == 1
    assert client.calls_from_cassette == 0
    assert client.total_cost_usd > 0.0

    # Deuxième appel identique (doit être servi par la cassette, coût 0$)
    res2 = client.generate(messages, max_tokens=10)
    assert res2["text"] == res1["text"]
    assert res2["from_cassette"] is True
    assert client.total_calls == 2
    assert client.calls_from_cassette == 1


def test_budget_exceeded(tmp_path):
    cassettes_dir = tmp_path / "test_cassettes"
    client = BedrockClient(
        model_id="amazon.nova-micro-v1:0",
        max_budget_usd=0.0000001,  # Budget minuscule pour forcer le dépassement
        cassettes_dir=str(cassettes_dir),
        use_cassettes=False,
    )
    client.total_cost_usd = 0.0000005  # Dépassement simulé

    with pytest.raises(BudgetExceededError):
        client.generate([{"role": "user", "content": [{"text": "test"}]}])
