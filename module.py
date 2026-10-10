#!/usr/bin/env python3
"""Deterministic CAD build entry point for XZORT Rescue Dragon Quadruped."""

from __future__ import annotations
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = Path(os.environ.get("XZORT_OUT", ROOT / "out"))
ENTRYPOINT = ROOT / "dragon_cad_v2.py"

def main() -> int:
    if not ENTRYPOINT.is_file():
        raise FileNotFoundError(f"CAD generator missing: {ENTRYPOINT}")
    OUT.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env["XZORT_ROOT"] = str(ROOT)
    env["XZORT_OUT"] = str(OUT)
    print(f"[XZORT-CAD] Generator: {ENTRYPOINT.name}", flush=True)
    result = subprocess.run([sys.executable, str(ENTRYPOINT)], cwd=ROOT, env=env)
    if result.returncode:
        raise RuntimeError(f"CAD generator failed with exit code {result.returncode}")
    artifacts = sorted(p for p in OUT.rglob("*") if p.is_file() and p.suffix.lower() in {".stl", ".step", ".stp"})
    if not artifacts:
        raise RuntimeError("No STL/STEP files were generated.")
    print(f"[XZORT-CAD] BUILD PASS: {len(artifacts)} CAD artifact(s)")
    for path in artifacts:
        print(f"[XZORT-CAD] {path.relative_to(ROOT)}")
    return 0

if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print("[XZORT-CAD] Interrupted.", file=sys.stderr)
        raise SystemExit(130)
    except Exception as exc:
        print(f"[XZORT-CAD] BUILD FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
