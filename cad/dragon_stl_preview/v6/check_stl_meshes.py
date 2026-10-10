#!/usr/bin/env python3
"""Fail-closed STL QA for XZORT Dragon V6 exports.

Usage: python check_stl_meshes.py [directory]
Requires trimesh. This validates mesh topology only; it does NOT validate fit,
servo loads, fasteners, battery clearance, or safe robot operation.
"""
from pathlib import Path
import sys
import trimesh

root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("out_v6")
files = sorted(root.glob("*.stl"))
if not files:
    raise SystemExit(f"FAIL: no STL files found in {root.resolve()}")

failed = False
print(f"Checking {len(files)} STL files in {root.resolve()}")
for path in files:
    try:
        mesh = trimesh.load_mesh(path, file_type="stl", process=True)
        if isinstance(mesh, trimesh.Scene):
            mesh = mesh.to_geometry()
        if not isinstance(mesh, trimesh.Trimesh) or mesh.is_empty:
            raise ValueError("empty or unsupported mesh")
        dims = tuple(round(float(v), 2) for v in mesh.extents)
        watertight = bool(mesh.is_watertight)
        winding = bool(mesh.is_winding_consistent)
        volume_ok = bool(mesh.is_volume)
        status = "PASS" if watertight and winding and volume_ok else "FAIL"
        print(f"{status}: {path.name}: extents={dims} mm, watertight={watertight}, "
              f"winding={winding}, positive_volume={volume_ok}, components={len(mesh.split())}")
        if status != "PASS":
            failed = True
    except Exception as exc:
        print(f"FAIL: {path.name}: {exc}")
        failed = True

if failed:
    raise SystemExit("STL QA FAILED. Do not use these files for functional printing until repaired.")
print("STL topology QA passed. This is not a mechanical fit or safety certification.")
