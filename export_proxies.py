import sqlite3
import os
import sys

# Connect to database
DB_PATH = os.path.join(os.path.dirname(__file__), 'data/proxies.db')

# ANSI Colors
C = '\033[96m'  # Cyan
G = '\033[92m'  # Green
Y = '\033[93m'  # Yellow
R = '\033[91m'  # Red
M = '\033[95m'  # Magenta
W = '\033[0m'   # Reset/White
B = '\033[1m'   # Bold

def analyze_proxies():
    if not os.path.exists(DB_PATH):
        print(f"{R}❌ Database not found at {DB_PATH}{W}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print(f"\n{B}{C}📊 FULL PROXY ANALYSIS & EXPORT 📊{W}")
    print(f"{C}{'='*80}{W}")

    # 1. Summary by Category
    print(f"\n{B}{M}🔹 SUMMARY BY PROTOCOL:{W}")
    cursor.execute("SELECT protocol, COUNT(*) FROM proxies WHERE health_score > 0 GROUP BY protocol")
    for row in cursor.fetchall():
        print(f"   {G}✔{W} {row[0].upper():<10}: {B}{row[1]}{W}")

    print(f"\n{B}{M}🔹 SUMMARY BY SPEED (Pools):{W}")
    try:
        cursor.execute("SELECT pool_name, COUNT(*) FROM pool_assignments GROUP BY pool_name")
        for row in cursor.fetchall():
            print(f"   {G}✔{W} {row[0]:<10}: {B}{row[1]}{W}")
    except sqlite3.OperationalError:
        print(f"   {Y}- Pool data not initialized yet.{W}")

    print(f"\n{B}{M}🔹 SUMMARY BY ANONYMITY:{W}")
    cursor.execute("SELECT anonymity, COUNT(*) FROM proxies WHERE health_score > 0 GROUP BY anonymity")
    for row in cursor.fetchall():
        print(f"   {G}✔{W} {row[0].capitalize():<15}: {B}{row[1]}{W}")

    print(f"\n{C}{'='*80}{W}")
    print(f"{B}{Y}🚀 DETAILED PROXY LIST (VERIFIED ACTIVE){W}")
    print(f"{B}{'IP:PORT':<22} | {'PROTO':<6} | {'SPEED':<7} | {'TYPE':<10} | {'ISP'}{W}")
    print(f"{C}{'-' * 80}{W}")

    # Show more proxies, ordered by speed
    cursor.execute("""
        SELECT ip, port, protocol, response_time_ms, anonymity, isp 
        FROM proxies 
        WHERE health_score > 0
        ORDER BY response_time_ms ASC
        LIMIT 200
    """)
    
    rows = cursor.fetchall()
    if not rows:
         print(f"{R}No active proxies found in the database. Run a scan first.{W}")
         
    for row in rows:
        ip, port, proto, speed, anon, isp = row
        proxy = f"{ip}:{port}"
        isp = (isp[:35] + '..') if isp and len(isp) > 35 else (isp or "Unknown")
        
        # Color code speed
        if speed and speed < 1000:
            spd_color = G
        elif speed and speed < 3000:
            spd_color = Y
        else:
            spd_color = R
            
        # Color code anonymity
        anon_color = M if anon.lower() == 'elite' else W
            
        print(f"{B}{proxy:<22}{W} | {proto:<6} | {spd_color}{speed:<5}ms{W} | {anon_color}{anon:<10}{W} | {isp}")

    print(f"{C}{'-' * 80}{W}")
    print(f"\n💡 {B}Total Verified Proxies Displayed:{W} {len(rows)}")
    print(f"💡 {B}Want to save to file?{W} Run: {G}./show_proxies > my_proxies.txt{W}")

    conn.close()

if __name__ == "__main__":
    analyze_proxies()
