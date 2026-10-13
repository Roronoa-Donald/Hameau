"""JSONL Event schema models for HAMEAU logging (FR-30 & Section 7.6)."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


@dataclass
class LogEvent:
    tick: int
    day: int
    event_type: str  # "decision", "llm_call", "move", "memory_write", "rumor_hop", "conversation_turn", "reflection", "gazette", "system"
    payload: Dict[str, Any]
    agent_id: Optional[str] = None
    real_timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_jsonl_dict(self) -> dict:
        return {
            "real_timestamp": self.real_timestamp,
            "tick": self.tick,
            "day": self.day,
            "agent_id": self.agent_id,
            "event_type": self.event_type,
            "payload": self.payload,
        }
