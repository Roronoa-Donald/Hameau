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
        self.r3_injected: bool = False

    def check_injections(
        self,
        day: int,
        tick: int,
        agents: Dict[str, Agent],
    ) -> List[LogEvent]:
        """Injecte les événements scénarisés aux moments clés."""
        global_tick: int = (day - 1) * 192 + tick
        events: List[LogEvent] = []

        # J1 - 08h00 (tick 24) : Rumeur R1 chez Yao
        if day == 1 and tick == 24 and not self.r1_injected:
            yao = agents.get("yao")
            if yao:
                r1_text = "Une source officieuse rapporte que la mairie envisage de fermer le marché samedi."
                mem = MemoryRecord(
                    id="mem_r1_init",
                    agent_id="yao",
                    tick=global_tick,
                    type="hearsay",
                    text=r1_text,
                    entities=["marche", "mairie", "samedi"],
                    fact_id="R1_fermeture_marche",
                    source_agent="inconnu",
                    hop_count=0,
                    importance=0.90,
                    confidence=0.85,
                    decision_author="scenario",
                    last_accessed_tick=global_tick,
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
                    tick=global_tick,
                    type="observation",
                    text=r2_text,
                    entities=["marche", "mairie", "Kofi"],
                    fact_id="R2_dementi_maire",
                    source_agent="mairie",
                    hop_count=0,
                    importance=0.95,
                    confidence=0.99,
                    decision_author="scenario",
                    last_accessed_tick=global_tick,
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

        # J3 - 07h00 (tick 12) : Ouverture officielle du Grand Marché du Samedi (Climax R3)
        if day == 3 and tick == 12 and not self.r3_injected:
            r3_text = "Le Grand Marché du Samedi est officiellement ouvert sur la place : les étals débordent de vivres et l'activité bat son plein."
            for target_id in ("awa", "yao"):
                target = agents.get(target_id)
                if target:
                    mem = MemoryRecord(
                        id=f"mem_r3_{target_id}",
                        agent_id=target_id,
                        tick=global_tick,
                        type="observation",
                        text=r3_text,
                        entities=["marche", "samedi", "place"],
                        fact_id="R3_ouverture_marche",
                        source_agent="marche",
                        hop_count=0,
                        importance=0.98,
                        confidence=1.0,
                        decision_author="scenario",
                        last_accessed_tick=global_tick,
                    )
                    target.add_memory(mem)
                    target.set_believed_fact("R3_ouverture_marche", 1.0)
                    events.append(
                        LogEvent(
                            tick=tick,
                            day=day,
                            agent_id=target_id,
                            event_type="rumor_hop",
                            payload={
                                "fact_id": "R3_ouverture_marche",
                                "sender": "marche",
                                "receiver": target_id,
                                "hop_count": 0,
                                "credibility": 1.0,
                                "text": r3_text,
                            },
                        )
                    )
            self.r3_injected = True

        return events
