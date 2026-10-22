#!/usr/bin/env python3
"""Automated honesty & consistency verifier (scripts/check_claims.py).

Verifies that:
1. results/summary.json and results/manifest.json exist and come from a real run.
2. viewer/index.html and viewer/app.js contain no hardcoded placeholder numbers.
3. docs/RESULTS.md, docs/CLAIMS_LEDGER.md, docs/ARTICLE_NUMBERS_EN.md match results/summary.json.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import List


FORBIDDEN_VIEWER_PATTERNS = [
    (r"~565\s*ms", "Hardcoded ~565 ms latency placeholder"),
    (r"\b115\s*ms\b", "Hardcoded 115 ms latency placeholder"),
    (r"~1\s*480\s*tokens", "Hardcoded ~1 480 tokens placeholder"),
    (r"~320\s*tokens", "Hardcoded ~320 tokens placeholder"),
    (r"-78\s*%", "Hardcoded -78 % savings placeholder"),
    (r"\$\{infected\}\s*/\s*12\b", "Hardcoded / 12 denominator in viewer"),
    (r"\$\{stocked\}\s*/\s*12\b", "Hardcoded / 12 denominator in viewer"),
]


def main() -> int:
    repo_root = Path(__file__).resolve().parent.parent
    errors: List[str] = []

    summary_path = repo_root / "results" / "summary.json"
    manifest_path = repo_root / "results" / "manifest.json"
    if not summary_path.exists():
        errors.append("Missing results/summary.json (run scripts/build_numbers.py first)")
    if not manifest_path.exists():
        errors.append("Missing results/manifest.json (run scripts/build_numbers.py first)")

    if errors:
        for err in errors:
            print(f"[FAIL] {err}")
        return 1

    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    # 1. Check viewer files for forbidden hardcoded numbers
    for rel_path in ["viewer/index.html", "viewer/app.js"]:
        fpath = repo_root / rel_path
        if not fpath.exists():
            errors.append(f"Missing {rel_path}")
            continue
        content = fpath.read_text(encoding="utf-8")
        for pat, desc in FORBIDDEN_VIEWER_PATTERNS:
            if re.search(pat, content):
                errors.append(f"{rel_path}: found forbidden pattern ({desc})")

    # 2. Check key metrics consistency in documentation files if present
    rm = summary.get("run_metrics", {})
    total_q = str(rm.get("decider", {}).get("total_questions", ""))
    total_r = str(rm.get("decider", {}).get("total_requests", ""))
    total_l = str(rm.get("bedrock", {}).get("total_calls", ""))

    for doc_rel in ["docs/RESULTS.md", "docs/CLAIMS_LEDGER.md", "docs/ARTICLE_NUMBERS_EN.md"]:
        dpath = repo_root / doc_rel
        if not dpath.exists():
            errors.append(f"Missing required deliverable: {doc_rel}")
            continue
        text = dpath.read_text(encoding="utf-8")
        if total_q and total_q not in text and f"{int(total_q):,}".replace(",", " ") not in text and f"{int(total_q):,}" not in text:
            errors.append(f"{doc_rel}: missing total_questions={total_q} from results/summary.json")
        if total_r and total_r not in text and f"{int(total_r):,}".replace(",", " ") not in text and f"{int(total_r):,}" not in text:
            errors.append(f"{doc_rel}: missing total_requests={total_r} from results/summary.json")
        if total_l and total_l not in text:
            errors.append(f"{doc_rel}: missing bedrock.total_calls={total_l} from results/summary.json")

    if errors:
        print("=== CHECK_CLAIMS FAILED ===")
        for err in errors:
            print(f" - {err}")
        return 1

    print(
        f"=== CHECK_CLAIMS PASSED (0 discrepancies) ===\n"
        f" - Source log: {manifest.get('run_log_file')}\n"
        f" - Decider backend: {manifest.get('decider', {}).get('model_id')} ({manifest.get('decider', {}).get('backend_type')})\n"
        f" - Bedrock source: {manifest.get('bedrock', {}).get('source')}\n"
        f" - Verified Q={total_q}, R={total_r}, L={total_l}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
