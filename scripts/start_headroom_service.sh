#!/bin/bash
# Headroom Compression Service - Startup Script
# Usage: ./start_headroom_service.sh

cd "$(dirname "$0")/.."

export HEADROOM_DISABLE_PROTECTION=1
export HF_HUB_DISABLE_TELEMETRY=1

echo "Starting Headroom Compression Service on port 8787"
echo "API endpoint: http://localhost:8787/compress"
echo "Press Ctrl+C to stop"
echo ""

exec python3 scripts/headroom_service.py
