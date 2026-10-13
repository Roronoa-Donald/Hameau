"""Main simulation engine for HAMEAU (FR-01 to FR-30)."""

import json
import os
import random
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from hameau.models.world import WorldGraph
from hameau.models.agent import Agent
from hameau.models.memory import MemoryRecord
from hameau.models.events import LogEvent
from hameau.decisions import (
    DeciderClient,
    ConfidenceThresholds,
    classify_zone,
    build_d1_action_picker,
    build_d2_importance_scorer,
    build_d4_talk_gate,
    build_d5_share_scorer,
    build_d6_reflect_gate,
    build_d7_continue_gate,
    build_d8_credibility_gate,
)
from patterns.memory_gate import MemoryGate, MemoryCandidate
from hameau.llm import (
    BedrockClient,
    generate_dialogue_turn,
    generate_reflection,
    generate_gazette,
)
from .scenario import ScenarioManager


class SimulationEngine:
    """Moteur de simulation déterministe avec ordonnancement par événements."""

    def __init__(
        self,
        world: WorldGraph,
        agents: Dict[str, Agent],
        decider: DeciderClient,
        bedrock: BedrockClient,
        memory_gate: MemoryGate,
        scenario: ScenarioManager,
        config: Dict[str, Any],
    ):
        self.world = world
        self.agents = agents
        self.decider = decider
        self.bedrock = bedrock
        self.memory_gate = memory_gate
        self.scenario = scenario
        self.config = config

        self.seed = config.get("seed", 42)
        self.rng = random.Random(self.seed)

        self.thresholds_cfg = config.get("decider", {}).get("thresholds", {})
        self.log_events: List[LogEvent] = []
        self.runs_dir = Path(config.get("logging", {}).get("runs_dir", "runs"))
        self.runs_dir.mkdir(parents=True, exist_ok=True)
        self.log_filepath = self.runs_dir / config.get("logging", {}).get("log_filename", "hameau_run.jsonl")

        # Résumé quotidien pour la Gazette
        self.daily_events_summary: List[str] = []

    def log(self, event: LogEvent) -> None:
        """Enregistre un événement dans la mémoire et dans le fichier JSONL."""
        self.log_events.append(event)
        with open(self.log_filepath, "a", encoding="utf-8") as f:
            f.write(json.dumps(event.to_jsonl_dict(), ensure_ascii=False) + "\n")

    def run(self, days: int = 1, ticks_per_day: int = 192) -> Dict[str, Any]:
        """Exécute la simulation sur le nombre de jours spécifié."""
        # Réinitialiser le fichier log
        if self.log_filepath.exists():
            self.log_filepath.unlink()

        self.log(
            LogEvent(
                tick=0,
                day=1,
                event_type="system",
                payload={
                    "message": "Démarrage de la simulation Hameau",
                    "num_agents": len(self.agents),
                    "days": days,
                    "seed": self.seed,
                    "decider_checkpoint": self.decider.checkpoint,
                    "bedrock_model": self.bedrock.model_id,
                },
            )
        )

        for day in range(1, days + 1):
            self.daily_events_summary = []
            print(f"\n--- [HAMEAU] Début du Jour {day} ---")

            for tick in range(ticks_per_day):
                # 1. Scénario d'injection
                injected = self.scenario.check_injections(day, tick, self.agents)
                for ev in injected:
                    self.log(ev)
                    if "text" in ev.payload:
                        self.daily_events_summary.append(f"Événement clé : {ev.payload['text']}")

                # 2. Déplacements en cours
                self._update_agent_movements(day, tick)

                # 3. Prises de décisions (ActionPicker D1)
                self._process_agent_decisions(day, tick)

                # 4. Rencontres et conversations (D4, D5, B1, D7, D8, D2)
                self._process_encounters(day, tick)

                # 5. Réflexions du soir à 21h30 (tick 186)
                if tick == 186:
                    self._process_evening_reflections(day, tick)

            # 6. Fin de journée : Gazette du Hameau (B4)
            self._generate_evening_gazette(day, ticks_per_day)

        # Bilan final
        ratio = (
            round(self.decider.total_decisions / max(1, self.bedrock.total_calls), 1)
            if self.bedrock.total_calls > 0
            else float(self.decider.total_decisions)
        )

        summary = {
            "total_ticks": days * ticks_per_day,
            "decider_total_decisions": self.decider.total_decisions,
            "decider_total_tokens": self.decider.total_tokens,
            "decider_latency_p50_ms": round(self.decider.total_latency_ms / max(1, self.decider.total_decisions), 2),
            "bedrock_total_calls": self.bedrock.total_calls,
            "bedrock_from_cassette": self.bedrock.calls_from_cassette,
            "bedrock_input_tokens": self.bedrock.total_input_tokens,
            "bedrock_output_tokens": self.bedrock.total_output_tokens,
            "bedrock_total_cost_usd": round(self.bedrock.total_cost_usd, 5),
            "ratio_decider_to_llm": ratio,
            "log_file": str(self.log_filepath),
        }

        print("\n=== BILAN SIMULATION HAMEAU ===")
        print(f"Décisions Decider 2B : {summary['decider_total_decisions']}")
        print(f"Appels Amazon Bedrock : {summary['bedrock_total_calls']} (dont {summary['bedrock_from_cassette']} en cassette)")
        print(f"Rapport Decider / LLM  : {summary['ratio_decider_to_llm']} pour 1 (Cible > 20:1)")
        print(f"Coût AWS consommé      : {summary['bedrock_total_cost_usd']} $")

        return summary

    def _update_agent_movements(self, day: int, tick: int) -> None:
        """Fait progresser les trajets des agents."""
        for agent in self.agents.values():
            if agent.state.travel_remaining_ticks > 0:
                agent.state.travel_remaining_ticks -= 1
                if agent.state.travel_remaining_ticks == 0 and agent.state.destination_id:
                    origin = agent.state.current_location_id
                    dest = agent.state.destination_id
                    agent.state.current_location_id = dest
                    agent.state.destination_id = None
                    self.log(
                        LogEvent(
                            tick=tick,
                            day=day,
                            agent_id=agent.persona.id,
                            event_type="move",
                            payload={
                                "from": origin,
                                "to": dest,
                                "duration_ticks": self.world.travel_time(origin, dest),
                            },
                        )
                    )

    def _process_agent_decisions(self, day: int, tick: int) -> None:
        """Gère les agents qui ont terminé leur activité courante."""
        for agent in self.agents.values():
            if not agent.is_available():
                continue
            if tick < agent.state.action_end_tick:
                continue

            # Construction des options pour D1
            curr_loc = agent.state.current_location_id
            workplace = agent.persona.workplace_id
            home = agent.persona.home_id

            options = {
                "routine": f"Effectuer sa tâche : {self.world.locations[curr_loc].default_routine}",
                "pause": "Faire une pause et observer les alentours",
            }
            if curr_loc != workplace:
                options["aller_travail"] = f"Se rendre à son travail ({self.world.locations[workplace].name})"
            if curr_loc != home:
                options["rentrer"] = f"Rentrer chez soi ({self.world.locations[home].name})"
            if curr_loc != "marche":
                options["aller_marche"] = "Aller sur la place du marché"
            if curr_loc != "cafe":
                options["aller_cafe"] = "Aller au café de la rivière"

            # Présélection et scoring MemoryGate
            mem_candidates = [
                MemoryCandidate(
                    id=m.id,
                    text=m.text,
                    tick=m.tick,
                    importance=m.importance,
                    entities=m.entities,
                    fact_id=m.fact_id,
                )
                for m in agent.memories
            ]
            top_memories = self.memory_gate.score_and_rank(
                self.memory_gate.preselect(mem_candidates, tick, [curr_loc, agent.persona.id]),
                tick,
                f"{agent.persona.name} est à {self.world.locations[curr_loc].name} à {6 + tick // 12}h{(tick % 12) * 5:02d}.",
            )

            state_text = (
                f"{agent.persona.name}, {agent.persona.job}. Lieu : {self.world.locations[curr_loc].name}. "
                f"Énergie : {agent.state.energy:.2f}. "
                f"Souvenirs clés : {'; '.join([sm.candidate.text for sm in top_memories]) if top_memories else 'aucun'}."
            )

            d1_q = build_d1_action_picker(options)
            res = self.decider.ask(state_text, {"D1": d1_q})
            d1_ans = res["D1"]

            chosen_key = d1_ans["value"]
            conf = d1_ans["confidence"]
            th = ConfidenceThresholds(
                green=self.thresholds_cfg.get("D1", {}).get("green", 0.60),
                orange=self.thresholds_cfg.get("D1", {}).get("orange", 0.40),
            )
            zone = classify_zone(conf, th)

            # Repli en zone rouge (FR-08)
            fallback = False
            if zone == "red":
                chosen_key = "routine"
                fallback = True

            # Application de l'action
            duration = self.rng.randint(3, 6)  # 15 à 30 minutes simulées
            agent.state.action_end_tick = tick + duration

            if chosen_key.startswith("aller_") or chosen_key == "rentrer":
                target_loc = (
                    workplace if chosen_key == "aller_travail"
                    else home if chosen_key == "rentrer"
                    else "marche" if chosen_key == "aller_marche"
                    else "cafe"
                )
                travel_time = self.world.travel_time(curr_loc, target_loc)
                agent.state.destination_id = target_loc
                agent.state.travel_remaining_ticks = travel_time
                agent.state.current_action = f"marche vers {self.world.locations[target_loc].name}"
            else:
                agent.state.current_action = options.get(chosen_key, "vaque à ses occupations")

            self.log(
                LogEvent(
                    tick=tick,
                    day=day,
                    agent_id=agent.persona.id,
                    event_type="decision",
                    payload={
                        "decision": "D1",
                        "options": options,
                        "chosen_option": chosen_key,
                        "confidence": conf,
                        "zone": zone,
                        "fallback_used": fallback,
                        "latency_ms": d1_ans.get("latency_ms", 0.0),
                    },
                )
            )

    def _process_encounters(self, day: int, tick: int) -> None:
        """Détecte les agents au même endroit et anime leurs conversations."""
        by_location: Dict[str, List[Agent]] = {}
        for a in self.agents.values():
            if a.is_available() and a.state.travel_remaining_ticks == 0:
                by_location.setdefault(a.state.current_location_id, []).append(a)

        for loc_id, agents_here in by_location.items():
            if len(agents_here) < 2:
                continue

            # Tirage d'une paire disponible
            pair = self.rng.sample(agents_here, 2)
            speaker, listener = pair[0], pair[1]

            # D4 — TalkGate
            state_text = f"{speaker.persona.name} croise {listener.persona.name} à {self.world.locations[loc_id].name}."
            d4_res = self.decider.ask(state_text, {"D4": build_d4_talk_gate(listener.persona.name)})
            d4_ans = d4_res["D4"]

            # Zone et seuils D4
            th_d4 = ConfidenceThresholds(
                green=self.thresholds_cfg.get("D4", {}).get("green", 0.65),
                orange=self.thresholds_cfg.get("D4", {}).get("orange", 0.45),
            )
            zone_d4 = classify_zone(d4_ans["confidence"], th_d4)

            # Si D4 dit oui (ou si repli proximité si haute affinité)
            wants_talk = d4_ans["value"]
            if zone_d4 == "red":
                wants_talk = speaker.persona.relationships.get(listener.persona.id, 0.0) >= 0.5

            if not wants_talk:
                continue

            # D5 — ShareScorer : choisir le souvenir à raconter
            shared_memory: Optional[MemoryRecord] = None
            if speaker.memories:
                questions_d5 = {
                    f"d5_{m.id}": build_d5_share_scorer(m.text, listener.persona.name)
                    for m in speaker.memories[-5:]  # Évalue les 5 derniers souvenirs
                }
                d5_res = self.decider.ask(state_text, questions_d5)
                # Trouver le meilleur score
                best_id = max(d5_res.keys(), key=lambda k: d5_res[k]["value"])
                target_mem_id = best_id.replace("d5_", "")
                shared_memory = next((m for m in speaker.memories if m.id == target_mem_id), None)

            topic = shared_memory.text if shared_memory else "les nouvelles de la journée et le temps"

            # B1 — Amazon Bedrock Nova Micro pour générer le dialogue
            dialogue_history = []
            max_turns = 2  # Conversation concise de 2 répliques
            for turn_idx in range(max_turns):
                active_speaker = speaker if turn_idx % 2 == 0 else listener
                active_listener = listener if turn_idx % 2 == 0 else speaker

                # Souvenirs injectés par MemoryGate
                cands = [
                    MemoryCandidate(m.id, m.text, m.tick, m.importance, m.entities, m.fact_id)
                    for m in active_speaker.memories
                ]
                top_mems = self.memory_gate.score_and_rank(
                    self.memory_gate.preselect(cands, tick, [loc_id, active_listener.persona.id]),
                    tick,
                    f"Discussion à {self.world.locations[loc_id].name}",
                )

                gen_res = generate_dialogue_turn(
                    bedrock=self.bedrock,
                    speaker=active_speaker,
                    listener=active_listener,
                    location_name=self.world.locations[loc_id].name,
                    injected_memories=top_mems,
                    topic=topic,
                    dialogue_history=dialogue_history,
                )

                utterance = gen_res["text"]
                dialogue_history.append({"speaker": active_speaker.persona.name, "text": utterance})

                self.log(
                    LogEvent(
                        tick=tick,
                        day=day,
                        agent_id=active_speaker.persona.id,
                        event_type="conversation_turn",
                        payload={
                            "speaker": active_speaker.persona.id,
                            "listener": active_listener.persona.id,
                            "turn_index": turn_idx,
                            "utterance": utterance,
                            "topic": topic,
                            "location": loc_id,
                            "cost_usd": gen_res["cost_usd"],
                            "from_cassette": gen_res["from_cassette"],
                        },
                    )
                )

            # Transmission de l'information / rumeur si fact_id présent (FR-13)
            if shared_memory and shared_memory.fact_id:
                # D8 — CredibilityGate chez le listener
                d8_res = self.decider.ask(
                    f"{listener.persona.name} entend {speaker.persona.name} rapporter cette affirmation.",
                    {"D8": build_d8_credibility_gate(shared_memory.text, speaker.persona.name)},
                )
                cred_score = d8_res["D8"]["value"]

                # D2 — ImportanceScorer chez le listener
                d2_res = self.decider.ask(
                    f"{listener.persona.name} évalue l'importance de ce fait.",
                    {"D2": build_d2_importance_scorer(shared_memory.text)},
                )
                imp_score = d2_res["D2"]["value"]

                # Nouveau souvenir chez le listener
                new_mem = MemoryRecord(
                    id=f"mem_hear_{listener.persona.id}_{tick}",
                    agent_id=listener.persona.id,
                    tick=tick,
                    type="hearsay",
                    text=f"{speaker.persona.name} m'a dit : « {shared_memory.text} »",
                    entities=list(set(shared_memory.entities + [speaker.persona.id])),
                    fact_id=shared_memory.fact_id,
                    source_agent=speaker.persona.id,
                    hop_count=shared_memory.hop_count + 1,
                    importance=imp_score,
                    confidence=d8_res["D8"]["confidence"],
                    decision_author="decider",
                    last_accessed_tick=tick,
                )
                listener.add_memory(new_mem)
                listener.set_believed_fact(shared_memory.fact_id, cred_score)

                self.log(
                    LogEvent(
                        tick=tick,
                        day=day,
                        agent_id=listener.persona.id,
                        event_type="rumor_hop",
                        payload={
                            "fact_id": shared_memory.fact_id,
                            "sender": speaker.persona.id,
                            "receiver": listener.persona.id,
                            "hop_count": shared_memory.hop_count + 1,
                            "credibility": cred_score,
                            "importance": imp_score,
                            "text": shared_memory.text,
                        },
                    )
                )
                self.daily_events_summary.append(
                    f"{speaker.persona.name} a transmis à {listener.persona.name} l'information : {shared_memory.fact_id} (crédibilité: {cred_score:.2f})"
                )

    def _process_evening_reflections(self, day: int, tick: int) -> None:
        """Déclenche les réflexions du soir avec D6 et Bedrock (B2)."""
        for agent in self.agents.values():
            if not agent.memories:
                continue

            d6_res = self.decider.ask(
                f"{agent.persona.name} termine sa journée à {agent.persona.home_id}.",
                {"D6": build_d6_reflect_gate()},
            )
            if not d6_res["D6"]["value"]:
                continue

            cands = [
                MemoryCandidate(m.id, m.text, m.tick, m.importance, m.entities, m.fact_id)
                for m in agent.memories
            ]
            top_mems = self.memory_gate.score_and_rank(cands, tick, "Bilan du soir")

            gen_res = generate_reflection(self.bedrock, agent, top_mems)
            reflection_text = gen_res["text"]

            ref_mem = MemoryRecord(
                id=f"mem_refl_{agent.persona.id}_{day}",
                agent_id=agent.persona.id,
                tick=tick,
                type="reflection",
                text=reflection_text,
                entities=[agent.persona.id],
                importance=0.90,
                confidence=1.0,
                decision_author="bedrock",
                last_accessed_tick=tick,
            )
            agent.add_memory(ref_mem)

            self.log(
                LogEvent(
                    tick=tick,
                    day=day,
                    agent_id=agent.persona.id,
                    event_type="reflection",
                    payload={
                        "reflection": reflection_text,
                        "cost_usd": gen_res["cost_usd"],
                        "from_cassette": gen_res["from_cassette"],
                    },
                )
            )

    def _generate_evening_gazette(self, day: int, tick: int) -> None:
        """Génère la Gazette du soir (B4) avec Amazon Nova Micro."""
        if not self.daily_events_summary:
            self.daily_events_summary = ["Le village a vécu une journée paisible sans incident particulier."]

        gen_res = generate_gazette(self.bedrock, day, self.daily_events_summary)
        gazette_text = gen_res["text"]

        self.log(
            LogEvent(
                tick=tick,
                day=day,
                agent_id="claire",
                event_type="gazette",
                payload={
                    "day": day,
                    "gazette_text": gazette_text,
                    "cost_usd": gen_res["cost_usd"],
                    "from_cassette": gen_res["from_cassette"],
                },
            )
        )
        print(f"\n--- [LA GAZETTE DU HAMEAU - JOUR {day}] ---")
        print(gazette_text[:300] + "...\n")
