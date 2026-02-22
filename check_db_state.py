import sqlite3
import os

def check_db():
    # Adjust path
    base_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(base_dir, "proxy_manager", "data", "proxies.db")
    
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return
        
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Get health score distribution for unknown proxies
    cursor.execute('SELECT health_score, COUNT(*) FROM proxies WHERE anonymity="unknown" GROUP BY health_score ORDER BY health_score DESC')
    dist = cursor.fetchall()
    print(f"Health Distribution of Unknowns: {dist}")

    # Get health score distribution for elite/anonymous
    cursor.execute('SELECT health_score, COUNT(*) FROM proxies WHERE anonymity!="unknown" GROUP BY health_score ORDER BY health_score DESC')
    dist_others = cursor.fetchall()
    print(f"Health Distribution of Elite/Anonymous: {dist_others}")
    
    conn.close()

if __name__ == "__main__":
    check_db()
