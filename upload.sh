#!/usr/bin/env bash
set -e

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

PYTHON="$ROOT/.venv/bin/python"

echo "======================================================"
echo " XZORT RESCUE DRAGON-LIZARD"
echo " AUTO BUILD -> VALIDATE -> COMMIT -> PUSH"
echo "======================================================"

# ------------------------------------------------------
# 1. Python environment
# ------------------------------------------------------

if [ ! -x "$PYTHON" ]; then
    echo "[SETUP] Creating .venv..."
    python3 -m venv "$ROOT/.venv"
fi

if ! "$PYTHON" -c "import build123d" >/dev/null 2>&1; then
    echo "[SETUP] Installing build123d..."
    "$PYTHON" -m pip install --upgrade pip
    "$PYTHON" -m pip install build123d
fi

# ------------------------------------------------------
# 2. Build CAD
# ------------------------------------------------------

echo
echo "[BUILD] Running modul.py..."
"$PYTHON" "$ROOT/modul.py"

# ------------------------------------------------------
# 3. Validate grouped output
# ------------------------------------------------------

PRINT="$ROOT/out/PRINT"
REF="$ROOT/out/REF"

REQUIRED=(
    "body.stl"
    "head.stl"
    "electronics.stl"
    "FL_leg.stl"
    "FR_leg.stl"
    "RL_leg.stl"
    "RR_leg.stl"
    "tail.stl"
)

echo
echo "[CHECK] Checking grouped STL files..."

for file in "${REQUIRED[@]}"; do
    if [ ! -s "$PRINT/$file" ]; then
        echo "[ERROR] Missing or empty: $PRINT/$file"
        exit 1
    fi
    echo "[OK] $file"
done

if [ ! -s "$REF/full_assembly.step" ]; then
    echo "[ERROR] Missing or empty: $REF/full_assembly.step"
    exit 1
fi

echo "[OK] full_assembly.step"

# ------------------------------------------------------
# 4. Make sure OLD individual outputs are NOT uploaded
# ------------------------------------------------------

echo
echo "[CHECK] Removing old individual CAD outputs from Git..."

git rm -r --cached --ignore-unmatch out/PRINT_* >/dev/null 2>&1 || true
git rm -r --cached --ignore-unmatch out/REF_* >/dev/null 2>&1 || true

# ------------------------------------------------------
# 5. Stage current grouped output
# ------------------------------------------------------

echo
echo "[GIT] Staging grouped CAD..."

git add modul.py upload.sh out/

# ------------------------------------------------------
# 6. Commit
# ------------------------------------------------------

if git diff --cached --quiet; then
    echo "[GIT] Nothing new to commit."
else
    git commit -m "Build grouped 35cm rescue dragon CAD"
fi

# ------------------------------------------------------
# 7. Rebase remote changes
# ------------------------------------------------------

echo
echo "[GIT] Syncing with origin/main..."

git pull --rebase origin main

# ------------------------------------------------------
# 8. Push
# ------------------------------------------------------

echo
echo "[GIT] Pushing to GitHub..."

git push origin main

# ------------------------------------------------------
# 9. Final
# ------------------------------------------------------

echo
echo "======================================================"
echo "             BUILD + UPLOAD COMPLETE"
echo "======================================================"
echo
echo "GitHub output:"
echo "  out/PRINT/body.stl"
echo "  out/PRINT/head.stl"
echo "  out/PRINT/electronics.stl"
echo "  out/PRINT/FL_leg.stl"
echo "  out/PRINT/FR_leg.stl"
echo "  out/PRINT/RL_leg.stl"
echo "  out/PRINT/RR_leg.stl"
echo "  out/PRINT/tail.stl"
echo "  out/REF/full_assembly.step"
echo
