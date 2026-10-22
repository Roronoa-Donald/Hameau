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
        self.r4_injected: bool = False
        self.r5_injected: bool = False
        self.r6_j1_injected: bool = False
        self.r6_j2_injected: bool = False

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

        # J1 - 09h20 (tick 40) : Élection municipale R4 - Victor défie Kofi
        if day == 1 and tick == 40 and not self.r4_injected:
            r4_text = "Victor lance officiellement sa campagne pour la mairie : il promet la rénovation du pont et une alliance commerciale avec le village voisin pour contrer Kofi."
            for aid, conf in [("victor", 0.98), ("fatou", 0.90), ("kofi", 0.95)]:
                ag = agents.get(aid)
                if ag:
                    mem = MemoryRecord(
                        id=f"mem_r4_{aid}",
                        agent_id=aid,
                        tick=global_tick,
                        type="observation" if aid == "victor" else "hearsay",
                        text=r4_text,
                        entities=["election", "mairie", "Victor", "Kofi", "pont"],
                        fact_id="R4_election_municipale",
                        source_agent="victor",
                        hop_count=0 if aid == "victor" else 1,
                        importance=0.92,
                        confidence=conf,
                        decision_author="scenario",
                        last_accessed_tick=global_tick,
                    )
                    ag.add_memory(mem)
                    ag.set_believed_fact("R4_election_municipale", conf)
                    events.append(
                        LogEvent(
                            tick=tick,
                            day=day,
                            agent_id=aid,
                            event_type="rumor_hop",
                            payload={
                                "fact_id": "R4_election_municipale",
                                "sender": "scenario" if aid == "victor" else "victor",
                                "receiver": aid,
                                "hop_count": 0 if aid == "victor" else 1,
                                "credibility": conf,
                                "text": r4_text,
                            },
                        )
                    )
            self.r4_injected = True

        # J1 - 20h00 (tick 168) : Veillée et Jeu du Loup J1
        if day == 1 and tick == 168 and not self.r6_j1_injected:
            r6_text = "La veillée commence à la place des fêtes : Bastien lance une partie du Jeu du Loup, les regards se croisent et la méfiance monte dans le village !"
            for aid in ["bastien", "mireille", "claire", "victor", "fatou", "lucas"]:
                ag = agents.get(aid)
                if ag:
                    mem = MemoryRecord(
                        id=f"mem_r6_j1_{aid}",
                        agent_id=aid,
                        tick=global_tick,
                        type="observation",
                        text=r6_text,
                        entities=["jeu_du_loup", "place_fetes", "soiree"],
                        fact_id="R6_jeu_du_loup",
                        source_agent="bastien",
                        hop_count=0,
                        importance=0.88,
                        confidence=0.95,
                        decision_author="scenario",
                        last_accessed_tick=global_tick,
                    )
                    ag.add_memory(mem)
                    ag.set_believed_fact("R6_jeu_du_loup", 0.95)
                    events.append(
                        LogEvent(
                            tick=tick,
                            day=day,
                            agent_id=aid,
                            event_type="rumor_hop",
                            payload={
                                "fact_id": "R6_jeu_du_loup",
                                "sender": "bastien",
                                "receiver": aid,
                                "hop_count": 0,
                                "credibility": 0.95,
                                "text": r6_text,
                            },
                        )
                    )
            self.r6_j1_injected = True

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

        # J2 - 11h00 (tick 60) : Alerte pont vers le village voisin R5
        if day == 2 and tick == 60 and not self.r5_injected:
            r5_text = "Sokhna alerte le village : les crues de la rivière fragilisent le pont reliant au village voisin, les passages de charrettes sont très risqués."
            for aid, conf in [("sokhna", 0.99), ("antoine", 0.95), ("kofi", 0.90)]:
                ag = agents.get(aid)
                if ag:
                    mem = MemoryRecord(
                        id=f"mem_r5_{aid}",
                        agent_id=aid,
                        tick=global_tick,
                        type="observation" if aid == "sokhna" else "hearsay",
                        text=r5_text,
                        entities=["pont", "riviere", "village_voisin", "crue"],
                        fact_id="R5_alerte_pont",
                        source_agent="sokhna",
                        hop_count=0 if aid == "sokhna" else 1,
                        importance=0.94,
                        confidence=conf,
                        decision_author="scenario",
                        last_accessed_tick=global_tick,
                    )
                    ag.add_memory(mem)
                    ag.set_believed_fact("R5_alerte_pont", conf)
                    events.append(
                        LogEvent(
                            tick=tick,
                            day=day,
                            agent_id=aid,
                            event_type="rumor_hop",
                            payload={
                                "fact_id": "R5_alerte_pont",
                                "sender": "scenario" if aid == "sokhna" else "sokhna",
                                "receiver": aid,
                                "hop_count": 0 if aid == "sokhna" else 1,
                                "credibility": conf,
                                "text": r5_text,
                            },
                        )
                    )
            self.r5_injected = True

        # J2 - 20h00 (tick 168) : Veillée et Jeu du Loup J2 (Révélations et votes)
        if day == 2 and tick == 168 and not self.r6_j2_injected:
            r6_text_j2 = "Seconde manche du Jeu du Loup à la place des fêtes : Mireille dénonce un comportement suspect pendant la nuit, le village débat vivement !"
            for aid in ["bastien", "mireille", "antoine", "sokhna", "salimata"]:
                ag = agents.get(aid)
                if ag:
                    mem = MemoryRecord(
                        id=f"mem_r6_j2_{aid}",
                        agent_id=aid,
                        tick=global_tick,
                        type="observation",
                        text=r6_text_j2,
                        entities=["jeu_du_loup", "place_fetes", "vote"],
                        fact_id="R6_jeu_du_loup",
                        source_agent="mireille",
                        hop_count=0,
                        importance=0.89,
                        confidence=0.95,
                        decision_author="scenario",
                        last_accessed_tick=global_tick,
                    )
                    ag.add_memory(mem)
                    ag.set_believed_fact("R6_jeu_du_loup", 0.95)
                    events.append(
                        LogEvent(
                            tick=tick,
                            day=day,
                            agent_id=aid,
                            event_type="rumor_hop",
                            payload={
                                "fact_id": "R6_jeu_du_loup",
                                "sender": "mireille",
                                "receiver": aid,
                                "hop_count": 0,
                                "credibility": 0.95,
                                "text": r6_text_j2,
                            },
                        )
                    )
            self.r6_j2_injected = True

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
