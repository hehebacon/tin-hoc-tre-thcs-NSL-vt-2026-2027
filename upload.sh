#!/bin/bash

set -e

# ============================================================
# XZORT RESCUE QUADRUPED — CAD BUILD + GITHUB UPLOADER
# - Runs modul.py
# - Generates CAD into ./out
# - Uploads STL/STEP from ./out
# - Same filename/path = Git replaces the previous version
# - Large STL/STEP files use Git LFS
# ============================================================

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

echo "=========================================="
echo "   XZORT CAD -> GITHUB UPLOADER"
echo "=========================================="
echo

echo "[1/7] Project"
echo "Root: $ROOT"
echo

echo "[2/7] Python / build123d"
PYTHON="python3"

if [ -x "$ROOT/.venv/bin/python" ]; then
    PYTHON="$ROOT/.venv/bin/python"
fi

if ! "$PYTHON" -c "import build123d" >/dev/null 2>&1; then
    echo "build123d is not installed."
    echo "Installing build123d..."
    "$PYTHON" -m pip install --upgrade pip
    "$PYTHON" -m pip install build123d
fi

echo "Python: $PYTHON"
echo

echo "[3/7] Git LFS"
if ! command -v git-lfs >/dev/null 2>&1; then
    echo "ERROR: git-lfs is not installed."
    echo
    echo "Install it once with:"
    echo "    sudo apt update && sudo apt install git-lfs"
    echo "    git lfs install"
    exit 1
fi

git lfs install

# Track heavy CAD binaries through Git LFS.
git lfs track "out/*.stl"
git lfs track "out/*.step"

echo

echo "[4/7] Building CAD"
rm -rf "$ROOT/out"
mkdir -p "$ROOT/out"

"$PYTHON" "$ROOT/modul.py"

echo
echo "Generated CAD files:"
find "$ROOT/out" -maxdepth 1 -type f \( -name "*.stl" -o -name "*.step" \) -printf "  %f  %s bytes\n" | sort
echo

echo "[5/7] Git"
if [ ! -d "$ROOT/.git" ]; then
    git init
fi

git branch -M main

REPO="git@github.com:hehebacon/tin-hoc-tre-thcs-NSL-vt-2026-2027.git"

if git remote get-url origin >/dev/null 2>&1; then
    git remote set-url origin "$REPO"
else
    git remote add origin "$REPO"
fi

echo "Remote: $REPO"
echo

echo "[6/7] Adding ./out"
git add .gitattributes
git add out/

echo
echo "Changes:"
git status --short
echo

if git diff --cached --quiet; then
    echo "No CAD changes to upload."
else
    git commit -m "Update generated CAD $(date '+%Y-%m-%d %H:%M:%S')"
fi

echo
echo "[7/7] Pushing"
git push -u origin main

echo
echo "=========================================="
echo "             CAD UPLOAD DONE"
echo "=========================================="
echo
echo "CAD location in GitHub:"
echo "out/*.stl"
echo "out/*.step"
echo
echo "Next time:"
echo "    ./upload.sh"
echo
echo "If modul.py changes, the same filenames are updated/replaced."
