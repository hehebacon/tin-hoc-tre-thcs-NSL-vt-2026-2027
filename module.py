#!/usr/bin/env python3
"""
XZORT Rescue Quadruped CAD build entry point.

This file is intentionally the single Python entry point used by build.sh.
It discovers the existing CAD generator in the repository, runs it, and
verifies that build output contains only STL/STEP artifacts.

Expected output directory:
    out/
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "out"

# Candidate existing CAD entry points. The first existing one is used.
CANDIDATES = [
    ROOT / "main.py",
    ROOT / "cad" / "main.py",
    ROOT / "CAD" / "main.py",
    ROOT / "src" / "main.py",
    ROOT / "scripts" / "main.py",
]


def log(message: str) -> None:
    print(f"[XZORT-CAD] {message}", flush=True)


def find_entrypoint() -> Path:
    for path in CANDIDATES:
        if path.is_file() and path.resolve() != Path(__file__).resolve():
            return path

    # Fall back to a shallow repository scan without touching .git/out.
    for path in sorted(ROOT.rglob("*.py")):
        if any(part in {".git", "out", "__pycache__", ".venv", "venv"} for part in path.parts):
            continue
        if path.name == "main.py":
            return path

    raise FileNotFoundError(
        "Khong tim thay CAD entry point (main.py). "
        "Hay dat generator chinh cua CAD vao root/cad/src va dat ten main.py."
    )


def clean_output() -> None:
    OUT.mkdir(parents=True, exist_ok=True)

    # Never delete source files here. Only remove old generated CAD artifacts.
    for item in OUT.iterdir():
        if item.is_file() and item.suffix.lower() in {".stl", ".step", ".stp"}:
            item.unlink()


def run_generator(entrypoint: Path) -> None:
    log(f"Generator: {entrypoint.relative_to(ROOT)}")
    env = os.environ.copy()
    env["XZORT_ROOT"] = str(ROOT)
    env["XZORT_OUT"] = str(OUT)

    result = subprocess.run(
        [sys.executable, str(entrypoint)],
        cwd=str(ROOT),
        env=env,
    )
    if result.returncode != 0:
        raise RuntimeError(f"CAD generator failed with exit code {result.returncode}")


def verify_output() -> None:
    allowed = {".stl", ".step", ".stp"}
    generated = [p for p in OUT.rglob("*") if p.is_file()]

    bad = [p for p in generated if p.suffix.lower() not in allowed]
    if bad:
        names = ", ".join(str(p.relative_to(ROOT)) for p in bad)
        raise RuntimeError(f"out/ co file khong phai STL/STEP: {names}")

    cad_files = [p for p in generated if p.suffix.lower() in allowed]
    if not cad_files:
        raise RuntimeError("Build khong tao ra STL/STEP nao trong out/.")

    log(f"Generated {len(cad_files)} CAD file(s):")
    for p in sorted(cad_files):
        log(f"  - {p.relative_to(ROOT)}")


def main() -> int:
    log(f"Root: {ROOT}")
    clean_output()
    entrypoint = find_entrypoint()
    run_generator(entrypoint)
    verify_output()
    log("BUILD PASS")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        log("Interrupted.")
        raise SystemExit(130)
    except Exception as exc:
        print(f"[XZORT-CAD] BUILD FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
