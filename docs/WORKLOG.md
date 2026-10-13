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
