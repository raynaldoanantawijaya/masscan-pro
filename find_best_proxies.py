import asyncio
import sys
import os
import aiosqlite

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))

from proxy_manager.core.storage import StorageManager

async def main():
    try:
        storage = StorageManager()
        db_path = storage.db_path
        print(f"Checking DB: {db_path}")
        
        async with aiosqlite.connect(db_path) as db:
            # Get best proxies: High Health, Low Latency, Indonesia
            query = """
                SELECT ip, port, protocol, response_time_ms, health_score, anonymity, isp 
                FROM proxies 
                WHERE country='ID' 
                ORDER BY health_score DESC, response_time_ms ASC 
                LIMIT 20
            """
            async with db.execute(query) as cursor:
                proxies = await cursor.fetchall()
                
                print(f"\n🌟 Top {len(proxies)} Indonesian Proxies Found:")
                print(f"{'IP:Port':<22} | {'Proto':<6} | {'Ping':<6} | {'Score':<5} | {'Type':<10} | {'ISP'}")
                print("-" * 80)
                
                for p in proxies:
                    ip_port = f"{p[0]}:{p[1]}"
                    proto = p[2]
                    ping = f"{p[3]}ms"
                    score = p[4]
                    anonymity = p[5]
                    isp = p[6]
                    print(f"{ip_port:<22} | {proto:<6} | {ping:<6} | {score:<5} | {anonymity:<10} | {isp}")

                if not proxies:
                    print("No Indonesian proxies found. Run 'python indonesia_pipeline.py' to fetch more.")

    except Exception as e:
        print(f"Error querying DB: {e}")

if __name__ == "__main__":
    # Force UTF-8 for Windows console
    sys.stdout.reconfigure(encoding='utf-8')
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
