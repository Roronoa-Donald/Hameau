"""Generate un-annotated human labeling templates from real simulation logs (FR honest evaluation)."""

import csv
import json
import random
from pathlib import Path

SEED = 42
rng = random.Random(SEED)

RUN_PATHS = [
    Path("runs/test_20agents.jsonl"),
    Path("runs/run_real_3j.jsonl"),
    Path("viewer/live_run.jsonl")
]

events = []
for p in RUN_PATHS:
    if p.exists():
        with open(p, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    events.append(json.loads(line))

# 1. Importance template: 40 real observations
# Extract candidate observations from memory events, rumors, reflections, and dialogs
raw_observations = []
seen_texts = set()

for e in events:
    agent_id = e.get("agent_id") or "inconnu"
    day = e.get("day", 1)
    tick = e.get("tick", 0)
    p = e.get("payload", {})

    text = None
    context = f"Jour {day}, tick {tick} (agent: {agent_id})"
    if e.get("event_type") == "rumor_hop" and "text" in p:
        text = p["text"]
    elif e.get("event_type") == "conversation_turn" and "utterance" in p:
        speaker = p.get("speaker", agent_id)
        listener = p.get("listener", "village")
        text = f"{speaker} dit à {listener} : « {p['utterance']} » (sujet : {p.get('topic', 'quotidien')})"
    elif e.get("event_type") == "reflection" and "text" in p:
        text = f"Réflexion de fin de journée : {p['text']}"
    elif p.get("decision") == "D2" and "question" in p:
        # Check if memory text is attached
        if "memory_text" in p:
            text = p["memory_text"]

    if text and text not in seen_texts and len(text.strip()) > 15:
        clean_text = " ".join(text.strip().split())
        seen_texts.add(clean_text)
        raw_observations.append({
            "agent_id": agent_id,
            "context": context,
            "observation_text": clean_text,
        })

rng.shuffle(raw_observations)
selected_obs = raw_observations[:40]

out_importance = Path("eval/importance_labels_TEMPLATE.csv")
with open(out_importance, "w", encoding="utf-8", newline="") as f:
    writer = csv.writer(f)
    writer.writerow([
        "id",
        "agent_id",
        "context",
        "observation_text",
        "human_rating"  # To be filled by human evaluator: faible, moyenne, or élevée
    ])
    for idx, item in enumerate(selected_obs, start=1):
        writer.writerow([
            f"obs_{idx:02d}",
            item["agent_id"],
            item["context"],
            item["observation_text"],
            ""  # empty for human labeler
        ])

print(f"Generated {len(selected_obs)} importance items in {out_importance}")


# 2. Relevance template: 30 real situations with 8 candidate memories each
# We reconstruct situations where agents had multiple candidate memories evaluated via D3
situation_dict = {}
for e in events:
    if e.get("event_type") == "decision" and e.get("payload", {}).get("decision") == "D3":
        p = e["payload"]
        mem_text = p.get("memory_text")
        if not mem_text:
            continue
        key = (e.get("day", 1), e.get("tick", 0), e.get("agent_id", "inconnu"))
        if key not in situation_dict:
            situation_dict[key] = []
        if mem_text not in situation_dict[key]:
            situation_dict[key].append(mem_text)

# We also collect pool of real memories for padding up to 8 if a situation had 4-7 candidates
all_pool_mems = list(seen_texts)

valid_situations = []
for (day, tick, agent_id), mem_list in situation_dict.items():
    if len(mem_list) >= 4:
        # Build 8 candidates
        cands = list(mem_list)
        if len(cands) > 8:
            cands = cands[:8]
        elif len(cands) < 8:
            # Pad with real memories not already in list
            pad_candidates = [m for m in all_pool_mems if m not in cands]
            rng.shuffle(pad_candidates)
            cands.extend(pad_candidates[:(8 - len(cands))])
        
        hour = 6 + tick // 12
        minute = (tick % 12) * 5
        time_str = f"{hour:02d}h{minute:02d}"
        situation_context = f"{agent_id.capitalize()} se prépare à agir à {time_str} (Jour {day}, tick {tick})."
        
        # Shuffle candidates so position bias is neutralized
        rng.shuffle(cands)
        valid_situations.append({
            "day": day,
            "tick": tick,
            "agent_id": agent_id,
            "situation_context": situation_context,
            "candidates": cands
        })

rng.shuffle(valid_situations)
selected_situations = valid_situations[:30]

out_relevance = Path("eval/relevance_labels_TEMPLATE.csv")
with open(out_relevance, "w", encoding="utf-8", newline="") as f:
    writer = csv.writer(f)
    writer.writerow([
        "situation_id",
        "agent_id",
        "situation_context",
        "candidate_1",
        "candidate_2",
        "candidate_3",
        "candidate_4",
        "candidate_5",
        "candidate_6",
        "candidate_7",
        "candidate_8",
        "human_top_3_indices"  # Human writes e.g. "1,3,7"
    ])
    for idx, sit in enumerate(selected_situations, start=1):
        writer.writerow([
            f"sit_{idx:02d}",
            sit["agent_id"],
            sit["situation_context"],
            sit["candidates"][0],
            sit["candidates"][1],
            sit["candidates"][2],
            sit["candidates"][3],
            sit["candidates"][4],
            sit["candidates"][5],
            sit["candidates"][6],
            sit["candidates"][7],
            ""
        ])

print(f"Generated {len(selected_situations)} relevance situations in {out_relevance}")
