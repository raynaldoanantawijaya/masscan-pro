import asyncio
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))

from proxy_manager.core.geoip import GeoIPManager
from proxy_manager.core.storage import StorageManager
from proxy_manager.core.lifecycle import LifecycleManager

async def test_geoip():
    print(">>> Testing GeoIP...")
    geoip = GeoIPManager()
    # Test Google DNS
    data = await geoip.lookup("8.8.8.8")
    print(f"Result for 8.8.8.8: {data}")
    if data.get("country") == "US":
        print(">>> GeoIP Success!")
    else:
        print(">>> GeoIP Failed or unexpected result.")

async def test_db_migration():
    print("\n>>> Testing DB Schema...")
    storage = StorageManager()
    await storage.init_db() # Should trigger migration
    
    import aiosqlite
    async with aiosqlite.connect(storage.db_path) as db:
         pass 
         # Wait, StorageManager uses aiosqlite. 
         # Let's just check columns via storage method or direct aiosqlite
    
    import aiosqlite
    async with aiosqlite.connect(storage.db_path) as db:
        async with db.execute("PRAGMA table_info(proxies)") as cursor:
            columns = [row[1] for row in await cursor.fetchall()]
            print(f"Columns: {columns}")
            if "isp" in columns and "health_score" in columns:
                print(">>> DB Migration Success!")
            else:
                print(">>> DB Migration Failed.")

async def main():
    await test_geoip()
    await test_db_migration()

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
