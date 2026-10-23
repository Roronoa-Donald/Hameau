# HAMEAU: Simulating a 20-Agent Living Village for 72 Hours on a Laptop GPU and $0.01 of Amazon Bedrock

**Tags:** `#strands-decider-2b`, `#context-memory`  
**Hackathon Track:** Strands Decider Agent Hackathon (AWS Builder Center)  
**Reusable Pattern:** [`patterns/memory_gate/`](../patterns/memory_gate/PATTERN.md)  
**Demo Video:** Under 3 minutes (YouTube link in [`docs/VIDEO_DEMO.md`](VIDEO_DEMO.md))  
**Code Repository:** Public, Apache-2.0 License  

---

## 1. Introduction: The Multi-Agent Bottleneck

Ever since Stanford's *Smallville* paper (*Generative Agents*, Park et al., 2023), multi-agent social simulations have captured the imagination of AI builders. However, anyone who has attempted to scale autonomous agents quickly hits a wall: **the generative bottleneck**.

In traditional architectures, every microscopic decision—whether an agent should step outside, wave to a neighbor, or remember breakfast—queries a frontier Large Language Model. For 20 agents interacting over three days (72 hours), this approach easily exceeds **millions of tokens and hundreds of dollars in cloud API costs**, while introducing 2 to 5 seconds of latency per step.

**HAMEAU** solves this with an architectural paradigm: **Cognitive Splitting**.
Instead of using an LLM for everything, we hand all high-frequency micro-decisions to **Strands Decider 2B** running on a local consumer laptop GPU (NVIDIA RTX 3050 6GB), reserving **Amazon Bedrock (Amazon Nova Micro)** exclusively for rich, generative dialogue and synthetic reflection.

---

## 2. The Agent: What HAMEAU Does

HAMEAU is a living, autonomous village of **20 distinct citizens** (Awa the baker, Yao the courier, Kofi the mayor, Victor the challenger, and 16 others) simulated across **72 hours (576 discrete ticks of 5 minutes)**.

Each agent possesses:
- An occupation, personal schedule, and spatial location in the village.
- A persistent memory stream with exponential recency decay.
- Social relationships and trust networks.
- An autonomous action loop driven by local Decider 2B evaluations.

During the 3-day simulation, emergent social phenomena unfold organically:
- **Day 1 (Rumor Inception):** Courier Yao hears an unverified rumor (R1) that the mayor plans to close the market on Saturday. The rumor propagates through peer-to-peer dialogues.
- **Day 2 (Panic & Reaction):** Villagers react; one agent begins stockpiling supplies before Mayor Kofi issues a public clarification.
- **Day 3 (The Municipal Election):** The village convenes at tick 516 (11:00 AM) for a democratic election between incumbent Mayor Kofi and challenger Victor, evaluated via Decider template D9.

---

## 3. The Meaningful Decision: Handing Memory to Decider 2B (`#context-memory`)

For the hackathon's `#context-memory` track, we built **MemoryGate** ([`patterns/memory_gate/`](../patterns/memory_gate/PATTERN.md)), a reusable decision module that scores and filters memories before prompt injection.

### The Problem in Memory Retrieval
Standard agent retrieval relies on raw vector cosine similarity or simple recency. However:
1. Vector similarity fails to capture whether a past event is *actionable* in the agent's current situation.
2. Injecting all candidate memories into the LLM context causes "needle-in-a-haystack" confusion, inflates latency, and wastes tokens.

### How MemoryGate Handled the Decision
Before calling Amazon Bedrock, MemoryGate extracts candidate memories and queries **Strands Decider 2B** using question template **D3** (`RelevanceScorer`):

* **Question:** *"Considering the agent's current situation and intentions, how relevant is this memory?"*
* **Option Set:**
  - `0`: Irrelevant or unrelated
  - `1`: Weakly related / distant context
  - `2`: Relevant and informative
  - `3`: Decisive and top priority

Strands Decider 2B evaluates the candidate memory in a single non-autoregressive forward pass, returning calibrated probabilities across the options. We compute a continuous relevance score $P_{\text{rel}} \in [0, 1]$ and combine it into a composite score:

$$S(m) = 0.333 \times \text{Recency}(m) + 0.333 \times \text{Importance}(m) + 0.334 \times \text{Relevance}_{\text{Decider}}(m)$$

Only the **Top-3 memories** pass through the gate into Bedrock's context window.

### Calibrated Confidence & Safety Handling
Decider 2B outputs a softmax margin confidence score $C \in [0, 1]$. We divide predictions into three operational zones:
- **Green Zone ($C \ge 0.40$):** High confidence. Decision applied directly.
- **Orange Zone ($0.30 \le C < 0.40$):** Moderate confidence. Decision applied and telemetry logged.
- **Red Zone ($C < 0.30$):** Low confidence. The system automatically triggers a **deterministic safety fallback** (defaulting to safe routine actions, abstention, or heuristic memory weighting).

Across 13,467 decisions, 1,843 (13.69%) safely fell back to deterministic routines without crashing or hallucinating.

---

## 4. Measured Results: Verification & Cost Comparison

All numbers below were measured during our official 3-day continuous simulation ([`results/summary.json`](../results/summary.json)):

| Metric | Measured Value | Architecture Impact |
| :--- | :--- | :--- |
| **Simulated Duration** | 72 hours (576 ticks) | Full village lifecycle |
| **Total Decider Questions ($Q$)** | **13,467** | High-frequency local micro-decisions |
| **Total GPU Inference Requests ($R$)** | **8,206** | Batched with KV prefix-sharing |
| **Amazon Bedrock Calls ($L$)** | **659** | 100% live network calls (`amazon.nova-micro-v1:0`) |
| **Decider to Bedrock Ratio ($Q / L$)** | **20.44 : 1** | **> 20 local decisions per cloud call** |
| **Decider Median Latency (P50)** | **1,403.57 ms** | Local NVIDIA RTX 3050 Laptop GPU |
| **Bedrock Median Latency (P50)** | **746.02 ms** | Cloud API (us-east-1) |
| **MemoryGate Token Reduction** | **-23.05 %** | **173,803 tokens eliminated** (580k vs 754k) |
| **Total AWS Bedrock Spend** | **$0.01194 USD** | **1.19 cents for 3 days of simulation!** |

### The Cost Comparison
- **Hypothetical All-LLM Baseline:** If all 13,467 decisions had been routed to an LLM at an average of 400 tokens per prompt, cloud inference costs would have reached **$25 to $150+** depending on the model, with minutes of cumulative API queueing.
- **HAMEAU Hybrid Approach:** By shifting routine decisions to Decider 2B on local hardware, our total AWS bill for the entire 3-day run was **$0.01194 (under 2 cents)**.

---

## 5. The Reusable Asset: Drop-In MemoryGate Pattern

To make our work reusable for the broader AWS builder community, we packaged MemoryGate as an independent, standalone component in [`patterns/memory_gate/`](../patterns/memory_gate/):

1. **Standard Strands SDK Hook:** Implements `strands.hooks.HookProvider` and registers to `BeforeModelCallEvent`.
2. **Clean Minimal Example:** [`patterns/memory_gate/example.py`](../patterns/memory_gate/example.py) shows how to use it in under 30 lines of code.
3. **Comprehensive Test Suite:** [`patterns/memory_gate/test_gate.py`](../patterns/memory_gate/test_gate.py) verifies preselection, scoring, and confidence zones under `pytest`.

```python
from patterns.memory_gate import MemoryGate, MemoryCandidate
from hameau.decisions import DeciderClient

# 1. Initialize Decider client and MemoryGate
decider = DeciderClient(mock=False)  # Local 2B GPU checkpoint
gate = MemoryGate(decider_client=decider, top_k=3)

# 2. Score candidate memories for the agent's current situation
top_memories = gate.score_and_rank(candidates, current_tick=50, situation_context=situation)
```

---

## 6. What We Learned

1. **Small Decision Models are Complementary, Not Competitive:** Decider 2B is not designed to write poetry or summarize documents. But for discrete, typed choices (navigation, memory relevance, conversational triggers), it provides deterministic, low-cost intelligence that unlocks multi-agent scale.
2. **Confidence Calibration is Essential for Agent Robustness:** Knowing *when* a 2B model is uncertain allows builders to implement safety fallbacks. The 13.69% red-zone fallback rate in HAMEAU ensured that zero agents became stuck in infinite loops.
3. **Context Pruning Saves Dollars:** Eliminating 23% of context tokens via MemoryGate directly translated into lower Bedrock latency and lower billing, proving that smart memory curation is as vital as model selection.

---

## 7. Try It Yourself

Clone the public repository and launch the interactive 2D village visualizer locally in one command:

```bash
git clone https://github.com/strands-labs/strands-decider-hackathon-hameau.git
cd strands-decider-hackathon-hameau
./start.sh
```

Navigate to `http://127.0.0.1:8000` to inspect the 20 villagers, replay all 576 ticks, inspect Decider decisions in real time, and view the live telemetry dashboard.

*HAMEAU proves that deep multi-agent simulations don't require deep pockets. Just local intelligence, and a village that remembers what matters.*
