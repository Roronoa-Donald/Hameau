#!/usr/bin/env bash
# ==============================================================================
# HAMEAU — Simulation Autonome en Mode Mock (Ultra-rapide, 0$ AWS, sans GPU)
# ==============================================================================
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

DAYS="${1:-1}"
OUTPUT_FILE="runs/run_mock_${DAYS}j.jsonl"
mkdir -p runs

echo "=========================================================="
echo "   HAMEAU — Exécution Simulation Mock (${DAYS} Jour(s))"
echo "=========================================================="
echo "Mode : Décisions Mock déterministes + Cassettes Bedrock"
echo "Fichier de sortie : $OUTPUT_FILE"
echo ""

START_TIME=$(date +%s)
uv run hameau --days "$DAYS" --mock-decider --output "$OUTPUT_FILE"
END_TIME=$(date +%s)

DURATION=$((END_TIME - START_TIME))

# Copie vers viewer/live_run.jsonl pour rejeu immédiat dans le visualiseur
cp "$OUTPUT_FILE" viewer/live_run.jsonl

echo ""
echo "=========================================================="
echo "   Simulation terminée avec succès en ${DURATION}s !"
echo "   Fichier généré : $OUTPUT_FILE"
echo "   Mis à jour     : viewer/live_run.jsonl"
echo "=========================================================="
echo "Pour visualiser ce run :"
echo "   ./scripts/run_viewer.sh"
echo "=========================================================="
