#!/usr/bin/env bash
# Build the dragon CAD in a temporary .venv, push generated files, then remove .venv.
set -Eeuo pipefail

ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

BRANCH="feat/dragon-shell-35cm"
VENV="$ROOT/.venv"
CREATED_VENV=0
PUSHED=0

cleanup() {
  status=$?
  if [[ "$CREATED_VENV" -eq 1 && -d "$VENV" ]]; then
    echo "[CLEANUP] Removing temporary .venv ..."
    rm -rf -- "$VENV"
    echo "[CLEANUP] .venv removed."
  fi
  if [[ "$PUSHED" -eq 1 ]]; then
    echo "[DONE] CAD build and GitHub push completed."
  elif [[ "$status" -ne 0 ]]; then
    echo "[STOP] Script failed (exit $status). Check the error above."
    echo "[INFO] Any generated output remains on disk for debugging; .venv was cleaned up if this script created it."
  fi
  exit "$status"
}
trap cleanup EXIT

command -v git >/dev/null || { echo "ERROR: git is not installed."; exit 1; }
command -v python3 >/dev/null || { echo "ERROR: python3 is not installed."; exit 1; }
git rev-parse --is-inside-work-tree >/dev/null 2>&1 || { echo "ERROR: run this from a cloned Git repository."; exit 1; }

CURRENT_BRANCH="$(git branch --show-current)"
if [[ "$CURRENT_BRANCH" != "$BRANCH" ]]; then
  echo "ERROR: current branch is '$CURRENT_BRANCH', expected '$BRANCH'."
  echo "Run: git switch $BRANCH"
  exit 1
fi

if [[ -e "$VENV" ]]; then
  echo "ERROR: .venv already exists. To avoid deleting an environment you may need, rename/remove it first:"
  echo "  mv .venv .venv.backup"
  exit 1
fi

if ! git remote get-url origin >/dev/null 2>&1; then
  echo "ERROR: Git remote 'origin' is missing."
  exit 1
fi

# Require a clean worktree so this script never accidentally includes unrelated edits.
if [[ -n "$(git status --porcelain)" ]]; then
  echo "ERROR: working tree is not clean. Commit/stash your changes first."
  git status --short
  exit 1
fi

if [[ ! -f module.py || ! -f dragon_cad_v2.py ]]; then
  echo "ERROR: module.py or dragon_cad_v2.py is missing."
  exit 1
fi

echo "[1/5] Creating temporary Python environment..."
python3 -m venv "$VENV"
CREATED_VENV=1

echo "[2/5] Installing Build123d..."
"$VENV/bin/python" -m pip install --upgrade pip
"$VENV/bin/python" -m pip install build123d

echo "[3/5] Building STEP/STL files..."
"$VENV/bin/python" module.py

STEP="$ROOT/out/REF/full_assembly.step"
MANIFEST="$ROOT/out/PRINT_MANIFEST.txt"
if [[ ! -s "$STEP" || ! -s "$MANIFEST" ]]; then
  echo "ERROR: expected STEP or manifest output is missing/empty."
  exit 1
fi
STL_COUNT="$(find "$ROOT/out/PRINT" -maxdepth 1 -type f -name '*.stl' -size +0c | wc -l)"
if [[ "$STL_COUNT" -lt 1 ]]; then
  echo "ERROR: no non-empty STL files were generated."
  exit 1
fi
echo "[CHECK] STEP exists; found $STL_COUNT non-empty STL file(s)."

echo "[4/5] Committing generated CAD files..."
git add out/REF/full_assembly.step out/PRINT/*.stl out/PRINT_MANIFEST.txt
if git diff --cached --quiet; then
  echo "[INFO] Generated files match the current commit; no new artifact commit needed."
else
  git commit -m "build: refresh generated dragon CAD artifacts"
fi

echo "[5/5] Pushing branch to GitHub..."
git push -u origin "$BRANCH"
PUSHED=1

# EXIT trap removes .venv after the push finishes.
echo "[INFO] Push succeeded; temporary .venv will now be removed."
