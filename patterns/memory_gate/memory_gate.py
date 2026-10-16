"""MemoryGate: Reusable Decision Pattern for Context & Memory Scoring.

Tag: #strands-decider-2b #context-memory
License: Apache-2.0
"""

import math
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple

try:
    from strands.hooks import HookProvider, HookRegistry
    from strands.hooks.events import BeforeModelCallEvent
except ImportError:  # pragma: no cover
    class HookProvider:  # type: ignore
        """Fallback base class when strands-agents is not available."""
        pass

    class HookRegistry:  # type: ignore
        def add_callback(self, event_type: Any, callback: Any) -> None:
            pass

    BeforeModelCallEvent = None  # type: ignore


@dataclass
class MemoryCandidate:
    id: str
    text: str
    tick: int
    importance: float = 0.5            # [0.0 - 1.0]
    entities: List[str] = field(default_factory=list)
    fact_id: Optional[str] = None
    source: Optional[str] = None
    hop_count: int = 0


@dataclass
class ScoredMemory:
    candidate: MemoryCandidate
    relevance_score: float             # Score D3 de pertinence [0.0 - 1.0]
    relevance_confidence: float        # Confiance de Decider [0.0 - 1.0]
    zone: str                          # "green", "orange", "red"
    recency_score: float               # [0.0 - 1.0]
    composite_score: float             # Score final pondéré [0.0 - 1.0]
    fallback_used: bool = False


class MemoryGate(HookProvider):
    """Module de scoring et de filtrage de souvenirs avant injection dans le contexte LLM.
    
    Compatible comme HookProvider standard pour le SDK Strands Agents.
    Effectue la sélection en 3 étapes :
    1. Pré-sélection déterministe (recouvrement d'entités + récents + importants, max 12)
    2. Scoring de pertinence via Strands Decider 2B (D3)
    3. Tri par score composite (Récence exponentielle + Importance + Pertinence)
    """

    def __init__(
        self,
        decider_client: Any,
        top_k: int = 3,
        max_candidates: int = 12,
        half_life_ticks: float = 192.0,  # 1 jour simulé (16h = 192 ticks à 5 min/tick)
        w_recency: float = 0.333,
        w_importance: float = 0.333,
        w_relevance: float = 0.334,
        confidence_green: float = 0.55,
        confidence_orange: float = 0.35,
    ):
        self.decider = decider_client
        self.top_k = top_k
        self.max_candidates = max_candidates
        self.half_life_ticks = half_life_ticks
        self.w_recency = w_recency
        self.w_importance = w_importance
        self.w_relevance = w_relevance
        self.confidence_green = confidence_green
        self.confidence_orange = confidence_orange

    def preselect(
        self,
        all_memories: List[MemoryCandidate],
        current_tick: int,
        situation_entities: Optional[List[str]] = None,
    ) -> List[MemoryCandidate]:
        """Étape 1 : Présélection déterministe de 12 candidats maximum."""
        if len(all_memories) <= self.max_candidates:
            return list(all_memories)

        entity_set = set(situation_entities or [])
        selected_ids = set()
        candidates: List[MemoryCandidate] = []

        # 1.1 Souvenirs partageant une entité avec la situation
        for m in all_memories:
            if entity_set.intersection(m.entities):
                candidates.append(m)
                selected_ids.add(m.id)

        # 1.2 Les 5 plus récents
        sorted_by_recency = sorted(all_memories, key=lambda m: m.tick, reverse=True)
        for m in sorted_by_recency[:5]:
            if m.id not in selected_ids:
                candidates.append(m)
                selected_ids.add(m.id)

        # 1.3 Les 5 plus importants
        sorted_by_importance = sorted(all_memories, key=lambda m: m.importance, reverse=True)
        for m in sorted_by_importance[:5]:
            if m.id not in selected_ids:
                candidates.append(m)
                selected_ids.add(m.id)

        # Plafond dur à max_candidates
        return candidates[:self.max_candidates]

    def score_and_rank(
        self,
        candidates: List[MemoryCandidate],
        current_tick: int,
        situation_context: str,
        on_decision: Optional[Callable[[str, ScoredMemory, Dict[str, Any]], None]] = None,
    ) -> List[ScoredMemory]:
        """Étapes 2 & 3 : Évaluation par Decider 2B et calcul du score composite."""
        if not candidates:
            return []

        # Préparation et évaluation par petits lots (max 4) pour préserver la VRAM
        from hameau.decisions.questions import build_d3_relevance_scorer
        chunk_size = 4
        decider_responses = {}
        for start_idx in range(0, len(candidates), chunk_size):
            chunk = candidates[start_idx:start_idx + chunk_size]
            questions = {
                f"rel_{c.id}": build_d3_relevance_scorer(c.text)
                for c in chunk
            }
            res = self.decider.ask(situation_context, questions)
            decider_responses.update(res)

        scored: List[ScoredMemory] = []

        for c in candidates:
            q_name = f"rel_{c.id}"
            ans = decider_responses.get(q_name, {})
            
            raw_relevance = ans.get("value", 0.5)
            confidence = ans.get("confidence", 0.5)

            # Zone de confiance (FR-08)
            if confidence >= self.confidence_green:
                zone = "green"
                relevance = raw_relevance
                fallback = False
            elif confidence >= self.confidence_orange:
                zone = "orange"
                relevance = raw_relevance
                fallback = False
            else:
                zone = "red"
                # Repli déterministe en zone rouge : moyenne importance + recouvrement
                relevance = (c.importance + 0.5) / 2.0
                fallback = True

            # Calcul récence avec décroissance exponentielle
            delta_ticks = max(0, current_tick - c.tick)
            decay_lambda = math.log(2) / self.half_life_ticks
            recency_score = math.exp(-decay_lambda * delta_ticks)

            # Score composite normalisé
            composite = (
                self.w_recency * recency_score
                + self.w_importance * c.importance
                + self.w_relevance * relevance
            )

            scored_item = ScoredMemory(
                candidate=c,
                relevance_score=round(relevance, 3),
                relevance_confidence=round(confidence, 3),
                zone=zone,
                recency_score=round(recency_score, 3),
                composite_score=round(composite, 3),
                fallback_used=fallback,
            )
            scored.append(scored_item)
            if on_decision is not None:
                on_decision(c.id, scored_item, ans)

        # Tri décroissant selon le score composite
        scored.sort(key=lambda s: s.composite_score, reverse=True)
        return scored[:self.top_k]

    def score_candidates(
        self,
        candidates: List[MemoryCandidate],
        context_text: str,
        current_tick: int,
    ) -> List[ScoredMemory]:
        """Alias for score_and_rank."""
        return self.score_and_rank(candidates, current_tick, context_text)

    def register_hooks(self, registry: Any) -> None:
        """Enregistre le hook MemoryGate auprès du HookRegistry de Strands Agents."""
        if BeforeModelCallEvent is not None and hasattr(registry, "add_callback"):
            registry.add_callback(BeforeModelCallEvent, self.on_before_model_call)

    def on_before_model_call(self, event: Any) -> None:
        """Intercepte le cycle de vie avant appel au modèle pour injecter les mémoires filtrées."""
        agent = getattr(event, "agent", None)
        invocation_state = getattr(event, "invocation_state", {})

        candidates = invocation_state.get("memory_candidates")
        if candidates is None and agent is not None:
            candidates = getattr(agent, "memory_candidates", None)
            if candidates is None and hasattr(agent, "memories"):
                candidates = [
                    MemoryCandidate(
                        id=f"mem_{i}",
                        text=getattr(m, "text", str(m)),
                        tick=getattr(m, "tick", 0),
                        importance=getattr(m, "importance", 0.5),
                        entities=getattr(m, "entities", []),
                    )
                    for i, m in enumerate(agent.memories)
                ]

        if not candidates:
            return

        current_tick = invocation_state.get("current_tick", getattr(agent, "current_tick", 0))
        context_text = invocation_state.get("context_text", "")
        if not context_text and agent is not None and hasattr(agent, "messages"):
            if agent.messages:
                context_text = str(agent.messages[-1])

        top_memories = self.score_and_rank(
            candidates=candidates,
            current_tick=current_tick,
            situation_context=context_text,
        )

        invocation_state["selected_memories"] = top_memories
        invocation_state["memory_gate_injected_text"] = "\n".join(
            f"- [Score: {m.composite_score:.2f} | Zone: {m.zone}] {m.candidate.text}"
            for m in top_memories
        )
