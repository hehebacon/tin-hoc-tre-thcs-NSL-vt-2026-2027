#!/usr/bin/env bash
set -Eeuo pipefail

# XZORT Rescue Quadruped - one-command CAD sync/build/push
# Usage:
#   ./build.sh
#
# Flow:
#   1. Check working tree
#   2. Pull latest source from GitHub
#   3. Run module.py
#   4. Verify out/ contains only STL/STEP
#   5. Commit changed source/build files
#   6. Push to the current upstream branch
#
# Important:
#   - Does NOT use git reset --hard.
#   - Does NOT delete source files.
#   - Does NOT push generated out/ files unless they are already tracked.
#   - If local changes exist before pull, the script stops instead of overwriting them.

ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

export PYTHONUNBUFFERED=1

echo "[XZORT-BUILD] root=$ROOT"

if [[ ! -d .git ]]; then
  echo "[XZORT-BUILD] ERROR: not a git repository."
  exit 1
fi

REMOTE="$(git remote get-url origin 2>/dev/null || true)"
if [[ -z "$REMOTE" ]]; then
  echo "[XZORT-BUILD] ERROR: origin remote is missing."
  exit 1
fi

BRANCH="$(git symbolic-ref --quiet --short HEAD || true)"
if [[ -z "$BRANCH" ]]; then
  echo "[XZORT-BUILD] ERROR: detached HEAD."
  exit 1
fi

UPSTREAM="$(git rev-parse --abbrev-ref --symbolic-full-name '@{u}' 2>/dev/null || true)"

if [[ -n "$(git status --porcelain)" ]]; then
  echo "[XZORT-BUILD] ERROR: local changes detected."
  echo "[XZORT-BUILD] Commit/stash them first so the pull cannot overwrite work."
  git status --short
  exit 1
fi

echo "[XZORT-BUILD] Fetching latest GitHub state..."
git fetch --prune origin

if [[ -n "$UPSTREAM" ]]; then
  echo "[XZORT-BUILD] Fast-forward pull from $UPSTREAM..."
  git pull --ff-only
else
  echo "[XZORT-BUILD] No upstream configured; syncing $BRANCH with origin/$BRANCH..."
  if git show-ref --verify --quiet "refs/remotes/origin/$BRANCH"; then
    git merge --ff-only "origin/$BRANCH"
  else
    echo "[XZORT-BUILD] origin/$BRANCH does not exist; continuing with local branch."
  fi
fi

if [[ ! -f module.py ]]; then
  echo "[XZORT-BUILD] ERROR: module.py is missing after sync."
  exit 1
fi

chmod +x module.py

echo "[XZORT-BUILD] Running module.py..."
python3 module.py

echo "[XZORT-BUILD] Checking git changes..."
git status --short

# Only source/build scripts are committed automatically.
# Generated CAD in out/ remains local unless it was already tracked.
git add module.py build.sh

if [[ -n "$(git diff --cached --name-only)" ]]; then
  git commit -m "chore(cad): update automated module build"
fi

echo "[XZORT-BUILD] Pushing..."
if [[ -n "$UPSTREAM" ]]; then
  git push
else
  git push -u origin "$BRANCH"
fi

echo "[XZORT-BUILD] DONE"
