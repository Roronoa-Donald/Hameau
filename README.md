# HAMEAU: Multi-Agent Village with Strands Decider 2B & Amazon Bedrock

[![License: Apache-2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python: 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Tags](https://img.shields.io/badge/Hackathon-strands--decider--2b%20%7C%20context--memory-orange)](https://community.aws)

**HAMEAU** is an autonomous multi-agent simulation of 12 villagers designed for the **Strands Decider Agent Hackathon** (AWS Builder Center).

It solves the foundational bottleneck of generative agent simulations (Stanford Smallville, AI Town): **the latency, cost, and context saturation caused by querying heavy Large Language Models for routine decisions.**

HAMEAU introduces a decoupled, hierarchical decision architecture:
- **Strands Decider 2B** (on local GPU / edge): Executes all high-frequency decisions (D1–D8) in a single forward pass without autoregressive decoding (~115 ms median latency).
- **Amazon Bedrock (Amazon Nova Micro)**: Reserved exclusively for rare, rich text generation (dialogue, agent reflections, evening village Gazette).
- **MemoryGate Reusable Pattern** (`patterns/memory_gate/`): A standardized Strands `HookProvider` that filters and scores memories before injecting them into the LLM context, saving **78% of prompt tokens** and eliminating context clutter.

---

## 1. Architecture: The Decoupled Agent Pattern

```
                       ┌──────────────────────────────────────────────┐
                       │          Agent Observation & State           │
                       └──────────────────────┬───────────────────────┘
                                              │
                     High-Frequency Decisions │ (D1–D8: Choice / Score / Noul)
                                              ▼
                       ┌──────────────────────────────────────────────┐
                       │         Strands Decider 2B (Local GPU)       │
                       │   - D1: ActionPicker (Choice among 2-8 items)│
                       │   - D2: ImportanceScorer (Score 0..1)        │
                       │   - D3: MemoryGate Relevance (Score 0..1)    │
                       │   - D4: TalkGate (Noul / Yes-No)             │
                       │   - D5: TopicSelector (Score 0..1)           │
                       │   - D6: ReflectGate (Noul / Yes-No)          │
                       │   - D7: ContinueGate (Noul / Yes-No)         │
                       │   - D8: CredibilityGate (Score 0..1)         │
                       └──────────────────────┬───────────────────────┘
                                              │
                      Rare Generative Triggers│ (Filtered Context + Gate Passed)
                                              ▼
                       ┌──────────────────────────────────────────────┐
                       │       Amazon Bedrock (Amazon Nova Micro)     │
                       │   - B1: Dialogue Turn Generation             │
                       │   - B2: Deep Evening Reflection Synthesis    │
                       │   - B4: Daily Village Gazette Newspaper      │
                       │   * Guardrailed to closed village persona    │
                       │   * Cassette-cached for $0 reproducible replay│
                       └──────────────────────────────────────────────┘
```

---

## 2. Reusable Pattern: MemoryGate (`#context-memory`)

Located in `patterns/memory_gate/`, `MemoryGate` is an Apache-2.0 reusable pattern that can be plugged into any agentic workflow.

### Three-Step Scoring Pipeline
1. **Deterministic Preselection**: Selects up to 12 candidates using entity co-occurrence, recency, and importance.
2. **Relevance Scoring via Decider 2B (D3)**: Evaluates candidates in a single forward pass against the current agent context.
3. **Composite Scoring & Ranking**:
   $$S(m) = w_r \cdot e^{-\lambda \Delta t} + w_i \cdot \text{Importance}(m) + w_p \cdot \text{Relevance}(m)$$
   where $\lambda = \frac{\ln(2)}{T_{1/2}}$ (configurable half-life, default 1 day = 192 ticks).

### Calibrated Confidence Zones
- **Green ($\ge 0.55$)**: Score accepted directly.
- **Orange ($0.35 \le c < 0.55$)**: Score accepted, flagged in observability logs.
- **Red ($< 0.35$)**: Automatic deterministic fallback: $\frac{\text{Importance} + 0.5}{2}$.

### Native Strands Agents SDK Integration
`MemoryGate` implements `strands.hooks.HookProvider` and registers to `BeforeModelCallEvent`:

```python
from strands import Agent
from strands.hooks import HookRegistry
from patterns.memory_gate import MemoryGate

gate = MemoryGate(decider_client=client, top_k=3)
registry = HookRegistry()
gate.register_hooks(registry)
```

---

## 3. Empirical Benchmark & Verification Results

All figures below are directly generated and measured from verifiable benchmark logs in `results/`.

### Comparative Strategy Performance (`results/comparison.csv`)

| Strategy | Decisions Taken | Bedrock LLM Calls | Decider / LLM Ratio | p50 Decision Latency | Est. Cost (1 Day) | Narrative Coherence |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Strategy A: Pure Heuristic** | 144 | 0 | 0 : 0 | 0.05 ms | $0.0000 | 0.250 |
| **Strategy B: All-LLM (Nova Micro)** | 221 | 244 | 1.0 : 1 | 680.0 ms | $0.0410 | 0.820 |
| **Strategy C: Hybrid Hameau (Ours)** | **221** | **23** | **9.6 : 1** | **115.0 ms** | **$0.0000\*** | **1.000** |
| **Ablation: No MemoryGate** | 215 | 23 | 9.3 : 1 | 115.0 ms | $0.0000\* | 0.750 |

*\* Replays are cached via Bedrock cassettes; live API runs cost <$0.003/day.*

### Calibration Metrics (`results/calibration.csv`)
Evaluated across ground-truth datasets in `eval/`:
- **E1 Importance Scoring (D2)**: MAE = **0.2775**, Spearman rank correlation = **0.3109**.
- **E2 Relevance Scoring (D3)**: MAE = **0.4420**, Binary Alignment Accuracy = **50.0%**.
- **E3 Confidence Calibration (Noul)**: Brier Score = **0.2552**, Expected Calibration Error (ECE) = **0.0585** across 5 bins.

---

## 4. Quick Start

### Prerequisites
- Linux / macOS with Python 3.11+
- [uv](https://github.com/astral-sh/uv) (recommended) or `pip`

```bash
# Clone the repository
git clone https://github.com/strands-labs/strands-decider-hackathon-hameau.git
cd strands-decider-hackathon-hameau

# Create virtual environment and install dependencies
uv venv
source .venv/bin/activate
uv pip install -e ".[dev]"
```

### Autonomous Launch Scripts (One-Click)

The repository provides automated executable scripts for one-click execution:

```bash
# 1. Launch the 2D character web viewer (starts server and opens browser)
./start.sh

# 2. Run a fast 1-day mock simulation (0$ AWS, 0 GPU) and view immediately
./start.sh --mock 1

# 3. Run the complete 3-day official simulation on local GPU + AWS Bedrock
./start.sh --real 3

# 4. Run the full verification and non-regression suite
./start.sh --verify
```

### Dedicated CLI Commands
```bash
# Run simulation using deterministic mock (0 API cost, bit-for-bit reproducible)
uv run hameau --days 2 --mock-decider

# Run simulation using local GPU RTX 3050 and live Bedrock Nova Micro
uv run hameau --days 3

# Launch Secure Replay Viewer manually
./scripts/run_viewer.sh   # or: uv run hameau --serve --port 8000
```
Open `http://127.0.0.1:8000/index.html` in your browser.

Features included in the viewer:
- **Canvas Tilemap**: Spatial village map with agent positions, speech bubbles, and location markers.
- **Epidemic Diffusion Curve (C1)**: Dual Canvas curve showing R1 rumor infection vs R2 official debunking across simulation time.
- **MemoryGate Prompt Diff (C2)**: Side-by-side prompt inspector showing un-gated (12 memories, ~1480 tokens) vs gated (3 memories, ~320 tokens) context with -78% token savings.
- **Dynamic Savings Ticker (C3)**: Live counter of USD savings vs All-LLM architecture and cumulative latency saved.

### Run Calibration & Comparative Benchmark
```bash
# Run calibration on eval datasets (outputs results/calibration.csv)
uv run python scripts/calibrate.py

# Run comparative benchmark suite across 4 strategies (outputs results/comparison.csv)
uv run python bench/run_benchmark.py
```

---

## 5. Security & Safety Principles

1. **Localhost Binding**: `hameau --serve` binds strictly to `127.0.0.1`.
2. **Filesystem Sandbox**: The server handler only serves `viewer/` and simulation files in `runs/`; directory traversal (`../`) and sensitive files (`.git/`, `config.yaml`) are blocked (404).
3. **DOM XSS Elimination**: All viewer rendering uses safe DOM construction (`createElement`, `textContent`) without `innerHTML`.
4. **Content Security Policy (CSP)**: `default-src 'self'` enforced in `viewer/index.html`.
5. **Entity Guardrails**: Bedrock prompts enforce a strict whitelist of 12 authorized village personas and enclose memories in `<memories>` XML tags.

---

## 6. Repository Layout

```
├── bench/
│   └── run_benchmark.py           # 4-strategy comparative benchmark runner
├── eval/
│   ├── e1_importance.jsonl        # 20 ground-truth importance scenarios
│   ├── e2_relevance.jsonl         # 20 ground-truth relevance pairs
│   └── e3_calibration.jsonl       # 20 ground-truth calibration propositions
├── patterns/
│   └── memory_gate/
│       ├── __init__.py            # Exports MemoryGate, MemoryGateHook
│       ├── memory_gate.py         # Reusable MemoryGate pattern + Strands HookProvider
│       ├── test_gate.py           # Unit tests for HookProvider & scoring
│       └── PATTERN.md             # Reusable pattern documentation
├── results/
│   ├── baseline.md                # Step 0 baseline measurements
│   ├── calibration.csv            # Measured ECE, Brier, and MAE scores
│   ├── comparison.csv             # Strategy benchmark measurements
│   └── decider_env.csv            # Step 0 GPU latency measurements
├── scripts/
│   ├── calibrate.py               # Calibration measurement script
│   ├── bench_decider_env.py       # Step 0 GPU environment benchmark
│   └── verify.sh                  # Single-command verification suite
├── src/hameau/
│   ├── cli.py                     # CLI with secure localhost server
│   ├── decisions/                 # Decider client, question builders, zones
│   ├── llm/                       # Bedrock Nova Micro client & guardrails
│   ├── models/                    # Agents, World, Memory, LogEvent models
│   └── simulation/                # Simulation engine, distribution, scenario
├── viewer/
│   ├── index.html                 # Replay viewer with CSP & diffusion curve
│   ├── app.js                     # Safe DOM replay application
│   └── styles.css                 # UI/UX Pro Max theme
├── tests/                         # Full automated pytest suite
├── docs/
│   ├── DECISIONS.md               # Architecture Decision Records (ADRs)
│   └── WORKLOG.md                 # Chronological dated work log
└── config.yaml                    # Village simulation configuration
```

---

## 7. License

Licensed under the Apache License, Version 2.0. See [LICENSE](LICENSE) for details.
