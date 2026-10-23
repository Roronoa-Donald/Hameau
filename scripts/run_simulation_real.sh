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
echo "   HAMEAU — Real Simulation Execution (${DAYS} Day(s))"
echo "=========================================================="
echo "Decision Model : Strands Decider 2B (Local CUDA GPU)"
echo "Dialogue Model : Amazon Bedrock Nova Micro (us-east-1)"
echo "Output Log     : $OUTPUT_FILE"
echo ""

# Verify CUDA GPU
echo "[*] Checking CUDA GPU..."
GPU_STATUS=$(uv run python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()} | GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"None\"}')" 2>/dev/null || echo "CUDA: Check error")
echo "    $GPU_STATUS"

# Verify AWS Bedrock
echo "[*] Checking AWS credentials..."
if command -v aws >/dev/null 2>&1; then
    AWS_IDENTITY=$(aws sts get-caller-identity --query "Arn" --output text 2>/dev/null || echo "Unauthenticated")
    echo "    AWS Account : $AWS_IDENTITY"
fi

echo ""
echo "[+] Starting real simulation (Local GPU + Live Bedrock)..."
START_TIME=$(date +%s)
uv run hameau --days "$DAYS" --no-cassettes --output "$OUTPUT_FILE"
END_TIME=$(date +%s)

DURATION=$((END_TIME - START_TIME))

echo "[+] Syncing viewer logs (live_run and sample_run)..."
cp "$OUTPUT_FILE" viewer/live_run.jsonl
cp "$OUTPUT_FILE" viewer/sample_run.jsonl

echo "[+] Updating official metrics and documentation..."
uv run python scripts/build_numbers.py --run-log "$OUTPUT_FILE" --sync-viewer --generate-docs

echo "[+] Re-generating distribution archives (.zip)..."
uv run python scripts/package_dist.py

echo ""
echo "=========================================================="
echo "   Real simulation completed in ${DURATION}s!"
echo "   Output log     : $OUTPUT_FILE"
echo "   Updated        : viewer/live_run.jsonl & viewer/sample_run.jsonl"
echo "   Metrics        : results/summary.json & viewer/summary.json"
echo "   Archives (.zip): hameau-visualiseur-3j.zip (refreshed)"
echo "=========================================================="
echo "To visualize the results with animated 2D citizens:"
echo "   ./scripts/run_viewer.sh"
echo "=========================================================="
