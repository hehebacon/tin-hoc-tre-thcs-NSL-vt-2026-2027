#!/usr/bin/env bash
# XZORT Dragon CAD: safe local build for zsh/bash.
# Usage from anywhere inside the cloned repository:
#   zsh run_dragon.sh
# Builds in a temporary directory and replaces out/ only after successful export.
set -Eeuo pipefail

die() { printf '\n[ERROR] %s\n' "$*" >&2; exit 1; }
command -v git >/dev/null 2>&1 || die "Git is required."
command -v python3 >/dev/null 2>&1 || die "Python 3 is required."
ROOT="$(git rev-parse --show-toplevel 2>/dev/null)" || die "Run this inside your cloned robot repository."
cd "$ROOT"
CAD_FILE="dragon_cad_v2.py"
[[ -f "$CAD_FILE" ]] || die "Missing $CAD_FILE at repository root."

TMP="$(mktemp -d "${TMPDIR:-/tmp}/xzort-dragon.XXXXXX")"
cleanup() { rc=$?; rm -rf -- "$TMP"; if [[ $rc -ne 0 ]]; then printf '\n[STOP] Build failed; existing out/ files were not replaced by this script.\n' >&2; fi; }
trap cleanup EXIT

VENV="$TMP/venv"
BUILD_OUT="$TMP/out"
mkdir -p "$BUILD_OUT/PRINT" "$BUILD_OUT/REF"

printf '\n[1/4] Create isolated Python environment...\n'
python3 -m venv "$VENV" || die "Could not create venv. On Kali/Debian, install it with: sudo apt install python3-venv"
"$VENV/bin/python" -m pip install --upgrade pip
"$VENV/bin/python" -m pip install build123d

printf '\n[2/4] Build CAD in temporary output (existing exports are untouched)...\n'
XZORT_OUT="$BUILD_OUT" "$VENV/bin/python" "$CAD_FILE"

[[ -s "$BUILD_OUT/REF/full_assembly.step" ]] || die "STEP file missing or empty."
[[ -s "$BUILD_OUT/PRINT_MANIFEST.txt" ]] || die "Print manifest missing or empty."
STL_COUNT="$(find "$BUILD_OUT/PRINT" -maxdepth 1 -type f -name '*.stl' -size +0c | wc -l | tr -d ' ')"
[[ "$STL_COUNT" -ge 1 ]] || die "No non-empty STL files generated."

printf '\n[3/4] Build checks passed: %s STL files. Installing exports...\n' "$STL_COUNT"
NEW_OUT="$TMP/new-out"
mkdir -p "$NEW_OUT/PRINT" "$NEW_OUT/REF"
cp -a "$BUILD_OUT/PRINT/." "$NEW_OUT/PRINT/"
cp -a "$BUILD_OUT/REF/." "$NEW_OUT/REF/"
cp "$BUILD_OUT/PRINT_MANIFEST.txt" "$NEW_OUT/PRINT_MANIFEST.txt"

# Back up old output in temp first; restore it if installation fails.
BACKUP="$TMP/old-out"
if [[ -d out ]]; then mv out "$BACKUP"; fi
if ! mv "$NEW_OUT" out; then
  [[ ! -d "$BACKUP" ]] || mv "$BACKUP" out
  die "Could not install new out/; previous out/ restored."
fi

printf '\n[4/4] Complete. No git commit or push was performed.\n'
printf 'STL count: %s\nSTEP: %s/out/REF/full_assembly.step\nManifest: %s/out/PRINT_MANIFEST.txt\n' "$STL_COUNT" "$ROOT" "$ROOT"
printf '\nTo inspect changes: git status --short\n'
printf 'Note: exported prototypes still require CAD/fit inspection before printing.\n'
