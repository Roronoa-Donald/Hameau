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
