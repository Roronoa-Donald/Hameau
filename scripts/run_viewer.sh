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

# Vérification de l'environnement : utilisation de uv si présent, sinon python3 standard
if command -v uv >/dev/null 2>&1 && uv run python -c "import hameau" >/dev/null 2>&1; then
    LAUNCH_CMD=(uv run hameau --serve --port "$PORT")
elif command -v python3 >/dev/null 2>&1; then
    echo "[i] Mode léger universel (sans GPU ni uv requis) : serveur HTTP Python standard"
    LAUNCH_CMD=(python3 -m http.server "$PORT" --bind "$HOST" --directory viewer)
else
    echo "[-] Erreur : Python 3 n'est pas installé sur ce système."
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
    elif command -v open >/dev/null 2>&1; then
        open "$URL" >/dev/null 2>&1 || true
    fi
) &

echo "[+] Démarrage du serveur visualiseur local..."
echo "----------------------------------------------------------"
echo "   Interface Principale : $URL"
echo "   Planche-Contact 12H  : $CONTACT_SHEET_URL"
echo "----------------------------------------------------------"
echo "Appuyez sur Ctrl+C pour arrêter le serveur."
echo ""

# Exécution du serveur
exec "${LAUNCH_CMD[@]}"
