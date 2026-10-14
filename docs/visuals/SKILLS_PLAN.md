# Plan d'Orchestration des Six Skills — Projet HAMEAU

Ce document répertorie l'inventaire réel des six skills installés sur l'environnement, leur version, leurs commandes effectives, et la matrice d'arbitrage stricte définissant qui décide de quoi.

---

## 1. Inventaire des Skills Réellement Installés

### 1.1 `superpowers`
- **Emplacement réel** : `/home/rd/.gemini/config/plugins/superpowers/skills/`
- **Sous-skills identifiés** :
  - `using-superpowers`
  - `brainstorming`
  - `writing-plans`
  - `using-git-worktrees`
  - `subagent-driven-development`
  - `test-driven-development`
  - `requesting-code-review`
  - `verification-before-completion`
  - `finishing-a-development-branch`
- **Rôle principal** : Gouvernance du processus de développement, des portes de qualité et du cycle d'ingénierie.

### 1.2 `agent-skills` (Addy Osmani)
- **Emplacement réel** : `/home/rd/.gemini/config/plugins/agent-skills/skills/`
- **Sous-skills identifiés** :
  - `spec-driven-development` (`/spec`)
  - `planning-and-task-breakdown` (`/plan`)
  - `incremental-implementation` (tranches verticales fines)
  - `frontend-ui-engineering`
  - `browser-testing-with-devtools` (captures Chrome DevTools, console, réseau)
  - `performance-optimization` (`/webperf`)
  - `code-review-and-quality`
  - `code-simplification` (`/code-simplify`)
  - `shipping-and-launch` (`/ship`)
- **Rôle principal** : Cadre d'exigence technique web, rigueur d'implémentation et audits devtools.

### 1.3 `ui-ux-pro-max`
- **Emplacement réel** : `/home/rd/.hermes/skills/ui-ux-pro-max`
- **Script exécutable** : `python3 /home/rd/.hermes/skills/ui-ux-pro-max/scripts/search.py`
- **Options et commandes disponibles** :
  - `--design-system` (`-ds`) : Génère une recommandation complète de design system.
  - `--persist` : Enregistre le design system hiérarchique dans `design-system/<project-slug>/MASTER.md`.
  - `--project-name` (`-p`) : Nom du projet (`Hameau`).
  - `--variance` (1-10) : Molette de variance stylistique (1=minimal, 10=audacieux/asymétrique).
  - `--motion` (1-10) : Molette d'intensité de mouvement.
  - `--density` (1-10) : Molette de densité visuelle (1=aéré, 10=dense/dashboard).
  - `--domain` : `style`, `color`, `chart`, `typography`, `ux`, etc.
  - `--page` : Crée une surcharge spécifique de page.
- **Rôle principal** : Générateur de tokens, palettes, typographies et hiérarchies de design system.

### 1.4 `impeccable`
- **Emplacement réel** : `/home/rd/.hermes/skills/impeccable` (v4.5.0)
- **Script exécutable** : `/home/rd/.hermes/skills/impeccable/scripts/impeccable`
- **Commandes et verbes de conception** :
  - `impeccable context` : Charge le contexte visuel et les directives de surface.
  - `detect` : Analyse les anti-patterns UI et problèmes de qualité de conception.
  - Guides de référence : `shape`, `critique`, `audit`, `polish`, `bolder`, `quieter`, `typeset`, `layout`, `colorize`, `animate`, `delight`.
  - Fichier de règles absolues : `reference/craft-floor.md`.
- **Rôle principal** : Direction artistique, œil critique de design, refus des designs génériques « IA », finition au pixel près.

### 1.5 `ponytail`
- **Emplacement réel** : `/home/rd/.gemini/config/plugins/ponytail/skills/`
- **Commandes et règles** :
  - `ponytail` (intensité lite/full/ultra) : Force la solution la plus simple, standard et sobre (échelle YAGNI).
  - `ponytail-review` : Revue de code chassant la sur-ingénierie et le code mort.
  - `ponytail-debt` : Inventaire des raccourcis étiquetés `ponytail:`.
  - `ponytail-audit` : Audit global de complexité.
- **Rôle principal** : Sobriété architecturale, recours prioritaire aux API natives (Canvas 2D, OffscreenCanvas, CSS) sans bibliothèques tierces superflues.

### 1.6 `build-it` (v3.1.0 par DevOtts)
- **Emplacement réel** : `/home/rd/.agents/skills/build-it`
- **Résumé de la méthode en 5 lignes** :
  1. *Contrat Goal-to-DoD* : Décompose tout objectif en critères numérotés de Définition de Terminé (DoD) testables.
  2. *Portes strictes (« Gates, not vibes »)* : Vérifications automatiques (Turn-end, State-change, Phase-boundary, Interlock, Worktree).
  3. *Persistance d'état sur disque* : Maintient un état non volatil dans `.taskstate/` (`grounding.md`, `decisions.md`, `evidence.md`, `run-memory.md`).
  4. *Registre de preuves* : Le statut `VERIFIED` découle obligatoirement d'une entrée horodatée dans `evidence.md` avec commande et sortie réelles.
  5. *Vérification avec un regard neuf (« Fresh-Eyes »)* : Protocole d'audit dégradé challengeant chaque résultat avant livraison finale.
- **Rôle déduit dans Hameau** : Moteur de cadrage autonome et garant de l'intégrité de la livraison : gestion du registre de preuves (`evidence.md`) et validation rigoureuse de la DoD.

---

## 2. Matrice d'Arbitrage des Sujets (Qui décide de quoi)

| Sujet / Étape | Skill Décideur Unique | Justification & Règle |
| :--- | :--- | :--- |
| **Gouvernance & Cycle global** | `superpowers` | Cadre de pilotage, phases, revue et validation. |
| **Architecture & Spécification** | `agent-skills` | Structuration en tranches verticales fines, critères d'acceptation. |
| **Design System & Tokens** | `ui-ux-pro-max` | Dérivation de la palette OKLCH, des échelles de densité et typographie. |
| **Direction Artistique & Finition** | `impeccable` | Jugement visuel, proportions, silhouettes, anti-patterns IA, critique d'artiste. |
| **Sobriété du Code & Performance** | `ponytail` | Zéro dépendance tierce, Canvas 2D natif, annotations `ponytail:`. |
| **Suivi des Preuves & DoD** | `build-it` | Registre `.taskstate/evidence.md`, audit de vérification dégradé. |

---

## 3. Ordre de Priorité en Cas de Conflit

1. **Règles absolues du projet** (section 2 du cahier des charges : pas d'innerHTML, pas d'asset tiers volé, vérifiabilité stricte, scripts/verify.sh toujours vert).
2. **`superpowers`** (portes de processus).
3. **`agent-skills`** (cadre de qualité web).
4. **`ui-ux-pro-max`** (tokens et design system).
5. **`impeccable`** (jugement visuel et esthétique).
6. **`ponytail`** (sobriété et minimalisme).
7. **`build-it`** (registre de preuves et vérification).
