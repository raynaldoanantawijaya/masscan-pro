import asyncio
import sys
import aiosqlite
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))
from proxy_manager.core.storage import StorageManager

async def check_fm():
    storage = StorageManager()
    async with aiosqlite.connect(storage.db_path) as db:
        async with db.execute("SELECT ip, port, isp, health_score, response_time_ms FROM proxies WHERE isp LIKE '%First Media%' OR isp LIKE '%LinkNet%'") as cursor:
            rows = await cursor.fetchall()
            print(f"Total First Media Candidates: {len(rows)}")
            for r in rows:
                print(r)

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(check_fm())
