#!/bin/bash
# scan_all_isps.sh - Automated scanner for multiple priority ISPs
# Run as: sudo ./scan_all_isps.sh

# List of ISP configs to scan sequentially
ISPS=("cbn" "indointernet" "icon" "myrepublic" "isp_kecil")

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PYTHON_BIN="$DIR/venv/bin/python3"
CONFIG_DIR="$DIR/proxy_manager/configs"
RESULTS_DIR="$DIR/proxy_manager/results"

echo "🚀 Starting Automated Masscan Pipeline for Premium ISPs..."

for ISP in "${ISPS[@]}"; do
    CONFIG_FILE="$CONFIG_DIR/${ISP}.conf"
    
    if [ ! -f "$CONFIG_FILE" ]; then
        echo "⚠️ Config $CONFIG_FILE not found, skipping $ISP..."
        continue
    fi
    
    # 1. Start Masscan
    echo "========================================================="
    echo "📡 [1/2] Scanning $ISP..."
    echo "========================================================="
    masscan -c "$CONFIG_FILE"
    
    # 2. Find the newest generated result file for this ISP
    # Because generate_configs sets output-filename with timestamp dynamically inside python
    # We find the most recently modified txt file starting with the ISP name
    LATEST_RESULT=$(ls -t "$RESULTS_DIR"/${ISP}_*.txt 2>/dev/null | head -n 1)
    
    if [ -z "$LATEST_RESULT" ]; then
        echo "❌ No result file found for $ISP. Moving to next..."
        continue
    fi
    
    # Check if file is empty
    FILE_SIZE=$(stat -c%s "$LATEST_RESULT")
    if [ "$FILE_SIZE" -eq 0 ]; then
        echo "⚠️ 0 hosts found for $ISP. Moving to next..."
        continue
    fi
    
    # 3. Import and Filter tightly
    echo "========================================================="
    echo "🛡️ [2/2] Filtering $ISP through Saringan Besi (TLS Emulation)..."
    echo "📁 File: $LATEST_RESULT"
    echo "========================================================="
    $PYTHON_BIN -m proxy_manager.main --import "$LATEST_RESULT"
    
done

echo "🎉 ALL DONE!"
echo "Run ./show_proxies to see your newly harvested elite proxies."
