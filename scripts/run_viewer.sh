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
echo "   HAMEAU — Multi-Agent 2D Interactive Viewer"
echo "=========================================================="
echo "Directory : $REPO_ROOT"
echo "Port      : $PORT"

# Environment check: use uv if present, otherwise fallback to standard python3
if command -v uv >/dev/null 2>&1 && uv run python -c "import hameau" >/dev/null 2>&1; then
    LAUNCH_CMD=(uv run hameau --serve --port "$PORT")
elif command -v python3 >/dev/null 2>&1; then
    echo "[i] Universal lightweight mode (no GPU or uv required): standard Python HTTP server"
    LAUNCH_CMD=(python3 -m http.server "$PORT" --bind "$HOST" --directory viewer)
else
    echo "[-] Error: Python 3 is not installed on this system."
    exit 1
fi

# Check if port is already in use
if command -v lsof >/dev/null 2>&1; then
    PID_ON_PORT=$(lsof -ti :"$PORT" 2>/dev/null || true)
    if [ -n "$PID_ON_PORT" ]; then
        echo "[!] Port $PORT is already in use by process $PID_ON_PORT."
        echo "    Attempting to free port..."
        kill -15 "$PID_ON_PORT" 2>/dev/null || kill -9 "$PID_ON_PORT" 2>/dev/null || true
        sleep 1
    fi
fi

# Attempt to open browser in background after 1.2s
(
    sleep 1.2
    if command -v xdg-open >/dev/null 2>&1; then
        xdg-open "$URL" >/dev/null 2>&1 || true
    elif command -v open >/dev/null 2>&1; then
        open "$URL" >/dev/null 2>&1 || true
    fi
) &

echo "[+] Starting local secure viewer server..."
echo "----------------------------------------------------------"
echo "   Main Interface : $URL"
echo "   Contact Sheet  : $CONTACT_SHEET_URL"
echo "----------------------------------------------------------"
echo "Press Ctrl+C to stop the server."
echo ""

# Exécution du serveur
exec "${LAUNCH_CMD[@]}"
