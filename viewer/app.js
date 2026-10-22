/**
 * HAMEAU — Application de Rejeu Web (Canvas & Inspecteur)
 * UI/UX Pro Max & Ponytail (Vanilla JS, 0 dépendance lourde)
 */

// Définition canonique des 19 lieux du village (étendus)
const VILLAGE_LOCATIONS = {
  marche: { id: "marche", name: "Place du Marché", category: "commerce", x: 0.50, y: 0.45, icon: "🧺" },
  boulangerie: { id: "boulangerie", name: "Boulangerie d'Awa", category: "artisanat", x: 0.34, y: 0.34, icon: "🥖" },
  mairie: { id: "mairie", name: "Mairie du Hameau", category: "civique", x: 0.50, y: 0.22, icon: "🏛️" },
  ecole: { id: "ecole", name: "École communale", category: "education", x: 0.68, y: 0.28, icon: "📚" },
  bibliotheque: { id: "bibliotheque", name: "Bibliothèque", category: "culture", x: 0.72, y: 0.48, icon: "📖" },
  atelier: { id: "atelier", name: "Atelier de forge", category: "artisanat", x: 0.26, y: 0.50, icon: "⚒️" },
  medical: { id: "medical", name: "Cabinet médical", category: "sante", x: 0.35, y: 0.62, icon: "🩺" },
  cafe: { id: "cafe", name: "Café de la Rivière", category: "social", x: 0.52, y: 0.68, icon: "☕" },
  riviere: { id: "riviere", name: "Berges Rivière", category: "nature", x: 0.65, y: 0.78, icon: "🎣" },
  ferme: { id: "ferme", name: "Ferme des Hauts", category: "agriculture", x: 0.18, y: 0.72, icon: "🌾" },
  village_voisin: { id: "village_voisin", name: "Village Voisin (Val-d'Or)", category: "exterieur", x: 0.88, y: 0.18, icon: "🏰" },
  moulin_riviere: { id: "moulin_riviere", name: "Vieux Moulin", category: "artisanat", x: 0.78, y: 0.70, icon: "⚙️" },
  place_fetes: { id: "place_fetes", name: "Place des Fêtes", category: "civique", x: 0.36, y: 0.20, icon: "🎪" },
  foret_loups: { id: "foret_loups", name: "Forêt des Loups", category: "nature", x: 0.15, y: 0.88, icon: "🌲" },
  maison_nord: { id: "maison_nord", name: "Maisons Nord", category: "residence", x: 0.58, y: 0.14, icon: "🏡" },
  maison_ouest: { id: "maison_ouest", name: "Maisons Ouest", category: "residence", x: 0.18, y: 0.38, icon: "🏡" },
  maison_centre: { id: "maison_centre", name: "Maisons Centre", category: "residence", x: 0.38, y: 0.56, icon: "🏡" },
  maison_est: { id: "maison_est", name: "Maisons Est", category: "residence", x: 0.82, y: 0.38, icon: "🏡" },
  maison_sud: { id: "maison_sud", name: "Maisons Sud", category: "residence", x: 0.40, y: 0.82, icon: "🏡" },
};

const VILLAGE_ROADS = [
  ["mairie", "marche"], ["mairie", "ecole"], ["mairie", "maison_nord"], ["mairie", "place_fetes"],
  ["place_fetes", "boulangerie"],
  ["marche", "boulangerie"], ["marche", "cafe"], ["marche", "bibliotheque"], ["marche", "maison_centre"],
  ["boulangerie", "atelier"], ["boulangerie", "maison_ouest"],
  ["atelier", "ferme"], ["atelier", "medical"], ["medical", "cafe"], ["medical", "maison_sud"],
  ["cafe", "riviere"], ["riviere", "moulin_riviere"], ["moulin_riviere", "bibliotheque"],
  ["ecole", "bibliotheque"], ["ecole", "maison_est"], ["ecole", "village_voisin"],
  ["bibliotheque", "riviere"], ["ferme", "medical"], ["ferme", "foret_loups"], ["maison_sud", "foret_loups"]
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
  victor: { name: "Victor", job: "Notaire & Candidat", age: 58, avatar: "📜", home: "maison_nord" },
  fatou: { name: "Fatou", job: "Meunière du Moulin", age: 31, avatar: "🌾", home: "maison_sud" },
  lucas: { name: "Lucas", job: "Bûcheron & Meneur", age: 19, avatar: "🪓", home: "maison_ouest" },
  sokhna: { name: "Sokhna", job: "Marchande itinérante", age: 47, avatar: "🧕", home: "maison_est" },
  antoine: { name: "Antoine", job: "Garde champêtre", age: 62, avatar: "💂", home: "maison_centre" },
  mireille: { name: "Mireille", job: "Herboriste", age: 29, avatar: "🌿", home: "maison_ouest" },
  bastien: { name: "Bastien", job: "Jeune Pêcheur", age: 24, avatar: "🛶", home: "maison_sud" },
  salimata: { name: "Salimata", job: "Aubergiste", age: 38, avatar: "🍲", home: "maison_est" },
};

// Topologie des relations sociales du village (Graphe social étendu à 20 agents)
const SOCIAL_RELATIONSHIPS = [
  { source: "awa", target: "yao", strength: 0.65, label: "Clients & livraisons" },
  { source: "awa", target: "mariam", strength: 0.70, label: "Partenaires de marché" },
  { source: "awa", target: "fatou", strength: 0.75, label: "Fourniture farine" },
  { source: "kofi", target: "claire", strength: 0.60, label: "Communication municipale" },
  { source: "kofi", target: "samuel", strength: 0.80, label: "Conseil des aînés" },
  { source: "kofi", target: "victor", strength: 0.40, label: "Rivalité politique" },
  { source: "victor", target: "antoine", strength: 0.65, label: "Ordre public électoral" },
  { source: "victor", target: "mariam", strength: 0.60, label: "Promesses marchandes" },
  { source: "mariam", target: "ibrahim", strength: 0.75, label: "Approvisionnement légumes" },
  { source: "paul", target: "tom", strength: 0.65, label: "Habitués du café" },
  { source: "paul", target: "bastien", strength: 0.85, label: "Transmission de pêche" },
  { source: "elise", target: "yao", strength: 0.60, label: "Voisins d'enfance" },
  { source: "elise", target: "lea", strength: 0.70, label: "Échange de livres" },
  { source: "nadia", target: "samuel", strength: 0.60, label: "Entretien matériel" },
  { source: "nadia", target: "kofi", strength: 0.55, label: "Santé communale" },
  { source: "claire", target: "tom", strength: 0.50, label: "Échos du comptoir" },
  { source: "paul", target: "nadia", strength: 0.50, label: "Consultations de routine" },
  { source: "ibrahim", target: "samuel", strength: 0.65, label: "Réparation d'outils" },
  { source: "awa", target: "kofi", strength: 0.55, label: "Doléances du marché" },
  { source: "yao", target: "sokhna", strength: 0.70, label: "Cargaisons fluviales" },
  { source: "lucas", target: "mireille", strength: 0.75, label: "Exploration des bois" },
  { source: "sokhna", target: "salimata", strength: 0.80, label: "Commerce inter-villages" },
  { source: "lucas", target: "bastien", strength: 0.70, label: "Compagnons de veillée" },
  { source: "fatou", target: "bastien", strength: 0.60, label: "Voisins de rivière" }
];

const NETWORK_AGENT_ORDER = [
  "awa", "yao", "mariam", "ibrahim",
  "kofi", "claire", "elise", "lea",
  "samuel", "nadia", "paul", "tom",
  "victor", "fatou", "lucas", "sokhna",
  "antoine", "mireille", "bastien", "salimata"
];

// État de l'application
class HameauViewer {
  constructor() {
    this.events = [];
    this.eventsByTick = {};
    this.maxTick = 576;
    this.currentTick = 0;
    this.currentDay = 1;

    this.viewMode = "map"; // "map" | "network"
    this.renderMode = "characters"; // "characters" | "dots"
    this.charRenderer = typeof CharacterRenderer2D !== "undefined" ? new CharacterRenderer2D() : null;
    this.hoveredAgentId = null;
    this.networkNodePositions = {};
    this.agentMapPositions = {};

    this.isPlaying = false;
    this.playbackSpeed = 1;
    this.lastFrameTime = 0;
    this.accumulatedTime = 0;

    this.selectedAgentId = "yao";

    // État dynamique des agents
    this.agentsState = {};
    this.decisionsHistory = {};
    this.scoredMemories = {};
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
      this.scoredMemories[id] = [];
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

    // Clic et survol sur le canvas pour sélectionner un agent ou lieu
    this.canvas.addEventListener("click", (e) => this.handleCanvasClick(e));
    this.canvas.addEventListener("mousemove", (e) => this.handleCanvasMouseMove(e));
    this.canvas.addEventListener("mouseleave", () => {
      this.hoveredAgentId = null;
      this.canvas.style.cursor = "default";
    });

    // Bascule de mode de vue (Plan du village vs Réseau social)
    document.getElementById("btn-view-map")?.addEventListener("click", () => this.setViewMode("map"));
    document.getElementById("btn-view-network")?.addEventListener("click", () => this.setViewMode("network"));
    document.getElementById("btn-toggle-render-mode")?.addEventListener("click", () => this.toggleRenderMode());

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

    // Boutons rejeu échantillon et run live
    const btnSample = document.getElementById("btn-load-sample");
    if (btnSample) {
      btnSample.addEventListener("click", () => {
        fetch("sample_run.jsonl")
          .then((r) => r.text())
          .then((txt) => this.loadJSONLContent(txt))
          .catch(() => this.generateSyntheticRun());
      });
    }

    const btnLive = document.getElementById("btn-load-live");
    if (btnLive) {
      btnLive.addEventListener("click", () => {
        fetch("live_run.jsonl")
          .then((r) => {
            if (!r.ok) throw new Error("live_run.jsonl non trouvé");
            return r.text();
          })
          .then((txt) => this.loadJSONLContent(txt))
          .catch((err) => {
            console.warn(err);
            alert("Fichier live_run.jsonl non disponible. Lancez d'abord une simulation réelle.");
          });
      });
    }

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
        const day = ev.day || 1;
        const tickInDay = ev.tick ?? 0;
        const globalT = (day - 1) * 192 + tickInDay;
        if (!this.eventsByTick[globalT]) this.eventsByTick[globalT] = [];
        this.eventsByTick[globalT].push(ev);
        if (globalT > maxT) maxT = globalT;
      } catch (err) {
        console.warn("Ligne invalide:", line);
      }
    }

    this.runAgentIds = this.computeRunRoster(this.events);

    this.maxTick = Math.max(576, maxT);
    this.slider.max = this.maxTick;
    document.getElementById("feed-status").textContent = `${this.events.length} événements chargés`;
    this.seekToTick(0);
    this.togglePlay(true);
  }

  computeRunRoster(events) {
    // La population affichée vient du journal, jamais d'une constante.
    const ids = new Set();
    for (const ev of events) {
      if (ev.agent_id && AGENTS_META[ev.agent_id]) ids.add(ev.agent_id);
      const rcv = ev.payload && ev.payload.receiver;
      if (rcv && AGENTS_META[rcv]) ids.add(rcv);
    }
    return ids.size > 0 ? ids : new Set(Object.keys(AGENTS_META));
  }

  populationSize() {
    return (this.runAgentIds && this.runAgentIds.size) || Object.keys(AGENTS_META).length;
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

  play() {
    this.togglePlay(true);
  }

  pause() {
    this.togglePlay(false);
  }

  seekToTick(targetTick) {
    const isStepForward = targetTick === this.currentTick + 1;
    this.currentTick = targetTick;
    this.slider.value = targetTick;

    if (isStepForward) {
      // Avance incrémentale rapide (O(1)) pour la lecture continue et le mode 15x
      const evs = this.eventsByTick[targetTick] || [];
      for (const ev of evs) {
        this.applyEvent(ev, true);
      }
    } else {
      // Recalcul complet déterministe lors d'un saut ou retour arrière
      this.recomputeStateUpToTick(targetTick);
    }
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
    this.electionVotes = {};
    this.electionResult = null;
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
    this.currentDay = day || (Math.floor(this.currentTick / 192) + 1);

    if (event_type === "decision") {
      this.deciderCount++;
      if (typeof payload.latency_ms === "number") {
        this.deciderLatencies.push(payload.latency_ms);
      }
      if (agent_id && this.agentsState[agent_id]) {
        this.agentsState[agent_id].confidenceZone = payload.zone;
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

        // Mise à jour de l'action en cours pour D1 (BUG-06)
        if (payload.decision === "D1" || payload.decision_type === "D1") {
          const act = (payload.options && payload.options[payload.chosen_option]) || payload.chosen_option;
          if (act) {
            this.agentsState[agent_id].currentAction = act;
          }
        }
        // Enregistrement dynamique des souvenirs D3 MemoryGate (BUG-03, BUG-05)
        if (payload.decision === "D3" || payload.decision_type === "D3") {
          this.recordScoredMemory(agent_id, payload, tick);
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
        this.agentsState[agent_id].isTalking = isCurrentTick;
        this.agentsState[agent_id].lastUtterance = payload.utterance;
        const otherName = AGENTS_META[payload.listener]?.name || payload.listener;
        this.agentsState[agent_id].currentAction = `discute avec ${otherName}`;
      }
      if (payload.listener && this.agentsState[payload.listener]) {
        const speakerName = AGENTS_META[payload.speaker]?.name || payload.speaker;
        this.agentsState[payload.listener].currentAction = `écoute ${speakerName}`;
      }
      if (isCurrentTick) {
        this.addFeedItem(tick, "tag-talk", "Bedrock", `« ${payload.utterance} » (${payload.speaker})`);
      }
    } else if (event_type === "reflection") {
      this.bedrockCount++;
      if (payload.from_cassette) this.cassetteCount++;
      this.totalCost += payload.cost_usd || 0.0;
      if (agent_id && this.agentsState[agent_id]) {
        this.agentsState[agent_id].currentAction = "synthétise ses pensées";
      }
      if (isCurrentTick && agent_id) {
        this.addFeedItem(tick, "tag-talk", "Réflexion", `${AGENTS_META[agent_id]?.name || agent_id} synthétise sa journée`);
      }
    } else if (event_type === "move") {
      if (agent_id && this.agentsState[agent_id]) {
        const ag = this.agentsState[agent_id];
        ag.prevLocation = payload.from || ag.location;
        ag.location = payload.to;
        ag.travelProgress = isCurrentTick ? 0.0 : 1.0;
        ag.currentAction = `se déplace vers ${VILLAGE_LOCATIONS[payload.to]?.name || payload.to}`;
      }
      if (isCurrentTick) {
        this.addFeedItem(tick, "tag-move", "Déplacement", `${AGENTS_META[agent_id]?.name || agent_id} -> ${VILLAGE_LOCATIONS[payload.to]?.name || payload.to}`);
      }
    } else if (event_type === "rumor_hop") {
      this.rumorHops.push(payload);
      const receiver = payload.receiver;
      if (receiver && this.agentsState[receiver]) {
        const prev = this.agentsState[receiver].believedFacts[payload.fact_id] || 0;
        this.agentsState[receiver].believedFacts[payload.fact_id] = Math.max(prev, payload.credibility);
        const r3 = this.agentsState[receiver].believedFacts["R3_ouverture_marche"] || 0;
        const r2 = this.agentsState[receiver].believedFacts["R2_dementi_maire"] || 0;
        if (payload.fact_id === "R1_fermeture_marche" && payload.credibility >= 0.55) {
          if (r3 < 0.55 && payload.credibility > r2) {
            this.agentsState[receiver].didStock = true;
          }
        } else if (payload.fact_id === "R2_dementi_maire" && payload.credibility >= 0.60) {
          this.agentsState[receiver].didStock = false;
        } else if (payload.fact_id === "R3_ouverture_marche" && payload.credibility >= 0.55) {
          this.agentsState[receiver].didStock = false;
        }
      }
      if (isCurrentTick) {
        this.addFeedItem(tick, "tag-rumor", "Rumeur", `${payload.sender} a transmis ${payload.fact_id} à ${payload.receiver}`);
      }
    } else if (event_type === "election_vote") {
      if (!this.electionVotes) this.electionVotes = {};
      const voter = payload.voter || agent_id;
      if (voter) {
        this.electionVotes[voter] = payload;
        if (this.agentsState[voter]) {
          this.agentsState[voter].vote = payload;
          const vLabel = AGENTS_META[payload.vote]?.name || payload.vote;
          this.agentsState[voter].currentAction = `a voté (${vLabel})`;
        }
      }
      if (isCurrentTick && voter) {
        const voterName = AGENTS_META[voter]?.name || voter;
        const choiceName = AGENTS_META[payload.vote]?.name || payload.vote;
        this.addFeedItem(tick, "tag-decision", "Vote D9", `${voterName} dépose son bulletin : ${choiceName}`);
      }
    } else if (event_type === "election_result") {
      this.electionResult = payload;
      const wName = AGENTS_META[payload.winner]?.name || payload.winner;
      const kCount = payload.tally?.kofi ?? 0;
      const vCount = payload.tally?.victor ?? 0;
      const aCount = payload.tally?.abstention ?? 0;
      for (const ag of Object.values(this.agentsState)) {
        ag.believedFacts["R7_resultat_election"] = 1.0;
      }
      if (isCurrentTick) {
        this.addFeedItem(tick, "tag-rumor", "Scrutin", `🏆 ${wName} élu Maire (Kofi ${kCount}, Victor ${vCount}, Abst. ${aCount})`);
      }
    } else if (event_type === "gazette") {
      this.bedrockCount++;
      if (payload.from_cassette) this.cassetteCount++;
      this.totalCost += payload.cost_usd || 0.0;
      this.gazetteContent = payload.gazette_text;
      this.renderGazetteFormatted(payload.gazette_text);
    }
  }

  recordScoredMemory(agent_id, payload, tick) {
    if (!this.scoredMemories[agent_id]) {
      this.scoredMemories[agent_id] = [];
    }
    const memId = payload.memory_id || (payload.question ? payload.question.replace("Pertinence du souvenir ", "").trim() : `mem_${tick}`);
    let memText = payload.memory_text;
    if (!memText) {
      if (memId === "mem_r1_init") {
        memText = "A entendu une rumeur sur la fermeture prochaine du marché hebdomadaire.";
      } else if (memId === "mem_r2_init") {
        memText = "Le maire a formellement démenti toute fermeture du marché.";
      } else if (memId.startsWith("mem_hear_")) {
        memText = "Échange de propos récents lors d'une discussion au village.";
      } else {
        memText = `Souvenir (${memId})`;
      }
    }

    const rel = typeof payload.relevance_score === "number" ? payload.relevance_score : (typeof payload.chosen_option === "number" ? payload.chosen_option : 0.5);
    const imp = typeof payload.importance_score === "number" ? payload.importance_score : 0.6;
    const rec = typeof payload.recency_score === "number" ? payload.recency_score : 0.7;
    const comp = typeof payload.composite_score === "number" ? payload.composite_score : Math.round((0.4 * rel + 0.3 * imp + 0.3 * rec) * 100) / 100;
    const zone = payload.zone || "green";
    const latency = typeof payload.latency_ms === "number" ? payload.latency_ms : null;

    const entry = {
      id: memId,
      text: memText,
      relevance: rel,
      importance: imp,
      recency: rec,
      composite: comp,
      zone: zone,
      latency: latency,
      tick: tick,
      fallbackUsed: !!payload.fallback_used,
    };

    const list = this.scoredMemories[agent_id];
    const existingIdx = list.findIndex(m => m.id === memId);
    if (existingIdx !== -1) {
      list[existingIdx] = entry;
    } else {
      list.push(entry);
    }
    list.sort((a, b) => b.composite - a.composite);
    if (list.length > 20) {
      list.pop();
    }
  }

  renderGazetteFormatted(markdownText) {
    const container = document.getElementById("gazette-content");
    if (!container) return;
    container.textContent = "";

    if (!markdownText) {
      container.textContent = "Aucune édition disponible pour le moment.";
      return;
    }

    const lines = markdownText.split("\n");
    lines.forEach((line) => {
      const trimmed = line.trim();
      if (!trimmed) return;
      if (trimmed.startsWith("### ")) {
        const h3 = document.createElement("h3");
        this.appendFormattedInline(h3, trimmed.slice(4));
        container.appendChild(h3);
      } else if (trimmed.startsWith("## ")) {
        const h2 = document.createElement("h2");
        this.appendFormattedInline(h2, trimmed.slice(3));
        container.appendChild(h2);
      } else if (trimmed.startsWith("# ")) {
        const h1 = document.createElement("h1");
        this.appendFormattedInline(h1, trimmed.slice(2));
        container.appendChild(h1);
      } else {
        const p = document.createElement("p");
        this.appendFormattedInline(p, trimmed);
        container.appendChild(p);
      }
    });
  }

  appendFormattedInline(parentEl, text) {
    const parts = text.split(/(\*\*.*?\*\*)/g);
    parts.forEach((part) => {
      if (part.startsWith("**") && part.endsWith("**") && part.length >= 4) {
        const strong = document.createElement("strong");
        strong.textContent = part.slice(2, -2);
        parentEl.appendChild(strong);
      } else if (part.length > 0) {
        parentEl.appendChild(document.createTextNode(part));
      }
    });
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
    // Horloge multi-jours
    const curDay = Math.floor(this.currentTick / 192) + 1;
    const tickInDay = this.currentTick % 192;
    this.clockDay.textContent = `JOUR ${curDay}`;
    this.clockTime.textContent = this.formatTickTime(tickInDay);
    this.clockTick.textContent = `Tick ${this.currentTick} / ${this.maxTick} (J${curDay} • ${this.formatTickTime(tickInDay)})`;

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
    const avgDecLat = this.deciderLatencies.length > 0
      ? this.deciderLatencies.reduce((a, b) => a + b, 0) / this.deciderLatencies.length
      : 0;
    if (this.counterLatencySaved) {
      const savedPerDecisionMs = Math.max(0, 680 - avgDecLat);
      const latencySec = (this.deciderCount * savedPerDecisionMs) / 1000;
      this.counterLatencySaved.textContent = `${Math.round(latencySec)} s`;
    }
    const latSubEl = document.getElementById("counter-latency-sub");
    if (latSubEl) {
      latSubEl.textContent = this.deciderLatencies.length > 0
        ? `-${Math.max(0, Math.round(680 - avgDecLat))} ms / décision`
        : "Mesuré depuis journal";
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
    const r3 = a.believedFacts["R3_ouverture_marche"];
    const r4 = a.believedFacts["R4_election_municipale"];
    document.getElementById("r1-cred").textContent = r1 ? `Crédibilité : ${(r1 * 100).toFixed(0)}%` : "Non informé";
    document.getElementById("r2-cred").textContent = r2 ? `Officiel : ${(r2 * 100).toFixed(0)}%` : "Non informé";
    const r3El = document.getElementById("r3-cred");
    if (r3El) r3El.textContent = r3 ? `Ouvert : ${(r3 * 100).toFixed(0)}%` : "Non informé";
    const r4El = document.getElementById("r4-cred");
    if (r4El) r4El.textContent = r4 ? `Informé : ${(r4 * 100).toFixed(0)}%` : "Non informé";
    const voteEl = document.getElementById("inspector-vote");
    if (voteEl) {
      const vObj = a.vote || (this.electionVotes && this.electionVotes[this.selectedAgentId]);
      if (vObj) {
        const vName = AGENTS_META[vObj.vote]?.name || vObj.vote;
        const confTxt = typeof vObj.confidence === "number" ? ` (${(vObj.confidence * 100).toFixed(0)}%, ${vObj.zone})` : " (candidat)";
        voteEl.textContent = `${vName}${confTxt}`;
      } else {
        voteEl.textContent = "En attente du scrutin (J3 17h)";
      }
    }

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

    // Souvenirs scorés par MemoryGate (BUG-05)
    const memList = document.getElementById("inspector-memories-list");
    if (memList) {
      memList.textContent = "";
      const memories = this.scoredMemories[this.selectedAgentId] || [];
      if (memories.length === 0) {
        const emptyDiv = document.createElement("div");
        emptyDiv.style.cssText = "color:var(--text-muted);font-size:0.75rem;padding:4px 0;";
        emptyDiv.textContent = "Aucun souvenir noté pour le moment.";
        memList.appendChild(emptyDiv);
      } else {
        memories.slice(0, 3).forEach((m, idx) => {
          const item = document.createElement("div");
          item.className = "memory-item";
          item.style.cssText = "background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.07);border-radius:6px;padding:6px 8px;margin-bottom:6px;font-size:0.75rem;";

          const head = document.createElement("div");
          head.style.cssText = "display:flex;justify-content:space-between;align-items:center;margin-bottom:4px;";

          const badge = document.createElement("span");
          badge.className = `zone-tag ${m.zone}`;
          badge.textContent = `TOP ${idx + 1} (${m.zone.toUpperCase()})`;

          const scoreSpan = document.createElement("span");
          scoreSpan.style.cssText = "font-size:0.7rem;color:var(--text-muted);";
          scoreSpan.textContent = `Score : ${m.composite.toFixed(2)}`;

          head.appendChild(badge);
          head.appendChild(scoreSpan);

          const body = document.createElement("div");
          body.style.cssText = "color:var(--text-secondary);line-height:1.3;";
          body.textContent = m.text;

          item.appendChild(head);
          item.appendChild(body);
          memList.appendChild(item);
        });
      }
    }
  }

  updateRumorTab() {
    let infected = 0;
    let stocking = 0;
    let r4Count = 0;
    const roster = this.runAgentIds || new Set(Object.keys(this.agentsState));
    for (const [id, a] of Object.entries(this.agentsState)) {
      if (!roster.has(id)) continue;
      if (a.believedFacts["R1_fermeture_marche"]) infected++;
      if (a.believedFacts["R4_election_municipale"]) r4Count++;
      if (a.didStock) stocking++;
    }
    const n = this.populationSize();

    document.getElementById("rumor-count").textContent = `${infected} / ${n}`;
    document.getElementById("stocking-count").textContent = `${stocking} / ${n}`;

    // Mise à jour du panneau Scrutin Municipal (D9)
    const statusBadge = document.getElementById("election-status-badge");
    const summaryLine = document.getElementById("election-summary-line");
    const kofiEl = document.getElementById("election-kofi-count");
    const victorEl = document.getElementById("election-victor-count");
    const abstEl = document.getElementById("election-abst-count");
    if (summaryLine && kofiEl && victorEl && abstEl) {
      let kofiVotes = 0;
      let victorVotes = 0;
      let abstVotes = 0;
      if (this.electionResult && this.electionResult.tally) {
        kofiVotes = this.electionResult.tally.kofi || 0;
        victorVotes = this.electionResult.tally.victor || 0;
        abstVotes = this.electionResult.tally.abstention || 0;
        const winnerName = AGENTS_META[this.electionResult.winner]?.name || this.electionResult.winner;
        if (statusBadge) statusBadge.textContent = "Scrutin clos (J3 17h)";
        summaryLine.textContent = `🏆 Maire élu : ${winnerName} (Participation : ${Math.round((this.electionResult.turnout || 0) * 100)}%)`;
      } else {
        for (const v of Object.values(this.electionVotes || {})) {
          if (v.vote === "kofi") kofiVotes++;
          else if (v.vote === "victor") victorVotes++;
          else abstVotes++;
        }
        if (statusBadge) statusBadge.textContent = `Campagne R4 : ${r4Count}/${n}`;
        summaryLine.textContent = r4Count > 0
          ? `Campagne active (${r4Count}/${n} informés) — Vote J3 à 17h00`
          : "En attente du lancement de campagne (J1 09h20)";
      }
      kofiEl.textContent = `${kofiVotes} voix`;
      victorEl.textContent = `${victorVotes} voix`;
      abstEl.textContent = `${abstVotes}`;
    }

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
      hopSpan.textContent = `${(h.fact_id || "").split("_")[0]} · Saut #${h.hop_count}`;

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
    const totalTicks = Math.max(1, this.maxTick || 576);

    ctx.strokeStyle = "#334155";
    ctx.lineWidth = 1;
    ctx.font = "9px monospace";
    ctx.fillStyle = "#64748b";

    const pop = this.populationSize();
    for (let count of [0, Math.round(pop / 2), pop]) {
      const y = padTop + plotH - (count / pop) * plotH;
      ctx.beginPath();
      ctx.moveTo(padLeft, y);
      ctx.lineTo(w - padRight, y);
      ctx.stroke();
      ctx.fillText(count.toString(), 6, y + 3);
    }

    if (totalTicks > 192) {
      ctx.fillText("J1 06h", padLeft, h - 5);
      ctx.fillText("J2 10h", padLeft + plotW * 0.42, h - 5);
      ctx.fillText("J3 22h", w - padRight - 35, h - 5);
    } else {
      ctx.fillText("06h", padLeft, h - 5);
      ctx.fillText("14h", padLeft + plotW * 0.5, h - 5);
      ctx.fillText("22h", w - padRight - 15, h - 5);
    }

    const r1Points = [];
    const r2Points = [];
    const r3Points = [];

    const r1Set = new Set();
    const r2Set = new Set();
    const r3Set = new Set();

    for (let t = 0; t <= this.currentTick; t++) {
      const evs = this.eventsByTick[t] || [];
      for (const ev of evs) {
        if (ev.event_type === "rumor_hop" && ev.payload) {
          if (ev.payload.fact_id === "R1_fermeture_marche" && ev.payload.receiver) {
            r1Set.add(ev.payload.receiver);
          } else if (ev.payload.fact_id === "R2_dementi_maire" && ev.payload.receiver) {
            r2Set.add(ev.payload.receiver);
          } else if (ev.payload.fact_id === "R3_ouverture_marche" && ev.payload.receiver) {
            r3Set.add(ev.payload.receiver);
          }
        }
      }
      r1Points.push({ tick: t, count: r1Set.size });
      r2Points.push({ tick: t, count: r2Set.size });
      r3Points.push({ tick: t, count: r3Set.size });
    }

    if (r1Points.length > 0) {
      ctx.beginPath();
      ctx.strokeStyle = "#f43f5e";
      ctx.lineWidth = 2;
      r1Points.forEach((pt, i) => {
        const x = padLeft + (pt.tick / totalTicks) * plotW;
        const y = padTop + plotH - (pt.count / pop) * plotH;
        if (i === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
      });
      ctx.stroke();
    }

    if (r2Points.length > 0) {
      ctx.beginPath();
      ctx.strokeStyle = "#06b6d4";
      ctx.lineWidth = 2;
      r2Points.forEach((pt, i) => {
        const x = padLeft + (pt.tick / totalTicks) * plotW;
        const y = padTop + plotH - (pt.count / pop) * plotH;
        if (i === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
      });
      ctx.stroke();
    }

    if (r3Points.length > 0) {
      ctx.beginPath();
      ctx.strokeStyle = "#10b981";
      ctx.lineWidth = 2;
      r3Points.forEach((pt, i) => {
        const x = padLeft + (pt.tick / totalTicks) * plotW;
        const y = padTop + plotH - (pt.count / pop) * plotH;
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

    // Récupérer les souvenirs scorés réels de l'agent
    const agentMemories = this.scoredMemories[this.selectedAgentId] || [];

    // Si l'agent a des souvenirs scorés réels issus de la simulation
    const fallbackLatency =
      this.deciderLatencies && this.deciderLatencies.length > 0
        ? this.deciderLatencies[this.deciderLatencies.length - 1]
        : null;
    let candidates = [];
    if (agentMemories.length > 0) {
      candidates = agentMemories.map((m, idx) => ({
        id: m.id || `m${idx + 1}`,
        text: m.text,
        imp: m.importance,
        rel: m.relevance,
        comp: m.composite,
        zone: m.zone || "green",
        latency: m.latency ?? fallbackLatency,
      }));
    } else {
      // Contexte initial canonique de l'agent (avant ses premières interactions)
      const locName = VILLAGE_LOCATIONS[a.location]?.name || a.location;
      const meta = AGENTS_META[this.selectedAgentId];
      candidates = [
        { id: "c1", text: `${a.name} est à ${locName} (${a.currentAction}).`, imp: 0.7, rel: 0.85, comp: 0.78, zone: "green", latency: fallbackLatency },
        { id: "c2", text: `Résidence principale : ${VILLAGE_LOCATIONS[meta?.home]?.name || meta?.home}.`, imp: 0.5, rel: 0.60, comp: 0.55, zone: "orange", latency: fallbackLatency },
        { id: "c3", text: "Le village s'éveille paisiblement au lever du soleil.", imp: 0.2, rel: 0.15, comp: 0.18, zone: "red", latency: fallbackLatency },
      ];
    }

    // Afficher tous les candidats dans la colonne "Brut (Sans MemoryGate)"
    candidates.forEach((c) => {
      const item = document.createElement("div");
      item.className = "diff-memory-item";
      item.textContent = `• [Brut] ${c.text}`;
      this.diffRawContent.appendChild(item);
    });

    // Sélectionner le Top 3 retenu (Avec MemoryGate)
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

    // Estimation réaliste des tokens (~3.8 caractères par token pour le français + base prompt)
    const basePromptTokens = 350;
    const rawTokens = basePromptTokens + candidates.reduce((sum, c) => sum + Math.ceil(c.text.length / 3.8) + 12, 0);
    const gatedTokens = basePromptTokens + top3.reduce((sum, c) => sum + Math.ceil(c.text.length / 3.8) + 12, 0);
    const tokensSavedPct = Math.max(0, Math.round((1 - (gatedTokens / rawTokens)) * 100));

    const rawBadge = document.getElementById("tokens-raw-badge");
    if (rawBadge) rawBadge.textContent = `~${rawTokens} tokens`;

    const gatedBadge = document.getElementById("tokens-gated-badge");
    if (gatedBadge) gatedBadge.textContent = `~${gatedTokens} tokens`;

    if (this.diffTokensSaved) this.diffTokensSaved.textContent = `-${tokensSavedPct} %`;
    if (this.diffNoiseRemoved) {
      const noise = Math.max(0, candidates.length - top3.length);
      this.diffNoiseRemoved.textContent = `${noise} / ${candidates.length} souvenirs`;
    }
    const latEl = document.getElementById("diff-decider-latency");
    if (latEl) {
      latEl.textContent =
        candidates[0]?.latency != null ? `${candidates[0].latency.toFixed(0)} ms` : "-- ms";
    }
  }

  handleCanvasClick(e) {
    const rect = this.canvas.getBoundingClientRect();
    const scaleX = this.canvas.width / rect.width;
    const scaleY = this.canvas.height / rect.height;
    const canvasX = (e.clientX - rect.left) * scaleX;
    const canvasY = (e.clientY - rect.top) * scaleY;

    if (this.viewMode === "network") {
      for (const [id, pos] of Object.entries(this.networkNodePositions)) {
        const d = Math.hypot(pos.x - canvasX, pos.y - canvasY);
        if (d <= pos.radius + 10 * this.dpr) {
          this.selectedAgentId = id;
          this.agentSelect.value = id;
          this.updateInspector();
          return;
        }
      }
    } else {
      // 1. Vérifier si un agent a été cliqué directement
      for (const [id, pos] of Object.entries(this.agentMapPositions)) {
        const d = Math.hypot(pos.x - canvasX, pos.y - canvasY);
        if (d <= pos.radius + 6 * this.dpr) {
          this.selectedAgentId = id;
          if (this.agentSelect) this.agentSelect.value = id;
          this.updateInspector();
          return;
        }
      }

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
            if (this.agentSelect) this.agentSelect.value = id;
            this.updateInspector();
            break;
          }
        }
      }
    }
  }

  handleCanvasMouseMove(e) {
    const rect = this.canvas.getBoundingClientRect();
    const scaleX = this.canvas.width / rect.width;
    const scaleY = this.canvas.height / rect.height;
    const canvasX = (e.clientX - rect.left) * scaleX;
    const canvasY = (e.clientY - rect.top) * scaleY;

    if (this.viewMode === "network") {
      let hovered = null;
      for (const [id, pos] of Object.entries(this.networkNodePositions)) {
        const d = Math.hypot(pos.x - canvasX, pos.y - canvasY);
        if (d <= pos.radius + 8 * this.dpr) {
          hovered = id;
          break;
        }
      }
      this.hoveredAgentId = hovered;
      this.canvas.style.cursor = hovered ? "pointer" : "default";
    } else {
      let hovered = null;
      for (const [id, pos] of Object.entries(this.agentMapPositions)) {
        const d = Math.hypot(pos.x - canvasX, pos.y - canvasY);
        if (d <= pos.radius + 6 * this.dpr) {
          hovered = id;
          break;
        }
      }
      this.hoveredAgentId = hovered;
      this.canvas.style.cursor = hovered ? "pointer" : "default";
    }
  }

  setViewMode(mode) {
    this.viewMode = mode;
    document.getElementById("btn-view-map")?.classList.toggle("active", mode === "map");
    document.getElementById("btn-view-network")?.classList.toggle("active", mode === "network");
    this.updateCanvasLegend();
  }

  toggleRenderMode() {
    this.renderMode = this.renderMode === "characters" ? "dots" : "characters";
    const btn = document.getElementById("btn-toggle-render-mode");
    if (btn) {
      btn.textContent = this.renderMode === "characters" ? "🎭 Personnages 2D" : "⚪ Points Schématiques";
      btn.classList.toggle("active", this.renderMode === "characters");
    }
    this.updateCanvasLegend();
  }

  updateCanvasLegend() {
    const legendEl = document.getElementById("canvas-legend");
    if (!legendEl) return;
    legendEl.textContent = "";

    const items = this.viewMode === "network"
      ? [
          { dot: "dot-neutral", label: "Serein / Neutre" },
          { dot: "dot-rumeur", label: "Rumeur R1 (Panique)" },
          { dot: "dot-dementi", label: "Démenti R2" },
          { dot: "dot-resolution", label: "Marché Ouvert R3" },
          { dot: "dot-stocking", label: "Cercle pointillé : Panique provisions" },
        ]
      : this.renderMode === "characters"
      ? [
          { dot: "dot-habitant", label: "Habitant Illustré 2D" },
          { dot: "dot-rumeur", label: "Inquiétude R1 (Regard furtif)" },
          { dot: "dot-dementi", label: "Soulagement R2 (Soupir apaisé)" },
          { dot: "dot-stocking", label: "Stockage (Panier garni)" },
        ]
      : [
          { dot: "dot-habitant", label: "Habitant" },
          { dot: "dot-rumeur", label: "Porte la Rumeur R1" },
          { dot: "dot-dementi", label: "A reçu le Démenti R2" },
          { dot: "dot-stocking", label: "Stocke des provisions" },
        ];

    items.forEach((it) => {
      const span = document.createElement("span");
      span.className = "legend-item";
      const dot = document.createElement("span");
      dot.className = `dot ${it.dot}`;
      span.appendChild(dot);
      span.appendChild(document.createTextNode(` ${it.label}`));
      legendEl.appendChild(span);
    });
  }

  animate(timestamp) {
    if (!this.lastFrameTime) this.lastFrameTime = timestamp;
    const dt = (timestamp - this.lastFrameTime) / 1000.0;
    this.lastFrameTime = timestamp;

    // Progression fluide des déplacements de marche
    const travelSpeed = 1.35 * this.playbackSpeed;
    for (const a of Object.values(this.agentsState)) {
      if (a.travelProgress < 1.0) {
        a.travelProgress = Math.min(1.0, a.travelProgress + (dt > 0 && dt < 0.2 ? dt : 0.016) * travelSpeed);
      }
    }

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
    this.renderInspectorBust();
    this.renderGazetteBust();
    requestAnimationFrame(this.animate);
  }

  renderInspectorBust() {
    const canvas = document.getElementById("inspector-bust-canvas");
    if (!canvas || !this.charRenderer) return;
    const ctx = canvas.getContext("2d");
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    const charDef = HAMEAU_CHARACTERS[this.selectedAgentId] || HAMEAU_CHARACTERS["yao"];
    const a = this.agentsState[this.selectedAgentId] || {};
    const currentHour = 6 + Math.floor((this.currentTick % 192) / 8);
    const isNight = currentHour >= 22 || currentHour < 6;

    ctx.save();
    // Fond camée subtil
    ctx.fillStyle = "rgba(15, 23, 42, 0.6)";
    ctx.beginPath();
    ctx.arc(canvas.width / 2, canvas.height / 2, canvas.width / 2 - 2, 0, Math.PI * 2);
    ctx.fill();

    this.charRenderer.draw(ctx, charDef, {
      tick: this.currentTick,
      isWalking: false,
      isTalking: a.isTalking || false,
      hasRumor: a.believedFacts && a.believedFacts["R1_fermeture_marche"] > 0,
      hasDebunk: a.believedFacts && a.believedFacts["R2_dementi_maire"] > 0,
      didStock: a.didStock || false,
      isHesitating: a.confidenceZone === "red",
      isNight
    }, {
      scale: 0.75,
      x: canvas.width / 2,
      y: canvas.height / 2 + 10,
      isPortrait: true
    });
    ctx.restore();
  }

  renderGazetteBust() {
    const canvas = document.getElementById("gazette-author-canvas");
    if (!canvas || !this.charRenderer) return;
    const ctx = canvas.getContext("2d");
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    const charDef = HAMEAU_CHARACTERS["claire"];
    ctx.save();
    ctx.fillStyle = "rgba(255, 255, 255, 0.9)";
    ctx.beginPath();
    ctx.arc(canvas.width / 2, canvas.height / 2, canvas.width / 2 - 2, 0, Math.PI * 2);
    ctx.fill();
    ctx.strokeStyle = "#cbd5e1";
    ctx.lineWidth = 1.2;
    ctx.stroke();

    this.charRenderer.draw(ctx, charDef, {
      tick: this.currentTick,
      isWalking: false,
      isTalking: true,
      hasRumor: false,
      hasDebunk: true,
      didStock: false,
      isHesitating: false,
      isNight: false
    }, {
      scale: 0.62,
      x: canvas.width / 2,
      y: canvas.height / 2 + 8,
      isPortrait: true
    });
    ctx.restore();
  }

  renderCanvas() {
    const w = this.canvas.width;
    const h = this.canvas.height;
    const ctx = this.ctx;

    ctx.clearRect(0, 0, w, h);

    if (this.viewMode === "network") {
      this.renderNetworkGraph(w, h, ctx);
    } else {
      this.renderMap(w, h, ctx);
    }
  }

  renderMap(w, h, ctx) {
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
      ctx.font = `600 ${10 * this.dpr}px 'Plus Jakarta Sans', sans-serif`;
      ctx.fillStyle = "#cbd5e1";
      const nameY = this.renderMode === "characters" ? py - radius - 9 * this.dpr : py + radius + 12 * this.dpr;
      ctx.fillText(loc.name, px, nameY);
    }

    // 4. Dessin des habitants
    if (this.renderMode === "dots" || !this.charRenderer) {
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

          this.agentMapPositions[a.id] = { x: ax, y: ay, radius: 14 * this.dpr };

          const isSelected = a.id === this.selectedAgentId;
          const hasRumor = a.believedFacts["R1_fermeture_marche"] > 0;
          const hasDebunk = a.believedFacts["R2_dementi_maire"] > 0;
          const hasOpen = a.believedFacts["R3_ouverture_marche"] > 0;

          // Halo d'état
          ctx.beginPath();
          ctx.arc(ax, ay, (isSelected ? 14 : 10) * this.dpr, 0, Math.PI * 2);
          ctx.fillStyle = hasOpen ? "#10b981" : hasDebunk ? "#06b6d4" : hasRumor ? "#f43f5e" : "#38bdf8";
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
          ctx.font = `700 ${9 * this.dpr}px 'Plus Jakarta Sans', sans-serif`;
          ctx.fillStyle = isSelected ? "#ffffff" : "#94a3b8";
          ctx.fillText(a.name, ax, ay - 12 * this.dpr);
        });
      }
      return;
    }

    // --- Mode Personnages Illustrés 2D Haute Définition ---
    const currentHour = 6 + Math.floor((this.currentTick % 192) / 8);
    const isNight = currentHour >= 22 || currentHour < 6;

    const stationaryByLoc = {};
    const travelingAgents = [];

    for (const [id, a] of Object.entries(this.agentsState)) {
      if (a.travelProgress < 1.0 && a.prevLocation && a.prevLocation !== a.location) {
        travelingAgents.push(a);
      } else {
        stationaryByLoc[a.location] = stationaryByLoc[a.location] || [];
        stationaryByLoc[a.location].push(a);
      }
    }

    // Rendu des agents en transit (marche le long du chemin)
    travelingAgents.forEach((a) => {
      const locFrom = VILLAGE_LOCATIONS[a.prevLocation] || VILLAGE_LOCATIONS[a.location];
      const locTo = VILLAGE_LOCATIONS[a.location];
      if (!locFrom || !locTo) return;

      const t = Math.max(0, Math.min(1, a.travelProgress));
      const s = t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;

      const x1 = locFrom.x * w;
      const y1 = locFrom.y * h + 24 * this.dpr;
      const x2 = locTo.x * w;
      const y2 = locTo.y * h + 24 * this.dpr;

      const arcH = -18 * this.dpr * Math.sin(t * Math.PI);
      const ax = x1 + (x2 - x1) * s;
      const ay = y1 + (y2 - y1) * s + arcH;
      const facing = (x2 - x1) >= 0 ? 1 : -1;

      this.drawMapCharacter(ctx, a, ax, ay, facing, true, isNight);
    });

    // Rendu des agents stationnaires avec disposition anti-collision en arc étagé
    for (const [locId, agents] of Object.entries(stationaryByLoc)) {
      const loc = VILLAGE_LOCATIONS[locId];
      if (!loc) continue;

      const basePx = loc.x * w;
      const basePy = loc.y * h;
      const radius = (loc.category === "residence" ? 18 : 26) * this.dpr;
      const K = agents.length;

      // Tri déterministe pour éviter tout sautillement
      agents.sort((x, y) => x.id.localeCompare(y.id));

      agents.forEach((a, i) => {
        let ax, ay;
        if (K === 1) {
          ax = basePx;
          ay = basePy + radius + 44 * this.dpr;
        } else {
          const spreadX = Math.min(52 * this.dpr, (180 * this.dpr) / K);
          const offsetX = (i - (K - 1) / 2) * spreadX;
          const arcDroop = Math.abs(i - (K - 1) / 2) * 5 * this.dpr;
          ax = basePx + offsetX;
          ay = basePy + radius + 42 * this.dpr + arcDroop;
        }

        this.drawMapCharacter(ctx, a, ax, ay, 1, false, isNight);
      });
    }
  }

  drawMapCharacter(ctx, a, ax, ay, facing, isWalking, isNight) {
    this.agentMapPositions[a.id] = { x: ax, y: ay, radius: 20 * this.dpr };

    const isSelected = a.id === this.selectedAgentId;
    const isHovered = a.id === this.hoveredAgentId;
    const hasRumor = a.believedFacts && a.believedFacts["R1_fermeture_marche"] > 0;
    const hasDebunk = a.believedFacts && a.believedFacts["R2_dementi_maire"] > 0;
    const didStock = !!a.didStock;
    const isHesitating = a.confidenceZone === "red";
    const isTalking = a.isTalking;

    // 1. Halo d'ambiance / croyance
    if (hasRumor || hasDebunk || didStock) {
      ctx.save();
      const haloColor = hasDebunk ? "rgba(6, 182, 212, 0.40)" : hasRumor ? "rgba(244, 63, 94, 0.40)" : "rgba(245, 158, 11, 0.40)";
      const hGrad = ctx.createRadialGradient(ax, ay, 2 * this.dpr, ax, ay, 22 * this.dpr);
      hGrad.addColorStop(0, haloColor);
      hGrad.addColorStop(0.65, haloColor.replace("0.40", "0.12"));
      hGrad.addColorStop(1, "rgba(0, 0, 0, 0)");
      ctx.fillStyle = hGrad;
      ctx.beginPath();
      ctx.ellipse(ax, ay, 24 * this.dpr, 9 * this.dpr, 0, 0, Math.PI * 2);
      ctx.fill();
      ctx.restore();
    }

    // 2. Anneau de sélection
    if (isSelected || isHovered) {
      ctx.save();
      ctx.strokeStyle = isSelected ? "#38bdf8" : "#f59e0b";
      ctx.lineWidth = (isSelected ? 2.5 : 1.5) * this.dpr;
      ctx.beginPath();
      ctx.ellipse(ax, ay, 18 * this.dpr, 7 * this.dpr, 0, 0, Math.PI * 2);
      ctx.stroke();
      ctx.restore();
    }

    // 3. Dessin du personnage vectoriel
    ctx.save();
    ctx.translate(ax, ay);
    if (facing === -1) {
      ctx.scale(-1, 1);
    }
    const charDef = HAMEAU_CHARACTERS[a.id] || HAMEAU_CHARACTERS["yao"];
    this.charRenderer.draw(ctx, charDef, {
      tick: this.currentTick,
      isWalking,
      isTalking,
      hasRumor,
      hasDebunk,
      didStock,
      isHesitating,
      isNight
    }, {
      scale: 0.68 * this.dpr,
      x: 0,
      y: 0,
      isPortrait: false
    });
    ctx.restore();

    // 4. Étiquette du nom (sous les pieds)
    ctx.save();
    ctx.font = `700 ${8.5 * this.dpr}px 'Plus Jakarta Sans', sans-serif`;
    ctx.textAlign = "center";
    ctx.textBaseline = "top";
    const nameText = a.name;
    const metrics = ctx.measureText(nameText);
    const padX = 4 * this.dpr;
    const tagH = 13 * this.dpr;
    ctx.fillStyle = isSelected ? "rgba(56, 189, 248, 0.25)" : "rgba(15, 23, 42, 0.85)";
    ctx.strokeStyle = isSelected ? "#38bdf8" : "rgba(255, 255, 255, 0.12)";
    ctx.lineWidth = 1 * this.dpr;
    ctx.beginPath();
    ctx.roundRect(ax - metrics.width / 2 - padX, ay + 6 * this.dpr, metrics.width + padX * 2, tagH, 3 * this.dpr);
    ctx.fill();
    ctx.stroke();
    ctx.fillStyle = isSelected ? "#ffffff" : "#cbd5e1";
    ctx.fillText(nameText, ax, ay + 7 * this.dpr);
    ctx.restore();

    // 5. Bulle de dialogue éditoriale si l'agent parle
    if (isTalking) {
      const bubbleText = a.lastUtterance
        ? (a.lastUtterance.length > 38 ? `« ${a.lastUtterance.slice(0, 36)}… »` : `« ${a.lastUtterance} »`)
        : "« Bonjour ! »";
      const bx = ax;
      const by = ay - 68 * this.dpr;

      ctx.save();
      ctx.font = `600 ${9 * this.dpr}px 'Plus Jakarta Sans', sans-serif`;
      const textW = ctx.measureText(bubbleText).width;
      const bw = Math.max(68 * this.dpr, textW + 16 * this.dpr);
      const bh = 22 * this.dpr;

      ctx.fillStyle = "#fffbeb";
      ctx.strokeStyle = "#d97706";
      ctx.lineWidth = 1.2 * this.dpr;
      ctx.beginPath();
      ctx.roundRect(bx - bw / 2, by - bh, bw, bh, 5 * this.dpr);
      ctx.fill();
      ctx.stroke();

      // Queue triangulaire
      ctx.fillStyle = "#fffbeb";
      ctx.beginPath();
      ctx.moveTo(bx - 4 * this.dpr, by);
      ctx.lineTo(bx, by + 6 * this.dpr);
      ctx.lineTo(bx + 4 * this.dpr, by);
      ctx.closePath();
      ctx.fill();
      ctx.stroke();

      ctx.fillStyle = "#78350f";
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";
      ctx.fillText(bubbleText, bx, by - bh / 2);
      ctx.restore();
    }
  }

  renderNetworkGraph(w, h, ctx) {
    const cx = w / 2;
    const cy = h / 2 - 10 * this.dpr;
    const R = Math.min(w, h) * 0.36;

    // 1. Fond avec dégradé radial immersif
    const bgGrad = ctx.createRadialGradient(cx, cy, 20 * this.dpr, cx, cy, R * 1.35);
    bgGrad.addColorStop(0, "#111827");
    bgGrad.addColorStop(0.65, "#0b0f19");
    bgGrad.addColorStop(1, "#06090e");
    ctx.fillStyle = bgGrad;
    ctx.fillRect(0, 0, w, h);

    // 2. Cercles d'orbite / concentric rings
    ctx.strokeStyle = "rgba(255, 255, 255, 0.04)";
    ctx.lineWidth = 1 * this.dpr;
    for (const factor of [0.45, 0.75, 1.0, 1.18]) {
      ctx.beginPath();
      ctx.arc(cx, cy, R * factor, 0, Math.PI * 2);
      ctx.stroke();
    }

    // 3. Cœur du village (Place Centrale)
    ctx.font = `${22 * this.dpr}px sans-serif`;
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    ctx.fillText("🏛️", cx, cy - 8 * this.dpr);
    ctx.font = `700 ${10 * this.dpr}px 'Plus Jakarta Sans', sans-serif`;
    ctx.fillStyle = "#94a3b8";
    ctx.fillText("PLACE DU MARCHÉ", cx, cy + 16 * this.dpr);
    ctx.font = `500 ${8 * this.dpr}px 'Plus Jakarta Sans', sans-serif`;
    ctx.fillStyle = "#64748b";
    ctx.fillText("Réseau de Confiance", cx, cy + 28 * this.dpr);

    // 4. Calcul des coordonnées des 12 nœuds
    this.networkNodePositions = {};
    const n = NETWORK_AGENT_ORDER.length;
    NETWORK_AGENT_ORDER.forEach((id, i) => {
      const angle = (i / n) * Math.PI * 2 - Math.PI / 2;
      const nx = cx + Math.cos(angle) * R;
      const ny = cy + Math.sin(angle) * R;
      this.networkNodePositions[id] = {
        x: nx,
        y: ny,
        radius: 22 * this.dpr,
        angle,
      };
    });

    // 5. Liens sociaux (Arêtes)
    const activeHop = this.rumorHops.length > 0 ? this.rumorHops[this.rumorHops.length - 1] : null;

    SOCIAL_RELATIONSHIPS.forEach((rel) => {
      const p1 = this.networkNodePositions[rel.source];
      const p2 = this.networkNodePositions[rel.target];
      if (!p1 || !p2) return;

      const isFocused =
        rel.source === this.selectedAgentId ||
        rel.target === this.selectedAgentId ||
        rel.source === this.hoveredAgentId ||
        rel.target === this.hoveredAgentId;

      ctx.beginPath();
      ctx.moveTo(p1.x, p1.y);
      ctx.lineTo(p2.x, p2.y);

      if (isFocused) {
        ctx.strokeStyle = "rgba(56, 189, 248, 0.85)";
        ctx.lineWidth = 3 * this.dpr;
        ctx.shadowColor = "#38bdf8";
        ctx.shadowBlur = 8 * this.dpr;
        ctx.stroke();
        ctx.shadowBlur = 0;

        // Label de la relation au centre
        const mx = (p1.x + p2.x) / 2;
        const my = (p1.y + p2.y) / 2;
        ctx.font = `600 ${8.5 * this.dpr}px 'Plus Jakarta Sans', sans-serif`;
        const labelText = rel.label;
        const textMetrics = ctx.measureText(labelText);
        const padX = 6 * this.dpr;
        const padY = 3 * this.dpr;

        ctx.fillStyle = "rgba(15, 23, 42, 0.92)";
        ctx.fillRect(
          mx - textMetrics.width / 2 - padX,
          my - 7 * this.dpr - padY,
          textMetrics.width + padX * 2,
          14 * this.dpr + padY * 2
        );
        ctx.strokeStyle = "#38bdf8";
        ctx.lineWidth = 1 * this.dpr;
        ctx.strokeRect(
          mx - textMetrics.width / 2 - padX,
          my - 7 * this.dpr - padY,
          textMetrics.width + padX * 2,
          14 * this.dpr + padY * 2
        );

        ctx.fillStyle = "#38bdf8";
        ctx.textAlign = "center";
        ctx.textBaseline = "middle";
        ctx.fillText(labelText, mx, my);
      } else {
        ctx.strokeStyle = `rgba(148, 163, 184, ${0.14 + rel.strength * 0.15})`;
        ctx.lineWidth = (1 + rel.strength * 1.5) * this.dpr;
        ctx.stroke();
      }
    });

    // 6. Impulsion animée de transmission (Particule lumineuse le long de l'arête active)
    if (activeHop && activeHop.sender && activeHop.receiver) {
      const pSrc = this.networkNodePositions[activeHop.sender];
      const pDst = this.networkNodePositions[activeHop.receiver];
      if (pSrc && pDst) {
        const tPulse = (Date.now() % 1200) / 1200.0;
        const px = pSrc.x + (pDst.x - pSrc.x) * tPulse;
        const py = pSrc.y + (pDst.y - pSrc.y) * tPulse;

        let pulseColor = "#38bdf8";
        if (activeHop.fact_id === "R1_fermeture_marche") pulseColor = "#f43f5e";
        else if (activeHop.fact_id === "R2_dementi_maire") pulseColor = "#06b6d4";
        else if (activeHop.fact_id === "R3_ouverture_marche") pulseColor = "#10b981";

        ctx.beginPath();
        ctx.arc(px, py, 6 * this.dpr, 0, Math.PI * 2);
        ctx.fillStyle = pulseColor;
        ctx.shadowColor = pulseColor;
        ctx.shadowBlur = 12 * this.dpr;
        ctx.fill();
        ctx.shadowBlur = 0;
      }
    }

    // 7. Dessin des nœuds (Habitants)
    NETWORK_AGENT_ORDER.forEach((id) => {
      const pos = this.networkNodePositions[id];
      const a = this.agentsState[id];
      const meta = AGENTS_META[id];
      if (!pos || !a || !meta) return;

      const isSelected = id === this.selectedAgentId;
      const isHovered = id === this.hoveredAgentId;

      const r1 = a.believedFacts["R1_fermeture_marche"] || 0;
      const r2 = a.believedFacts["R2_dementi_maire"] || 0;
      const r3 = a.believedFacts["R3_ouverture_marche"] || 0;

      let haloColor = "#64748b";
      let statusText = "Serein";
      let statusColor = "#94a3b8";

      if (r3 >= 0.55) {
        haloColor = "#10b981";
        statusText = `Marché Ouvert (${(r3 * 100).toFixed(0)}%)`;
        statusColor = "#10b981";
      } else if (r2 >= 0.60) {
        haloColor = "#06b6d4";
        statusText = `Démenti R2 (${(r2 * 100).toFixed(0)}%)`;
        statusColor = "#06b6d4";
      } else if (r1 >= 0.55) {
        haloColor = "#f43f5e";
        statusText = `Rumeur R1 (${(r1 * 100).toFixed(0)}%)`;
        statusColor = "#f43f5e";
      }

      // Cercle de panique / stockage de provisions (pointillés tournants en orange)
      if (a.didStock) {
        ctx.save();
        ctx.beginPath();
        ctx.arc(pos.x, pos.y, 30 * this.dpr, 0, Math.PI * 2);
        ctx.strokeStyle = "#f59e0b";
        ctx.lineWidth = 2 * this.dpr;
        ctx.setLineDash([4 * this.dpr, 4 * this.dpr]);
        ctx.lineDashOffset = (Date.now() / 45) % 8;
        ctx.stroke();
        ctx.restore();
      }

      // Halo externe
      ctx.beginPath();
      ctx.arc(pos.x, pos.y, (isSelected ? 26 : 23) * this.dpr, 0, Math.PI * 2);
      ctx.fillStyle = isSelected ? "rgba(255, 255, 255, 0.15)" : isHovered ? "rgba(56, 189, 248, 0.18)" : "transparent";
      ctx.fill();

      // Corps du nœud
      ctx.beginPath();
      ctx.arc(pos.x, pos.y, 20 * this.dpr, 0, Math.PI * 2);
      ctx.fillStyle = "#1e293b";
      ctx.fill();

      ctx.strokeStyle = isSelected ? "#ffffff" : isHovered ? "#38bdf8" : haloColor;
      ctx.lineWidth = (isSelected ? 3.5 : isHovered ? 3 : 2) * this.dpr;
      if (isSelected || isHovered) {
        ctx.shadowColor = isSelected ? "#ffffff" : "#38bdf8";
        ctx.shadowBlur = 10 * this.dpr;
      }
      ctx.stroke();
      ctx.shadowBlur = 0;

      // Avatar emoji
      ctx.font = `${18 * this.dpr}px sans-serif`;
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";
      ctx.fillText(meta.avatar, pos.x, pos.y);

      // Bulle si en train de parler
      if (a.isTalking) {
        ctx.font = `${13 * this.dpr}px sans-serif`;
        ctx.fillText("💬", pos.x + 16 * this.dpr, pos.y - 14 * this.dpr);
      }

      // Nom de l'agent
      ctx.font = `700 ${10 * this.dpr}px 'Plus Jakarta Sans', sans-serif`;
      ctx.fillStyle = isSelected ? "#ffffff" : isHovered ? "#38bdf8" : "#e2e8f0";
      ctx.fillText(a.name, pos.x, pos.y + 28 * this.dpr);

      // Badge de croyance
      ctx.font = `600 ${8 * this.dpr}px 'Plus Jakarta Sans', sans-serif`;
      ctx.fillStyle = statusColor;
      ctx.fillText(statusText, pos.x, pos.y + 40 * this.dpr);
    });
  }
}

// Initialisation au chargement du DOM (robuste à readyState)
function initHameau() {
  if (window.hameauViewer) return;
  window.hameauViewer = new HameauViewer();
  // Chargement automatique : live_run.jsonl en priorité, puis sample_run.jsonl
  fetch("live_run.jsonl")
    .then((r) => {
      if (r.ok) return r.text();
      return fetch("sample_run.jsonl").then((r2) => r2.text());
    })
    .then((txt) => window.hameauViewer.loadJSONLContent(txt))
    .catch(() => console.log("Prêt pour chargement JSONL"));
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", initHameau);
} else {
  initHameau();
}
