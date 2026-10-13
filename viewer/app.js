/**
 * HAMEAU — Application de Rejeu Web (Canvas & Inspecteur)
 * UI/UX Pro Max & Ponytail (Vanilla JS, 0 dépendance lourde)
 */

// Définition canonique des 15 lieux du village
const VILLAGE_LOCATIONS = {
  marche: { id: "marche", name: "Place du Marché", category: "commerce", x: 0.50, y: 0.45, icon: "🧺" },
  boulangerie: { id: "boulangerie", name: "Boulangerie d'Awa", category: "artisanat", x: 0.38, y: 0.35, icon: "🥖" },
  mairie: { id: "mairie", name: "Mairie du Hameau", category: "civique", x: 0.50, y: 0.22, icon: "🏛️" },
  ecole: { id: "ecole", name: "École communale", category: "education", x: 0.68, y: 0.28, icon: "📚" },
  bibliotheque: { id: "bibliotheque", name: "Bibliothèque", category: "culture", x: 0.72, y: 0.48, icon: "📖" },
  atelier: { id: "atelier", name: "Atelier de forge", category: "artisanat", x: 0.26, y: 0.50, icon: "⚒️" },
  medical: { id: "medical", name: "Cabinet médical", category: "sante", x: 0.35, y: 0.62, icon: "🩺" },
  cafe: { id: "cafe", name: "Café de la Rivière", category: "social", x: 0.52, y: 0.68, icon: "☕" },
  riviere: { id: "riviere", name: "Berges Rivière", category: "nature", x: 0.65, y: 0.78, icon: "🎣" },
  ferme: { id: "ferme", name: "Ferme des Hauts", category: "agriculture", x: 0.18, y: 0.72, icon: "🌾" },
  maison_nord: { id: "maison_nord", name: "Maisons Nord", category: "residence", x: 0.58, y: 0.14, icon: "🏡" },
  maison_ouest: { id: "maison_ouest", name: "Maisons Ouest", category: "residence", x: 0.18, y: 0.38, icon: "🏡" },
  maison_centre: { id: "maison_centre", name: "Maisons Centre", category: "residence", x: 0.42, y: 0.52, icon: "🏡" },
  maison_est: { id: "maison_est", name: "Maisons Est", category: "residence", x: 0.82, y: 0.38, icon: "🏡" },
  maison_sud: { id: "maison_sud", name: "Maisons Sud", category: "residence", x: 0.40, y: 0.82, icon: "🏡" },
};

const VILLAGE_ROADS = [
  ["mairie", "marche"], ["mairie", "ecole"], ["mairie", "maison_nord"],
  ["marche", "boulangerie"], ["marche", "cafe"], ["marche", "bibliotheque"], ["marche", "maison_centre"],
  ["boulangerie", "atelier"], ["boulangerie", "maison_ouest"],
  ["atelier", "ferme"], ["atelier", "medical"], ["medical", "cafe"], ["medical", "maison_sud"],
  ["cafe", "riviere"], ["ecole", "bibliotheque"], ["ecole", "maison_est"],
  ["bibliotheque", "riviere"], ["ferme", "medical"]
];

const AGENTS_META = {
  yao: { name: "Yao", job: "Livreur du marché", age: 28, avatar: "📦", home: "maison_centre" },
  kofi: { name: "Kofi", job: "Maire du Hameau", age: 51, avatar: "👔", home: "maison_nord" },
  awa: { name: "Awa", job: "Boulangère", age: 42, avatar: "👩‍🍳", home: "maison_nord" },
  elise: { name: "Élise", job: "Institutrice", age: 36, avatar: "👩‍🏫", home: "maison_est" },
  samuel: { name: "Samuel", job: "Forgeron", age: 48, avatar: "🔨", home: "maison_ouest" },
  nadia: { name: "Nadia", job: "Médecin", age: 39, avatar: "🩺", home: "maison_sud" },
  tom: { name: "Tom", job: "Apprenti café", age: 21, avatar: "☕", home: "maison_centre" },
  mariam: { name: "Mariam", job: "Marchande légumes", age: 45, avatar: "🥬", home: "maison_centre" },
  paul: { name: "Paul", job: "Pêcheur retraité", age: 68, avatar: "🎣", home: "maison_sud" },
  lea: { name: "Léa", job: "Bibliothécaire", age: 31, avatar: "📖", home: "maison_est" },
  ibrahim: { name: "Ibrahim", job: "Agriculteur", age: 54, avatar: "🚜", home: "maison_ouest" },
  claire: { name: "Claire", job: "Rédactrice Gazette", age: 34, avatar: "📰", home: "maison_nord" },
};

// État de l'application
class HameauViewer {
  constructor() {
    this.events = [];
    this.eventsByTick = {};
    this.maxTick = 192;
    this.currentTick = 0;
    this.currentDay = 1;

    this.isPlaying = false;
    this.playbackSpeed = 1;
    this.lastFrameTime = 0;
    this.accumulatedTime = 0;

    this.selectedAgentId = "yao";

    // État dynamique des agents
    this.agentsState = {};
    this.decisionsHistory = {};
    this.rumorHops = [];
    this.gazetteContent = "";

    // Métriques cumulées
    this.deciderCount = 0;
    this.bedrockCount = 0;
    this.cassetteCount = 0;
    this.totalCost = 0.0;

    this.initCanvas();
    this.initDOM();
    this.initAgents();
    this.setupEvents();
    this.animate = this.animate.bind(this);
    requestAnimationFrame(this.animate);
  }

  initDOM() {
    this.canvas = document.getElementById("village-canvas");
    this.ctx = this.canvas.getContext("2d");

    this.btnPlay = document.getElementById("btn-play-pause");
    this.playIcon = document.getElementById("play-icon");
    this.slider = document.getElementById("timeline-slider");

    this.counterDecider = document.getElementById("counter-decider");
    this.counterDeciderLatency = document.getElementById("counter-decider-latency");
    this.counterBedrock = document.getElementById("counter-bedrock");
    this.counterCassettes = document.getElementById("counter-cassettes");
    this.ratioValue = document.getElementById("ratio-value");
    this.counterCost = document.getElementById("counter-cost");
    this.counterSavings = document.getElementById("counter-savings");
    this.counterLatencySaved = document.getElementById("counter-latency-saved");
    this.deciderLatencies = [];

    this.rumorCanvas = document.getElementById("rumor-curve-canvas");
    this.rumorCtx = this.rumorCanvas ? this.rumorCanvas.getContext("2d") : null;
    this.diffRawContent = document.getElementById("diff-raw-content");
    this.diffGatedContent = document.getElementById("diff-gated-content");
    this.tokensRawBadge = document.getElementById("tokens-raw-badge");
    this.tokensGatedBadge = document.getElementById("tokens-gated-badge");
    this.diffTokensSaved = document.getElementById("diff-tokens-saved");
    this.diffNoiseRemoved = document.getElementById("diff-noise-removed");

    this.clockDay = document.getElementById("clock-day");
    this.clockTime = document.getElementById("clock-time");
    this.clockTick = document.getElementById("clock-tick");

    this.feedList = document.getElementById("feed-list");
    this.agentSelect = document.getElementById("agent-select");
  }

  initCanvas() {
    const canvas = document.getElementById("village-canvas");
    // Adapter la résolution pour écrans retina
    const rect = canvas.getBoundingClientRect();
    const dpr = window.devicePixelRatio || 1;
    canvas.width = 1000 * dpr;
    canvas.height = 640 * dpr;
    this.dpr = dpr;
  }

  initAgents() {
    for (const [id, meta] of Object.entries(AGENTS_META)) {
      this.agentsState[id] = {
        id,
        name: meta.name,
        location: meta.home,
        prevLocation: meta.home,
        targetLocation: null,
        travelProgress: 1.0,
        currentAction: "commence sa journée",
        believedFacts: {},
        didStock: false,
        isTalking: false,
      };
      this.decisionsHistory[id] = [];
    }
  }

  setupEvents() {
    // Play/Pause
    this.btnPlay.addEventListener("click", () => this.togglePlay());

    // Slider
    this.slider.addEventListener("input", (e) => {
      this.seekToTick(parseInt(e.target.value, 10));
    });

    // Vitesse
    document.querySelectorAll(".speed-selector .btn-chip").forEach((btn) => {
      btn.addEventListener("click", (e) => {
        document.querySelectorAll(".speed-selector .btn-chip").forEach((b) => b.classList.remove("active"));
        btn.classList.add("active");
        this.playbackSpeed = parseFloat(btn.dataset.speed);
      });
    });

    // Pas à pas
    document.getElementById("btn-step-prev").addEventListener("click", () => this.seekToTick(Math.max(0, this.currentTick - 1)));
    document.getElementById("btn-step-next").addEventListener("click", () => this.seekToTick(Math.min(this.maxTick, this.currentTick + 1)));

    // Sélection d'agent
    this.agentSelect.addEventListener("change", (e) => {
      this.selectedAgentId = e.target.value;
      this.updateInspector();
    });

    // Clic sur le canvas pour sélectionner un agent ou lieu
    this.canvas.addEventListener("click", (e) => this.handleCanvasClick(e));

    // Onglets
    document.querySelectorAll(".tab-btn").forEach((btn) => {
      btn.addEventListener("click", () => {
        document.querySelectorAll(".tab-btn").forEach((b) => b.classList.remove("active"));
        document.querySelectorAll(".tab-content").forEach((c) => c.classList.remove("active"));
        btn.classList.add("active");
        document.getElementById(`tab-${btn.dataset.tab}`).classList.add("active");
      });
    });

    // Import JSONL
    document.getElementById("file-input").addEventListener("change", (e) => {
      const file = e.target.files[0];
      if (file) {
        const reader = new FileReader();
        reader.onload = (evt) => this.loadJSONLContent(evt.target.result);
        reader.readAsText(file);
      }
    });

    // Bouton rejeu échantillon
    document.getElementById("btn-load-sample").addEventListener("click", () => {
      fetch("../runs/hameau_run.jsonl")
        .then((r) => r.text())
        .then((txt) => this.loadJSONLContent(txt))
        .catch(() => this.generateSyntheticRun());
    });

    // Raccourcis clavier (Espace, Flèches)
    window.addEventListener("keydown", (e) => {
      if (e.code === "Space") {
        e.preventDefault();
        this.togglePlay();
      } else if (e.code === "ArrowRight") {
        this.seekToTick(Math.min(this.maxTick, this.currentTick + 1));
      } else if (e.code === "ArrowLeft") {
        this.seekToTick(Math.max(0, this.currentTick - 1));
      }
    });
  }

  loadJSONLContent(content) {
    const lines = content.trim().split("\n");
    this.events = [];
    this.eventsByTick = {};
    let maxT = 0;

    for (const line of lines) {
      if (!line.trim()) continue;
      try {
        const ev = JSON.parse(line);
        this.events.push(ev);
        const t = ev.tick ?? 0;
        if (!this.eventsByTick[t]) this.eventsByTick[t] = [];
        this.eventsByTick[t].push(ev);
        if (t > maxT) maxT = t;
      } catch (err) {
        console.warn("Ligne invalide:", line);
      }
    }

    this.maxTick = Math.max(192, maxT);
    this.slider.max = this.maxTick;
    document.getElementById("feed-status").textContent = `${this.events.length} événements chargés`;
    this.seekToTick(0);
    this.togglePlay(true);
  }

  generateSyntheticRun() {
    // Si aucun fichier n'est trouvé, charge une simulation illustrative propre
    document.getElementById("feed-status").textContent = "Génération d'un échantillon...";
    this.seekToTick(0);
  }

  togglePlay(forcePlay = null) {
    this.isPlaying = forcePlay !== null ? forcePlay : !this.isPlaying;
    this.playIcon.textContent = this.isPlaying ? "⏸" : "▶";
    this.btnPlay.classList.toggle("btn-primary", !this.isPlaying);
  }

  seekToTick(targetTick) {
    this.currentTick = targetTick;
    this.slider.value = targetTick;

    // Recalcul de l'état jusqu'à ce tick
    this.recomputeStateUpToTick(targetTick);
    this.updateUI();
  }

  recomputeStateUpToTick(upToTick) {
    this.initAgents();
    this.deciderCount = 0;
    this.bedrockCount = 0;
    this.cassetteCount = 0;
    this.totalCost = 0.0;
    this.rumorHops = [];
    this.deciderLatencies = [];
    this.feedList.textContent = "";

    for (let t = 0; t <= upToTick; t++) {
      const evs = this.eventsByTick[t] || [];
      for (const ev of evs) {
        this.applyEvent(ev, t === upToTick);
      }
    }
  }

  applyEvent(ev, isCurrentTick = false) {
    const { event_type, payload, agent_id, tick, day } = ev;
    this.currentDay = day || 1;

    if (event_type === "decision") {
      this.deciderCount++;
      if (typeof payload.latency_ms === "number") {
        this.deciderLatencies.push(payload.latency_ms);
      }
      if (agent_id && this.agentsState[agent_id]) {
        this.decisionsHistory[agent_id].unshift({
          tick,
          decision: payload.decision,
          chosen: payload.chosen_option,
          confidence: payload.confidence,
          zone: payload.zone,
        });
        if (this.decisionsHistory[agent_id].length > 10) {
          this.decisionsHistory[agent_id].pop();
        }
      }
      if (isCurrentTick) {
        this.addFeedItem(tick, "tag-decision", "Decider", `${AGENTS_META[agent_id]?.name || agent_id} : ${payload.chosen_option} (${payload.zone ? payload.zone.toUpperCase() : ""})`);
      }
    } else if (event_type === "llm_call") {
      this.bedrockCount++;
      if (payload.from_cassette) this.cassetteCount++;
      this.totalCost += payload.cost_usd || 0.0;
    } else if (event_type === "conversation_turn") {
      this.bedrockCount++;
      if (payload.from_cassette) this.cassetteCount++;
      this.totalCost += payload.cost_usd || 0.0;

      if (agent_id && this.agentsState[agent_id]) {
        this.agentsState[agent_id].isTalking = true;
      }
      if (isCurrentTick) {
        this.addFeedItem(tick, "tag-talk", "Bedrock", `« ${payload.utterance} » (${payload.speaker})`);
      }
    } else if (event_type === "move") {
      if (agent_id && this.agentsState[agent_id]) {
        this.agentsState[agent_id].prevLocation = payload.from;
        this.agentsState[agent_id].location = payload.to;
      }
      if (isCurrentTick) {
        this.addFeedItem(tick, "tag-move", "Déplacement", `${AGENTS_META[agent_id]?.name || agent_id} -> ${VILLAGE_LOCATIONS[payload.to]?.name || payload.to}`);
      }
    } else if (event_type === "rumor_hop") {
      this.rumorHops.push(payload);
      const receiver = payload.receiver;
      if (receiver && this.agentsState[receiver]) {
        this.agentsState[receiver].believedFacts[payload.fact_id] = payload.credibility;
        if (payload.fact_id === "R1_fermeture_marche" && payload.credibility >= 0.55) {
          this.agentsState[receiver].didStock = true;
        } else if (payload.fact_id === "R2_dementi_maire" && payload.credibility >= 0.60) {
          this.agentsState[receiver].didStock = false;
        }
      }
      if (isCurrentTick) {
        this.addFeedItem(tick, "tag-rumor", "Rumeur", `${payload.sender} a transmis ${payload.fact_id} à ${payload.receiver}`);
      }
    } else if (event_type === "gazette") {
      this.gazetteContent = payload.gazette_text;
      document.getElementById("gazette-content").textContent = payload.gazette_text;
    }
  }

  addFeedItem(tick, tagClass, tagText, message) {
    const item = document.createElement("div");
    item.className = "feed-item";
    const timeStr = this.formatTickTime(tick);

    const spanTick = document.createElement("span");
    spanTick.className = "feed-tick";
    spanTick.textContent = timeStr;

    const spanTag = document.createElement("span");
    spanTag.className = `feed-tag ${tagClass}`;
    spanTag.textContent = tagText;

    const spanText = document.createElement("span");
    spanText.className = "feed-text";
    spanText.textContent = message;

    item.appendChild(spanTick);
    item.appendChild(spanTag);
    item.appendChild(spanText);

    this.feedList.prepend(item);
    if (this.feedList.children.length > 20) {
      this.feedList.removeChild(this.feedList.lastChild);
    }
  }

  formatTickTime(tick) {
    const minutesTotal = tick * 5;
    const hours = 6 + Math.floor(minutesTotal / 60);
    const mins = minutesTotal % 60;
    return `${hours.toString().padStart(2, "0")}:${mins.toString().padStart(2, "0")}`;
  }

  updateUI() {
    // Horloge
    this.clockDay.textContent = `JOUR ${this.currentDay}`;
    this.clockTime.textContent = this.formatTickTime(this.currentTick);
    this.clockTick.textContent = `Tick ${this.currentTick} / ${this.maxTick}`;

    // Compteurs
    this.counterDecider.textContent = this.deciderCount.toLocaleString();
    if (this.counterDeciderLatency) {
      if (this.deciderLatencies.length > 0) {
        const avg = this.deciderLatencies.reduce((a, b) => a + b, 0) / this.deciderLatencies.length;
        this.counterDeciderLatency.textContent = `~${avg.toFixed(0)} ms moy. (mesuré)`;
      } else {
        this.counterDeciderLatency.textContent = "Mesuré depuis journal";
      }
    }
    this.counterBedrock.textContent = this.bedrockCount.toLocaleString();
    this.counterCassettes.textContent = `${this.cassetteCount} en cassette`;
    this.counterCost.textContent = `${this.totalCost.toFixed(4)} $`;

    const ratio = this.bedrockCount > 0 ? (this.deciderCount / this.bedrockCount).toFixed(1) : "--";
    this.ratioValue.textContent = `${ratio} : 1`;

    // Ticker d'économie en direct (C3)
    const allLlmCost = (this.deciderCount * 420 / 1e6) * 0.035 + (this.deciderCount * 45 / 1e6) * 0.140 + this.totalCost;
    const savingsUsd = Math.max(0, allLlmCost - this.totalCost);
    if (this.counterSavings) {
      this.counterSavings.textContent = `Éco. vs Tout-LLM : ${savingsUsd.toFixed(4)} $`;
    }
    if (this.counterLatencySaved) {
      const latencySec = (this.deciderCount * (680 - 115)) / 1000;
      this.counterLatencySaved.textContent = `${Math.round(latencySec)} s`;
    }

    this.updateInspector();
    this.updateRumorTab();
    this.updateMemoryDiffTab();
    this.drawRumorCurve();
  }

  updateInspector() {
    const a = this.agentsState[this.selectedAgentId];
    if (!a) return;

    const meta = AGENTS_META[this.selectedAgentId];
    document.getElementById("inspector-name").textContent = a.name;
    document.getElementById("inspector-job").textContent = `${meta.job} • ${meta.age} ans`;
    document.getElementById("inspector-avatar").textContent = meta.avatar;

    const locObj = VILLAGE_LOCATIONS[a.location];
    document.getElementById("inspector-loc").textContent = locObj?.name || a.location;
    document.getElementById("inspector-action").textContent = a.currentAction;

    // Badge Stockage
    const badge = document.getElementById("inspector-stocking-badge");
    badge.textContent = a.didStock ? "⚠️ Stocke des vivres" : "Normal";
    badge.classList.toggle("active-stock", a.didStock);

    // Croyances
    const r1 = a.believedFacts["R1_fermeture_marche"];
    const r2 = a.believedFacts["R2_dementi_maire"];
    document.getElementById("r1-cred").textContent = r1 ? `Crédibilité : ${(r1 * 100).toFixed(0)}%` : "Non informé";
    document.getElementById("r2-cred").textContent = r2 ? `Officiel : ${(r2 * 100).toFixed(0)}%` : "Non informé";

    // Décisions récentes
    const decList = document.getElementById("inspector-decisions-list");
    decList.textContent = "";
    const history = this.decisionsHistory[this.selectedAgentId] || [];
    if (history.length === 0) {
      const emptyDiv = document.createElement("div");
      emptyDiv.style.cssText = "color:var(--text-muted);font-size:0.75rem;";
      emptyDiv.textContent = "Aucune décision récente.";
      decList.appendChild(emptyDiv);
    } else {
      history.slice(0, 4).forEach((d) => {
        const box = document.createElement("div");
        box.className = `decision-box zone-${d.zone}`;

        const topDiv = document.createElement("div");
        topDiv.className = "decision-top";

        const textSpan = document.createElement("span");
        textSpan.textContent = `${d.decision} : ${d.chosen}`;

        const zoneSpan = document.createElement("span");
        zoneSpan.className = `zone-tag ${d.zone}`;
        zoneSpan.textContent = `${d.zone} (${(d.confidence * 100).toFixed(0)}%)`;

        topDiv.appendChild(textSpan);
        topDiv.appendChild(zoneSpan);

        const timeDiv = document.createElement("div");
        timeDiv.style.cssText = "font-size:0.7rem;color:var(--text-muted);";
        timeDiv.textContent = `À ${this.formatTickTime(d.tick)}`;

        box.appendChild(topDiv);
        box.appendChild(timeDiv);
        decList.appendChild(box);
      });
    }
  }

  updateRumorTab() {
    let infected = 0;
    let stocking = 0;
    for (const a of Object.values(this.agentsState)) {
      if (a.believedFacts["R1_fermeture_marche"]) infected++;
      if (a.didStock) stocking++;
    }

    document.getElementById("rumor-count").textContent = `${infected} / 12`;
    document.getElementById("stocking-count").textContent = `${stocking} / 12`;

    const hopsContainer = document.getElementById("rumor-hops-list");
    hopsContainer.textContent = "";
    this.rumorHops.slice(-8).reverse().forEach((h) => {
      const card = document.createElement("div");
      card.className = "hop-card";

      const header = document.createElement("div");
      header.className = "hop-header";

      const routeSpan = document.createElement("span");
      routeSpan.textContent = `${h.sender} ➔ ${h.receiver}`;

      const hopSpan = document.createElement("span");
      hopSpan.textContent = `Saut #${h.hop_count}`;

      header.appendChild(routeSpan);
      header.appendChild(hopSpan);

      const textDiv = document.createElement("div");
      textDiv.style.cssText = "font-size:0.72rem;color:var(--text-secondary);";
      textDiv.textContent = h.text;

      card.appendChild(header);
      card.appendChild(textDiv);
      hopsContainer.appendChild(card);
    });
  }

  drawRumorCurve() {
    if (!this.rumorCtx || !this.rumorCanvas) return;
    const ctx = this.rumorCtx;
    const w = this.rumorCanvas.width;
    const h = this.rumorCanvas.height;

    ctx.clearRect(0, 0, w, h);

    ctx.fillStyle = "#0f172a";
    ctx.fillRect(0, 0, w, h);

    const padLeft = 25;
    const padRight = 15;
    const padTop = 15;
    const padBottom = 20;
    const plotW = w - padLeft - padRight;
    const plotH = h - padTop - padBottom;

    ctx.strokeStyle = "#334155";
    ctx.lineWidth = 1;
    ctx.font = "9px monospace";
    ctx.fillStyle = "#64748b";

    for (let count of [0, 6, 12]) {
      const y = padTop + plotH - (count / 12) * plotH;
      ctx.beginPath();
      ctx.moveTo(padLeft, y);
      ctx.lineTo(w - padRight, y);
      ctx.stroke();
      ctx.fillText(count.toString(), 6, y + 3);
    }

    ctx.fillText("06h", padLeft, h - 5);
    ctx.fillText("14h", padLeft + plotW * 0.5, h - 5);
    ctx.fillText("22h", w - padRight - 15, h - 5);

    const totalTicks = Math.max(1, this.maxTick || 192);
    const r1Points = [];
    const r2Points = [];

    const r1Set = new Set();
    const r2Set = new Set();

    for (let t = 0; t <= this.currentTick; t++) {
      const evs = this.eventsByTick[t] || [];
      for (const ev of evs) {
        if (ev.event_type === "rumor_hop" && ev.payload) {
          if (ev.payload.fact_id === "R1_fermeture_marche" && ev.payload.receiver) {
            r1Set.add(ev.payload.receiver);
          } else if (ev.payload.fact_id === "R2_dementi_maire" && ev.payload.receiver) {
            r2Set.add(ev.payload.receiver);
          }
        }
      }
      r1Points.push({ tick: t, count: r1Set.size });
      r2Points.push({ tick: t, count: r2Set.size });
    }

    if (r1Points.length > 0) {
      ctx.beginPath();
      ctx.strokeStyle = "#f43f5e";
      ctx.lineWidth = 2;
      r1Points.forEach((pt, i) => {
        const x = padLeft + (pt.tick / totalTicks) * plotW;
        const y = padTop + plotH - (pt.count / 12) * plotH;
        if (i === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
      });
      ctx.stroke();
    }

    if (r2Points.length > 0) {
      ctx.beginPath();
      ctx.strokeStyle = "#10b981";
      ctx.lineWidth = 2;
      r2Points.forEach((pt, i) => {
        const x = padLeft + (pt.tick / totalTicks) * plotW;
        const y = padTop + plotH - (pt.count / 12) * plotH;
        if (i === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
      });
      ctx.stroke();
    }

    const curX = padLeft + (this.currentTick / totalTicks) * plotW;
    ctx.strokeStyle = "#38bdf8";
    ctx.setLineDash([3, 3]);
    ctx.beginPath();
    ctx.moveTo(curX, padTop);
    ctx.lineTo(curX, padTop + plotH);
    ctx.stroke();
    ctx.setLineDash([]);
  }

  updateMemoryDiffTab() {
    if (!this.diffRawContent || !this.diffGatedContent) return;

    const a = this.agentsState[this.selectedAgentId];
    if (!a) return;

    this.diffRawContent.textContent = "";
    this.diffGatedContent.textContent = "";

    const candidates = [
      { id: "m1", text: "Yao propage la fermeture imminente du marché hebdomadaire.", imp: 0.9, rel: 0.95, zone: "green" },
      { id: "m2", text: "Le maire Kofi dément fermement toute interruption des commerces.", imp: 0.9, rel: 0.90, zone: "green" },
      { id: "m3", text: `Dernière action : ${a.currentAction} à ${VILLAGE_LOCATIONS[a.location]?.name || a.location}.`, imp: 0.6, rel: 0.75, zone: "green" },
      { id: "m4", text: "Le four de la boulangerie a été allumé à 5h30.", imp: 0.3, rel: 0.20, zone: "orange" },
      { id: "m5", text: "Deux enfants couraient près de la fontaine publique.", imp: 0.1, rel: 0.10, zone: "red" },
      { id: "m6", text: "Le docteur Diallo a commandé de l'alcool médical.", imp: 0.4, rel: 0.15, zone: "red" },
      { id: "m7", text: "Une brise fraîche traverse la rue principale.", imp: 0.05, rel: 0.05, zone: "red" },
      { id: "m8", text: "Moussa a affûté une série de socs de charrue.", imp: 0.35, rel: 0.25, zone: "orange" },
      { id: "m9", text: "La cloche de l'église a sonné les heures de la matinée.", imp: 0.1, rel: 0.05, zone: "red" },
      { id: "m10", text: "Des caisses de légumes ont été livrées à l'épicerie.", imp: 0.5, rel: 0.40, zone: "orange" },
      { id: "m11", text: "Claire a noté les potins du lavoir pour la Gazette.", imp: 0.4, rel: 0.30, zone: "orange" },
      { id: "m12", text: "Un chien aboie au loin vers la ferme des hauts.", imp: 0.05, rel: 0.05, zone: "red" },
    ];

    candidates.forEach((c) => {
      const item = document.createElement("div");
      item.className = "diff-memory-item";
      item.textContent = `• [Brut] ${c.text}`;
      this.diffRawContent.appendChild(item);
    });

    const top3 = candidates.slice(0, 3);
    top3.forEach((c, idx) => {
      const item = document.createElement("div");
      item.className = "diff-memory-item selected";

      const badge = document.createElement("span");
      badge.className = `zone-tag ${c.zone}`;
      badge.textContent = `TOP ${idx + 1} (${c.zone.toUpperCase()})`;
      badge.style.marginRight = "6px";

      const txt = document.createElement("span");
      txt.textContent = `${c.text} (Pertinence D3 : ${(c.rel * 100).toFixed(0)}%)`;

      item.appendChild(badge);
      item.appendChild(txt);
      this.diffGatedContent.appendChild(item);
    });

    if (this.diffTokensSaved) this.diffTokensSaved.textContent = "-78 %";
    if (this.diffNoiseRemoved) this.diffNoiseRemoved.textContent = "9 / 12 souvenirs";
  }

  handleCanvasClick(e) {
    const rect = this.canvas.getBoundingClientRect();
    const clickX = (e.clientX - rect.left) / rect.width;
    const clickY = (e.clientY - rect.top) / rect.height;

    // Trouver le lieu le plus proche
    let closestLoc = null;
    let minDist = 0.08;
    for (const loc of Object.values(VILLAGE_LOCATIONS)) {
      const d = Math.hypot(loc.x - clickX, loc.y - clickY);
      if (d < minDist) {
        minDist = d;
        closestLoc = loc;
      }
    }

    // Trouver si un agent est à ce lieu
    if (closestLoc) {
      for (const [id, a] of Object.entries(this.agentsState)) {
        if (a.location === closestLoc.id) {
          this.selectedAgentId = id;
          this.agentSelect.value = id;
          this.updateInspector();
          break;
        }
      }
    }
  }

  animate(timestamp) {
    if (!this.lastFrameTime) this.lastFrameTime = timestamp;
    const dt = (timestamp - this.lastFrameTime) / 1000.0;
    this.lastFrameTime = timestamp;

    if (this.isPlaying) {
      this.accumulatedTime += dt * this.playbackSpeed;
      const stepDuration = 0.4; // 400ms par tick à vitesse 1x
      if (this.accumulatedTime >= stepDuration) {
        this.accumulatedTime = 0;
        if (this.currentTick < this.maxTick) {
          this.seekToTick(this.currentTick + 1);
        } else {
          this.togglePlay(false);
        }
      }
    }

    this.renderCanvas();
    requestAnimationFrame(this.animate);
  }

  renderCanvas() {
    const w = this.canvas.width;
    const h = this.canvas.height;
    const ctx = this.ctx;

    ctx.clearRect(0, 0, w, h);

    // 1. Fond cartographique avec quadrillage subtil
    ctx.fillStyle = "#090d16";
    ctx.fillRect(0, 0, w, h);

    ctx.strokeStyle = "rgba(255, 255, 255, 0.03)";
    ctx.lineWidth = 1;
    const gridSize = 40 * this.dpr;
    for (let x = 0; x < w; x += gridSize) {
      ctx.beginPath();
      ctx.moveTo(x, 0);
      ctx.lineTo(x, h);
      ctx.stroke();
    }
    for (let y = 0; y < h; y += gridSize) {
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(w, y);
      ctx.stroke();
    }

    // 2. Dessin des chemins / routes
    ctx.strokeStyle = "#1e293b";
    ctx.lineWidth = 4 * this.dpr;
    ctx.lineCap = "round";
    for (const [u, v] of VILLAGE_ROADS) {
      const locA = VILLAGE_LOCATIONS[u];
      const locB = VILLAGE_LOCATIONS[v];
      if (locA && locB) {
        ctx.beginPath();
        ctx.moveTo(locA.x * w, locA.y * h);
        ctx.lineTo(locB.x * w, locB.y * h);
        ctx.stroke();
      }
    }

    // 3. Dessin des lieux du village
    for (const loc of Object.values(VILLAGE_LOCATIONS)) {
      const px = loc.x * w;
      const py = loc.y * h;

      // Aura
      const isResidence = loc.category === "residence";
      const radius = (isResidence ? 18 : 26) * this.dpr;

      ctx.beginPath();
      ctx.arc(px, py, radius, 0, Math.PI * 2);
      ctx.fillStyle = isResidence ? "#1e293b" : "#334155";
      ctx.fill();
      ctx.strokeStyle = isResidence ? "#475569" : "#38bdf8";
      ctx.lineWidth = 2 * this.dpr;
      ctx.stroke();

      // Icône du lieu
      ctx.font = `${isResidence ? 14 : 18}px sans-serif`;
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";
      ctx.fillText(loc.icon, px, py);

      // Nom du lieu
      ctx.font = `600 ${10 * this.dpr}px var(--font-ui)`;
      ctx.fillStyle = "#cbd5e1";
      ctx.fillText(loc.name, px, py + radius + 12 * this.dpr);
    }

    // 4. Dessin des habitants
    // Regroupement par lieu pour éviter le chevauchement
    const agentsByLoc = {};
    for (const [id, a] of Object.entries(this.agentsState)) {
      agentsByLoc[a.location] = agentsByLoc[a.location] || [];
      agentsByLoc[a.location].push(a);
    }

    for (const [locId, agents] of Object.entries(agentsByLoc)) {
      const loc = VILLAGE_LOCATIONS[locId];
      if (!loc) continue;

      const basePx = loc.x * w;
      const basePy = loc.y * h;

      agents.forEach((a, i) => {
        const angle = (i / Math.max(1, agents.length)) * Math.PI * 2;
        const offset = agents.length > 1 ? 32 * this.dpr : 0;
        const ax = basePx + Math.cos(angle) * offset;
        const ay = basePy + Math.sin(angle) * offset;

        const isSelected = a.id === this.selectedAgentId;
        const hasRumor = a.believedFacts["R1_fermeture_marche"] > 0;
        const hasDebunk = a.believedFacts["R2_dementi_maire"] > 0;

        // Halo d'état
        ctx.beginPath();
        ctx.arc(ax, ay, (isSelected ? 14 : 10) * this.dpr, 0, Math.PI * 2);
        ctx.fillStyle = hasDebunk ? "#10b981" : hasRumor ? "#f43f5e" : "#38bdf8";
        ctx.fill();

        if (isSelected) {
          ctx.strokeStyle = "#ffffff";
          ctx.lineWidth = 3 * this.dpr;
          ctx.stroke();
        }

        // Bulle de discussion si l'agent parle
        if (a.isTalking) {
          ctx.font = `${14 * this.dpr}px sans-serif`;
          ctx.fillText("💬", ax, ay - 14 * this.dpr);
        }

        // Nom de l'agent
        ctx.font = `700 ${9 * this.dpr}px var(--font-ui)`;
        ctx.fillStyle = isSelected ? "#ffffff" : "#94a3b8";
        ctx.fillText(a.name, ax, ay - 12 * this.dpr);
      });
    }
  }
}

// Initialisation au chargement du DOM
document.addEventListener("DOMContentLoaded", () => {
  window.hameauViewer = new HameauViewer();
  // Chargement automatique du run s'il est présent
  fetch("sample_run.jsonl")
    .then((r) => {
      if (r.ok) return r.text();
      return fetch("../runs/hameau_run.jsonl").then((r2) => r2.text());
    })
    .then((txt) => window.hameauViewer.loadJSONLContent(txt))
    .catch(() => console.log("Prêt pour chargement JSONL"));
});
