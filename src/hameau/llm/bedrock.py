"""Amazon Bedrock client using Amazon Nova Micro with cassette caching and budget guardrails."""

import hashlib
import json
import os
import time
from pathlib import Path
from typing import Any, Dict, List, Optional
import boto3
from botocore.exceptions import ClientError


class BudgetExceededError(RuntimeError):
    """Levée lorsque le plafond budgétaire Bedrock est atteint."""
    pass


class BedrockClient:
    """Client Bedrock optimisé pour Amazon Nova Micro (amazon.nova-micro-v1:0)."""

    def __init__(
        self,
        model_id: str = "amazon.nova-micro-v1:0",
        region_name: str = "us-east-1",
        max_budget_usd: float = 2.00,
        price_per_1m_input: float = 0.035,
        price_per_1m_output: float = 0.140,
        cassettes_dir: str = "cassettes",
        use_cassettes: bool = True,
        seed: int = 42,
    ):
        self.model_id = model_id
        self.region_name = region_name
        self.max_budget_usd = max_budget_usd
        self.price_per_1m_input = price_per_1m_input
        self.price_per_1m_output = price_per_1m_output
        self.cassettes_dir = Path(cassettes_dir)
        self.use_cassettes = use_cassettes
        self.seed = seed

        self.cassettes_dir.mkdir(parents=True, exist_ok=True)

        self._client = None

        # Compteurs d'observabilité
        self.total_calls: int = 0
        self.calls_from_cassette: int = 0
        self.total_input_tokens: int = 0
        self.total_output_tokens: int = 0
        self.total_cost_usd: float = 0.0

    @property
    def client(self):
        if self._client is None:
            from botocore.config import Config
            config = Config(read_timeout=15, retries={"max_attempts": 3, "mode": "standard"})
            self._client = boto3.client("bedrock-runtime", region_name=self.region_name, config=config)
        return self._client

    def _compute_cassette_key(
        self,
        messages: List[Dict[str, Any]],
        system_prompt: Optional[str],
        max_tokens: int,
        temperature: float,
    ) -> str:
        payload = {
            "model_id": self.model_id,
            "seed": self.seed,
            "messages": messages,
            "system": system_prompt,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }
        raw = json.dumps(payload, sort_keys=True)
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def generate(
        self,
        messages: List[Dict[str, Any]],
        system_prompt: Optional[str] = None,
        max_tokens: int = 150,
        temperature: float = 0.7,
    ) -> Dict[str, Any]:
        """Génère une réponse avec Amazon Nova Micro, ou la lit depuis la cassette locale."""
        if self.total_cost_usd >= self.max_budget_usd:
            raise BudgetExceededError(
                f"Plafond dur de budget AWS ({self.max_budget_usd:.2f} $) atteint. Arrêt préventif."
            )

        key = self._compute_cassette_key(messages, system_prompt, max_tokens, temperature)
        cassette_path = self.cassettes_dir / f"{key}.json"

        # 1. Vérification cassette
        if self.use_cassettes and cassette_path.exists():
            with open(cassette_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.total_calls += 1
            self.calls_from_cassette += 1
            return {
                "text": data["text"],
                "input_tokens": data["input_tokens"],
                "output_tokens": data["output_tokens"],
                "cost_usd": 0.0,  # 0$ car rejoué depuis cassette
                "latency_ms": 0.5,
                "from_cassette": True,
            }

        # 2. Appel direct Bedrock Converse API
        t0 = time.perf_counter()

        kwargs: Dict[str, Any] = {
            "modelId": self.model_id,
            "messages": messages,
            "inferenceConfig": {
                "maxTokens": max_tokens,
                "temperature": temperature,
            },
        }
        if system_prompt:
            kwargs["system"] = [{"text": system_prompt}]

        try:
            response = self.client.converse(**kwargs)
        except Exception as e:
            raise RuntimeError(f"Amazon Bedrock converse failed for model {self.model_id}: {e}") from e
        latency_ms = round((time.perf_counter() - t0) * 1000, 2)

        # Extraction
        content_text = ""
        output_blocks = response.get("output", {}).get("message", {}).get("content", [])
        if output_blocks and "text" in output_blocks[0]:
            content_text = output_blocks[0]["text"].strip()

        usage = response.get("usage", {})
        inp_tokens = usage.get("inputTokens", 0)
        out_tokens = usage.get("outputTokens", 0)

        cost = (
            (inp_tokens / 1_000_000.0) * self.price_per_1m_input
            + (out_tokens / 1_000_000.0) * self.price_per_1m_output
        )

        self.total_calls += 1
        self.total_input_tokens += inp_tokens
        self.total_output_tokens += out_tokens
        self.total_cost_usd += cost

        # Sauvegarde en cassette (même si la lecture du cache est désactivée, pour permettre le rejeu ultérieur)
        if self.cassettes_dir:
            record = {
                "text": content_text,
                "input_tokens": inp_tokens,
                "output_tokens": out_tokens,
                "cost_usd": round(cost, 6),
                "timestamp": time.time(),
            }
            with open(cassette_path, "w", encoding="utf-8") as f:
                json.dump(record, f, ensure_ascii=False, indent=2)

        return {
            "text": content_text,
            "input_tokens": inp_tokens,
            "output_tokens": out_tokens,
            "cost_usd": round(cost, 6),
            "latency_ms": latency_ms,
            "from_cassette": False,
        }
