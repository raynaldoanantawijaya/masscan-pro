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
            async with db.execute("SELECT ip, port, protocol, response_time_ms, country FROM proxies WHERE country='ID'") as cursor:
                proxies = await cursor.fetchall()
                print(f"Total Indonesian Proxies Found: {len(proxies)}")
                for p in proxies[:10]:
                    print(f"{p[0]}:{p[1]} | {p[2]} | {p[3]}ms | {p[4]}")

    except Exception as e:
        print(f"Error querying DB: {e}")

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
