#!/usr/bin/env python3
"""
XZORT Rescue Quadruped CAD build entry point.

The canonical CAD generator is modul.py. Keep this wrapper as the single
entry point used by build.sh, but never fall through to the rescue simulator
(rescue_robot_demo/main.py) as a CAD generator.

Outputs:
    out/PRINT/*.stl
    out/REF/*.step
    out/PRINT_MANIFEST.txt
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "out"
GENERATOR = ROOT / "modul.py"
ALLOWED_SUFFIXES = {".stl", ".step", ".stp"}
ALLOWED_METADATA = {"PRINT_MANIFEST.txt"}


def log(message: str) -> None:
    print(f"[XZORT-CAD] {message}", flush=True)


def clean_output() -> None:
    """Remove stale CAD artifacts only; preserve source and unrelated files."""
    if not OUT.exists():
        OUT.mkdir(parents=True)
        return
    for path in OUT.rglob("*"):
        if path.is_file() and path.suffix.lower() in ALLOWED_SUFFIXES:
            path.unlink()


def run_generator() -> None:
    if not GENERATOR.is_file():
        raise FileNotFoundError(f"CAD generator is missing: {GENERATOR}")
    log(f"Generator: {GENERATOR.name}")
    env = os.environ.copy()
    env["XZORT_ROOT"] = str(ROOT)
    env["XZORT_OUT"] = str(OUT)
    result = subprocess.run(
        [sys.executable, str(GENERATOR)],
        cwd=str(ROOT),
        env=env,
        check=False,
    )
    if result.returncode:
        raise RuntimeError(f"CAD generator failed with exit code {result.returncode}")


def verify_output() -> None:
    if not OUT.is_dir():
        raise RuntimeError("CAD generator did not create out/")

    files = [path for path in OUT.rglob("*") if path.is_file()]
    unexpected = [
        path for path in files
        if path.suffix.lower() not in ALLOWED_SUFFIXES
        and path.name not in ALLOWED_METADATA
    ]
    if unexpected:
        names = ", ".join(str(path.relative_to(ROOT)) for path in unexpected)
        raise RuntimeError(f"Unexpected build output: {names}")

    cad_files = [path for path in files if path.suffix.lower() in ALLOWED_SUFFIXES]
    stl_files = [path for path in cad_files if path.suffix.lower() == ".stl"]
    step_files = [path for path in cad_files if path.suffix.lower() in {".step", ".stp"}]
    if not stl_files:
        raise RuntimeError("CAD build produced no STL print modules.")
    if not step_files:
        raise RuntimeError("CAD build produced no STEP assembly/reference file.")
    empty = [path for path in cad_files if path.stat().st_size == 0]
    if empty:
        raise RuntimeError("Empty CAD output(s): " + ", ".join(map(str, empty)))

    log(f"Verified {len(stl_files)} STL file(s) and {len(step_files)} STEP file(s).")
    for path in sorted(cad_files):
        log(f"  - {path.relative_to(ROOT)}")


def main() -> int:
    log(f"Root: {ROOT}")
    clean_output()
    run_generator()
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
