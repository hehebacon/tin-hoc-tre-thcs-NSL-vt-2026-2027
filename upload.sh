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
PYTHON="$ROOT/.venv/bin/python"

# Create an isolated environment automatically; avoids Kali/Debian PEP 668.
if [ ! -x "$PYTHON" ]; then
    echo "[INFO] Creating local Python environment: .venv"
    if ! python3 -m venv "$ROOT/.venv"; then
        echo "[ERROR] Python venv support is missing. Run: sudo apt install python3-venv"
        exit 1
    fi
fi

if ! "$PYTHON" -c "import build123d" >/dev/null 2>&1; then
    echo "[INFO] Installing build123d into .venv..."
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

echo "[4/8] Cleaning old generated CAD"
rm -rf "$ROOT/out"
mkdir -p "$ROOT/out"

# Remove old generated CAD already tracked in Git; source files are untouched.
while IFS= read -r tracked; do
    [ -n "$tracked" ] && git rm -f --ignore-unmatch -- "$tracked" >/dev/null 2>&1 || true
done < <(git ls-files | grep -Ei "\\.(stl|step|stp)$" || true)

echo

echo "[5/8] Building CAD"

"$PYTHON" "$ROOT/modul.py"

echo
echo "Generated CAD files:"
find "$ROOT/out" -maxdepth 1 -type f \( -name "*.stl" -o -name "*.step" \) -printf "  %f  %s bytes\n" | sort
echo

echo "[6/8] Git"
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

echo "[7/8] Adding generated CAD"
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
echo "[8/8] Pushing"
git push -u origin main

echo
echo "=========================================="
echo "             CAD UPLOAD DONE"
echo "=========================================="
echo
echo "CAD location in GitHub:"
echo "out/PRINT/*.stl"
echo "out/REF/full_assembly.step"
echo
echo "Next time:"
echo "    ./upload.sh"
echo
echo "Old STL/STEP are removed before every build; grouped outputs replace them cleanly."
