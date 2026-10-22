from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import os
import threading
import time
from typing import Any, Dict, List, Optional, Tuple
import urllib3
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


def _deterministic_hash(seed: int, *args: Any) -> int:
    """Calcul d'un entier 64-bit déterministe indépendant de PYTHONHASHSEED."""
    h = hashlib.sha256()
    h.update(str(seed).encode("utf-8"))
    for arg in args:
        h.update(b"|")
        h.update(str(arg).encode("utf-8"))
    return int.from_bytes(h.digest()[:8], byteorder="big", signed=False)


class DeciderClient:
    """Client gérant les requêtes à Strands Decider 2B (local GPU, distant Colab ou mock)."""

    DEFAULT_CHECKPOINT = "StrandsAgents/strands-decider-2B-hobson-v21"

    def __init__(
        self,
        checkpoint: str = DEFAULT_CHECKPOINT,
        device: str = "cuda",
        mock: bool = False,
        seed: int = 42,
        server_urls: Optional[List[str] | str] = None,
    ):
        self.checkpoint = checkpoint
        self.device = device
        self.mock = mock
        self.seed = seed
        self._engine: Optional[SystemOneEngine] = None
        self._rng = None

        # Gestion des URLs de workers distants (ex: Google Colab via Cloudflare Tunnel)
        if isinstance(server_urls, str):
            self.server_urls = [u.strip().rstrip("/") for u in server_urls.split(",") if u.strip()]
        elif server_urls:
            self.server_urls = [u.strip().rstrip("/") for u in server_urls if u.strip()]
        else:
            self.server_urls = []

        self._current_worker_idx = 0
        self._lock = threading.Lock()

        # Pool de connexions persistant HTTP Keep-Alive (réduit la latence TLS à 0)
        self._pool = urllib3.PoolManager(
            maxsize=64,
            num_pools=20,
            timeout=urllib3.Timeout(connect=5.0, read=45.0),
            headers={"User-Agent": "HameauClient/1.0", "Connection": "keep-alive"},
        )

        # Métriques cumulées
        self.total_decisions: int = 0
        self.total_tokens: int = 0
        self.total_latency_ms: float = 0.0
        self.latencies_ms: List[float] = []

        if self.mock:
            import random
            self._rng = random.Random(seed)

    def load(self) -> None:
        """Charge le modèle sur GPU/CPU ou teste la connexion aux workers distants."""
        if self.mock:
            return

        # Si des workers distants sont fournis, vérifier leur disponibilité
        if self.server_urls:
            active_workers = []
            for u in self.server_urls:
                try:
                    resp = self._pool.request("GET", f"{u}/health", timeout=5.0)
                    if resp.status == 200:
                        active_workers.append(u)
                except Exception as err:
                    print(f"[DeciderClient] Avertissement: Worker distant injoignable '{u}': {err}")

            if not active_workers:
                raise RuntimeError(
                    f"[DeciderClient] Tous les workers distants configurés ({self.server_urls}) sont injoignables. "
                    f"Vérifie le tunnel Cloudflare ou le serveur Colab."
                )
            self.server_urls = active_workers
            print(f"[DeciderClient] Connecté avec succès à {len(self.server_urls)} worker(s) GPU distant(s) : {self.server_urls}")
            return

        if self._engine is None:
            # Vérifier si CUDA est disponible
            target_device = self.device
            if target_device == "cuda" and not torch.cuda.is_available():
                target_device = "cpu"

            try:
                self._engine = load_engine(self.checkpoint, device=target_device)
                if hasattr(self._engine, "cfg"):
                    self._engine.cfg.max_batch = 4
                self.device = target_device
            except Exception as e:
                # Jamais de repli silencieux vers le mock : lever une erreur explicite
                raise RuntimeError(
                    f"[DeciderClient] Échec du chargement du modèle Decider '{self.checkpoint}' "
                    f"sur le périphérique '{target_device}': {e}. "
                    f"Pour exécuter les tests ou une simulation sans modèle, activez explicitement mock=True."
                ) from e

    def ask(
        self,
        state: str | dict | list,
        questions: Dict[str, Question],
    ) -> Dict[str, Dict[str, Any]]:
        """Pose un lot de questions sur un même état (en local ou distribué sur Colab)."""
        t_start = time.perf_counter()

        # 1. Mode Mock
        if self.mock:
            results = self._mock_ask(state, questions)
            latency_ms = round((time.perf_counter() - t_start) * 1000, 2)
            input_tokens = len(str(state).split()) + sum(len(str(q).split()) for q in questions.values())
            used_backend = "mock"

        # 2. Mode Workers Distants (Google Colab / Cloudflare Tunnel)
        elif self.server_urls:
            results, latency_ms, input_tokens, used_backend = self._remote_ask(state, questions, t_start)

        # 3. Mode GPU/CPU Local
        else:
            if self._engine is None:
                self.load()
            response: SystemOneResponse = self._engine.ask(state, questions)
            if self.device == "cuda" and torch.cuda.is_available():
                torch.cuda.empty_cache()
            latency_ms = round((time.perf_counter() - t_start) * 1000, 2)
            input_tokens = response.usage.input_tokens
            results = {}
            for name, ans in response.answers.items():
                results[name] = self._format_answer(ans)
            used_backend = self.checkpoint

        with self._lock:
            self.total_decisions += len(questions)
            self.total_tokens += input_tokens
            self.total_latency_ms += latency_ms
            self.latencies_ms.append(latency_ms)

        # Injection métadonnées globales
        for name in results:
            results[name]["latency_ms"] = latency_ms
            results[name]["model"] = used_backend

        return results

    def ask_batch(
        self,
        items: List[Tuple[str | dict | list, Dict[str, Question]]],
    ) -> List[Dict[str, Dict[str, Any]]]:
        """Évalue un lot de questions en parallèle à travers les workers GPU distants."""
        if not items:
            return []

        # Si mock déterministe
        if self.mock:
            return [self.ask(state, qs) for state, qs in items]

        # Si workers distants configurés : parallélisation multi-threads Keep-Alive
        if self.server_urls:
            max_workers = min(32, max(len(items), len(self.server_urls) * 4))
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                return list(executor.map(lambda item: self.ask(item[0], item[1]), items))

        # Mode GPU/CPU local
        return [self.ask(state, qs) for state, qs in items]

    def _remote_ask(
        self,
        state: str | dict | list,
        questions: Dict[str, Question],
        t_start: float,
    ) -> tuple[Dict[str, Dict[str, Any]], float, int, str]:
        """Achemine la requête vers l'un des workers distants via pool HTTP Keep-Alive persistant."""
        # Sérialisation des questions pour SystemOneRequest
        serialized_questions = {}
        for q_name, q in questions.items():
            if isinstance(q, ChoiceQuestion):
                serialized_questions[q_name] = {
                    "type": "choice",
                    "instructions": q.instructions,
                    "criteria": q.criteria,
                }
            elif isinstance(q, ScoreQuestion):
                serialized_questions[q_name] = {
                    "type": "score",
                    "instructions": q.instructions,
                    "criteria": q.criteria,
                }
            elif isinstance(q, NoulQuestion):
                serialized_questions[q_name] = {
                    "type": "noul",
                    "instructions": q.instructions,
                    "criteria": q.criteria,
                }
            else:
                raise ValueError(f"Type de question non supporté pour worker distant: {type(q)}")

        payload = {
            "state": state,
            "questions": serialized_questions,
        }
        body_bytes = json.dumps(payload, ensure_ascii=False).encode("utf-8")

        # Essai avec load-balancing Round-Robin thread-safe et retry sur worker suivant si indisponible
        last_err = None
        n_workers = len(self.server_urls)
        for _ in range(n_workers):
            with self._lock:
                worker_url = self.server_urls[self._current_worker_idx]
                self._current_worker_idx = (self._current_worker_idx + 1) % n_workers

            target_endpoint = f"{worker_url}/v1/systemone"
            try:
                resp = self._pool.request(
                    "POST",
                    target_endpoint,
                    body=body_bytes,
                    headers={"Content-Type": "application/json", "Connection": "keep-alive"},
                )
                if resp.status != 200:
                    raise RuntimeError(f"HTTP {resp.status}: {resp.data.decode('utf-8', errors='ignore')}")

                resp_data = json.loads(resp.data.decode("utf-8"))
                latency_ms = round((time.perf_counter() - t_start) * 1000, 2)

                results = {}
                for name, ans_data in resp_data.get("answers", {}).items():
                    ans_type = ans_data.get("type")
                    if ans_type == "choice":
                        results[name] = {
                            "type": "choice",
                            "value": ans_data["choice"],
                            "probabilities": ans_data.get("probabilities", {}),
                            "confidence": ans_data.get("confidence", 1.0),
                        }
                    elif ans_type == "score":
                        legend = ans_data.get("legend", {})
                        levels_count = len(legend)
                        raw_sc = float(ans_data["score"])
                        norm_sc = raw_sc / (levels_count - 1) if levels_count > 1 else 0.0
                        results[name] = {
                            "type": "score",
                            "value": round(norm_sc, 4),
                            "raw_score": raw_sc,
                            "probabilities": ans_data.get("probabilities", {}),
                            "confidence": ans_data.get("confidence", 1.0),
                            "legend": legend,
                        }
                    elif ans_type == "noul":
                        prob = float(ans_data["noul"])
                        results[name] = {
                            "type": "noul",
                            "value": prob >= 0.5,
                            "probability": prob,
                            "confidence": round(abs(2 * prob - 1), 4),
                        }

                input_tokens = resp_data.get("usage", {}).get("input_tokens", len(str(state).split()))
                return results, latency_ms, input_tokens, resp_data.get("model", self.checkpoint)

            except Exception as e:
                last_err = e
                print(f"[DeciderClient] Échec de la requête sur le worker '{worker_url}', tentative sur un autre worker...")

        raise RuntimeError(f"[DeciderClient] Tous les workers distants ont échoué: {last_err}") from last_err

    def get_p50_latency_ms(self) -> float:
        """Calcule la médiane (p50) réelle des temps de réponse observés."""
        if not self.latencies_ms:
            return 0.0
        sorted_lat = sorted(self.latencies_ms)
        return float(sorted_lat[len(sorted_lat) // 2])

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
            levels_count = len(ans.legend)
            norm_score = ans.score / (levels_count - 1) if levels_count > 1 else 0.0
            return {
                "type": "score",
                "value": round(float(norm_score), 4),
                "raw_score": float(ans.score),
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
        """Mock déterministe pour tests sans GPU (indépendant de PYTHONHASHSEED)."""
        out = {}
        for name, q in questions.items():
            if isinstance(q, ChoiceQuestion):
                options = list(q.criteria.keys())
                h = _deterministic_hash(self.seed, state, name) % len(options)
                chosen = options[h]
                conf = 0.70 + (_deterministic_hash(self.seed, chosen, name) % 25) / 100.0
                probs = {opt: (0.1 if opt != chosen else 0.7) for opt in options}
                out[name] = {
                    "type": "choice",
                    "value": chosen,
                    "probabilities": probs,
                    "confidence": round(conf, 3),
                }
            elif isinstance(q, ScoreQuestion):
                levels_count = len(q.criteria)
                base_score = 1.0 + (_deterministic_hash(self.seed, state, name) % max(1, levels_count - 1))
                norm_score = base_score / (levels_count - 1) if levels_count > 1 else 0.0
                conf = 0.65 + (_deterministic_hash(self.seed, name) % 30) / 100.0
                out[name] = {
                    "type": "score",
                    "value": round(norm_score, 3),
                    "raw_score": round(base_score, 3),
                    "probabilities": {str(i): 1.0 / levels_count for i in range(levels_count)},
                    "confidence": round(conf, 3),
                    "legend": q.criteria,
                }
            elif isinstance(q, NoulQuestion):
                prob = 0.3 + (_deterministic_hash(self.seed, state, name) % 50) / 100.0
                out[name] = {
                    "type": "noul",
                    "value": prob >= 0.5,
                    "probability": round(prob, 3),
                    "confidence": round(abs(2 * prob - 1), 3),
                }
        return out

