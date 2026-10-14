/**
 * viewer/dev/character_renderer.js
 * Moteur de rendu procédural 2D pour les habitants du HAMEAU.
 * Direction artistique éditoriale semi-réaliste (~7 têtes), volumes ombrés,
 * anatomie articulée, lumière orientée à 45° et accessoires distinctifs.
 * 
 * Licence : Apache-2.0
 */

// Définitions canoniques des 12 habitants du Hameau
const HAMEAU_CHARACTERS = {
  awa: {
    id: "awa",
    name: "Awa",
    role: "Boulangère",
    age: 42,
    gender: "f",
    build: "robust",
    skin: { base: "#5c3826", shadow: "#3e2316", highlight: "#784b33" },
    hair: { color: "#1c1917", style: "turban_white" },
    eyes: { color: "#2d1b12" },
    palette: {
      primary: "#d97706",      // Robe moutarde
      primaryShadow: "#92400e",
      secondary: "#f5efe6",    // Tablier écru lin
      secondaryShadow: "#dcd2c4",
      trousers: "#78350f",
      trim: "#1c1917"
    },
    accessory: "bread_basket"
  },
  kofi: {
    id: "kofi",
    name: "Kofi",
    role: "Maire du Hameau",
    age: 51,
    gender: "m",
    build: "commanding",
    skin: { base: "#825338", shadow: "#5c3520", highlight: "#9f6a4b" },
    hair: { color: "#2d2a29", style: "short_greying", beard: "short_neat" },
    eyes: { color: "#261911" },
    palette: {
      primary: "#1e293b",      // Costume bleu marine
      primaryShadow: "#0f172a",
      secondary: "#f8fafc",    // Chemise blanche
      secondaryShadow: "#cbd5e1",
      trousers: "#1e293b",
      sash: "#881337",         // Écharpe municipale bordeaux
      trim: "#475569"
    },
    accessory: "mayoral_sash"
  },
  yao: {
    id: "yao",
    name: "Yao",
    role: "Livreur du marché",
    age: 28,
    gender: "m",
    build: "athletic",
    skin: { base: "#b57a52", shadow: "#844e2e", highlight: "#cb8e65" },
    hair: { color: "#1c1917", style: "newsboy_cap" },
    eyes: { color: "#362216" },
    palette: {
      primary: "#2d4a6e",      // Veste indigo
      primaryShadow: "#1b2f4a",
      secondary: "#f1f5f9",    // T-shirt chiné
      secondaryShadow: "#cbd5e1",
      trousers: "#475569",
      cap: "#1e3a5f",
      trim: "#1e293b"
    },
    accessory: "wooden_crate"
  },
  elise: {
    id: "elise",
    name: "Élise",
    role: "Institutrice",
    age: 36,
    gender: "f",
    build: "slender",
    skin: { base: "#ecc3a2", shadow: "#be9070", highlight: "#f5d7bf" },
    hair: { color: "#543310", style: "bun_pencil" },
    eyes: { color: "#22543d" },
    palette: {
      primary: "#1e3a2f",      // Jupe vert forêt
      primaryShadow: "#11221c",
      secondary: "#881337",    // Châle bordeaux
      secondaryShadow: "#4c0519",
      blouse: "#fdf8f0",
      trousers: "#1e3a2f",
      trim: "#b45309"
    },
    accessory: "glasses_book"
  },
  samuel: {
    id: "samuel",
    name: "Samuel",
    role: "Forgeron",
    age: 48,
    gender: "m",
    build: "stocky",
    skin: { base: "#a36e49", shadow: "#744627", highlight: "#ba835d" },
    hair: { color: "#262626", style: "tied_back", beard: "heavy_beard" },
    eyes: { color: "#291b12" },
    palette: {
      primary: "#78350f",      // Tablier cuir lourd
      primaryShadow: "#451a03",
      secondary: "#334155",    // Chemise de travail
      secondaryShadow: "#1e293b",
      trousers: "#1c1917",
      trim: "#d97706"
    },
    accessory: "blacksmith_hammer"
  },
  nadia: {
    id: "nadia",
    name: "Nadia",
    role: "Médecin",
    age: 39,
    gender: "f",
    build: "slender",
    skin: { base: "#d29d75", shadow: "#a36e49", highlight: "#e1b490" },
    hair: { color: "#0f172a", style: "sharp_bob" },
    eyes: { color: "#1e293b" },
    palette: {
      primary: "#f8fafc",      // Blouse médicale immaculée
      primaryShadow: "#cbd5e1",
      secondary: "#0284c7",    // Col stéthoscope bleu ciel
      secondaryShadow: "#0369a1",
      trousers: "#334155",
      trim: "#64748b"
    },
    accessory: "stethoscope"
  },
  tom: {
    id: "tom",
    name: "Tom",
    role: "Apprenti café",
    age: 21,
    gender: "m",
    build: "lanky",
    skin: { base: "#d8a47f", shadow: "#aa7451", highlight: "#e5b999" },
    hair: { color: "#451a03", style: "tousled_bangs" },
    eyes: { color: "#1f2937" },
    palette: {
      primary: "#c2410c",      // Sweat rouille à capuche
      primaryShadow: "#7c2d12",
      secondary: "#3b82f6",    // Jean bleu
      secondaryShadow: "#1d4ed8",
      trousers: "#1e3a5f",
      trim: "#0f172a"
    },
    accessory: "headphones_backpack"
  },
  mariam: {
    id: "mariam",
    name: "Mariam",
    role: "Marchande légumes",
    age: 45,
    gender: "f",
    build: "generous",
    skin: { base: "#825338", shadow: "#5c3520", highlight: "#9f6a4b" },
    hair: { color: "#18181b", style: "turban_green" },
    eyes: { color: "#2d1b12" },
    palette: {
      primary: "#b45309",      // Tunique terre de sienne
      primaryShadow: "#78350f",
      secondary: "#4d7c0f",    // Grand tablier vert maraîcher
      secondaryShadow: "#365314",
      trousers: "#3b2314",
      trim: "#f59e0b"
    },
    accessory: "vegetable_basket"
  },
  paul: {
    id: "paul",
    name: "Paul",
    role: "Pêcheur retraité",
    age: 68,
    gender: "m",
    build: "stooped",
    skin: { base: "#c99b79", shadow: "#966847", highlight: "#dcb08f" },
    hair: { color: "#e2e8f0", style: "white_curly", beard: "white_bushy" },
    eyes: { color: "#0369a1" },
    palette: {
      primary: "#eab308",      // Ciré jaune patiné
      primaryShadow: "#a16207",
      secondary: "#f1f5f9",    // Gilet en laine
      secondaryShadow: "#94a3b8",
      trousers: "#451a03",
      cap: "#1e293b",
      trim: "#0f172a"
    },
    accessory: "fishing_cane"
  },
  lea: {
    id: "lea",
    name: "Léa",
    role: "Bibliothécaire",
    age: 31,
    gender: "f",
    build: "slender",
    skin: { base: "#ecc3a2", shadow: "#be9070", highlight: "#f5d7bf" },
    hair: { color: "#b91c1c", style: "long_wavy_red" },
    eyes: { color: "#15803d" },
    palette: {
      primary: "#4d7c0f",      // Cardigan vert sauge
      primaryShadow: "#365314",
      secondary: "#fffbeb",    // Robe crème
      secondaryShadow: "#fef3c7",
      trousers: "#14532d",
      trim: "#b45309"
    },
    accessory: "book_tote"
  },
  ibrahim: {
    id: "ibrahim",
    name: "Ibrahim",
    role: "Agriculteur",
    age: 54,
    gender: "m",
    build: "tall_lean",
    skin: { base: "#5c3826", shadow: "#3e2316", highlight: "#784b33" },
    hair: { color: "#27272a", style: "straw_hat", beard: "salt_pepper_stache" },
    eyes: { color: "#18181b" },
    palette: {
      primary: "#0369a1",      // Salopette bleu fermier
      primaryShadow: "#075985",
      secondary: "#991b1b",    // Chemise carreaux
      secondaryShadow: "#7f1d1d",
      trousers: "#0369a1",
      hat: "#eab308",
      trim: "#78350f"
    },
    accessory: "straw_hat_pitchfork"
  },
  claire: {
    id: "claire",
    name: "Claire",
    role: "Rédactrice Gazette",
    age: 34,
    gender: "f",
    build: "dynamic",
    skin: { base: "#d29d75", shadow: "#a36e49", highlight: "#e1b490" },
    hair: { color: "#18181b", style: "high_ponytail" },
    eyes: { color: "#1e3a5f" },
    palette: {
      primary: "#0f766e",      // Veste velours vert émeraude
      primaryShadow: "#115e59",
      secondary: "#f8fafc",    // Chemisier blanc
      secondaryShadow: "#e2e8f0",
      trousers: "#0f172a",
      bag: "#78350f",
      trim: "#0d9488"
    },
    accessory: "press_notebook"
  }
};

/**
 * Moteur de dessin anatomique procédural.
 */
class CharacterRenderer2D {
  constructor() {
    this.cache = new Map();
  }

  /**
   * Dessine un personnage complet sur un contexte 2D donné.
   * @param {CanvasRenderingContext2D} ctx - Contexte de dessin
   * @param {Object} charDef - Définition de l'habitant (HAMEAU_CHARACTERS[id])
   * @param {Object} state - État dynamique de simulation
   * @param {Object} opts - Options de rendu (taille, buste, LOD)
   */
  draw(ctx, charDef, state = {}, opts = {}) {
    const scale = opts.scale || 1.0;
    const isPortrait = opts.isPortrait || false;
    const tick = state.tick || 0;
    const agentSeed = (charDef.name.charCodeAt(0) * 17 + charDef.age * 31) % 1000;

    // Cinématique temporelle déterministe
    const breathPhase = (tick * 0.12 + agentSeed) % (Math.PI * 2);
    const breathY = Math.sin(breathPhase) * 1.5;

    // Détection de clignement déterministe (fermeture de 150ms toutes les 4s environ)
    const blinkCycle = (tick + agentSeed * 3) % 48;
    const isBlinking = blinkCycle === 0 || blinkCycle === 1;

    // Cinématique de marche
    const isWalking = state.isWalking || false;
    const walkPhase = isWalking ? (tick * 0.45) % (Math.PI * 2) : 0;
    const stride = isWalking ? Math.sin(walkPhase) : 0;
    const bobbing = isWalking ? Math.abs(Math.cos(walkPhase)) * 2 : 0;

    ctx.save();
    ctx.translate(opts.x || 0, opts.y || 0);
    ctx.scale(scale, scale);

    // 1. Ombre portée au sol (pour les personnages en pied uniquement)
    if (!isPortrait) {
      this.drawGroundShadow(ctx, charDef, stride);
    }

    if (isPortrait) {
      // Rendu Buste Haute Résolution (pour l'Inspecteur d'Agent et la Gazette)
      this.drawBustPortrait(ctx, charDef, state, { breathY, isBlinking });
    } else {
      // Rendu Sprite Entier Corps (~7 têtes)
      this.drawFullBody(ctx, charDef, state, { breathY, isBlinking, stride, bobbing });
    }

    // 2. Filtre de nuit si sommeil ou nocturne
    if (state.isNight) {
      ctx.fillStyle = "rgba(30, 41, 59, 0.35)";
      ctx.fillRect(-35, -95, 70, 110);
    }

    ctx.restore();
  }

  drawGroundShadow(ctx, charDef, stride) {
    const rx = 18 + Math.abs(stride) * 3;
    const ry = 6;
    const grad = ctx.createRadialGradient(0, 0, 2, 0, 0, rx);
    grad.addColorStop(0, "rgba(15, 23, 42, 0.55)");
    grad.addColorStop(0.6, "rgba(15, 23, 42, 0.25)");
    grad.addColorStop(1, "rgba(15, 23, 42, 0)");

    ctx.save();
    ctx.scale(1, ry / rx);
    ctx.beginPath();
    ctx.arc(0, 0, rx, 0, Math.PI * 2);
    ctx.fillStyle = grad;
    ctx.fill();
    ctx.restore();
  }

  drawFullBody(ctx, charDef, state, anim) {
    const { breathY, isBlinking, stride, bobbing } = anim;
    const skin = charDef.skin;
    const pal = charDef.palette;

    ctx.save();
    ctx.translate(0, -bobbing);

    // --- COUCHE 1 : JAMBES & PIEDS ---
    const legOffset = stride * 6;
    // Jambe Arrière (gauche)
    this.drawLimb(ctx, -5 - legOffset, -30, -6 - legOffset, -2, 5, pal.trousers || pal.primaryShadow, "#0f172a");
    // Chaussure Arrière
    ctx.fillStyle = "#1e293b";
    ctx.beginPath();
    ctx.ellipse(-7 - legOffset, -1, 5, 2.5, 0, 0, Math.PI * 2);
    ctx.fill();

    // Jambe Avant (droite)
    this.drawLimb(ctx, 5 + legOffset, -30, 6 + legOffset, -2, 5.5, pal.trousers || pal.primary, "#0f172a");
    // Chaussure Avant
    ctx.fillStyle = "#0f172a";
    ctx.beginPath();
    ctx.ellipse(7 + legOffset, 0, 5.5, 3, 0, 0, Math.PI * 2);
    ctx.fill();

    // --- COUCHE 2 : BASSIN & TORSE ---
    ctx.save();
    ctx.translate(0, breathY * 0.4);

    // Bassin / Hanches
    ctx.fillStyle = pal.primaryShadow;
    ctx.beginPath();
    ctx.roundRect(-10, -38, 20, 10, 3);
    ctx.fill();

    // Torse / Veste
    ctx.fillStyle = pal.primary;
    ctx.beginPath();
    ctx.moveTo(-11, -38);
    ctx.lineTo(-13, -56);
    ctx.lineTo(13, -56);
    ctx.lineTo(11, -38);
    ctx.closePath();
    ctx.fill();
    ctx.strokeStyle = "#1c1917";
    ctx.lineWidth = 1.2;
    ctx.stroke();

    // Reflet de volume torse (ombrage haut-gauche)
    const torsoGrad = ctx.createLinearGradient(-13, -56, 13, -38);
    torsoGrad.addColorStop(0, "rgba(255, 255, 255, 0.12)");
    torsoGrad.addColorStop(0.5, "rgba(0, 0, 0, 0)");
    torsoGrad.addColorStop(1, "rgba(0, 0, 0, 0.22)");
    ctx.fillStyle = torsoGrad;
    ctx.fill();

    // Tablier ou couche secondaire spécifique
    if (charDef.id === "awa") {
      ctx.fillStyle = pal.secondary;
      ctx.beginPath();
      ctx.moveTo(-9, -52);
      ctx.lineTo(9, -52);
      ctx.lineTo(11, -35);
      ctx.lineTo(-11, -35);
      ctx.closePath();
      ctx.fill();
      ctx.strokeStyle = "#dcd2c4";
      ctx.stroke();
      // Farine sur tablier
      ctx.fillStyle = "rgba(255, 255, 255, 0.4)";
      ctx.beginPath();
      ctx.arc(3, -42, 4, 0, Math.PI * 2);
      ctx.fill();
    } else if (charDef.id === "kofi") {
      // Écharpe tricolore municipale
      ctx.strokeStyle = pal.sash;
      ctx.lineWidth = 3.5;
      ctx.beginPath();
      ctx.moveTo(-12, -56);
      ctx.lineTo(10, -38);
      ctx.stroke();
    } else if (charDef.id === "samuel") {
      // Tablier de cuir
      ctx.fillStyle = pal.primary;
      ctx.fillRect(-9, -52, 18, 20);
      ctx.strokeStyle = "#451a03";
      ctx.strokeRect(-9, -52, 18, 20);
    }

    // Col / Chemise
    ctx.fillStyle = pal.secondary;
    ctx.beginPath();
    ctx.moveTo(-4, -56);
    ctx.lineTo(0, -48);
    ctx.lineTo(4, -56);
    ctx.closePath();
    ctx.fill();

    // --- COUCHE 3 : BRAS GAUCHE (arrière) ---
    const armSwing = stride * 12;
    ctx.save();
    ctx.translate(-12, -54);
    ctx.rotate((state.didStock ? -45 : armSwing) * (Math.PI / 180));
    ctx.fillStyle = pal.primaryShadow;
    ctx.fillRect(-2, 0, 4.5, 16);
    // Main gauche
    ctx.fillStyle = skin.shadow;
    ctx.beginPath();
    ctx.arc(0.5, 17, 2.5, 0, Math.PI * 2);
    ctx.fill();
    ctx.restore();

    // --- COUCHE 4 : COU & TÊTE ---
    // Cou
    ctx.fillStyle = skin.shadow;
    ctx.fillRect(-3, -60, 6, 6);

    // Forme du crâne & mâchoire
    ctx.save();
    ctx.translate(0, -68);

    // Tête
    ctx.fillStyle = skin.base;
    ctx.beginPath();
    ctx.ellipse(0, 0, 7.5, 9, 0, 0, Math.PI * 2);
    ctx.fill();
    ctx.strokeStyle = "#1c1917";
    ctx.lineWidth = 1.0;
    ctx.stroke();

    // Ombrage volumétrique du visage (lumière haut-gauche)
    const faceGrad = ctx.createLinearGradient(-7, -7, 7, 7);
    faceGrad.addColorStop(0, skin.highlight);
    faceGrad.addColorStop(0.5, skin.base);
    faceGrad.addColorStop(1, skin.shadow);
    ctx.fillStyle = faceGrad;
    ctx.fill();

    // Yeux & Regard
    this.drawEyes(ctx, charDef, state, isBlinking);

    // Nez discret
    ctx.fillStyle = skin.shadow;
    ctx.beginPath();
    ctx.moveTo(0, -1);
    ctx.lineTo(1.2, 1);
    ctx.lineTo(-0.5, 1.2);
    ctx.closePath();
    ctx.fill();

    // Bouche (animée si l'agent parle)
    this.drawMouth(ctx, charDef, state);

    // Chevelure / Chapeau / Coiffure
    this.drawHairAndHeadwear(ctx, charDef);

    // Lunettes pour Élise
    if (charDef.id === "elise") {
      ctx.strokeStyle = "#d97706";
      ctx.lineWidth = 0.8;
      ctx.strokeRect(-5.5, -3, 4, 3);
      ctx.strokeRect(1.5, -3, 4, 3);
      ctx.beginPath();
      ctx.moveTo(-1.5, -1.5);
      ctx.lineTo(1.5, -1.5);
      ctx.stroke();
    }

    ctx.restore(); // Fin tête

    // --- COUCHE 5 : BRAS DROIT (avant) ---
    ctx.save();
    ctx.translate(12, -54);
    const rightArmAngle = state.isHesitating
      ? -110 // Main au menton
      : state.isTalking
      ? -35 + Math.sin(tick * 0.3) * 15 // Geste expressif
      : -armSwing;
    ctx.rotate(rightArmAngle * (Math.PI / 180));
    ctx.fillStyle = pal.primary;
    ctx.fillRect(-2.5, 0, 5, 16);
    // Main droite
    ctx.fillStyle = skin.base;
    ctx.beginPath();
    ctx.arc(0, 17, 2.8, 0, Math.PI * 2);
    ctx.fill();

    // Accessoires tenus en main droite
    if (state.didStock || charDef.accessory === "bread_basket" || charDef.accessory === "vegetable_basket") {
      this.drawBasket(ctx, charDef, state);
    } else if (charDef.accessory === "blacksmith_hammer") {
      // Marteau de forgeron
      ctx.fillStyle = "#78350f";
      ctx.fillRect(-1, 8, 2, 14);
      ctx.fillStyle = "#475569";
      ctx.fillRect(-4, 6, 8, 4);
    } else if (charDef.accessory === "fishing_cane") {
      // Canne à pêche en bambou
      ctx.strokeStyle = "#a16207";
      ctx.lineWidth = 1.2;
      ctx.beginPath();
      ctx.moveTo(0, 16);
      ctx.lineTo(4, -25);
      ctx.stroke();
    } else if (charDef.accessory === "press_notebook") {
      // Bloc-notes de Claire
      ctx.fillStyle = "#f8fafc";
      ctx.fillRect(-2, 15, 6, 8);
      ctx.strokeStyle = "#78350f";
      ctx.strokeRect(-2, 15, 6, 8);
    }
    ctx.restore();

    ctx.restore(); // Fin torse
    ctx.restore(); // Fin root translate
  }

  drawEyes(ctx, charDef, state, isBlinking) {
    if (isBlinking || state.isNight) {
      // Yeux fermés (arc fin)
      ctx.strokeStyle = "#1c1917";
      ctx.lineWidth = 0.9;
      ctx.beginPath();
      ctx.arc(-3.2, -1.5, 1.8, 0.1 * Math.PI, 0.9 * Math.PI);
      ctx.stroke();
      ctx.beginPath();
      ctx.arc(3.2, -1.5, 1.8, 0.1 * Math.PI, 0.9 * Math.PI);
      ctx.stroke();
    } else {
      // Blanc des yeux (sclère)
      ctx.fillStyle = "#ffffff";
      ctx.fillRect(-4.5, -3, 3, 2.2);
      ctx.fillRect(1.5, -3, 3, 2.2);

      // Iris
      ctx.fillStyle = charDef.eyes.color || "#1c1917";
      const gazeShift = state.hasRumor ? 0.8 : 0; // Regard en coin si porteur de rumeur
      ctx.beginPath();
      ctx.arc(-3 + gazeShift, -2, 1.0, 0, Math.PI * 2);
      ctx.arc(3 + gazeShift, -2, 1.0, 0, Math.PI * 2);
      ctx.fill();

      // Sourcils
      ctx.strokeStyle = charDef.hair.color;
      ctx.lineWidth = 0.8;
      const browTilt = state.hasRumor ? 0.8 : state.isHesitating ? -0.5 : 0;
      ctx.beginPath();
      ctx.moveTo(-5, -4.5 + browTilt);
      ctx.lineTo(-2, -4.5 - browTilt);
      ctx.moveTo(2, -4.5 - browTilt);
      ctx.lineTo(5, -4.5 + browTilt);
      ctx.stroke();
    }
  }

  drawMouth(ctx, charDef, state) {
    ctx.fillStyle = "#7f1d1d";
    if (state.isTalking) {
      // Bouche ouverte animée
      const mouthOpen = (Math.sin((state.tick || 0) * 0.8) + 1) * 1.0;
      ctx.beginPath();
      ctx.ellipse(0, 4, 1.8, 0.8 + mouthOpen, 0, 0, Math.PI * 2);
      ctx.fill();
    } else if (state.hasDebunk) {
      // Sourire apaisé
      ctx.strokeStyle = "#7f1d1d";
      ctx.lineWidth = 0.8;
      ctx.beginPath();
      ctx.arc(0, 2.5, 2.2, 0.2 * Math.PI, 0.8 * Math.PI);
      ctx.stroke();
    } else {
      // Lèvre neutre
      ctx.strokeStyle = "#7f1d1d";
      ctx.lineWidth = 0.8;
      ctx.beginPath();
      ctx.moveTo(-1.8, 3.8);
      ctx.lineTo(1.8, 3.8);
      ctx.stroke();
    }
  }

  drawHairAndHeadwear(ctx, charDef) {
    const hair = charDef.hair;
    ctx.fillStyle = hair.color;

    switch (hair.style) {
      case "turban_white":
        ctx.fillStyle = "#f8fafc";
        ctx.beginPath();
        ctx.ellipse(0, -6, 9, 6.5, 0, 0, Math.PI * 2);
        ctx.fill();
        ctx.strokeStyle = "#cbd5e1";
        ctx.stroke();
        break;

      case "turban_green":
        ctx.fillStyle = "#15803d";
        ctx.beginPath();
        ctx.ellipse(0, -6, 9.5, 7, 0, 0, Math.PI * 2);
        ctx.fill();
        ctx.strokeStyle = "#14532d";
        ctx.stroke();
        break;

      case "newsboy_cap":
        ctx.fillStyle = "#1e3a5f";
        ctx.beginPath();
        ctx.ellipse(0, -6.5, 9, 5, 0, 0, Math.PI * 2);
        ctx.fill();
        // Visière
        ctx.beginPath();
        ctx.ellipse(3, -4, 6, 2, 0.2, 0, Math.PI * 2);
        ctx.fillStyle = "#0f172a";
        ctx.fill();
        break;

      case "straw_hat":
        ctx.fillStyle = "#eab308";
        // Bord large
        ctx.beginPath();
        ctx.ellipse(0, -5, 14, 4.5, 0, 0, Math.PI * 2);
        ctx.fill();
        // Calotte
        ctx.beginPath();
        ctx.ellipse(0, -8, 7, 5, 0, 0, Math.PI * 2);
        ctx.fillStyle = "#ca8a04";
        ctx.fill();
        break;

      case "bun_pencil":
        ctx.beginPath();
        ctx.arc(0, -7, 8, Math.PI, 0);
        ctx.arc(0, -11, 4, 0, Math.PI * 2);
        ctx.fill();
        // Crayon
        ctx.strokeStyle = "#f59e0b";
        ctx.lineWidth = 1.0;
        ctx.beginPath();
        ctx.moveTo(-5, -13);
        ctx.lineTo(5, -9);
        ctx.stroke();
        break;

      case "high_ponytail":
        ctx.beginPath();
        ctx.arc(0, -6, 8, Math.PI * 0.9, 0.1 * Math.PI);
        ctx.fill();
        // Queue de cheval sur le côté
        ctx.beginPath();
        ctx.moveTo(-6, -6);
        ctx.quadraticCurveTo(-11, -2, -9, 8);
        ctx.lineWidth = 3.5;
        ctx.strokeStyle = hair.color;
        ctx.stroke();
        break;

      case "sharp_bob":
        ctx.beginPath();
        ctx.arc(0, -5, 8.5, Math.PI, 0);
        ctx.lineTo(8.5, 2);
        ctx.lineTo(6, 3);
        ctx.lineTo(6, -2);
        ctx.lineTo(-6, -2);
        ctx.lineTo(-6, 3);
        ctx.lineTo(-8.5, 2);
        ctx.closePath();
        ctx.fill();
        break;

      case "tousled_bangs":
        ctx.beginPath();
        ctx.arc(0, -6, 8, Math.PI * 0.8, 0.2 * Math.PI);
        ctx.lineTo(7, -3);
        ctx.lineTo(3, -2);
        ctx.lineTo(0, -3.5);
        ctx.lineTo(-4, -2);
        ctx.lineTo(-7, -3);
        ctx.closePath();
        ctx.fill();
        break;

      case "white_curly":
      case "short_greying":
      default:
        ctx.beginPath();
        ctx.arc(0, -6, 8, Math.PI * 0.85, 0.15 * Math.PI);
        ctx.fill();
        break;
    }

    // Barbe / Moustache si applicable
    if (hair.beard === "short_neat" || hair.beard === "heavy_beard" || hair.beard === "white_bushy") {
      ctx.fillStyle = hair.beard === "white_bushy" ? "#f1f5f9" : hair.color;
      ctx.beginPath();
      ctx.arc(0, 3, 5, 0, Math.PI);
      ctx.fill();
    } else if (hair.beard === "salt_pepper_stache") {
      ctx.strokeStyle = "#3f3f46";
      ctx.lineWidth = 1.2;
      ctx.beginPath();
      ctx.moveTo(-3, 2.5);
      ctx.lineTo(3, 2.5);
      ctx.stroke();
    }
  }

  drawLimb(ctx, x1, y1, x2, y2, width, color, strokeColor) {
    ctx.strokeStyle = color;
    ctx.lineWidth = width;
    ctx.lineCap = "round";
    ctx.beginPath();
    ctx.moveTo(x1, y1);
    ctx.lineTo(x2, y2);
    ctx.stroke();
  }

  drawBasket(ctx, charDef, state) {
    ctx.save();
    ctx.translate(2, 12);
    ctx.fillStyle = "#b45309";
    ctx.beginPath();
    ctx.roundRect(-4, 0, 10, 8, 2);
    ctx.fill();
    ctx.strokeStyle = "#78350f";
    ctx.lineWidth = 0.8;
    ctx.stroke();

    // Contenu du panier (pain doré ou légumes verts)
    if (charDef.id === "awa") {
      ctx.fillStyle = "#d97706";
      ctx.beginPath();
      ctx.ellipse(1, 0, 4, 2.5, 0, 0, Math.PI * 2);
      ctx.fill();
    } else {
      ctx.fillStyle = "#22c55e";
      ctx.beginPath();
      ctx.arc(0, 0, 2.5, 0, Math.PI * 2);
      ctx.arc(3, -1, 2, 0, Math.PI * 2);
      ctx.fill();
    }
    ctx.restore();
  }

  /**
   * Rendu Buste Haute Définition pour l'Inspecteur d'Agent & la Gazette.
   */
  drawBustPortrait(ctx, charDef, state, anim) {
    const { breathY, isBlinking } = anim;
    const skin = charDef.skin;
    const pal = charDef.palette;

    ctx.save();
    // Épaules et Veste Buste
    ctx.fillStyle = pal.primary;
    ctx.beginPath();
    ctx.ellipse(0, 26 + breathY, 24, 16, 0, 0, Math.PI * 2);
    ctx.fill();
    ctx.strokeStyle = "#1c1917";
    ctx.lineWidth = 1.5;
    ctx.stroke();

    // Col / Chemise
    ctx.fillStyle = pal.secondary;
    ctx.beginPath();
    ctx.moveTo(-7, 10);
    ctx.lineTo(0, 20);
    ctx.lineTo(7, 10);
    ctx.closePath();
    ctx.fill();

    // Cou
    ctx.fillStyle = skin.shadow;
    ctx.fillRect(-6, -4, 12, 15);

    // Tête haute résolution
    ctx.fillStyle = skin.base;
    ctx.beginPath();
    ctx.ellipse(0, -16, 15, 18, 0, 0, Math.PI * 2);
    ctx.fill();
    ctx.strokeStyle = "#1c1917";
    ctx.lineWidth = 1.6;
    ctx.stroke();

    // Yeux Buste
    if (isBlinking || state.isNight) {
      ctx.strokeStyle = "#1c1917";
      ctx.lineWidth = 1.8;
      ctx.beginPath();
      ctx.arc(-6, -16, 3.5, 0.1 * Math.PI, 0.9 * Math.PI);
      ctx.stroke();
      ctx.beginPath();
      ctx.arc(6, -16, 3.5, 0.1 * Math.PI, 0.9 * Math.PI);
      ctx.stroke();
    } else {
      // Yeux détaillés avec iris et pupille
      ctx.fillStyle = "#ffffff";
      ctx.beginPath();
      ctx.ellipse(-6, -16, 4.5, 3.2, 0, 0, Math.PI * 2);
      ctx.ellipse(6, -16, 4.5, 3.2, 0, 0, Math.PI * 2);
      ctx.fill();
      ctx.stroke();

      ctx.fillStyle = charDef.eyes.color || "#1c1917";
      ctx.beginPath();
      ctx.arc(-6, -16, 2.0, 0, Math.PI * 2);
      ctx.arc(6, -16, 2.0, 0, Math.PI * 2);
      ctx.fill();

      // Reflet spéculaire blanc
      ctx.fillStyle = "#ffffff";
      ctx.beginPath();
      ctx.arc(-6.8, -16.8, 0.7, 0, Math.PI * 2);
      ctx.arc(5.2, -16.8, 0.7, 0, Math.PI * 2);
      ctx.fill();
    }

    // Nez sculpté
    ctx.strokeStyle = skin.shadow;
    ctx.lineWidth = 1.6;
    ctx.beginPath();
    ctx.moveTo(-0.5, -18);
    ctx.lineTo(1.8, -10);
    ctx.lineTo(-1.0, -9);
    ctx.stroke();

    // Bouche buste
    ctx.fillStyle = "#881337";
    ctx.beginPath();
    ctx.ellipse(0, -4, 3.5, 1.5, 0, 0, Math.PI * 2);
    ctx.fill();

    // Coiffure buste agrandie
    ctx.save();
    ctx.scale(1.9, 1.9);
    ctx.translate(0, -6.5);
    this.drawHairAndHeadwear(ctx, charDef);
    ctx.restore();

    ctx.restore();
  }
}

// Export pour module ES ou script classique dans le navigateur
if (typeof module !== "undefined" && module.exports) {
  module.exports = { CharacterRenderer2D, HAMEAU_CHARACTERS };
} else {
  window.CharacterRenderer2D = CharacterRenderer2D;
  window.HAMEAU_CHARACTERS = HAMEAU_CHARACTERS;
}
