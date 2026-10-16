#!/usr/bin/env bash
# ==============================================================================
# HAMEAU — Simulation Autonome en Mode Réel (GPU Local CUDA + AWS Bedrock)
# ==============================================================================
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

DAYS="${1:-3}"
OUTPUT_FILE="runs/run_real_${DAYS}j.jsonl"
mkdir -p runs

echo "=========================================================="
echo "   HAMEAU — Exécution Simulation Réelle (${DAYS} Jour(s))"
echo "=========================================================="
echo "Modèle de décision : Strands Decider 2B (GPU Local CUDA)"
echo "Modèle de dialogue : Amazon Bedrock Nova Micro (us-east-1)"
echo "Fichier de sortie  : $OUTPUT_FILE"
echo ""

# Vérification GPU CUDA
echo "[*] Vérification du GPU CUDA..."
GPU_STATUS=$(uv run python -c "import torch; print(f'CUDA disponible: {torch.cuda.is_available()} | GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"Aucun\"}')" 2>/dev/null || echo "CUDA: Erreur vérification")
echo "    $GPU_STATUS"

# Vérification AWS Bedrock
echo "[*] Vérification des accès AWS..."
if command -v aws >/dev/null 2>&1; then
    AWS_IDENTITY=$(aws sts get-caller-identity --query "Arn" --output text 2>/dev/null || echo "Non authentifié")
    echo "    Compte AWS : $AWS_IDENTITY"
fi

echo ""
echo "[+] Lancement de la simulation..."
START_TIME=$(date +%s)
uv run hameau --days "$DAYS" --output "$OUTPUT_FILE"
END_TIME=$(date +%s)

DURATION=$((END_TIME - START_TIME))

# Copie vers viewer/live_run.jsonl pour rejeu immédiat dans le visualiseur
cp "$OUTPUT_FILE" viewer/live_run.jsonl

echo ""
echo "=========================================================="
echo "   Simulation réelle achevée en ${DURATION}s !"
echo "   Fichier généré : $OUTPUT_FILE"
echo "   Mis à jour     : viewer/live_run.jsonl"
echo "=========================================================="
echo "Pour visualiser le résultat avec les personnages 2D animés :"
echo "   ./scripts/run_viewer.sh"
echo "=========================================================="
