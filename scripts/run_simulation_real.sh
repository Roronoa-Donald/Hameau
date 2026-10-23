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
echo "[+] Lancement de la simulation en mode réel (GPU local + Bedrock en direct)..."
START_TIME=$(date +%s)
uv run hameau --days "$DAYS" --no-cassettes --output "$OUTPUT_FILE"
END_TIME=$(date +%s)

DURATION=$((END_TIME - START_TIME))

echo "[+] Synchronisation du visualiseur (live_run et sample_run)..."
cp "$OUTPUT_FILE" viewer/live_run.jsonl
cp "$OUTPUT_FILE" viewer/sample_run.jsonl

echo "[+] Mise à jour des métriques officielles et de la documentation..."
uv run python scripts/build_numbers.py --run-log "$OUTPUT_FILE" --sync-viewer --generate-docs

echo "[+] Régénération des archives de distribution (.zip)..."
uv run python scripts/package_dist.py

echo ""
echo "=========================================================="
echo "   Simulation réelle achevée en ${DURATION}s !"
echo "   Fichier généré : $OUTPUT_FILE"
echo "   Mis à jour     : viewer/live_run.jsonl & viewer/sample_run.jsonl"
echo "   Métriques      : results/summary.json & viewer/summary.json"
echo "   Archives .zip  : hameau-visualiseur-3j.zip (actualisé)"
echo "=========================================================="
echo "Pour visualiser le résultat avec les personnages 2D animés :"
echo "   ./scripts/run_viewer.sh"
echo "=========================================================="
