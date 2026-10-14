# Bible Artistique — HAMEAU (ART_BIBLE.md)

Direction artistique, anatomie, système de lumière, palette en tokens OKLCH et fiches des 12 habitants pour la refonte visuelle 2D du visualiseur.

---

## 1. Philosophie & Direction Artistique

### 1.1 Le Parti-Pris : L'Illustration Éditoriale Semi-Réaliste
HAMEAU met en scène un village vivant où les interactions sociales et la diffusion de l'information sont le cœur du sujet. Le rendu visuel abandonne définitivement les disques primitifs et les emojis pour adopter une **direction artistique d'illustration éditoriale narrative** :
- **Proportions réalistes (~7 têtes)** : Corps articulé respectant les proportions humaines adultes (tête, cou, torse, bassin, bras à deux segments, mains, jambes et pieds).
- **Stylisation soignée et chaleureuse** : Les traits sont épurés mais précis, rejetant le faux photoréalisme (qui génère de la vallée de l'étrange) au profit d'un trait d'encrage expressif et de volumes doux.
- **Interdictions formelles** :
  - *Pas de pixel-art* (inadapté au caractère littéraire et analytique du projet).
  - *Pas de chibi / anime outrancier* (décrédibiliserait la simulation de sociologie rurale).
  - *Pas d'emojis comme icônes ou têtes d'agents* (contraire au craft floor Impeccable).
  - *Pas d'actifs volés ou copiés* : 100 % généré procéduralement par code Canvas 2D natif sous licence Apache-2.0.
- **Double échelle de rendu (Dual-LOD)** :
  1. **Sprite de carte (64 à 96 px)** : Silhouette nette, contraste marqué, détails hiérarchisés pour une lisibilité instantanée en vue trois-quarts.
  2. **Portrait en buste grand format (180 à 240 px)** : Affiché dans l'Inspecteur d'Agent, le Réseau Social et la Gazette, révélant la finesse des expressions, des regards et des textures vestimentaires.

---

## 2. Système de Lumière, Volumes et Encrage

### 2.1 Éclairage Global et Direction de la Clé de Lumière
- **Source principale (Key Light)** : Orientée depuis le **haut-gauche à 45°** ($x=-0.707, y=-0.707$).
- **Volumes en 3 valeurs par composant** :
  1. *Lumière / Ton local* : Teinte nominale du vêtement ou de la peau.
  2. *Ombre propre (Self-Shadow)* : Teinte rabattue de 20-30 % de luminosité avec glissement chromatique chaud ou froid (ex: une peau dorée s'ombrera vers un ambre chaud, un tissu bleu vers un outremer profond).
  3. *Rehaut discret (Rim/Specular)* : Liseré doux sur l'épaule et la chevelure côté haut-gauche.
- **Ombre portée au sol (Ground Ambient Occlusion)** :
  - Chaque personnage projette à ses pieds une ellipse douce dégradée (`rgba(15, 23, 42, 0.45)` au centre s'estompant à `0`), ancrant le personnage fermement sur le sol du village.
  - En marche, l'ombre oscille subtilement en largeur pour souligner le transfert de masse.

### 2.2 Règle d'Encrage et de Trait
- Les contours sont tracés avec une teinte **encre chaude sépia sombre** (`#1c1917` ou `#0f172a`), jamais un noir pur synthétique `#000000`.
- Épaisseur de trait :
  - Silhouette extérieure : $1.8 \times \text{dpr}$ px.
  - Détails internes (plis, yeux, col) : $1.0 \times \text{dpr}$ px.
- Lisibilité à 64 px : Tous les petits détails superflus disparaissent automatiquement au LOD carte au profit des aplats et des contrastes de valeurs.

---

## 3. Palette de Tokens de Couleur (Espace OKLCH & Hex)

Les tokens sont définis pour garantir une harmonie éditoriale et respecter les critères d'accessibilité WCAG AA (contraste $\ge 4.5:1$).

### 3.1 Carnations & Teints (Diversité Réaliste)
| Token | Valeur Hex | Teinte & Utilisation |
| :--- | :--- | :--- |
| `--skin-deep-warm` | `#5c3826` / Ombre `#3e2316` | Teint ébène chaud (Awa, Ibrahim) |
| `--skin-rich-umber` | `#825338` / Ombre `#5c3520` | Teint brun profond (Kofi, Mariam) |
| `--skin-warm-bronze` | `#b57a52` / Ombre `#844e2e` | Teint ambré / cuivré (Yao, Samuel) |
| `--skin-olive-warm` | `#d29d75` / Ombre `#a36e49` | Teint méditerranéen / olive (Nadia, Tom) |
| `--skin-fair-golden` | `#ecc3a2` / Ombre `#be9070` | Teint clair doré (Élise, Léa) |
| `--skin-weathered` | `#c99b79` / Ombre `#966847` | Teint patiné par le soleil (Paul) |

### 3.2 Textiles & Matières du Village
| Token | Valeur Hex | Utilisation |
| :--- | :--- | :--- |
| `--fabric-linen-cream` | `#f5efe6` / Ombre `#dcd2c4` | Tablier de boulangerie, chemises légères |
| `--fabric-work-indigo` | `#2d4a6e` / Ombre `#1b2f4a` | Salopettes, vareuses de travail, casquette |
| `--fabric-civic-navy` | `#1e293b` / Ombre `#0f172a` | Costume de maire, manteau officiel |
| `--fabric-earth-terracotta`| `#b45309` / Ombre `#78350f`| Cardigan, robes de marché, tabliers de cuir |
| `--fabric-sage-green` | `#4d7c0f` / Ombre `#365314` | Vêtements agricoles, parkas |
| `--fabric-warm-burgundy` | `#881337` / Ombre `#4c0519` | Écharpe tricolore municipale, châle d'Élise |
| `--fabric-gazette-teal` | `#0f766e` / Ombre `#115e59` | Veste de reporter de Claire |

### 3.3 Indicateurs Sémantiques d'État (Forme + Couleur)
| État | Couleur | Signe Distinctif Morphologique / Posture |
| :--- | :--- | :--- |
| **Normal / Serein** | `--color-slate` (`#64748b`) | Posture droite équilibrée, regard calme |
| **Porteur Rumeur R1** | `--color-rose` (`#f43f5e`) | Sourcils arqués d'inquiétude, tête légèrement penchée, sacoche serrée |
| **Démenti R2 Reçu** | `--color-cyan` (`#06b6d4`) | Épaules détendues, sourire discret, posture ouverte |
| **Stockage Vivres** | `--color-amber` (`#f59e0b`) | Port d'un sac de jute ou panier bien visible au coude |
| **Zone Rouge (Hésite)**| `--color-crimson` (`#e11d48`)| Main posée sur le menton, posture d'arrêt pensive |
| **En Train de Parler** | `--color-sky` (`#38bdf8`) | Bouche articulée, bras expressif, bulle de dialogue |
| **Nuit / Sommeil** | `--color-indigo` (`#312e81`)| Yeux fermés en courbe douce, éclairage bleuté tamisé |

---

## 4. Fiches Détaillées des 12 Habitants Canoniques

### 1. Awa — La Boulangère du Hameau
- **Âge & Morphologie** : 42 ans, silhouette robuste et chaleureuse, épaules solides.
- **Teint & Cheveux** : Teint ébène chaud (`--skin-deep-warm`), foulard blanc noué en turban masquant une chevelure tressée haute.
- **Tenue** : Robe en lin jaune moutarde sous un grand tablier écru fariné (`--fabric-linen-cream`), manches retroussées aux coudes.
- **Accessoire signature** : Torchon de lin à la ceinture et trace de farine blanche sur l'avant-bras.
- **Pose signature** : Mains sur les hanches d'un air accueillant et énergique.

### 2. Kofi — Le Maire du Hameau
- **Âge & Morphologie** : 51 ans, stature imposante, maintien digne et paternaliste.
- **Teint & Cheveux** : Teint brun profond (`--skin-rich-umber`), cheveux courts poivre et sel aux tempes, fine barbe soignée.
- **Tenue** : Costume trois pièces en drap de laine bleu marine (`--fabric-civic-navy`), chemise blanche à col ouvert.
- **Accessoire signature** : Écharpe républicaine bordeaux/or portée en sautoir lors des déclarations.
- **Pose signature** : Bras croisés dans le dos en observation calme, ou bras tendu lors des discours civiques.

### 3. Yao — Le Livreur du Marché
- **Âge & Morphologie** : 28 ans, silhouette athlétique, vive et dynamique, posture toujours prête à bondir.
- **Teint & Cheveux** : Teint ambré cuivré (`--skin-warm-bronze`), casquette gavroche bleu travail inclinée sur des cheveux courts bouclés.
- **Tenue** : Veste en toile indigo sans manches (`--fabric-work-indigo`), t-shirt écru chiné, pantalon retroussé sur bottines de cuir.
- **Accessoire signature** : Caisse en bois de cagettes sous le bras ou courroie de sacoche en bandoulière.
- **Pose signature** : Enjambée rapide vers l'avant, buste légèrement incliné dans l'action.

### 4. Élise — L'Institutrice
- **Âge & Morphologie** : 36 ans, silhouette mince et élégante, port de tête attentif.
- **Teint & Cheveux** : Teint clair doré (`--skin-fair-golden`), cheveux châtains relevés en chignon souple retenu par un crayon.
- **Tenue** : Jupe plissée vert forêt, chemisier crème et châle en fine maille bordeaux (`--fabric-warm-burgundy`).
- **Accessoire signature** : Lunettes fines rondes en métal doré et registre de classe tenu contre la poitrine.
- **Pose signature** : Index levé pour expliquer ou livre entrouvert entre les mains.

### 5. Samuel — Le Forgeron
- **Âge & Morphologie** : 48 ans, silhouette trapue et puissante, avant-bras très musclés.
- **Teint & Cheveux** : Teint basané patiné (`--skin-warm-bronze`), cheveux noirs grisonnants attachés court, barbe fournie.
- **Tenue** : Tablier de cuir lourd huilé brun foncé (`--fabric-earth-terracotta`) sur chemise de travail anthracite sans manches.
- **Accessoire signature** : Marteau de forge à manche en frêne calé à la ceinture et gants de cuir souple.
- **Pose signature** : Appui lourd sur la jambe gauche, posture solide inébranlable.

### 6. Nadia — Le Médecin du Village
- **Âge & Morphologie** : 39 ans, silhouette élancée, gestes précis et assurés.
- **Teint & Cheveux** : Teint méditerranéen chaud (`--skin-olive-warm`), cheveux noirs lisses mi-longs coupés au carré net.
- **Tenue** : Pantalon élégant bleu ardoise sous une blouse de praticien immaculée à col relevé.
- **Accessoire signature** : Stéthoscope argenté passé autour du cou et mallette médicale en cuir noir à la main.
- **Pose signature** : Regard concentré, carnet d'ordonnances ou main tendue rassurante.

### 7. Tom — L'Apprenti du Café / Étudiant
- **Âge & Morphologie** : 21 ans, silhouette jeune et dégingandée, silhouette moderne.
- **Teint & Cheveux** : Teint olive clair (`--skin-olive-warm`), chevelure ébouriffée avec mèche rebelle sur le front.
- **Tenue** : Sweat à capuche zippé ocre/rouille, jean délavé confortable, baskets légères.
- **Accessoire signature** : Casque audio posé autour du cou et sac à dos à une seule bretelle.
- **Pose signature** : Mains plongées dans les poches, écoute curieuse de toutes les conversations qui passent.

### 8. Mariam — La Marchande de Légumes
- **Âge & Morphologie** : 45 ans, silhouette généreuse, vive et expressive.
- **Teint & Cheveux** : Teint brun chaleureux (`--skin-rich-umber`), grand foulard imprimé wax vert et terracotta noué avec élégance.
- **Tenue** : Tunique ample en coton terre de Sienne (`--fabric-earth-terracotta`) et grand tablier à poches multiples.
- **Accessoire signature** : Grand panier tressé en osier débordant de légumes frais calé sur la hanche.
- **Pose signature** : Geste de la main ouverte pour inviter le chaland ou peser une balance imaginaire.

### 9. Paul — Le Pêcheur Retraité
- **Âge & Morphologie** : 68 ans, silhouette courbée mais noueuse, démarche lente et sereine.
- **Teint & Cheveux** : Teint tanné par les intempéries (`--skin-weathered`), barbe blanche fournie, sourcils broussailleux bienveillants.
- **Tenue** : Ciré jaune patiné ou gros gilet en laine tricotée écrue, pantalon de velours côtelé marron.
- **Accessoire signature** : Casquette de marin feutrée et canne à pêche en bambou ou canne de marche en châtaignier.
- **Pose signature** : Buste appuyé sur sa canne, regardant paisiblement la rivière ou les passants.

### 10. Léa — La Bibliothécaire
- **Âge & Morphologie** : 31 ans, silhouette fine, attitude douce et réservée.
- **Teint & Cheveux** : Teint diaphane doré (`--skin-fair-golden`), longs cheveux roux ondulés tombant sur les épaules.
- **Tenue** : Cardigan doux tricoté en laine vert sauge (`--fabric-sage-green`) sur une robe fluide fleurie.
- **Accessoire signature** : Sac cabas en toile garni de livres reliés et marque-pages rubans.
- **Pose signature** : Tête doucement penchée, un livre serré à deux mains.

### 11. Ibrahim — L'Agriculteur des Hauts
- **Âge & Morphologie** : 54 ans, silhouette haute et sèche, visage taillé par le vent des collines.
- **Teint & Cheveux** : Teint sombre hâlé (`--skin-deep-warm`), moustache poivre et sel, regard franc et perçant.
- **Tenue** : Chemise à carreaux rouge et bleu, salopette de toile brute et bottes de terre cuite.
- **Accessoire signature** : Grand chapeau de paille tressée à large bord et brin de paille entre les dents.
- **Pose signature** : Poings calés aux hanches, scrutant l'horizon ou le ciel.

### 12. Claire — La Rédactrice de la Gazette
- **Âge & Morphologie** : 34 ans, allure citadine dynamique, regard vif et observateur.
- **Teint & Cheveux** : Teint miel doré (`--skin-olive-warm`), cheveux noirs ondulés attachés en queue de cheval haute.
- **Tenue** : Veste tailleur décontractée en velours vert émeraude (`--fabric-gazette-teal`), pantalon cigarette et mocassins.
- **Accessoire signature** : Bloc-notes à spirale et crayon graphite toujours dégainé, sacoche besace en cuir havane.
- **Pose signature** : Crayon levé prête à noter un scoop, ou lisant avidement un feuillet d'imprimerie.

---

## 5. Spécification du Générateur Paramétrique (Passage à 25 Habitants)

Pour passer à 25 agents sans écrire une seule ligne de code supplémentaire, chaque habitant est défini par une structure JSON canonique :

```json
{
  "id": "personnage_25",
  "name": "Nom de l'Habitant",
  "role": "Métier / Rôle",
  "age": 40,
  "gender": "f" | "m" | "nb",
  "build": "robust" | "slender" | "stocky" | "tall",
  "skinToken": "skin-warm-bronze",
  "hair": { "style": "bun" | "curly_cap" | "short_gray" | "braids" | "ponytail", "color": "#1c1917" },
  "palette": {
    "primary": "#2d4a6e",
    "secondary": "#f5efe6",
    "accent": "#b45309",
    "trim": "#1e293b"
  },
  "accessory": "basket" | "briefcase" | "cane" | "hammer" | "notebook" | "stethoscope" | "bread",
  "signaturePose": "hands_on_hips" | "arms_crossed" | "active_stride" | "thoughtful"
}
```

Le moteur de rendu interprète cette déclaration en appliquant la cinématique squelettique correspondante.

---

## 6. Cinématique Squelettique & États d'Animation Procédurale

Toutes les animations sont **déterministes**, calculées en fonction du `globalTick` et d'une graine `hash(agentId)` :

1. **Respiration (Idle Breathing)** :
   $$y_{\text{torse}} = \sin\left(\frac{2\pi \cdot t}{T_{\text{breath}}} + \phi_i\right) \times 1.5\text{ px}$$
   Cycle de 3,2 secondes. Le torse et les épaules montent et descendent doucement, les bras suivent avec 150 ms de retard de phase.
2. **Clignement des Yeux (Deterministic Blink)** :
   Déclenché toutes les 3,5 à 5,5 secondes. Fermeture complète des paupières pendant 120 ms (soit environ 7 frames à 60 FPS).
3. **Marche (Procedural Stride)** :
   Balancement opposé des bras et jambes ($[-25^\circ, +25^\circ]$), oscillation verticale du bassin (bobbing de 2 px à chaque foulée).
4. **Prise de Parole (Talking Gesture)** :
   Ouverture/fermeture cadencée de la lèvre inférieure, légère inclinaison de la tête et gesticulation douce de la main libre.
5. **Posture d'Inquiétude / Rumeur R1** :
   Épaules légèrement rentrées ($+3^\circ$), tête penchée en avant, regard en coin.
6. **Posture de Stockage (didStock)** :
   Le bras gauche est coudé à $90^\circ$ portant fermement un sac de ravitaillement ou un panier chargé de provisions.
7. **Posture de Doute / Zone Rouge Decider** :
   Arrêt de la marche, bras droit replié avec main sur le menton, point d'interrogation discret ou regard pensif levé.
8. **Sommeil / Nuit** :
   Paupières baissées, épaules relâchées, filtre nocturne bleu profond (`rgba(30, 41, 59, 0.40)`) appliqué au personnage.
