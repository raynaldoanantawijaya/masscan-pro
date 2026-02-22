import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), 'proxy_manager', 'data', 'proxies.db')

def check_db():
    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute("SELECT health_score, COUNT(*) FROM proxies GROUP BY health_score")
        print("Health Score Distribution:")
        for row in cur.fetchall():
            print(f"Health: {row[0]}, Count: {row[1]}")
    except Exception as e:
        print(f"Error: {e}")

check_db()
