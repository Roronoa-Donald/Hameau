# HAMEAU — Official Hackathon Demo Video Guide (< 3 Minutes)

**Video Title:** HAMEAU: Multi-Agent Village Simulation with Strands Decider 2B & Amazon Bedrock  
**Target Duration:** 2 minutes 58 seconds (178 seconds) — *Strictly under the 3-minute hackathon limit*  
**Hackathon Tags:** `#strands-decider-2b`, `#context-memory`  
**Video Hosting URL:** `https://youtu.be/EXAMPLE_HAMEAU_DEMO` *(Replace with your uploaded public video URL)*  

---

## 1. Video Overview & Hackathon Rubric Alignment

This video demonstrates the working HAMEAU agent system, focusing on:
1. **The Core Innovation (30% Creativity & Cool Factor):** 20 autonomous villagers living, working, gossiping, and holding an election over 72 simulated hours.
2. **Effective Use of Decider 2B (30%):** Demonstrating the cognitive split where 13,467 micro-decisions run locally on a laptop GPU, and only 659 dialogues reach Amazon Bedrock Nova Micro.
3. **The Reusable Pattern (`#context-memory`):** Showing MemoryGate actively pruning memory clutter with Decider 2B (D3), reducing context tokens by 23.05%.
4. **Communication Quality (25%):** Clear, professional English narration synchronized with live visualizer screencasts, inspection panels, and verified telemetry.

---

## 2. Timed Scene Breakdown & Visual Storyboard

| Timestamp | Scene Name | Visual Display / Visualizer Screen | Spoken Focus |
| :--- | :--- | :--- | :--- |
| **0:00 – 0:18** | **The Bottleneck** | Motion graphics: 20 agent nodes, escalating LLM cost curve vs HAMEAU flat curve. | The cost and context bottleneck of traditional generative agents. |
| **0:19 – 0:43** | **The Cognitive Split** | Dual pipeline diagram: Local GPU (Decider 2B) vs AWS Cloud (Amazon Nova Micro). | Offloading high-frequency micro-decisions to Decider 2B; reserving Bedrock for dialogues. |
| **0:44 – 1:08** | **The Living Village** | Visualizer 2D Map (`http://localhost:8000`): 20 villagers moving, Day/Night lighting cycle. | 20 unique agents over 72 hours (576 ticks) with organic emergent behaviors. |
| **1:09 – 1:36** | **Decider in Action (D1)** | Agent Inspector: Awa the baker at Tick 397 (Day 3, 07:05). 5 options, 0.57 green zone confidence, 1,244 ms latency. | Step-by-step breakdown of a Decider 2B forward pass and calibrated confidence safety fallbacks. |
| **1:37 – 2:03** | **MemoryGate (#context-memory)** | MemoryGate Diff panel: 10 raw memories pruned to Top-3 using D3 relevance scoring. | The composite scoring formula and the -23.05% context token reduction before Bedrock calls. |
| **2:04 – 2:29** | **Social Dynamics & Election** | Rumor propagation curve (R1) & Municipal Election (D9) at Tick 516 (Kofi 5, Victor 4, Abstentions 11). | Real-time social transmission, emergent panic buying, and democratic municipal election. |
| **2:30 – 2:48** | **Verified Run Telemetry** | Telemetry Bento Grid: 13,467 Decider questions, 659 Bedrock calls, $0.01194 total cloud bill. | Empirical verification, 20.44:1 decision ratio, and reproducible audit logs. |
| **2:49 – 2:58** | **Conclusion & Takeaway** | Dusk over the village pixel-art map with project credits and GitHub link. | *"A village that remembers what matters."* Public repo under Apache-2.0. |

---

## 3. Complete English Voiceover Script (Word-for-Word)

```text
[0:00 - 0:18]
Simulating a living society of twenty autonomous AI agents for three simulated days usually requires millions of LLM tokens and hundreds of dollars in cloud API calls. Most architectures break under the cost of constant routine micro-decisions.

[0:19 - 0:43]
HAMEAU solves this through a strict cognitive split. High-frequency micro-decisions—navigation, routine chores, and memory relevance—run entirely on a modest laptop GPU using a specialized two-billion-parameter Small Language Model: Decider 2B. The cloud is reserved exclusively for rich conversational dialogue through Amazon Bedrock Nova Micro.

[0:44 - 1:08]
Over seventy-two simulated hours and five hundred and seventy-six ticks, twenty unique villagers go about their lives in real time. They wake up, discuss morning gossip, work their trades, and react to emergent village events—all without scripted behavior.

[1:09 - 1:36]
Here, at tick thirteen on Day Three, Awa the baker decides her next action. Decider 2B evaluates five distinct options in twelve hundred and forty-four milliseconds. With a fifty-seven percent confidence score, well within the calibrated green zone, she chooses to go to the market square. If confidence had dropped below thirty percent, a deterministic safety fallback would have taken over automatically.

[1:37 - 2:03]
This is the essence of our context-memory pattern. Instead of stuffing every past interaction into Bedrock's prompt, our local MemoryGate evaluates candidate memories on the fly. Decider 2B scores the contextual relevance of each memory before pruning the pool down to the top three. Across three days, this eliminated over one hundred and seventy-three thousand tokens—a twenty-three percent reduction in context bloat.

[2:04 - 2:29]
Social dynamics unfold organically. When a rumor about market closures spreads from Yao, panic buying begins until the mayor intervenes. And by Saturday morning, the village holds a municipal election. Twenty citizens cast their votes through Decider template D9. Kofi is re-elected five to four, with eleven abstentions, including five citizens whose confidence was too low to decide.

[2:30 - 2:48]
Every single metric is logged and verifiable. Thirteen thousand four hundred and sixty-seven local decisions. Six hundred and fifty-nine live calls to Amazon Nova Micro. Total AWS cloud cost for seventy-two hours of living simulation: one point nineteen cents.

[2:49 - 2:58]
HAMEAU proves that deep multi-agent simulations don't require deep pockets. Just local intelligence, and a village that remembers what matters.
```

---

## 4. How to Record the Visualizer Screencasts

To capture the footage needed for the video:
1. Run `./start.sh` in the terminal.
2. Open `http://localhost:8000` in Google Chrome or Firefox (1920x1080 resolution).
3. Use the playback controls at the top of the interface:
   - Click **Play (►)** and adjust speed to **2x** or **5x** to capture the bustling village and day-night cycle.
   - Click on **Awa** in the character list or on the map to open the Inspector panel at tick 397 (Day 3, 07:05).
   - Switch to the **MemoryGate Diff** tab to capture the memory pruning demonstration.
   - Switch to the **Analytics / Telemetry** tab to display the verified counters and cost scoreboard.
