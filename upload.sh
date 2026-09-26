#!/bin/bash

set -e

PROJECT="/home/bao/Documents/01_firmware/du an robot/servo_controller"
REPO="git@github.com:hehebacon/tin-hoc-tre-thcs-NSL-vt-2026-2027.git"

echo "=========================================="
echo "   ROBOT FIRMWARE -> GITHUB SSH UPLOADER"
echo "=========================================="
echo

echo "[1/7] Checking project..."
cd "$PROJECT"
echo "Project: $(pwd)"
echo

echo "[2/7] Checking Git..."
if [ ! -d ".git" ]; then
    echo "Initializing Git repository..."
    git init
fi

git branch -M main
echo

echo "[3/7] Configuring SSH remote..."
if git remote get-url origin >/dev/null 2>&1; then
    git remote set-url origin "$REPO"
else
    git remote add origin "$REPO"
fi

echo "Remote:"
git remote -v
echo

echo "[4/7] Checking GitHub SSH..."
SSH_TEST=$(ssh -T git@github.com 2>&1 || true)

if echo "$SSH_TEST" | grep -q "successfully authenticated"; then
    echo "SSH authentication: OK"
else
    echo "$SSH_TEST"
    echo
    echo "ERROR: GitHub SSH authentication failed."
    echo
    echo "Run:"
    echo "    ssh -T git@github.com"
    echo
    exit 1
fi

echo
echo "[5/7] Adding files..."
git add .

echo
echo "Current changes:"
git status --short
echo

echo "[6/7] Creating commit..."

if git diff --cached --quiet; then
    echo "No new changes to commit."
else
    git commit -m "Update robot firmware $(date '+%Y-%m-%d %H:%M:%S')"
fi

echo
echo "[7/7] Uploading to GitHub..."
git push -u origin main

echo
echo "=========================================="
echo "             UPLOAD DONE"
echo "=========================================="
echo
echo "Repository:"
echo "https://github.com/hehebacon/tin-hoc-tre-thcs-NSL-vt-2026-2027"
echo
