#!/bin/bash
# scan_datacenter.sh - Dedicated scanner for High-Yield Indonesian Datacenters
# Run as: sudo ./scan_datacenter.sh

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PYTHON_BIN="$DIR/venv/bin/python3"
CONFIG_DIR="$DIR/proxy_manager/configs"
RESULTS_DIR="$DIR/proxy_manager/results"
ISP="datacenter"

# Check if datacenter.txt exists, if not generate it
if [ ! -f "$DIR/proxy_manager/ranges/datacenter.txt" ]; then
    echo "Fetching Datacenter IP ranges via API..."
    $PYTHON_BIN $DIR/fetch_datacenter_ips.py
fi

# 1. Generate Config
echo "Generating Masscan Config for $ISP..."
$PYTHON_BIN $DIR/proxy_manager/scripts/generate_configs.py

CONFIG_FILE="$CONFIG_DIR/${ISP}.conf"

if [ ! -f "$CONFIG_FILE" ]; then
    echo "❌ Config $CONFIG_FILE not found. Exiting."
    exit 1
fi

echo "========================================================="
echo "🏢 📡 [1/2] Scanning Data Centers & Cloud Providers..."
echo "========================================================="
masscan -c "$CONFIG_FILE"

# 2. Find the newest generated result file
LATEST_RESULT=$(ls -t "$RESULTS_DIR"/${ISP}_*.txt 2>/dev/null | head -n 1)

if [ -z "$LATEST_RESULT" ]; then
    echo "❌ No result file found. Exiting."
    exit 1
fi

FILE_SIZE=$(stat -c%s "$LATEST_RESULT")
if [ "$FILE_SIZE" -eq 0 ]; then
    echo "⚠️ 0 hosts found. Exiting."
    exit 1
fi

# 3. Import and Filter tightly
echo "========================================================="
echo "🛡️ [2/2] Filtering $ISP through Saringan Besi..."
echo "📁 File: $LATEST_RESULT"
echo "========================================================="
$PYTHON_BIN -m proxy_manager.main --import-file "$LATEST_RESULT"

echo "🎉 CLOUD SCAN COMPLETE!"
echo "Run ./show_proxies to see your new Cloud/DC Elite Proxies!"
