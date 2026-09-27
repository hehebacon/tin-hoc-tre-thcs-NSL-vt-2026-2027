#!/bin/bash
set -e
cd "$(dirname "$0")"
python3 api_server.py & API_PID=$!
python3 dashboard_server.py & WEB_PID=$!
trap 'kill "$API_PID" "$WEB_PID" 2>/dev/null || true' EXIT INT TERM
echo "RESCUE ROBOT DEMO"
echo "API: http://127.0.0.1:8787"
echo "WEB: http://127.0.0.1:8080"
wait
