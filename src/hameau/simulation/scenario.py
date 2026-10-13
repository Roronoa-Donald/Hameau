"""Rumor injection scenario for HAMEAU (FR-14)."""

from typing import Dict, List, Optional
from hameau.models.agent import Agent
from hameau.models.memory import MemoryRecord
from hameau.models.events import LogEvent


class ScenarioManager:
    """Gère l'injection des faits fondateurs (R1 rumeur, R2 démenti)."""

    def __init__(self):
        self.r1_injected: bool = False
        self.r2_injected: bool = False

    def check_injections(
        self,
        day: int,
        tick: int,
        agents: Dict[str, Agent],
    ) -> List[LogEvent]:
        """Injecte les événements scénarisés aux moments clés."""
        events: List[LogEvent] = []

        # J1 - 08h00 (tick 24) : Rumeur R1 chez Yao
        if day == 1 and tick == 24 and not self.r1_injected:
            yao = agents.get("yao")
            if yao:
                r1_text = "Une source officieuse rapporte que la mairie envisage de fermer le marché samedi."
                mem = MemoryRecord(
                    id="mem_r1_init",
                    agent_id="yao",
                    tick=tick,
                    type="hearsay",
                    text=r1_text,
                    entities=["marche", "mairie", "samedi"],
                    fact_id="R1_fermeture_marche",
                    source_agent="inconnu",
                    hop_count=0,
                    importance=0.90,
                    confidence=0.85,
                    decision_author="scenario",
                    last_accessed_tick=tick,
                )
                yao.add_memory(mem)
                yao.set_believed_fact("R1_fermeture_marche", 0.85)
                self.r1_injected = True

                events.append(
                    LogEvent(
                        tick=tick,
                        day=day,
                        agent_id="yao",
                        event_type="rumor_hop",
                        payload={
                            "fact_id": "R1_fermeture_marche",
                            "sender": "scenario",
                            "receiver": "yao",
                            "hop_count": 0,
                            "credibility": 0.85,
                            "text": r1_text,
                        },
                    )
                )

        # J2 - 10h00 (tick 48) : Démenti officiel R2 chez Kofi (Maire)
        if day == 2 and tick == 48 and not self.r2_injected:
            kofi = agents.get("kofi")
            if kofi:
                r2_text = "Le maire Kofi publie un démenti officiel : le marché de samedi se tiendra sans aucune interruption."
                mem = MemoryRecord(
                    id="mem_r2_init",
                    agent_id="kofi",
                    tick=tick,
                    type="observation",
                    text=r2_text,
                    entities=["marche", "mairie", "Kofi"],
                    fact_id="R2_dementi_maire",
                    source_agent="mairie",
                    hop_count=0,
                    importance=0.95,
                    confidence=0.99,
                    decision_author="scenario",
                    last_accessed_tick=tick,
                )
                kofi.add_memory(mem)
                kofi.set_believed_fact("R2_dementi_maire", 0.99)
                self.r2_injected = True

                events.append(
                    LogEvent(
                        tick=tick,
                        day=day,
                        agent_id="kofi",
                        event_type="rumor_hop",
                        payload={
                            "fact_id": "R2_dementi_maire",
                            "sender": "mairie",
                            "receiver": "kofi",
                            "hop_count": 0,
                            "credibility": 0.99,
                            "text": r2_text,
                        },
                    )
                )

        return events
