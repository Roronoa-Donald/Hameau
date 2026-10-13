"""Confidence policy and zone classification for HAMEAU (FR-08)."""

from dataclasses import dataclass
from typing import Literal

ZoneType = Literal["green", "orange", "red"]


@dataclass(frozen=True)
class ConfidenceThresholds:
    green: float
    orange: float


def classify_zone(confidence: float, thresholds: ConfidenceThresholds) -> ZoneType:
    """Classifie la confiance d'une décision en zone Verte, Orange ou Rouge."""
    if confidence >= thresholds.green:
        return "green"
    elif confidence >= thresholds.orange:
        return "orange"
    else:
        return "red"
