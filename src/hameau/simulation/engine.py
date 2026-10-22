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
        raw_log = config.get("logging", {}).get("log_filename", "hameau_run.jsonl")
        p = Path(raw_log)
        if p.is_absolute() or len(p.parts) > 1:
            self.log_filepath = p
        else:
            self.log_filepath = self.runs_dir / p
        self.log_filepath.parent.mkdir(parents=True, exist_ok=True)

        # Résumé quotidien pour la Gazette
        self.daily_events_summary: List[str] = []
        self.agent_last_conversation_tick: Dict[str, int] = {}

    def log(self, event: LogEvent) -> None:
        """Enregistre un événement dans la mémoire et dans le fichier JSONL."""
        self.log_events.append(event)
        with open(self.log_filepath, "a", encoding="utf-8") as f:
            f.write(json.dumps(event.to_jsonl_dict(), ensure_ascii=False) + "\n")

    def _log_decision(
        self,
        day: int,
        tick: int,
        global_tick: int,
        agent_id: str,
        decision_type: str,
        question_text: str,
        answer_dict: Dict[str, Any],
        options_or_criteria: Any,
        zone: str,
        fallback_used: bool,
        effective_choice: Any = None,
        extra_payload: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Enregistre chaque décision D1 à D8 dans le journal d'événements (FR-30 & Étape A3)."""
        chosen = effective_choice if effective_choice is not None else answer_dict.get("value")
        payload = {
            "decision": decision_type,
            "decision_type": decision_type,
            "question": question_text,
            "options": options_or_criteria,
            "probabilities": answer_dict.get("probabilities", {}),
            "chosen_option": chosen,
            "confidence": answer_dict.get("confidence", 1.0),
            "zone": zone,
            "fallback_used": fallback_used,
            "latency_ms": answer_dict.get("latency_ms", 0.0),
            "backend": answer_dict.get("model", "mock"),
            "global_tick": global_tick,
        }
        if extra_payload:
            payload.update(extra_payload)

        self.log(
            LogEvent(
                tick=tick,
                day=day,
                agent_id=agent_id,
                event_type="decision",
                payload=payload,
            )
        )

    def _make_on_d3_decision(self, day: int, tick: int, global_tick: int, agent_id: str):
        """Fabrique le callback d'enregistrement pour les décisions D3 dans MemoryGate."""
        def _cb(cand_id: str, sm: Any, ans_dict: Dict[str, Any]) -> None:
            extra = {
                "memory_id": cand_id,
                "memory_text": getattr(getattr(sm, "candidate", None), "text", f"Souvenir {cand_id}"),
                "recency_score": getattr(sm, "recency_score", 0.5),
                "importance_score": getattr(getattr(sm, "candidate", None), "importance", 0.5),
                "composite_score": getattr(sm, "composite_score", 0.5),
                "relevance_score": getattr(sm, "relevance_score", 0.5),
            }
            self._log_decision(
                day=day,
                tick=tick,
                global_tick=global_tick,
                agent_id=agent_id,
                decision_type="D3",
                question_text=f"Pertinence du souvenir {cand_id}",
                answer_dict=ans_dict,
                options_or_criteria=ans_dict.get("legend", {}),
                zone=sm.zone,
                fallback_used=sm.fallback_used,
                effective_choice=getattr(sm, "relevance_score", ans_dict.get("value")),
                extra_payload=extra,
            )
        return _cb

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

            # A1: Réveil à l'aube (6h00, tick 0 de chaque jour) chez soi
            start_global_tick = (day - 1) * ticks_per_day
            for agent in self.agents.values():
                agent.state.current_location_id = agent.persona.home_id
                agent.state.destination_id = None
                agent.state.travel_remaining_ticks = 0
                agent.state.current_action = "se réveille chez soi"
                agent.state.action_end_tick = start_global_tick
                agent.state.energy = 0.95
                agent.state.hunger = 0.15

            for tick in range(ticks_per_day):
                global_tick = (day - 1) * ticks_per_day + tick

                # Mise à jour des besoins dynamiques
                for agent in self.agents.values():
                    agent.state.energy = max(0.10, agent.state.energy - 0.003)
                    agent.state.hunger = min(0.95, agent.state.hunger + 0.004)

                # 1. Scénario d'injection
                injected = self.scenario.check_injections(day, tick, self.agents)
                for ev in injected:
                    self.log(ev)
                    if "text" in ev.payload:
                        self.daily_events_summary.append(f"Événement clé : {ev.payload['text']}")

                # 2. Déplacements en cours
                self._update_agent_movements(day, tick, global_tick)

                # 3. Prises de décisions (ActionPicker D1)
                self._process_agent_decisions(day, tick, global_tick)

                # 4. Rencontres et conversations (D4, D5, B1, D7, D8, D2)
                self._process_encounters(day, tick, global_tick)

                # 5. Réflexions du soir à 21h30 (tick 186)
                if tick == 186:
                    self._process_evening_reflections(day, tick, global_tick)

            # 6. Fin de journée : Gazette du Hameau (B4)
            self._generate_evening_gazette(day, ticks_per_day)

        # Bilan final calculé par réduction exacte du flux d'événements (FR-30 & Étape A3)
        decision_events = [e for e in self.log_events if e.event_type == "decision"]
        total_decisions = len(decision_events)

        latencies = [
            float(e.payload.get("latency_ms", 0.0))
            for e in decision_events
            if "latency_ms" in e.payload and e.payload["latency_ms"] is not None
        ]
        latencies.sort()
        p50 = latencies[len(latencies) // 2] if latencies else 0.0
        p95 = latencies[int(len(latencies) * 0.95)] if latencies else 0.0

        ratio = (
            round(total_decisions / max(1, self.bedrock.total_calls), 1)
            if self.bedrock.total_calls > 0
            else float(total_decisions)
        )

        summary = {
            "total_ticks": days * ticks_per_day,
            "decider_total_decisions": total_decisions,
            "decider_total_tokens": self.decider.total_tokens,
            "decider_latency_p50_ms": round(p50, 2),
            "decider_latency_p95_ms": round(p95, 2),
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

    def _update_agent_movements(self, day: int, tick: int, global_tick: int) -> None:
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
                                "global_tick": global_tick,
                            },
                        )
                    )

    def _process_agent_decisions(self, day: int, tick: int, global_tick: int) -> None:
        """Gère les agents qui ont terminé leur activité courante avec inférence GPU vectorisée/parallèle."""
        candidates = []
        for agent in self.agents.values():
            if not agent.is_available():
                continue
            if global_tick < agent.state.action_end_tick:
                continue

            # Construction des options pour D1 avec rythme de village
            curr_loc = agent.state.current_location_id
            workplace = agent.persona.workplace_id
            home = agent.persona.home_id

            hour = 6 + tick // 12
            minute = (tick % 12) * 5
            time_str = f"{hour:02d}h{minute:02d}"

            is_morning = 6 <= hour < 8
            is_work_time = (8 <= hour < 12) or (14 <= hour < 17)
            is_lunch = 12 <= hour < 14
            is_evening = hour >= 17

            options = {
                "routine": f"Effectuer sa tâche : {self.world.locations[curr_loc].default_routine}",
                "pause": "Faire une pause et observer les alentours",
            }
            if curr_loc != workplace:
                if is_work_time or is_morning:
                    options["aller_travail"] = f"Se rendre à son travail ({self.world.locations[workplace].name})"
            if curr_loc != home:
                if is_evening or is_morning:
                    options["rentrer"] = f"Rentrer chez soi ({self.world.locations[home].name})"
            if curr_loc != "marche":
                if is_lunch:
                    options["aller_marche"] = "Aller sur la place du marché pour déjeuner et voir du monde"
                elif is_evening:
                    options["aller_marche"] = "Aller sur la place du marché pour discuter en fin de journée"
                else:
                    options["aller_marche"] = "Aller sur la place du marché"
            if curr_loc != "cafe":
                if is_lunch or is_evening:
                    options["aller_cafe"] = "Aller au café de la rivière pour faire une pause"
                else:
                    options["aller_cafe"] = "Aller au café de la rivière"
            if is_evening and curr_loc != "place_fetes":
                options["aller_place_fetes"] = "Aller à la place des fêtes pour la veillée et les animations"

            # Présélection et scoring MemoryGate
            mem_candidates = [
                MemoryCandidate(
                    id=m.id,
                    text=m.text,
                    tick=m.tick,
                    importance=m.importance,
                    entities=m.entities,
                    fact_id=m.fact_id,
                    source=m.source_agent,
                    hop_count=m.hop_count,
                )
                for m in agent.memories
            ]
            top_memories = self.memory_gate.score_and_rank(
                self.memory_gate.preselect(mem_candidates, global_tick, [curr_loc, agent.persona.id]),
                global_tick,
                f"{agent.persona.name} est à {self.world.locations[curr_loc].name} à {time_str}.",
                on_decision=self._make_on_d3_decision(day, tick, global_tick, agent.persona.id),
            )

            context_period = (
                "matinée" if is_morning
                else "travail" if is_work_time
                else "pause déjeuner" if is_lunch
                else "soirée détendue"
            )

            state_text = (
                f"Il est {time_str} ({context_period}). {agent.persona.name}, {agent.persona.job}. "
                f"Lieu actuel : {self.world.locations[curr_loc].name}. "
                f"Énergie : {agent.state.energy:.2f}. "
                f"Souvenirs clés : {'; '.join([sm.candidate.text for sm in top_memories]) if top_memories else 'aucun'}."
            )

            d1_q = build_d1_action_picker(options)
            candidates.append({
                "agent": agent,
                "options": options,
                "d1_q": d1_q,
                "state_text": state_text,
                "curr_loc": curr_loc,
                "workplace": workplace,
                "home": home,
            })

        if not candidates:
            return

        # Évaluation en parallèle / par lot sur les workers GPU distants
        batch_items = [(c["state_text"], {"D1": c["d1_q"]}) for c in candidates]
        batch_results = self.decider.ask_batch(batch_items)

        for c, res in zip(candidates, batch_results):
            agent = c["agent"]
            options = c["options"]
            d1_q = c["d1_q"]
            curr_loc = c["curr_loc"]
            workplace = c["workplace"]
            home = c["home"]

            d1_ans = res["D1"]
            chosen_key = d1_ans["value"]
            conf = d1_ans["confidence"]
            th = ConfidenceThresholds(
                green=self.thresholds_cfg.get("D1", {}).get("green", 0.50),
                orange=self.thresholds_cfg.get("D1", {}).get("orange", 0.30),
            )
            zone = classify_zone(conf, th)

            # Repli en zone rouge (FR-08)
            fallback = False
            if zone == "red":
                chosen_key = "routine"
                fallback = True

            # Application de l'action
            duration = self.rng.randint(3, 6)  # 15 à 30 minutes simulées
            agent.state.action_end_tick = global_tick + duration

            if chosen_key.startswith("aller_") or chosen_key == "rentrer":
                if chosen_key == "aller_travail":
                    target_loc = workplace
                elif chosen_key == "rentrer":
                    target_loc = home
                else:
                    dest = chosen_key[len("aller_"):]
                    if dest in self.world.locations:
                        target_loc = dest
                    elif dest == "marche":
                        target_loc = "marche"
                    elif dest == "cafe":
                        target_loc = "cafe"
                    else:
                        target_loc = "marche"
                travel_time = self.world.travel_time(curr_loc, target_loc)
                agent.state.destination_id = target_loc
                agent.state.travel_remaining_ticks = travel_time
                agent.state.current_action = f"marche vers {self.world.locations[target_loc].name}"
            else:
                agent.state.current_action = options.get(chosen_key, "vaque à ses occupations")

            self._log_decision(
                day=day,
                tick=tick,
                global_tick=global_tick,
                agent_id=agent.persona.id,
                decision_type="D1",
                question_text=d1_q.instructions,
                answer_dict=d1_ans,
                options_or_criteria=options,
                zone=zone,
                fallback_used=fallback,
                effective_choice=chosen_key,
            )

    def _process_encounters(self, day: int, tick: int, global_tick: int) -> None:
        """Détecte les agents au même endroit et anime leurs conversations."""
        by_location: Dict[str, List[Agent]] = {}
        for a in self.agents.values():
            if a.is_available() and a.state.travel_remaining_ticks == 0:
                # Cooldown de 6 ticks (30 min) pour espacer les conversations naturelles
                if global_tick - self.agent_last_conversation_tick.get(a.persona.id, -999) >= 6:
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
                green=self.thresholds_cfg.get("D4", {}).get("green", 0.35),
                orange=self.thresholds_cfg.get("D4", {}).get("orange", 0.18),
            )
            zone_d4 = classify_zone(d4_ans["confidence"], th_d4)
            fallback_d4 = False
            wants_talk = d4_ans["value"]
            if zone_d4 == "red":
                wants_talk = speaker.persona.relationships.get(listener.persona.id, 0.0) >= 0.5
                fallback_d4 = True

            self._log_decision(
                day=day,
                tick=tick,
                global_tick=global_tick,
                agent_id=speaker.persona.id,
                decision_type="D4",
                question_text=f"Engager la conversation avec {listener.persona.name}",
                answer_dict=d4_ans,
                options_or_criteria={"true": "Engager la discussion", "false": "Passer son chemin"},
                zone=zone_d4,
                fallback_used=fallback_d4,
                effective_choice=wants_talk,
            )

            if not wants_talk:
                continue

            # Marquer le tick de conversation pour le cooldown
            self.agent_last_conversation_tick[speaker.persona.id] = global_tick
            self.agent_last_conversation_tick[listener.persona.id] = global_tick

            # D3 & D5 : Scoring des souvenirs du speaker via MemoryGate
            cands_speaker = [
                MemoryCandidate(m.id, m.text, m.tick, m.importance, m.entities, m.fact_id, m.source_agent, m.hop_count)
                for m in speaker.memories
            ]
            speaker_top_mems = self.memory_gate.score_and_rank(
                self.memory_gate.preselect(cands_speaker, global_tick, [loc_id, listener.persona.id]),
                global_tick,
                f"Discussion avec {listener.persona.name} à {self.world.locations[loc_id].name}",
                on_decision=self._make_on_d3_decision(day, tick, global_tick, speaker.persona.id),
            )

            # D5 — ShareScorer : choisir le souvenir à raconter parmi les top souvenirs MemoryGate
            # Ne pas re-raconter à l'interlocuteur ce qu'il nous a lui-même rapporté
            raw_cands = [m.candidate for m in speaker_top_mems] if speaker_top_mems else (
                cands_speaker[-5:] if cands_speaker else []
            )
            d5_candidates = [c for c in raw_cands if getattr(c, "source", None) != listener.persona.id] or raw_cands

            shared_memory: Optional[MemoryRecord] = None
            if d5_candidates:
                questions_d5 = {
                    f"d5_{c.id}": build_d5_share_scorer(c.text, listener.persona.name)
                    for c in d5_candidates
                }
                d5_res = self.decider.ask(state_text, questions_d5)
                # Trouver le meilleur score
                best_id = max(d5_res.keys(), key=lambda k: d5_res[k]["value"])
                target_mem_id = best_id.replace("d5_", "")
                shared_memory = next((m for m in speaker.memories if m.id == target_mem_id), None)

                # Enregistrement de chaque évaluation D5
                th_d5 = ConfidenceThresholds(
                    green=self.thresholds_cfg.get("D5", {}).get("green", 0.45),
                    orange=self.thresholds_cfg.get("D5", {}).get("orange", 0.25),
                )
                for q_key, d5_eval in d5_res.items():
                    m_eval_id = q_key.replace("d5_", "")
                    zone_d5 = classify_zone(d5_eval["confidence"], th_d5)
                    self._log_decision(
                        day=day,
                        tick=tick,
                        global_tick=global_tick,
                        agent_id=speaker.persona.id,
                        decision_type="D5",
                        question_text=f"Partager souvenir {m_eval_id} avec {listener.persona.name}",
                        answer_dict=d5_eval,
                        options_or_criteria=d5_eval.get("legend", {}),
                        zone=zone_d5,
                        fallback_used=False,
                    )

            topic = shared_memory.text if shared_memory else "les nouvelles de la journée et le temps"

            # B1 — Amazon Bedrock Nova Micro pour générer le dialogue
            dialogue_history = []
            max_turns = 2  # Conversation concise de 2 répliques
            for turn_idx in range(max_turns):
                active_speaker = speaker if turn_idx % 2 == 0 else listener
                active_listener = listener if turn_idx % 2 == 0 else speaker

                # Souvenirs injectés par MemoryGate (avec logging D3)
                if turn_idx == 0:
                    top_mems = speaker_top_mems
                else:
                    cands = [
                        MemoryCandidate(m.id, m.text, m.tick, m.importance, m.entities, m.fact_id)
                        for m in active_speaker.memories
                    ]
                    top_mems = self.memory_gate.score_and_rank(
                        self.memory_gate.preselect(cands, global_tick, [loc_id, active_listener.persona.id]),
                        global_tick,
                        f"Discussion à {self.world.locations[loc_id].name}",
                        on_decision=self._make_on_d3_decision(day, tick, global_tick, active_speaker.persona.id),
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
                            "global_tick": global_tick,
                        },
                    )
                )

                # D7 ContinueGate pour décider si on poursuit l'échange
                if turn_idx < max_turns - 1:
                    d7_res = self.decider.ask(
                        f"Après {turn_idx + 1} réplique(s), {active_speaker.persona.name} discute avec {active_listener.persona.name}.",
                        {"D7": build_d7_continue_gate(turn_idx + 1)},
                    )
                    d7_ans = d7_res["D7"]
                    th_d7 = ConfidenceThresholds(
                        green=self.thresholds_cfg.get("D7", {}).get("green", 0.40),
                        orange=self.thresholds_cfg.get("D7", {}).get("orange", 0.25),
                    )
                    zone_d7 = classify_zone(d7_ans["confidence"], th_d7)
                    fallback_d7 = False
                    want_continue = d7_ans["value"]
                    if zone_d7 == "red":
                        want_continue = True
                        fallback_d7 = True

                    self._log_decision(
                        day=day,
                        tick=tick,
                        global_tick=global_tick,
                        agent_id=active_speaker.persona.id,
                        decision_type="D7",
                        question_text=f"Poursuivre la conversation après {turn_idx + 1} répliques",
                        answer_dict=d7_ans,
                        options_or_criteria={"true": "Poursuivre", "false": "Terminer"},
                        zone=zone_d7,
                        fallback_used=fallback_d7,
                    )
                    if not want_continue:
                        break

            # Transmission de l'information / rumeur si fact_id présent (FR-13)
            if shared_memory and shared_memory.fact_id:
                # D8 — CredibilityGate chez le listener
                d8_res = self.decider.ask(
                    f"{listener.persona.name} entend {speaker.persona.name} rapporter cette affirmation.",
                    {"D8": build_d8_credibility_gate(shared_memory.text, speaker.persona.name)},
                )
                d8_ans = d8_res["D8"]
                th_d8 = ConfidenceThresholds(
                    green=self.thresholds_cfg.get("D8", {}).get("green", 0.40),
                    orange=self.thresholds_cfg.get("D8", {}).get("orange", 0.25),
                )
                zone_d8 = classify_zone(d8_ans["confidence"], th_d8)
                fallback_d8 = False
                cred_score = d8_ans["value"]
                if zone_d8 == "red":
                    cred_score = 0.50 * speaker.persona.relationships.get(listener.persona.id, 0.5)
                    fallback_d8 = True

                self._log_decision(
                    day=day,
                    tick=tick,
                    global_tick=global_tick,
                    agent_id=listener.persona.id,
                    decision_type="D8",
                    question_text=f"Crédibilité de l'affirmation rapportée par {speaker.persona.name}",
                    answer_dict=d8_ans,
                    options_or_criteria=d8_ans.get("legend", {}),
                    zone=zone_d8,
                    fallback_used=fallback_d8,
                    effective_choice=cred_score,
                )

                # D2 — ImportanceScorer chez le listener
                d2_res = self.decider.ask(
                    f"{listener.persona.name} évalue l'importance de ce fait.",
                    {"D2": build_d2_importance_scorer(shared_memory.text)},
                )
                d2_ans = d2_res["D2"]
                th_d2 = ConfidenceThresholds(
                    green=self.thresholds_cfg.get("D2", {}).get("green", 0.45),
                    orange=self.thresholds_cfg.get("D2", {}).get("orange", 0.25),
                )
                zone_d2 = classify_zone(d2_ans["confidence"], th_d2)
                fallback_d2 = False
                imp_score = d2_ans["value"]
                if zone_d2 == "red":
                    imp_score = 0.50
                    fallback_d2 = True

                self._log_decision(
                    day=day,
                    tick=tick,
                    global_tick=global_tick,
                    agent_id=listener.persona.id,
                    decision_type="D2",
                    question_text=f"Importance du fait pour {listener.persona.name}",
                    answer_dict=d2_ans,
                    options_or_criteria=d2_ans.get("legend", {}),
                    zone=zone_d2,
                    fallback_used=fallback_d2,
                    effective_choice=imp_score,
                )

                # Nouveau souvenir chez le listener (dé-imbrication pour éviter l'explosion de tokens)
                clean_text = shared_memory.text
                while "m'a dit : « " in clean_text and clean_text.endswith(" »"):
                    start_idx = clean_text.find("m'a dit : « ") + len("m'a dit : « ")
                    clean_text = clean_text[start_idx:-2].strip()

                new_mem = MemoryRecord(
                    id=f"mem_hear_{listener.persona.id}_{global_tick}",
                    agent_id=listener.persona.id,
                    tick=global_tick,
                    type="hearsay",
                    text=f"{speaker.persona.name} m'a dit : « {clean_text} »",
                    entities=list(set(shared_memory.entities + [speaker.persona.id])),
                    fact_id=shared_memory.fact_id,
                    source_agent=speaker.persona.id,
                    hop_count=shared_memory.hop_count + 1,
                    importance=imp_score,
                    confidence=d8_ans["confidence"],
                    decision_author="decider",
                    last_accessed_tick=global_tick,
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
                            "global_tick": global_tick,
                        },
                    )
                )
                self.daily_events_summary.append(
                    f"{speaker.persona.name} a transmis à {listener.persona.name} l'information : {shared_memory.fact_id} (crédibilité: {cred_score:.2f})"
                )

    def _process_evening_reflections(self, day: int, tick: int, global_tick: int) -> None:
        """Déclenche les réflexions du soir avec D6 et Bedrock (B2) en parallèle sur GPU."""
        candidate_agents = [agent for agent in self.agents.values() if agent.memories]
        if not candidate_agents:
            return

        batch_items = [
            (f"{agent.persona.name} termine sa journée à {agent.persona.home_id}.", {"D6": build_d6_reflect_gate()})
            for agent in candidate_agents
        ]
        batch_results = self.decider.ask_batch(batch_items)

        for agent, d6_res in zip(candidate_agents, batch_results):
            d6_ans = d6_res["D6"]
            th_d6 = ConfidenceThresholds(
                green=self.thresholds_cfg.get("D6", {}).get("green", 0.45),
                orange=self.thresholds_cfg.get("D6", {}).get("orange", 0.25),
            )
            zone_d6 = classify_zone(d6_ans["confidence"], th_d6)
            fallback_d6 = False
            do_reflect = d6_ans["value"]
            if zone_d6 == "red":
                do_reflect = len(agent.memories) >= 5
                fallback_d6 = True

            self._log_decision(
                day=day,
                tick=tick,
                global_tick=global_tick,
                agent_id=agent.persona.id,
                decision_type="D6",
                question_text="Bilan et réflexion de fin de journée",
                answer_dict=d6_ans,
                options_or_criteria={"true": "Prendre un temps calme", "false": "Poursuivre sans introspection"},
                zone=zone_d6,
                fallback_used=fallback_d6,
            )

            if not do_reflect:
                continue

            cands = [
                MemoryCandidate(m.id, m.text, m.tick, m.importance, m.entities, m.fact_id, m.source_agent, m.hop_count)
                for m in agent.memories
            ]
            top_mems = self.memory_gate.score_and_rank(
                self.memory_gate.preselect(cands, global_tick, [agent.persona.home_id, agent.persona.id]),
                global_tick,
                "Bilan du soir",
                on_decision=self._make_on_d3_decision(day, tick, global_tick, agent.persona.id),
            )

            gen_res = generate_reflection(self.bedrock, agent, top_mems)
            reflection_text = gen_res["text"]

            ref_mem = MemoryRecord(
                id=f"mem_refl_{agent.persona.id}_{global_tick}",
                agent_id=agent.persona.id,
                tick=global_tick,
                type="reflection",
                text=reflection_text,
                entities=[agent.persona.id],
                importance=0.90,
                confidence=1.0,
                decision_author="bedrock",
                last_accessed_tick=global_tick,
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
