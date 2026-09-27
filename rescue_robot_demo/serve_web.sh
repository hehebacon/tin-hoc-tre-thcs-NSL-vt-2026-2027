#!/bin/bash
set -e
cd "$(dirname "$0")"
python3 api_server.py
