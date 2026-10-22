#!/usr/bin/env python3
"""Packaging utility to create ultra-lightweight replay archives for HAMEAU."""

import os
import zipfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def build_viewer_zip(output_name: str = "hameau-visualiseur-3j.zip") -> Path:
    out_path = REPO_ROOT / output_name
    viewer_files = ["roadmap.html", "README.md", "scripts/run_viewer.sh"]
    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as z:
        for f in viewer_files:
            fp = REPO_ROOT / f
            if fp.exists():
                z.write(fp, f)
        viewer_dir = REPO_ROOT / "viewer"
        for root, _, files in os.walk(viewer_dir):
            for file in files:
                p = Path(root) / file
                rel = p.relative_to(REPO_ROOT)
                z.write(p, str(rel))
    mb = out_path.stat().st_size / (1024 * 1024)
    print(f"[OK] {output_name} généré : {mb:.2f} Mo")
    return out_path


def build_full_dist_zip(output_name: str = "hameau-complet-sans-venv.zip") -> Path:
    out_path = REPO_ROOT / output_name
    excluded = {".venv", ".git", "runs", "__pycache__", ".pytest_cache", ".taskstate"}
    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as z:
        for root, _, files in os.walk(REPO_ROOT):
            parts = Path(root).relative_to(REPO_ROOT).parts
            if any(p in excluded for p in parts):
                continue
            for file in files:
                if file.endswith(".zip"):
                    continue
                p = Path(root) / file
                rel = p.relative_to(REPO_ROOT)
                z.write(p, str(rel))
    mb = out_path.stat().st_size / (1024 * 1024)
    print(f"[OK] {output_name} généré : {mb:.2f} Mo")
    return out_path


if __name__ == "__main__":
    build_viewer_zip()
    build_full_dist_zip()
