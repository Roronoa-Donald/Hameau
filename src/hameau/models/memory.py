"""Memory record data model for HAMEAU."""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class MemoryRecord:
    id: str
    agent_id: str
    tick: int
    type: str  # "observation", "dialogue", "reflection", "plan", "hearsay"
    text: str
    entities: List[str] = field(default_factory=list)
    fact_id: Optional[str] = None          # Ex: "R1_fermeture_marche", "R2_dementi_maire"
    source_agent: Optional[str] = None     # Qui a transmis l'information
    hop_count: int = 0                     # Nombre de sauts (transmissions)
    importance: float = 0.5                # Score D2 [0.0 - 1.0]
    confidence: float = 1.0                # Confiance associée à la décision
    decision_author: str = "decider"       # "decider", "rule", "bedrock"
    last_accessed_tick: int = 0

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "agent_id": self.agent_id,
            "tick": self.tick,
            "type": self.type,
            "text": self.text,
            "entities": self.entities,
            "fact_id": self.fact_id,
            "source_agent": self.source_agent,
            "hop_count": self.hop_count,
            "importance": round(self.importance, 3),
            "confidence": round(self.confidence, 3),
            "decision_author": self.decision_author,
            "last_accessed_tick": self.last_accessed_tick,
        }
