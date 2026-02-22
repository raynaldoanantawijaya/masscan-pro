#!/bin/bash
# hunt_until_target.sh - Automated Proxy Hunter
# Runs Masscan on various Indonesian ISPs/ASNs in sequence.
# It automatically stops the moment the total number of Elite proxies in your database reaches the TARGET.
#
# Run as: sudo ./hunt_until_target.sh [TARGET_COUNT]

TARGET=${1:-10}  # Default target is 10

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PYTHON_BIN="$DIR/venv/bin/python3"
CONFIG_DIR="$DIR/proxy_manager/configs"
RESULTS_DIR="$DIR/proxy_manager/results"
DB_PATH="$DIR/proxy_manager/data/proxies.db"

# We order ISPs from best yield (Datacenter/Cloud) to massive broadband
ISPS=("datacenter" "biznet" "myrepublic" "cbn" "indointernet" "icon" "isp_kecil" "firstmedia" "indihome_lama")

echo "========================================================="
echo " 🕵️‍♂️ BOTOX HUNTER: AUTOPILOT MODE ACTIVATED "
echo " 🎯 MISSION: SURVIVE & HUNT UNTIL $TARGET ELITE PROXIES FOUND "
echo "========================================================="

# Regenerate latest configs just in case
echo "-> Ensuring latest IPs are loaded..."
$PYTHON_BIN $DIR/proxy_manager/scripts/generate_configs.py > /dev/null

count_elite() {
    $PYTHON_BIN -c "import sqlite3; \
conn = sqlite3.connect('$DB_PATH'); \
print(conn.execute(\"SELECT COUNT(*) FROM proxies WHERE anonymity IN ('elite', 'anonymous') AND status = 'active'\").fetchone()[0]); \
conn.close()" 2>/dev/null || echo 0
}

CURRENT_COUNT=$(count_elite)
echo "Current Database Balance: $CURRENT_COUNT / $TARGET Elite Proxies."

if [ "$CURRENT_COUNT" -ge "$TARGET" ]; then
    echo "🎉 MISSION ACCOMPLISHED BEFORE STARTING ($CURRENT_COUNT >= $TARGET)."
    echo "Run ./show_proxies to see your elite proxies!"
    exit 0
fi

for ISP in "${ISPS[@]}"; do
    CONFIG_FILE="$CONFIG_DIR/${ISP}.conf"
    if [ ! -f "$CONFIG_FILE" ]; then
        echo "⚠️ Config $CONFIG_FILE not found, skipping $ISP..."
        continue
    fi
    
    echo ""
    echo "🔥 [PHASE START] Launching Masscan against: $ISP"
    echo "---------------------------------------------------------"
    # --wait 0 ensures masscan doesn't pointlessy wait 10s at the end
    masscan -c "$CONFIG_FILE" --wait 0
    
    LATEST_RESULT=$(ls -t "$RESULTS_DIR"/${ISP}_*.txt 2>/dev/null | head -n 1)
    
    if [ -n "$LATEST_RESULT" ] && [ $(stat -c%s "$LATEST_RESULT") -gt 0 ]; then
        echo "🛡️ Sending $(wc -l < "$LATEST_RESULT") hosts from $ISP to Saringan Besi..."
        $PYTHON_BIN -m proxy_manager.main --import-file "$LATEST_RESULT"
    else
        echo "⚠️ 0 Hosts found for $ISP."
    fi
    
    CURRENT_COUNT=$(count_elite)
    echo "========================================================="
    echo "📊 PROGRESS REPORT: $CURRENT_COUNT / $TARGET Elite Proxies Secured."
    echo "========================================================="
    
    if [ "$CURRENT_COUNT" -ge "$TARGET" ]; then
        echo "🎉🎉 BINGOOOO! TARGET REACHED ($CURRENT_COUNT >= $TARGET) !! 🎉🎉"
        echo "Stopping Autopilot. Run ./show_proxies to deploy your new proxies!"
        exit 0
    fi
    
    echo "Target not yet reached. Proceeding to next ISP..."
    sleep 2
done

echo "🏁 All targets exhausted. Final Count: $CURRENT_COUNT / $TARGET Elite Proxies."
