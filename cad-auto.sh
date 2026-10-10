#!/usr/bin/env bash
set -Eeuo pipefail

# Run from anywhere inside the robot Git repository:
#   bash cad-auto.sh
# It preserves existing STL/STEP files unless a new build passes validation.

BRANCH="feat/dragon-shell-35cm"
CAD_FILE="dragon_cad_v2.py"
OUT_DIR="out"
TEMP_DIR=""
STASHED=0

die() { printf '\n[ERROR] %s\n' "$*" >&2; exit 1; }
cleanup() {
  rc=$?
  if [[ -n "${TEMP_DIR:-}" && -d "$TEMP_DIR" ]]; then rm -rf -- "$TEMP_DIR"; fi
  if [[ $rc -ne 0 ]]; then
    printf '\n[STOP] Build/push did not complete. Existing generated STL/STEP files were kept unless installation had already finished.\n' >&2
  fi
}
trap cleanup EXIT

command -v git >/dev/null 2>&1 || die "Git is required."
command -v python3 >/dev/null 2>&1 || die "Python 3 is required."
ROOT="$(git rev-parse --show-toplevel 2>/dev/null)" || die "Run this inside the cloned robot repository."
cd "$ROOT"
[[ -f "$CAD_FILE" ]] || die "Missing $CAD_FILE in repository root."

CURRENT_BRANCH="$(git branch --show-current)"
[[ "$CURRENT_BRANCH" == "$BRANCH" ]] || die "Current branch is '$CURRENT_BRANCH', expected '$BRANCH'. Switch to it first."

TEMP_DIR="$(mktemp -d "${TMPDIR:-/tmp}/xzort-cad.XXXXXX")"
VENV="$TEMP_DIR/venv"
BUILD_OUT="$TEMP_DIR/out"
mkdir -p "$BUILD_OUT"

# Save tracked and untracked local work before updating from the remote.
if [[ -n "$(git status --porcelain)" ]]; then
  git stash push --include-untracked -m "cad-auto.sh safety stash $(date +%Y%m%d-%H%M%S)" || die "Could not safely stash local changes."
  STASHED=1
fi

git fetch origin "$BRANCH" || die "Could not fetch origin/$BRANCH."
git pull --ff-only origin "$BRANCH" || die "Local branch cannot fast-forward. Your work is saved in Git stash; no files were overwritten."

# Restore user changes after updating. If conflicts occur, stop rather than overwrite them.
if [[ "$STASHED" -eq 1 ]]; then
  git stash pop || die "Stash restore had conflicts. Your stash is retained; resolve the conflicts before rerunning."
  STASHED=0
fi

[[ -f "$CAD_FILE" ]] || die "CAD source is missing after update."
printf '\n[1/4] Creating temporary Python environment...\n'
python3 -m venv "$VENV" || die "Could not create venv. Install python3-venv using your system package manager."
"$VENV/bin/python" -m pip install --upgrade pip
"$VENV/bin/python" -m pip install build123d

printf '\n[2/4] Building CAD in a temporary folder...\n'
XZORT_OUT="$BUILD_OUT" "$VENV/bin/python" "$CAD_FILE"

[[ -s "$BUILD_OUT/REF/full_assembly.step" ]] || die "STEP export missing or empty."
[[ -s "$BUILD_OUT/PRINT_MANIFEST.txt" ]] || die "Print manifest missing or empty."
STL_COUNT="$(find "$BUILD_OUT/PRINT" -maxdepth 1 -type f -name '*.stl' -size +0c | wc -l | tr -d ' ')"
[[ "$STL_COUNT" -ge 1 ]] || die "No non-empty STL files were generated."

printf '[3/4] CAD build passed: %s STL files. Installing generated files...\n' "$STL_COUNT"
# Prepare a staged output tree, then swap only after the new exports validate.
NEW_OUT="$TEMP_DIR/new-out"
mkdir -p "$NEW_OUT/PRINT" "$NEW_OUT/REF"
cp -a "$BUILD_OUT/PRINT/." "$NEW_OUT/PRINT/"
cp -a "$BUILD_OUT/REF/." "$NEW_OUT/REF/"
cp "$BUILD_OUT/PRINT_MANIFEST.txt" "$NEW_OUT/PRINT_MANIFEST.txt"

BACKUP="$TEMP_DIR/old-out"
if [[ -d "$OUT_DIR" ]]; then mv "$OUT_DIR" "$BACKUP"; fi
if ! mv "$NEW_OUT" "$OUT_DIR"; then
  [[ ! -d "$BACKUP" ]] || mv "$BACKUP" "$OUT_DIR"
  die "Could not install new output; previous output restored."
fi

printf '\n[4/4] Committing and pushing CAD source + verified exports...\n'
git add -- "$CAD_FILE" "$OUT_DIR/PRINT" "$OUT_DIR/REF" "$OUT_DIR/PRINT_MANIFEST.txt"
if git diff --cached --quiet; then
  printf '[INFO] No tracked CAD changes to commit.\n'
else
  git commit -m "build(cad): regenerate validated dragon robot STL and STEP"
fi
git push origin "$BRANCH" || die "Push failed. Your local commit and generated files remain saved."
printf '\n[DONE] CAD build succeeded and branch was pushed.\n'
printf 'STL parts: %s\nSTEP: %s\nManifest: %s\n' "$STL_COUNT" "$OUT_DIR/REF/full_assembly.step" "$OUT_DIR/PRINT_MANIFEST.txt"
