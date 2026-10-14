"""Agent data models (Persona, DynamicState, Agent) for HAMEAU."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from .memory import MemoryRecord


@dataclass
class Persona:
    id: str
    name: str
    age: int
    job: str
    traits: List[str]
    goals: List[str]
    home_id: str
    workplace_id: str
    relationships: Dict[str, float] = field(default_factory=dict)
    believed_facts: Dict[str, float] = field(default_factory=dict)  # fact_id -> credibility score D8
    did_stock_provisions: bool = False  # Preuve comportementale face à la rumeur


@dataclass
class DynamicState:
    current_location_id: str
    destination_id: Optional[str] = None
    travel_remaining_ticks: int = 0
    current_action: str = "disponible"
    action_end_tick: int = 0
    energy: float = 0.95
    hunger: float = 0.10
    social: float = 0.50


@dataclass
class Agent:
    persona: Persona
    state: DynamicState
    memories: List[MemoryRecord] = field(default_factory=list)

    def add_memory(self, memory: MemoryRecord) -> None:
        self.memories.append(memory)

    def get_believed_fact(self, fact_id: str) -> Optional[float]:
        return self.persona.believed_facts.get(fact_id)

    def set_believed_fact(self, fact_id: str, credibility: float) -> None:
        # On conserve la certitude la plus forte acquise pour un même fait
        prev_cred = self.persona.believed_facts.get(fact_id, 0.0)
        credibility = max(prev_cred, credibility)
        self.persona.believed_facts[fact_id] = credibility

        r2_cred = self.persona.believed_facts.get("R2_dementi_maire", 0.0)
        r3_cred = self.persona.believed_facts.get("R3_ouverture_marche", 0.0)

        # Déclenchement du changement de comportement (FR-15)
        if fact_id == "R1_fermeture_marche" and credibility >= 0.55:
            # Si le marché est ouvert (R3 >= 0.55) ou le démenti (R2 >= 0.60) prévaut, pas de panique
            if r3_cred < 0.55 and credibility > r2_cred:
                self.persona.did_stock_provisions = True
        elif fact_id == "R2_dementi_maire" and credibility >= 0.60:
            # Le démenti apaise l'inquiétude
            self.persona.did_stock_provisions = False
        elif fact_id == "R3_ouverture_marche" and credibility >= 0.55:
            # L'ouverture effective du marché dissipe toute crainte de pénurie
            self.persona.did_stock_provisions = False

    def is_available(self) -> bool:
        """Vérifie si l'agent est disponible pour parler ou entreprendre une nouvelle action."""
        return self.state.travel_remaining_ticks == 0 and not self.state.current_action.startswith("dort")

    def to_summary(self) -> dict:
        return {
            "id": self.persona.id,
            "name": self.persona.name,
            "job": self.persona.job,
            "location": self.state.current_location_id,
            "action": self.state.current_action,
            "energy": round(self.state.energy, 2),
            "hunger": round(self.state.hunger, 2),
            "social": round(self.state.social, 2),
            "memories_count": len(self.memories),
            "believed_facts": self.persona.believed_facts,
            "did_stock_provisions": self.persona.did_stock_provisions,
        }
