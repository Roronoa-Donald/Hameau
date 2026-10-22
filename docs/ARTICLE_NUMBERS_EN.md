# Key Performance Indicators & Claims — HAMEAU Project

*Official reference data generated from verified run log [`runs/real_final_3j.jsonl`](../runs/real_final_3j.jsonl) on 2026-10-22.*

## 1. Executive Summary Table

| Metric | Measured Value | Unit / Note |
| :--- | :--- | :--- |
| **Population** | 20 | Canonical agents in Hameau village |
| **Simulated Duration** | 3 days (576 ticks) | 5 minutes per tick (6:00 to 22:00 daily) |
| **Wall-Clock Duration** | 1965.4 s (32.8 min) | 655.1 s per simulated day |
| **Decider Questions ($Q$)** | **13,351** | D1–D9 evaluated by Strands Decider 2B |
| **Decider Requests ($R$)** | **8,122** | GPU inference calls after prefix-sharing |
| **Amazon Bedrock Calls ($L$)** | **655** | 100% live calls to `amazon.nova-micro-v1:0` |
| **Decider / LLM Ratio ($Q / L$)** | **20.38 : 1** | Target > 20:1 exceeded |
| **Decider / LLM Request Ratio ($R / L$)** | **12.4 : 1** | Decider requests per generative LLM call |
| **Decider Latency (p50 / p95)** | **124.31 ms / 411.59 ms** | Measured on RTX 3050 Laptop GPU |
| **Bedrock Latency (p50 / p95)** | **755.08 ms / 1041.8 ms** | Amazon Nova Micro (us-east-1) |
| **MemoryGate Token Savings** | **-22.99 %** | 573,854 gated vs 745,167 raw tokens |
| **AWS Total Cost** | **$0.01184 USD** | 275,632 total tokens processed |
| **Election Turnout (D9)** | **40.0 %** | 8 cast ballots, tie broken by incumbency (Kofi) |

## 2. Text Snippets for Builder Center Article

```markdown
In our 3-day benchmark with 20 autonomous villagers, the hybrid architecture processed
13,351 cognitive decisions (8,122 GPU inference requests) using Strands Decider 2B,
while dispatching only 655 generation calls to Amazon Bedrock Nova Micro.
This yields a decision-to-generation ratio of 20.38:1, keeping total AWS inference
costs under $0.02 ($0.01184) for 275,632 generated tokens.
MemoryGate trimmed prompt overhead by 22.99%, selecting only the top-3 relevant memories
per interaction.
```
