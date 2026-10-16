# Implementation Plan — Tranche 1: Jury-Ready Quick Wins (Score 68 -> 86+)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

## Overview
This plan implements all 5 high-impact, high-ROI items from **Tranche 1** identified in the 360° audit report of Hameau. It repairs visual glitches, makes the MemoryGate Diff tab and Inspector Memories dynamically driven by real JSONL simulation data, symmetrizes social relationships for realistic rumor diffusion, fixes offline tests, and eliminates hardcoded benchmark numbers.

---

## File Structure

- **Modified Files**:
  - `viewer/app.js`:
    - Dynamic `currentAction` in `applyEvent()` (BUG-06)
    - Safe DOM markdown formatting for Gazette (BUG-08)
    - Accounting for `reflection` and `gazette` in Bedrock calls/costs (BUG-12)
    - Real Canvas typography without `var(--font-ui)` (BUG-16)
    - Dynamic `#inspector-memories-list` and `#tab-memory-diff` (BUG-03, BUG-05)
    - Anti-collision spacing adjustments for village locations and agent arcs (BUG-10)
  - `viewer/styles.css`:
    - Fix `.legend-color.r2` to `#06b6d4` and add `.legend-color.r3` (BUG-13)
  - `viewer/index.html`:
    - Add R3 item to rumor chart legend and dynamic ID `diff-decider-latency`
  - `src/hameau/simulation/engine.py`:
    - Enrich D3 decision callback payload with `memory_id`, `memory_text`, `recency_score`, `importance_score`, `composite_score`, `relevance_score`
    - Add `effective_choice` parameter to `_log_decision` for accurate fallback logging (BUG-07)
    - Feed MemoryGate candidate memories into D5 `ShareScorer` (BUG-02)
  - `src/hameau/simulation/distribution.py`:
    - Symmetrize social relationships for mutual interactions (BUG-02)
  - `bench/run_benchmark.py`:
    - Remove hardcoded `coherence * 0.75` and `115.0` latency constants (BUG-01)
  - `src/hameau/llm/bedrock.py`:
    - Add botocore timeout/retries config and robust exception handling in `converse()` (BUG-09)
  - `tests/test_simulation.py`:
    - Point `cassettes_dir` to repository `cassettes/` instead of empty `tmp_path` (BUG-09)
  - `tests/test_bedrock.py`:
    - Add mock fallback for offline test execution when AWS credentials are absent (BUG-09)

---

## Implementation Tasks

### Task 1: UI Polish & Visual Bug Fixes in Viewer
- [ ] Update `this.agentsState[agent_id].currentAction` in `applyEvent()` for `decision` (D1), `move`, and `conversation_turn` (BUG-06).
- [ ] Implement `renderGazetteSafe()` with safe DOM nodes (`<h3>`, `<strong>`, `<p>`) without `innerHTML` (BUG-08).
- [ ] Add `reflection` and `gazette` events to `bedrockCount` and `totalCost` metrics (BUG-12).
- [ ] Fix legend colors in `viewer/styles.css` (`.legend-color.r2` = `#06b6d4`, `.legend-color.r3` = `#10b981`) and update `viewer/index.html` (BUG-13).
- [ ] Replace `var(--font-ui)` with `'Plus Jakarta Sans', sans-serif` in all Canvas `ctx.font` assignments in `viewer/app.js` (BUG-16).
- [ ] Adjust agent arc fan-out spread (`spreadX`) and offset `boulangerie` / `maison_centre` coordinates to eliminate label/character collisions (BUG-10).

### Task 2: Dynamic MemoryGate Connection & Inspector Memories
- [ ] In `src/hameau/simulation/engine.py`:
  - Enhance `_log_decision` with `effective_choice` and `extra_payload` arguments (BUG-07).
  - In `_make_on_d3_decision`, populate `memory_id`, `memory_text`, `recency_score`, `importance_score`, `composite_score`, and `relevance_score`.
- [ ] In `viewer/app.js`:
  - Record scored memories per agent upon receiving D3 events in `applyEvent()`.
  - In `updateInspector()`, render Top 3 scored memories dynamically inside `#inspector-memories-list` (BUG-05).
  - In `updateMemoryDiffTab()`, delete all hardcoded mock arrays (`Dr Diallo`, `Moussa`, `-78%`, `115ms`). Render evaluated memories and gated memories dynamically, computing genuine token savings and filtered noise from simulation data (BUG-03).

### Task 3: Symmetrize Social Graph & Ground D5 in MemoryGate
- [ ] In `src/hameau/simulation/distribution.py`:
  - Symmetrize relationships so friendships are bidirectional (`agents[u].persona.relationships[v] = w` and `agents[v].persona.relationships[u] = w`).
  - Add mutual relationships for Yao with Awa (0.6) and Élise (0.6) (BUG-02).
- [ ] In `src/hameau/simulation/engine.py`:
  - Run MemoryGate scoring on speaker memories before D5, and pass those ranked memories to `build_d5_share_scorer`.
- [ ] In `bench/run_benchmark.py`:
  - Remove hardcoded `coherence * 0.75` on line 151.
  - Measure real Decider latency rather than hardcoding `115.0` on lines 101 and 148 (BUG-01).

### Task 4: Robust Offline Testing & Bedrock Error Handling
- [ ] In `src/hameau/llm/bedrock.py`:
  - Add `botocore.config.Config(read_timeout=15, retries={"max_attempts": 3, "mode": "standard"})`.
  - Wrap `self.client.converse` in `try...except` with informative error handling (BUG-09).
- [ ] In `tests/test_simulation.py`:
  - Set `cassettes_dir="cassettes"` to utilize pre-recorded cassettes offline (BUG-09).
- [ ] In `tests/test_bedrock.py`:
  - Support offline test mode with mocked responses when AWS credentials are unavailable (BUG-09).

### Task 5: End-to-End Verification & Validation
- [ ] Run `uv run pytest tests/` and verify all tests pass cleanly.
- [ ] Run `bash scripts/verify.sh` and ensure all checks succeed.
- [ ] Run a test simulation and inspect the generated JSONL and viewer outputs to confirm dynamic memory binding.
