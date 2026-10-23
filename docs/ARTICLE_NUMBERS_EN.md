# Key Performance Indicators & Claims — HAMEAU Project

*Official reference data generated from verified run log [`runs/run_real_3j.jsonl`](../runs/run_real_3j.jsonl) on 2026-10-22.*

## 1. Executive Summary Table

| Metric | Measured Value | Unit / Note |
| :--- | :--- | :--- |
| **Population** | 20 | Canonical agents in Hameau village |
| **Simulated Duration** | 3 days (576 ticks) | 5 minutes per tick (6:00 to 22:00 daily) |
| **Wall-Clock Duration** | 16616.0 s (276.9 min) | 5538.7 s per simulated day |
| **Decider Questions ($Q$)** | **13,467** | D1–D9 evaluated by Strands Decider 2B |
| **Decider Requests ($R$)** | **8,206** | GPU inference calls after prefix-sharing |
| **Amazon Bedrock Calls ($L$)** | **659** | 100% live calls to `amazon.nova-micro-v1:0` |
| **Decider / LLM Ratio ($Q / L$)** | **20.44 : 1** | Target > 20:1 exceeded |
| **Decider / LLM Request Ratio ($R / L$)** | **12.45 : 1** | Decider requests per generative LLM call |
| **Decider Latency (p50 / p95)** | **1403.57 ms / 4348.15 ms** | Measured on RTX 3050 Laptop GPU |
| **Bedrock Latency (p50 / p95)** | **746.02 ms / 1224.4 ms** | Amazon Nova Micro (us-east-1) |
| **MemoryGate Token Savings** | **-23.05 %** | 580,162 gated vs 753,965 raw tokens |
| **AWS Total Cost** | **$0.01194 USD** | 278,661 total tokens processed |
| **Election Turnout (D9)** | **45.0 %** | 8 cast ballots, tie broken by incumbency (Kofi) |

## 2. Text Snippets for Builder Center Article

```markdown
In our 3-day benchmark with 20 autonomous villagers, the hybrid architecture processed
13,467 cognitive decisions (8,206 GPU inference requests) using Strands Decider 2B,
while dispatching only 659 generation calls to Amazon Bedrock Nova Micro.
This yields a decision-to-generation ratio of 20.44:1, keeping total AWS inference
costs under $0.02 ($0.01194) for 278,661 generated tokens.
MemoryGate trimmed prompt overhead by 23.05%, selecting only the top-3 relevant memories
per interaction.
```
