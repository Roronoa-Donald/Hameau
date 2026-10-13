# Architecture & Engineering Decisions (ADR)

## DEC-001: Verification Harness & Strict Evidence Rule
- **Context**: The hackathon grading rewards verified efficiency and penalizes ungrounded numbers.
- **Decision**: Every metric, latency, cost, and decision count must derive directly from executed logs or benchmark scripts. A single `scripts/verify.sh` runs all automated health checks.
- **Status**: Accepted.

## DEC-002: Model Checkpoint Selection
- **Context**: Official strands-decider repository recommends `StrandsAgents/strands-decider-2B-qwen3.5-v1-2610` as latest reference model, with `hobson-v21` as predecessor.
- **Decision**: Benchmark both models in Step 0. Use v1-2610 as primary if supported by local environment, keeping v21 as baseline comparison.
- **Status**: Under evaluation in Step 0.

## DEC-003: Agent Count Fixed to 12 Canonical Agents
- **Context**: Empirical GPU benchmark in Step 0 showed ~4.1s per batch of 4 questions on RTX 3050 without fused CUDA kernels (`flash-linear-attention` / `causal-conv1d`).
- **Decision**: Restrict the simulation target to the 12 canonical hand-crafted agents rather than 25. This ensures a 1-day simulation finishes in under 10 minutes locally, while enabling 100% deterministic, high-depth social interactions and rumor dynamics.
- **Status**: Accepted.

## DEC-004: Decoupled Decision & Generation Architecture
- **Context**: Querying heavy LLMs for routine agent decisions (whether to talk, walk, or rate memory) creates a multi-second latency bottleneck and rapidly exhausts API budgets.
- **Decision**: Decouple high-frequency decisions (D1 to D8) to Strands Decider 2B running locally on GPU/CPU in a single forward pass without autoregressive decoding (~115ms p50). Amazon Bedrock Nova Micro is strictly reserved for generative dialogue turns, evening reflections, and the daily village Gazette.
- **Status**: Accepted.

## DEC-005: MemoryGate as Strands HookProvider
- **Context**: In multi-agent simulations, context bloat degrades LLM reasoning and inflates token cost. Agents need context filtered before Bedrock invocation.
- **Decision**: Implement `MemoryGate` as a standard `strands.hooks.HookProvider` intercepting `BeforeModelCallEvent`. It scores memory candidates via Decider D3, computes composite exponential recency/importance/relevance scores, and injects only the top-3 scored memories into `invocation_state`.
- **Status**: Accepted.

## DEC-006: Global Tick Clock & Dawn State Reset
- **Context**: In multi-day simulations, restarting tick to 0 each morning caused day 2 decisions to freeze because `action_end_tick` was absolute (>180), and caused memory recency decay to treat day-1 memories as future events.
- **Decision**: Track simulation time globally using `global_tick = (day - 1) * ticks_per_day + tick`. Reset pending actions, restore agent energy, and return agents to their home location during daily dawn rollover (06:00, tick 0).
- **Status**: Accepted.

## DEC-007: Localhost-only Web Serving & DOM XSS Elimination
- **Context**: `hameau --serve` previously bound to `0.0.0.0` and exposed the whole repository, while the web viewer rendered untrusted LLM and JSONL strings into `innerHTML`.
- **Decision**: Implement `RestrictedViewerHandler` binding strictly to `127.0.0.1` and restricted only to `viewer/` and `runs/`. Replaced all `innerHTML` usages in `viewer/app.js` with safe DOM construction (`createElement`, `textContent`) and enforced a strict Content Security Policy (`default-src 'self'`).
- **Status**: Accepted.

## DEC-008: Deterministic SHA-256 Hashing for Mock Engine
- **Context**: Python built-in `hash()` is randomized across processes by `PYTHONHASHSEED`, preventing identical event replays.
- **Decision**: Replace `hash()` in `DeciderClient` mock with a deterministic SHA-256 hash function (`_deterministic_hash`). Verified bit-for-bit event equality across runs in `tests/test_determinism.py`.
- **Status**: Accepted.
