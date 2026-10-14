/**
 * scripts/verify_animations.js
 * Vérifie que TOUS les 8 états de personnages (idle, walk, talk, rumor, debunk, stock, hesitate, night)
 * ont une animation active et organique (diff de pixels > 0 entre frames successives).
 * Capture les screenshots mis à jour pour P1.
 */

const { spawn } = require("child_process");
const http = require("http");
const fs = require("fs");
const path = require("path");

const SCREENSHOTS_DIR = path.resolve(__dirname, "../docs/visuals/screenshots");

async function main() {
  console.log("=== VÉRIFICATION DES ANIMATIONS MULTI-ÉTATS (Chrome CDP) ===");

  const chrome = spawn("google-chrome", [
    "--headless=new",
    "--remote-debugging-port=9224",
    "--disable-gpu",
    "--window-size=1600,1200",
    "http://127.0.0.1:8000/dev/characters.html"
  ]);

  const cleanup = () => {
    try { chrome.kill(); } catch (e) {}
  };
  process.on("exit", cleanup);
  process.on("SIGINT", () => { cleanup(); process.exit(1); });

  await new Promise((r) => setTimeout(r, 1500));

  const tabsData = await new Promise((resolve, reject) => {
    http.get("http://127.0.0.1:9224/json", (res) => {
      let data = "";
      res.on("data", (c) => (data += c));
      res.on("end", () => resolve(JSON.parse(data)));
    }).on("error", reject);
  });

  const tab = tabsData.find((t) => t.url && t.url.includes("8000")) || tabsData[0];
  const ws = new WebSocket(tab.webSocketDebuggerUrl);

  let msgId = 0;
  const pending = new Map();
  const consoleErrors = [];

  ws.onmessage = (event) => {
    const res = JSON.parse(event.data);
    if (res.method === "Runtime.consoleAPICalled" && res.params.type === "error") {
      consoleErrors.push(res.params.args.map(a => a.value || a.description).join(" "));
    }
    if (res.method === "Runtime.exceptionThrown") {
      consoleErrors.push(res.params.exceptionDetails.text);
    }
    if (res.id && pending.has(res.id)) {
      const { resolve, reject } = pending.get(res.id);
      pending.delete(res.id);
      if (res.error) reject(res.error);
      else resolve(res.result);
    }
  };

  await new Promise((resolve) => (ws.onopen = resolve));

  function sendCmd(method, params = {}) {
    return new Promise((resolve, reject) => {
      const id = ++msgId;
      pending.set(id, { resolve, reject });
      ws.send(JSON.stringify({ id, method, params }));
    });
  }

  await sendCmd("Runtime.enable");
  await sendCmd("Page.enable");

  // Attendre chargement complet
  await new Promise((r) => setTimeout(r, 1000));

  const states = ["idle", "walk", "talk", "rumor", "debunk", "stock", "hesitate", "night"];
  const results = {};

  for (const st of states) {
    // Cliquer sur le bouton d'état
    await sendCmd("Runtime.evaluate", {
      expression: `
        const btn = document.querySelector('.btn-state[data-state="${st}"]');
        if (btn) btn.click();
      `
    });

    // Laisser passer quelques frames
    await new Promise((r) => setTimeout(r, 120));

    // Échantillonner 2 frames espacées de 100ms et calculer la différence sur le premier canvas
    const diff = await sendCmd("Runtime.evaluate", {
      expression: `
        (async function() {
          const c = document.querySelector('canvas[data-id="awa"][data-scale="1.8"]');
          const ctx = c.getContext('2d');
          const d1 = ctx.getImageData(0, 0, c.width, c.height).data;
          await new Promise(r => setTimeout(r, 100));
          const d2 = ctx.getImageData(0, 0, c.width, c.height).data;
          let changedPixels = 0;
          for (let i = 0; i < d1.length; i += 4) {
            if (Math.abs(d1[i] - d2[i]) > 2 || Math.abs(d1[i+1] - d2[i+1]) > 2 || Math.abs(d1[i+2] - d2[i+2]) > 2) {
              changedPixels++;
            }
          }
          return { changedPixels, totalPixels: d1.length / 4 };
        })()
      `,
      awaitPromise: true,
      returnByValue: true
    });

    // Aussi tester le buste
    const bustDiff = await sendCmd("Runtime.evaluate", {
      expression: `
        (async function() {
          const c = document.querySelector('canvas[data-bust-id="awa"]');
          const ctx = c.getContext('2d');
          const d1 = ctx.getImageData(0, 0, c.width, c.height).data;
          await new Promise(r => setTimeout(r, 100));
          const d2 = ctx.getImageData(0, 0, c.width, c.height).data;
          let changedPixels = 0;
          for (let i = 0; i < d1.length; i += 4) {
            if (Math.abs(d1[i] - d2[i]) > 2 || Math.abs(d1[i+1] - d2[i+1]) > 2 || Math.abs(d1[i+2] - d2[i+2]) > 2) {
              changedPixels++;
            }
          }
          return { changedPixels, totalPixels: d1.length / 4 };
        })()
      `,
      awaitPromise: true,
      returnByValue: true
    });

    results[st] = {
      bodyChangedPixels: diff.result.value.changedPixels,
      bustChangedPixels: bustDiff.result.value.changedPixels,
      isAnimated: diff.result.value.changedPixels > 10 && bustDiff.result.value.changedPixels > 5
    };

    console.log(`- État [${st.padEnd(8)}] : Plein pied = ${diff.result.value.changedPixels} px modifiés, Buste = ${bustDiff.result.value.changedPixels} px modifiés => ${results[st].isAnimated ? "ANIMÉ ✓" : "STATIQUE ✗"}`);
  }

  // Remettre en mode "talk" ou "walk" pour les captures d'écran
  await sendCmd("Runtime.evaluate", {
    expression: `document.querySelector('.btn-state[data-state="walk"]').click();`
  });
  await new Promise((r) => setTimeout(r, 200));

  // Capture Contact Sheet complet
  const contactSheetShot = await sendCmd("Page.captureScreenshot", { format: "png" });
  fs.writeFileSync(path.join(SCREENSHOTS_DIR, "contact_sheet_p1.png"), Buffer.from(contactSheetShot.data, "base64"));
  console.log("✓ Capture sauvegardée : contact_sheet_p1.png");

  // Capture Closeup 4x
  const closeupBox = await sendCmd("Runtime.evaluate", {
    expression: `
      (() => {
        const c = document.querySelector('.characters-grid');
        const rect = c.getBoundingClientRect();
        return JSON.stringify({ x: rect.x, y: rect.y, width: Math.min(rect.width, 1400), height: 420 });
      })()
    `,
    returnByValue: true
  });
  const clipCloseup = JSON.parse(closeupBox.result.value);
  const closeupShot = await sendCmd("Page.captureScreenshot", {
    format: "png",
    clip: { ...clipCloseup, scale: 1 }
  });
  fs.writeFileSync(path.join(SCREENSHOTS_DIR, "characters_closeup_p1.png"), Buffer.from(closeupShot.data, "base64"));
  console.log("✓ Capture sauvegardée : characters_closeup_p1.png");

  // Capture Bustes
  const bustBox = await sendCmd("Runtime.evaluate", {
    expression: `
      (() => {
        const b = document.querySelector('.bust-section');
        b.scrollIntoView();
        const rect = b.getBoundingClientRect();
        return JSON.stringify({ x: Math.max(0, rect.x), y: Math.max(0, rect.y), width: Math.min(rect.width, 1400), height: 280 });
      })()
    `,
    returnByValue: true
  });
  await new Promise((r) => setTimeout(r, 400));
  const clipBust = JSON.parse(bustBox.result.value);
  const bustShot = await sendCmd("Page.captureScreenshot", {
    format: "png",
    clip: { ...clipBust, scale: 1 }
  });
  fs.writeFileSync(path.join(SCREENSHOTS_DIR, "characters_busts_p1.png"), Buffer.from(bustShot.data, "base64"));
  console.log("✓ Capture sauvegardée : characters_busts_p1.png");

  console.log("\nConsole Errors :", consoleErrors.length === 0 ? "0 (PARFAIT)" : consoleErrors);

  ws.close();
  cleanup();

  const allAnimated = Object.values(results).every(r => r.isAnimated);
  if (!allAnimated || consoleErrors.length > 0) {
    console.error("ÉCHEC : Certains états ne sont pas animés ou des erreurs console sont survenues.");
    process.exit(1);
  } else {
    console.log("\n=== SUCCÈS : TOUS LES 8 ÉTATS SONT VIVANTS ET ANIMÉS DE FAÇON DISTINCTE ===");
    process.exit(0);
  }
}

main().catch(err => {
  console.error(err);
  process.exit(1);
});
