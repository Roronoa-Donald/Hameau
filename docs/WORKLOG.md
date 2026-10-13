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

