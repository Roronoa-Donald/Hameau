# HAMEAU Work Log

This document tracks all engineering actions, measurements, and commits in chronological order.

## 2026-10-13

### Step 0: Initial State & Baseline Setup (COMPLETED)
- Created `scripts/verify.sh` for one-command integrity checks.
- Baseline measurement documented in `results/baseline.md`:
  - Total events: 1,079 in 2-day mock run.
  - Defect 2.1 reproduced: Day 1 had 510 decisions, Day 2 had 0 (frozen).
  - Defect 2.2 reproduced: Rumor reached only 1 other agent (Élise) and repeated 20 times.
  - Defect 2.3 reproduced: ScoreAnswer score values in 0..4 unnormalized.
  - Defect 2.4 reproduced: hash() used in mock.
  - Defect 2.5 reproduced: 2,700 decisions claimed vs 510 logged.
- All 5 audit defects reproduced by automated tests in `tests/audit_repro/test_defects.py` (5/5 PASS).
- Decider GPU benchmark measured on RTX 3050 (6GB VRAM) and recorded in `results/decider_env.csv`:
  - 1 question: p50 = 2340.6 ms
  - 4 questions: p50 = 4107.9 ms
  - 8 questions: p50 = 5445.3 ms
  - VRAM: ~3.7 to 4.0 GB used out of 5.8 GB.
  - Root cause of >2s latency: `flash-linear-attention` and `causal-conv1d` missing in environment, falling back to pure PyTorch loops.
- Conclusion: Confirmed **12 agents** as target for local hardware to stay within reasonable runtimes (<10 min/day).

### Step A: Making the Project Real (COMPLETED)
- **A1 Global Tick & Dawn Reset**:
  - Implemented `global_tick = (day - 1) * 192 + tick` across engine, memory gate, and scenarios.
  - Implemented 06:00 dawn reset restoring energy, resetting pending actions, and placing agents at home.
  - Verified by `tests/test_multi_day.py` (Day 2 decisions active, >100).
- **A2 Score Normalization & Confidence Zones**:
  - Normalized `ScoreAnswer.score` to `[0.0, 1.0]` using `raw_score / (len(legend) - 1)` while preserving `raw_score`.
  - Added strict `ValueError` in `DeciderClient.load()` to prevent silent mock fallback in production.
  - Verified by `tests/test_score_norm.py`.
- **A3 Comprehensive Decision Logging**:
  - Wired D1 to D8 through explicit `_log_decision` events with full metadata (options, probabilities, confidence, zone, latency, backend).
  - Wired D3 inside `MemoryGate.score_and_rank` via `on_decision` callback.
  - Summary metrics computed strictly by reducing the event stream (157 counted == 157 logged).
  - Verified by `tests/test_logging_completeness.py`.
- **A4 Social Dynamics & Rumor Diffusion**:
  - Added 6-tick (30 min) conversation cooldown between pairs of agents to eliminate repetitive conversation loops.
  - Added dynamic needs decay per tick (hunger, energy, social).
  - Rumor spreads dynamically across village (all 12 agents reached over 2 days).
- **A6 Determinism Guarantee**:
  - Replaced Python `hash()` with SHA-256 deterministic hash in mock decider.
  - Verified bit-for-bit event equality across runs with different `PYTHONHASHSEED` in `tests/test_determinism.py`.
- **A7 Bedrock Guardrails**:
  - Bound dialogue generation to strict authorized entity list (`VILLAGEOIS_AUTORISES`).
  - Formatted memories within `<memories><memory>...</memory></memories>` XML tags.
- Verified entire test suite and integrity checks with `scripts/verify.sh` (ALL CHECKS PASSED).

### Step B4: Security Hardening (COMPLETED)
- **Localhost & Path Restriction**:
  - Refactored `hameau --serve` in `src/hameau/cli.py` to use `create_viewer_server()` with `RestrictedViewerHandler`.
  - Server binds strictly to `127.0.0.1` (no external network exposure).
  - Restricted filesystem access: only files inside `viewer/` and simulation logs inside `runs/` are reachable; path traversal (`../`) and sensitive files (`.git/`, `config.yaml`) return 404.
  - Automated tests added in `tests/test_security_serve.py` (PASS).
- **DOM XSS Elimination**:
  - Replaced all unescaped `innerHTML` occurrences in `viewer/app.js` (feed items, inspector decision cards, rumor hops) with safe DOM manipulation (`createElement`, `textContent`).
  - Added strict Content Security Policy (CSP) `<meta>` tag to `viewer/index.html`.
  - Removed hardcoded metric strings (`~100 ms · Local GPU`) in `viewer/index.html` and bound them dynamically to measured event latency in `viewer/app.js`.
- Verified entire suite with `scripts/verify.sh` (ALL CHECKS PASSED).

### Step B1: MemoryGate as Strands HookProvider (COMPLETED)
- **Strands Agents SDK Hook Integration**:
  - Subclassed `HookProvider` in `patterns/memory_gate/memory_gate.py`.
  - Implemented `register_hooks(registry)` binding callback to `BeforeModelCallEvent`.
  - Implemented `on_before_model_call(event)`: intercepts model invocation, evaluates candidate memories via `MemoryGate.score_and_rank()`, and injects top-k scored memories directly into `invocation_state["selected_memories"]` and formatted prompt text.
  - Exported `MemoryGateHook = MemoryGate` in `patterns/memory_gate/__init__.py`.
  - Created standalone unit test suite in `patterns/memory_gate/test_gate.py` covering preselection, scoring, composite score weighting, confidence zones, HookProvider registration, and event interception (4/4 tests PASS).
  - Documented pattern usage with Strands Agent in `patterns/memory_gate/PATTERN.md`.
- Verified entire suite with `scripts/verify.sh` (ALL CHECKS PASSED).

### Step B3: Evaluation Datasets & Confidence Calibration (COMPLETED)
- **Ground-Truth Datasets (`eval/`)**:
  - `eval/e1_importance.jsonl`: 20 labeled scenarios evaluating D2 importance scoring.
  - `eval/e2_relevance.jsonl`: 20 labeled pairs evaluating D3 MemoryGate relevance scoring.
  - `eval/e3_calibration.jsonl`: 20 labeled binary propositions evaluating calibration, Brier score, and ECE.
- **Calibration Tool (`scripts/calibrate.py`)**:
  - Computes Mean Absolute Error (MAE) and Spearman rank correlation.
  - Computes Brier Score ($0.2552$) and Expected Calibration Error ($ECE=0.0585$) with 5 equal-width confidence bins.
  - Outputs results to `results/calibration.csv`.
- **Unit Tests**:
  - Added test suite in `tests/test_calibration.py` (3/3 PASS).

### Step B2: Comparative Benchmark Suite (COMPLETED)
- **Benchmark Suite (`bench/run_benchmark.py`)**:
  - Compares 4 strategies on standardized village metrics:
    1. Strategy A: Pure Heuristic (0 AI models, 0.05ms latency, $0 cost, coherence 0.25).
    2. Strategy B: All-LLM Nova Micro (244 calls, 680ms latency, estimated $0.0051/48 ticks, coherence 0.82).
    3. Strategy C: Hybrid Hameau (221 Decider decisions, 23 Bedrock calls, 9.6:1 ratio, 115ms p50 latency, $0 on cached runs, coherence 1.0).
    4. Ablation: Hameau without MemoryGate (215 decisions, 23 Bedrock calls, coherence drops to 0.75 due to context clutter).
  - Metrics recorded in `results/comparison.csv`.
- **Unit Tests**:
  - Added test suite in `tests/test_bench.py` (1/1 PASS).
- Verified entire suite with `scripts/verify.sh` (ALL CHECKS PASSED).

### Step C: High Impact UX & MemoryGate Visualization (COMPLETED)
- **C1 Epidemic Rumor Diffusion Curve**:
  - Implemented real-time Canvas rendering in `viewer/app.js` (`drawRumorCurve()`) and `viewer/index.html`.
  - Visualizes dual epidemic curves: R1 rumor transmission (red `#f43f5e`) vs R2 official debunk (green `#10b981`) over village time (06h to 22h).
  - Synchronized vertical playback cursor tracking current tick.
- **C2 MemoryGate Side-by-Side Prompt Diff**:
  - Added dedicated `Diff MemoryGate` tab in `viewer/index.html` and `viewer/app.js` (`updateMemoryDiffTab()`).
  - Side-by-side comparison:
    - Raw un-gated context: 12 noisy memories, ~1,480 tokens.
    - MemoryGate filtered context: Top-3 scored memories (via Strands Decider 2B D3), ~320 tokens, confidence zone badges.
    - Live economy metric: -78% tokens saved, 9/12 memories eliminated from LLM prompt.
- **C3 Dynamic Live Cost & Latency Ticker**:
  - Bound dynamic counters in `viewer/index.html` and `viewer/app.js`:
    - Real-time savings vs All-LLM architecture ($).
    - Cumulative user latency avoided (seconds saved compared to 680ms LLM roundtrips).
- Verified entire suite with `scripts/verify.sh` (ALL CHECKS PASSED).

### Step D: Documentation & Final Verification (COMPLETED)
- **README.md Overhaul**:
  - Authored comprehensive English README including architecture diagram, problem statement, MemoryGate HookProvider code, measured calibration & benchmark tables, quickstart guide, security practices, and repository layout.
- **Architectural Decision Records (`docs/DECISIONS.md`)**:
  - Added DEC-004 through DEC-008 explaining the decoupled Decider/LLM pattern, MemoryGate as HookProvider, global tick clock, localhost serving, and SHA-256 determinism.
### Step E1: 3-Day Simulation Expansion & Saturday Market Climax (COMPLETED)
- **Multi-Day Expansion (3 Days / 576 Ticks)**:
  - Updated default configuration in `config.yaml` to `simulation.days: 3` (576 ticks).
  - Implemented Saturday morning climax event `R3_ouverture_marche` at Day 3 tick 12 (07:00) in `src/hameau/simulation/scenario.py`.
  - Delivered direct observation of open market stalls to key villagers Awa and Yao (`credibility: 1.0`, `confidence: 1.0`).
- **Belief State Dynamics Hardening**:
  - Enhanced `set_believed_fact()` in `src/hameau/models/agent.py`:
    - Prevents old closure rumors (`R1_fermeture_marche`) from triggering panic stockpiling when the market is confirmed open (`R3_ouverture_marche >= 0.55`).
    - Dissipates panic stockpiling (`did_stock_provisions = False`) when market opening is confirmed.
    - Preserves maximum established credibility for known facts against noisy hearsay degradation.
- **Verification & Testing**:
  - Added `test_three_day_simulation_and_r3_climax` in `tests/test_multi_day.py` verifying full 3-day run with >100 decisions per day and peaceful market resolution.
  - Updated `scripts/verify.sh` to enforce 3-day simulation and log completeness across Days 1, 2, and 3.
  - All tests and verification checks PASS.


