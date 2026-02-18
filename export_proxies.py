import sqlite3
import os
import sys

# Connect to database
DB_PATH = os.path.join(os.path.dirname(__file__), 'data/proxies.db')

def analyze_proxies():
    if not os.path.exists(DB_PATH):
        print(f"❌ Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("\n📊 **FULL PROXY ANALYSIS & EXPORT** 📊")
    print("="*60)

    # 1. Summary by Category
    print("\n🔹 **SUMMARY BY PROTOCOL:**")
    cursor.execute("SELECT protocol, COUNT(*) FROM proxies WHERE health_score > 0 GROUP BY protocol")
    for row in cursor.fetchall():
        print(f"   - {row[0].upper():<10}: {row[1]}")

    print("\n🔹 **SUMMARY BY SPEED (Pools):**")
    cursor.execute("SELECT pool, COUNT(*) FROM pool_assignments GROUP BY pool")
    for row in cursor.fetchall():
        print(f"   - {row[0]:<10}: {row[1]}")

    print("\n🔹 **SUMMARY BY ANONYMITY:**")
    cursor.execute("SELECT anonymity, COUNT(*) FROM proxies WHERE health_score > 0 GROUP BY anonymity")
    for row in cursor.fetchall():
        print(f"   - {row[0].capitalize():<15}: {row[1]}")

    print("\n" + "="*60)
    print("🚀 **DETAILED PROXY LIST (TOP 50 FASTEST)**")
    print(f"{'IP:PORT':<22} | {'PROTO':<6} | {'SPEED':<5} | {'TYPE':<10} | {'ISP'}")
    print("-" * 75)

    cursor.execute("""
        SELECT ip, port, protocol, response_time_ms, anonymity, isp 
        FROM proxies 
        WHERE health_score > 0
        ORDER BY response_time_ms ASC
        LIMIT 50
    """)
    
    for row in cursor.fetchall():
        ip, port, proto, speed, anon, isp = row
        proxy = f"{ip}:{port}"
        # Truncate ISP if too long
        isp = (isp[:25] + '..') if isp and len(isp) > 25 else (isp or "Unknown")
        
        print(f"{proxy:<22} | {proto:<6} | {speed:<3}ms | {anon:<10} | {isp}")

    print("-" * 75)
    print("\n💡 **Want to save to file?**")
    print("   Run: `python3 export_proxies.py > my_proxies.txt`")

    conn.close()

if __name__ == "__main__":
    analyze_proxies()
