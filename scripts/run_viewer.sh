#!/usr/bin/env bash
# ==============================================================================
# HAMEAU — Script de lancement autonome du Visualiseur Web 2D
# ==============================================================================
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

PORT="${PORT:-8000}"
HOST="127.0.0.1"
URL="http://${HOST}:${PORT}/index.html"
CONTACT_SHEET_URL="http://${HOST}:${PORT}/dev/characters.html"

echo "=========================================================="
echo "   HAMEAU — Visualiseur Multi-Agents (Personnages 2D)"
echo "=========================================================="
echo "Répertoire : $REPO_ROOT"
echo "Port       : $PORT"

# Vérification de l'environnement virtuel / uv
if ! command -v uv >/dev/null 2>&1; then
    echo "[-] Erreur : 'uv' n'est pas installé ou n'est pas dans le PATH."
    echo "    Installez uv ou activez votre environnement virtuel Python."
    exit 1
fi

# Vérification si le port est déjà occupé
if command -v lsof >/dev/null 2>&1; then
    PID_ON_PORT=$(lsof -ti :"$PORT" 2>/dev/null || true)
    if [ -n "$PID_ON_PORT" ]; then
        echo "[!] Le port $PORT est déjà utilisé par le processus $PID_ON_PORT."
        echo "    Tentative de libération du port..."
        kill -15 "$PID_ON_PORT" 2>/dev/null || kill -9 "$PID_ON_PORT" 2>/dev/null || true
        sleep 1
    fi
fi

# Tenter d'ouvrir le navigateur en arrière-plan après 1 seconde
(
    sleep 1.2
    if command -v xdg-open >/dev/null 2>&1; then
        xdg-open "$URL" >/dev/null 2>&1 || true
    fi
) &

echo "[+] Démarrage du serveur local sécurisé..."
echo "----------------------------------------------------------"
echo "   Interface Principale : $URL"
echo "   Planche-Contact 12H  : $CONTACT_SHEET_URL"
echo "----------------------------------------------------------"
echo "Appuyez sur Ctrl+C pour arrêter le serveur."
echo ""

# Exécution du serveur
exec uv run hameau --serve --port "$PORT"
