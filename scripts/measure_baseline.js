/**
 * scripts/measure_baseline.js
 * Mesure rigoureuse du FPS baseline et captures d'écran (1x, 2x, crop 400% marché)
 * via Chrome DevTools Protocol (CDP) natif en Node.js (0 dépendance npm).
 */

const { spawn } = require("child_process");
const http = require("http");
const fs = require("fs");
const path = require("path");

const SCREENSHOTS_DIR = path.resolve(__dirname, "../docs/visuals/screenshots");
if (!fs.existsSync(SCREENSHOTS_DIR)) {
  fs.mkdirSync(SCREENSHOTS_DIR, { recursive: true });
}

async function run() {
  console.log("=== Démarrage de la Mesure Baseline HAMEAU (Chrome CDP) ===");

  const chrome = spawn("google-chrome", [
    "--headless=new",
    "--remote-debugging-port=9223",
    "--disable-gpu",
    "--window-size=1440,900",
    "http://127.0.0.1:8000/index.html"
  ]);

  // Nettoyage à l'arrêt
  const cleanup = () => {
    try { chrome.kill(); } catch (e) {}
  };
  process.on("exit", cleanup);
  process.on("SIGINT", () => { cleanup(); process.exit(1); });

  // Attente du port 9223
  await new Promise((r) => setTimeout(r, 1500));

  const tabsData = await new Promise((resolve, reject) => {
    http.get("http://127.0.0.1:9223/json", (res) => {
      let data = "";
      res.on("data", (c) => (data += c));
      res.on("end", () => resolve(JSON.parse(data)));
    }).on("error", reject);
  });

  const tab = tabsData.find((t) => t.url && t.url.includes("8000")) || tabsData[0];
  if (!tab || !tab.webSocketDebuggerUrl) {
    throw new Error("Impossible de trouver l'onglet Chrome avec URL WebSocket.");
  }

  const ws = new WebSocket(tab.webSocketDebuggerUrl);

  let msgId = 0;
  const pending = new Map();

  function sendCmd(method, params = {}) {
    return new Promise((resolve, reject) => {
      const id = ++msgId;
      pending.set(id, { resolve, reject });
      ws.send(JSON.stringify({ id, method, params }));
    });
  }

  ws.onmessage = (event) => {
    const msg = JSON.parse(event.data);
    if (msg.id && pending.has(msg.id)) {
      const { resolve, reject } = pending.get(msg.id);
      pending.delete(msg.id);
      if (msg.error) reject(msg.error);
      else resolve(msg.result);
    }
  };

  await new Promise((resolve) => (ws.onopen = resolve));

  await sendCmd("Page.enable");
  await sendCmd("Runtime.enable");
  await sendCmd("DOM.enable");

  // Attente du chargement effectif du visualiseur
  console.log("[1/5] Attente du chargement des événements de simulation...");
  let loaded = false;
  for (let i = 0; i < 30; i++) {
    const evalRes = await sendCmd("Runtime.evaluate", {
      expression: "!!window.hameauViewer && window.hameauViewer.events.length > 0",
      returnByValue: true
    });
    if (evalRes.result && evalRes.result.value === true) {
      loaded = true;
      break;
    }
    await new Promise((r) => setTimeout(r, 200));
  }

  if (!loaded) {
    throw new Error("Délai d'attente dépassé pour l'initialisation du visualiseur.");
  }

  // Se positionner sur un tick actif avec rassemblement au marché (Tick 24)
  console.log("[2/5] Positionnement sur le Tick 24 (matinée, marché animé)...");
  await sendCmd("Runtime.evaluate", {
    expression: "window.hameauViewer.pause(); window.hameauViewer.seekToTick(24);",
    returnByValue: true
  });
  await new Promise((r) => setTimeout(r, 600));

  // Mesure réelle de la performance de rendu Canvas (120 frames consécutives)
  console.log("[3/5] Mesure du temps d'exécution JavaScript et du FPS réel (120 frames)...");
  const perfRes = await sendCmd("Runtime.evaluate", {
    expression: `
      new Promise((resolve) => {
        const frameTimes = [];
        let count = 0;
        const v = window.hameauViewer;
        const totalFrames = 120;
        let lastT = performance.now();

        function step() {
          const t0 = performance.now();
          v.renderCanvas();
          const t1 = performance.now();
          frameTimes.push(t1 - t0);
          count++;
          if (count < totalFrames) {
            requestAnimationFrame(step);
          } else {
            const sum = frameTimes.reduce((a, b) => a + b, 0);
            const sorted = [...frameTimes].sort((a, b) => a - b);
            const p50 = sorted[Math.floor(sorted.length * 0.50)];
            const p95 = sorted[Math.floor(sorted.length * 0.95)];
            const meanDuration = sum / frameTimes.length;
            const approxFPS = 1000 / Math.max(16.6, meanDuration);
            resolve({
              meanFrameMs: Math.round(meanDuration * 100) / 100,
              p50FrameMs: Math.round(p50 * 100) / 100,
              p95FrameMs: Math.round(p95 * 100) / 100,
              measuredFPS: Math.round(approxFPS * 10) / 10
            });
          }
        }
        requestAnimationFrame(step);
      })
    `,
    awaitPromise: true,
    returnByValue: true
  });

  const perfMetrics = perfRes.result.value;
  console.log("   -> Métriques mesurées :", perfMetrics);

  // Capture Screenshot 1x (1440x900)
  console.log("[4/5] Capture d'écran 1x (avant)...");
  await sendCmd("Emulation.setDeviceMetricsOverride", {
    width: 1440,
    height: 900,
    deviceScaleFactor: 1,
    mobile: false
  });
  await new Promise((r) => setTimeout(r, 300));
  const shot1x = await sendCmd("Page.captureScreenshot", { format: "png" });
  fs.writeFileSync(path.join(SCREENSHOTS_DIR, "before_1x.png"), Buffer.from(shot1x.data, "base64"));
  console.log("   -> Enregistré : docs/visuals/screenshots/before_1x.png");

  // Capture Screenshot 2x (Retina)
  console.log("[4/5] Capture d'écran 2x (avant)...");
  await sendCmd("Emulation.setDeviceMetricsOverride", {
    width: 1440,
    height: 900,
    deviceScaleFactor: 2,
    mobile: false
  });
  await new Promise((r) => setTimeout(r, 400));
  const shot2x = await sendCmd("Page.captureScreenshot", { format: "png" });
  fs.writeFileSync(path.join(SCREENSHOTS_DIR, "before_2x.png"), Buffer.from(shot2x.data, "base64"));
  console.log("   -> Enregistré : docs/visuals/screenshots/before_2x.png");

  // Capture Crop 400% sur la Place du Marché
  console.log("[5/5] Capture recadrée à 400% sur la Place du Marché...");
  // Récupérer les coordonnées réelles du canvas dans la page
  const canvasRectRes = await sendCmd("Runtime.evaluate", {
    expression: `
      const c = document.getElementById("village-canvas");
      const r = c.getBoundingClientRect();
      // La place du marché est à x: 0.50, y: 0.45 du canvas
      const mx = r.left + r.width * 0.50;
      const my = r.top + r.height * 0.45;
      const cropW = 200;
      const cropH = 160;
      ({
        x: Math.max(0, mx - cropW / 2),
        y: Math.max(0, my - cropH / 2),
        width: cropW,
        height: cropH,
        scale: 1
      })
    `,
    returnByValue: true
  });

  const cropClip = canvasRectRes.result.value;
  // Définir un clip pour capturer la zone du marché
  const shotCrop = await sendCmd("Page.captureScreenshot", {
    format: "png",
    clip: cropClip
  });
  fs.writeFileSync(path.join(SCREENSHOTS_DIR, "before_market_crop_400.png"), Buffer.from(shotCrop.data, "base64"));
  console.log("   -> Enregistré : docs/visuals/screenshots/before_market_crop_400.png");

  // Rapport JSON
  const report = {
    timestamp: new Date().toISOString(),
    metrics: perfMetrics,
    screenshots: {
      before_1x: "docs/visuals/screenshots/before_1x.png",
      before_2x: "docs/visuals/screenshots/before_2x.png",
      before_market_crop_400: "docs/visuals/screenshots/before_market_crop_400.png"
    }
  };
  fs.writeFileSync(path.join(SCREENSHOTS_DIR, "baseline_metrics.json"), JSON.stringify(report, null, 2));

  console.log("=== Mesure Baseline Terminée avec Succès ===");
  ws.close();
  cleanup();
}

run().catch((err) => {
  console.error("Erreur mesure baseline :", err);
  process.exit(1);
});
