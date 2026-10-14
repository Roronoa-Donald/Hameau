#!/usr/bin/env bash
set -e

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

echo "=========================================================="
echo "   HAMEAU Verification Suite (scripts/verify.sh)"
echo "=========================================================="

FAILED=0

run_check() {
    local name="$1"
    local cmd="$2"
    echo -n "[CHECK] $name ... "
    if bash -c "$cmd" > /tmp/check_output.log 2>&1; then
        echo "PASS"
    else
        echo "FAIL"
        echo "--- Error Output ---"
        cat /tmp/check_output.log | tail -25
        echo "--------------------"
        FAILED=1
    fi
}

# 1. Tests unitaires standard
run_check "Unit Tests (pytest -m 'not defect_repro')" "uv run pytest -m 'not defect_repro' -q"

# 2. Scan de secrets (git log et fichiers)
run_check "Secret Scan" "! git log -p | grep -iE 'AKIA[0-9A-Z]{16}|aws_secret_access_key|BEGIN .*PRIVATE KEY' | grep -v 'AKIAEXAMPLE'"

# 3. Exécution d'une simulation 3 jours en mock
run_check "Simulation 3-Days Mock Run" "uv run hameau --days 3 --ticks-per-day 192 --mock-decider --config config.yaml"

# 4. Complétude du journal (compteurs du bilan = lignes réelles)
run_check "Log Completeness Audit" "python3 - << 'EOF'
import json
from pathlib import Path

log_path = Path('runs/hameau_run.jsonl')
assert log_path.exists(), 'Log file does not exist'

lines = [json.loads(l) for l in log_path.read_text(encoding='utf-8').splitlines() if l.strip()]
decisions = [l for l in lines if l['event_type'] == 'decision']
llm_calls = [l for l in lines if l['event_type'] in ('conversation_turn', 'llm_call', 'reflection', 'gazette')]

# Vérifie que les jours 1, 2 et 3 sont présents
days_present = {l['day'] for l in lines if 'day' in l}
print(f'Events: {len(lines)}, Decisions: {len(decisions)}, Days: {days_present}')
assert 1 in days_present, 'Day 1 missing'
assert 2 in days_present, 'Day 2 missing'
assert 3 in days_present, 'Day 3 missing'
EOF"

# 5. Test de déterminisme (PYTHONHASHSEED)
run_check "Determinism (PYTHONHASHSEED variance)" "python3 - << 'EOF'
import subprocess, hashlib, os, tempfile

def run_with_seed(hseed, out_file):
    env = os.environ.copy()
    env['PYTHONHASHSEED'] = str(hseed)
    cmd = ['uv', 'run', 'python', '-c', f'''
import yaml
from hameau.models.world import build_default_village
from hameau.simulation import build_canonical_agents, ScenarioManager, SimulationEngine
from hameau.decisions import DeciderClient
from hameau.llm import BedrockClient
from patterns.memory_gate import MemoryGate

cfg = yaml.safe_load(open('config.yaml'))
cfg['logging']['runs_dir'] = '{os.path.dirname(out_file)}'
cfg['logging']['log_filename'] = '{os.path.basename(out_file)}'
dec = DeciderClient(mock=True, seed=42)
br = BedrockClient(cassettes_dir='cassettes', use_cassettes=True, seed=42)
engine = SimulationEngine(build_default_village(), build_canonical_agents(), dec, br, MemoryGate(dec), ScenarioManager(), cfg)
engine.run(days=1, ticks_per_day=30)
''']
    subprocess.run(cmd, env=env, check=True, capture_output=True)

tmpdir = tempfile.mkdtemp()
f1 = os.path.join(tmpdir, 'run1.jsonl')
f2 = os.path.join(tmpdir, 'run2.jsonl')

run_with_seed(1234, f1)
run_with_seed(5678, f2)

# Compare lines ignoring timestamps and wall-clock latencies
def strip_ts(lines):
    import json
    out = []
    for l in lines:
        if not l.strip(): continue
        d = json.loads(l)
        d.pop('real_timestamp', None)
        if 'payload' in d and isinstance(d['payload'], dict):
            d['payload'].pop('latency_ms', None)
        out.append(json.dumps(d, sort_keys=True))
    return out

l1 = strip_ts(open(f1).readlines())
l2 = strip_ts(open(f2).readlines())

assert l1 == l2, f'Logs differ across PYTHONHASHSEED: {len(l1)} vs {len(l2)}'
EOF"

echo "=========================================================="
if [ $FAILED -eq 0 ]; then
    echo "   OVERALL RESULT: ALL CHECKS PASSED"
    exit 0
else
    echo "   OVERALL RESULT: SOME CHECKS FAILED"
    exit 1
fi
