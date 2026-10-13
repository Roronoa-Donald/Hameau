"""Strands Decider 2B client supporting GPU (RTX 3050), CPU, and deterministic mock."""

import time
from typing import Any, Dict, List, Optional
import torch

from strands_decider.infer import SystemOneEngine, load_engine
from strands_decider.schema import (
    Answer,
    ChoiceAnswer,
    NoulAnswer,
    ScoreAnswer,
    Question,
    ChoiceQuestion,
    NoulQuestion,
    ScoreQuestion,
    SystemOneResponse,
)
from .confidence import ConfidenceThresholds, classify_zone, ZoneType


class DeciderClient:
    """Client gérant les requêtes à Strands Decider 2B."""

    DEFAULT_CHECKPOINT = "StrandsAgents/strands-decider-2B-hobson-v21"

    def __init__(
        self,
        checkpoint: str = DEFAULT_CHECKPOINT,
        device: str = "cuda",
        mock: bool = False,
        seed: int = 42,
    ):
        self.checkpoint = checkpoint
        self.device = device
        self.mock = mock
        self.seed = seed
        self._engine: Optional[SystemOneEngine] = None
        self._rng = None

        # Métriques cumulées
        self.total_decisions: int = 0
        self.total_tokens: int = 0
        self.total_latency_ms: float = 0.0

        if self.mock:
            import random
            self._rng = random.Random(seed)

    def load(self) -> None:
        """Charge le modèle sur GPU/CPU si ce n'est pas déjà fait."""
        if self.mock:
            return
        if self._engine is None:
            # Vérifier si CUDA est disponible
            target_device = self.device
            if target_device == "cuda" and not torch.cuda.is_available():
                target_device = "cpu"

            try:
                self._engine = load_engine(self.checkpoint, device=target_device)
                self.device = target_device
            except Exception as e:
                # Repli de sécurité si l'environnement n'a pas accès aux poids
                print(f"[DeciderClient] Échec chargement GPU ({e}), activation du mode mock déterministe.")
                self.mock = True
                import random
                self._rng = random.Random(self.seed)

    def ask(
        self,
        state: str | dict | list,
        questions: Dict[str, Question],
    ) -> Dict[str, Dict[str, Any]]:
        """Pose un lot de questions sur un même état."""
        t_start = time.perf_counter()

        if not self.mock and self._engine is None:
            self.load()

        if self.mock or self._engine is None:
            results = self._mock_ask(state, questions)
            latency_ms = round((time.perf_counter() - t_start) * 1000, 2)
            input_tokens = len(str(state).split()) + sum(len(str(q).split()) for q in questions.values())
        else:
            response: SystemOneResponse = self._engine.ask(state, questions)
            latency_ms = round((time.perf_counter() - t_start) * 1000, 2)
            input_tokens = response.usage.input_tokens
            results = {}
            for name, ans in response.answers.items():
                results[name] = self._format_answer(ans)

        self.total_decisions += len(questions)
        self.total_tokens += input_tokens
        self.total_latency_ms += latency_ms

        # Injection métadonnées globales
        for name in results:
            results[name]["latency_ms"] = latency_ms
            results[name]["model"] = "mock" if self.mock else self.checkpoint

        return results

    def _format_answer(self, ans: Answer) -> Dict[str, Any]:
        """Convertit la réponse System One en format unifié."""
        if isinstance(ans, ChoiceAnswer):
            return {
                "type": "choice",
                "value": ans.choice,
                "probabilities": ans.probabilities,
                "confidence": ans.confidence,
            }
        elif isinstance(ans, ScoreAnswer):
            return {
                "type": "score",
                "value": ans.score,
                "probabilities": ans.probabilities,
                "confidence": ans.confidence,
                "legend": ans.legend,
            }
        elif isinstance(ans, NoulAnswer):
            prob = ans.noul
            confidence = round(abs(2 * prob - 1), 4)  # distance à l'incertitude 0.5
            return {
                "type": "noul",
                "value": prob >= 0.5,
                "probability": prob,
                "confidence": confidence,
            }
        raise ValueError(f"Type de réponse inconnu: {type(ans)}")

    def _mock_ask(
        self,
        state: str | dict | list,
        questions: Dict[str, Question],
    ) -> Dict[str, Dict[str, Any]]:
        """Mock déterministe pour tests sans GPU."""
        assert self._rng is not None
        out = {}
        for name, q in questions.items():
            if isinstance(q, ChoiceQuestion):
                options = list(q.criteria.keys())
                # Choix pseudo-déterministe basé sur l'état et la graine
                h = abs(hash(str(state) + name)) % len(options)
                chosen = options[h]
                conf = 0.70 + (abs(hash(chosen)) % 25) / 100.0
                probs = {opt: (0.1 if opt != chosen else 0.7) for opt in options}
                out[name] = {
                    "type": "choice",
                    "value": chosen,
                    "probabilities": probs,
                    "confidence": round(conf, 3),
                }
            elif isinstance(q, ScoreQuestion):
                levels_count = len(q.criteria)
                # Score de 0 à levels_count - 1
                base_score = 1.0 + (abs(hash(str(state) + name)) % (levels_count - 1))
                norm_score = base_score / (levels_count - 1)
                conf = 0.65 + (abs(hash(name)) % 30) / 100.0
                out[name] = {
                    "type": "score",
                    "value": round(norm_score, 3),
                    "probabilities": {str(i): 1.0 / levels_count for i in range(levels_count)},
                    "confidence": round(conf, 3),
                    "legend": q.criteria,
                }
            elif isinstance(q, NoulQuestion):
                # Oui/non
                prob = 0.3 + (abs(hash(str(state) + name)) % 50) / 100.0
                out[name] = {
                    "type": "noul",
                    "value": prob >= 0.5,
                    "probability": round(prob, 3),
                    "confidence": round(abs(2 * prob - 1), 3),
                }
        return out
