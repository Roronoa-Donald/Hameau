#!/usr/bin/env bash
# ==============================================================================
# HAMEAU — Lanceur Principal Autonome (Entrypoint)
# ==============================================================================
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$REPO_ROOT"

show_help() {
    cat <<EOF
Usage: ./start.sh [OPTION]

Lance l'application HAMEAU de manière entièrement autonome.

Options disponibles :
  (aucune option)     Démarre le visualiseur web 2D immédiatement (par défaut)
  --viewer            Démarre le visualiseur web sur http://127.0.0.1:8000
  --mock [JOURS]      Exécute une simulation Mock rapide (défaut: 1 jour) puis ouvre le visualiseur
  --real [JOURS]      Exécute la simulation réelle sur GPU + AWS Bedrock (défaut: 3 jours) puis ouvre le visualiseur
  --verify            Lance la suite officielle de vérification (tests, secrets, déterminisme)
  --bench             Lance le benchmark de latence / profilage d'inférence
  --help, -h          Affiche cette aide

Exemples :
  ./start.sh                  # Lance l'interface web directement
  ./start.sh --mock 1         # Simulation mock rapide 1 jour + visualiseur
  ./start.sh --real 3         # Scénario officiel 3 jours avec GPU & Bedrock
  ./start.sh --verify         # Vérification globale de non-régression
EOF
}

ACTION="viewer"
ARG_DAYS=""

if [ $# -gt 0 ]; then
    case "$1" in
        --help|-h)
            show_help
            exit 0
            ;;
        --viewer)
            ACTION="viewer"
            ;;
        --mock)
            ACTION="mock"
            ARG_DAYS="${2:-1}"
            ;;
        --real)
            ACTION="real"
            ARG_DAYS="${2:-3}"
            ;;
        --verify)
            ACTION="verify"
            ;;
        --bench)
            ACTION="bench"
            ;;
        *)
            echo "[-] Option inconnue : $1"
            echo "    Utilisez ./start.sh --help pour voir les options."
            exit 1
            ;;
    esac
fi

case "$ACTION" in
    viewer)
        exec ./scripts/run_viewer.sh
        ;;
    mock)
        ./scripts/run_simulation_mock.sh "$ARG_DAYS"
        echo ""
        echo "[*] Lancement automatique du visualiseur..."
        exec ./scripts/run_viewer.sh
        ;;
    real)
        ./scripts/run_simulation_real.sh "$ARG_DAYS"
        echo ""
        echo "[*] Lancement automatique du visualiseur..."
        exec ./scripts/run_viewer.sh
        ;;
    verify)
        exec ./scripts/verify.sh
        ;;
    bench)
        exec uv run python scripts/bench_decider_env.py
        ;;
esac
