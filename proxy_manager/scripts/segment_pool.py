import sys
import os
import aiosqlite
import asyncio
from datetime import datetime

# Add project root
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PACKAGE_DIR = os.path.dirname(SCRIPT_DIR)
PROJECT_ROOT = os.path.dirname(PACKAGE_DIR)
sys.path.append(PROJECT_ROOT)

from proxy_manager.core.storage import StorageManager

async def segment_pool():
    print("🌊 Segmenting Proxy Pool...")
    
    storage = StorageManager()
    db_path = storage.db_path
    
    async with aiosqlite.connect(db_path) as db:
        # 1. Create Pools Table if not exists
        await db.execute('''
            CREATE TABLE IF NOT EXISTS pool_assignments (
                proxy_ip TEXT,
                proxy_port INTEGER,
                pool_name TEXT,
                assigned_at TIMESTAMP,
                PRIMARY KEY (proxy_ip, proxy_port)
            )
        ''')
        await db.commit()
        
        # 2. Get active proxies
        # Note: 'is_active' might not be a column in my current schema if I didn't add it explicitly,
        # but I have 'health_score'. Let's use health_score > 0.
        query = "SELECT ip, port, response_time_ms FROM proxies WHERE health_score > 0"
        
        updated_count = 0
        
        async with db.execute(query) as cursor:
            async for row in cursor:
                ip, port, latency = row
                
                # Logic per user request
                if latency < 1000:
                    pool = 'fast'
                elif latency < 3000:
                    pool = 'medium'
                else:
                    pool = 'slow'
                    
                # Insert/Update assignment
                await db.execute('''
                    INSERT OR REPLACE INTO pool_assignments (proxy_ip, proxy_port, pool_name, assigned_at)
                    VALUES (?, ?, ?, datetime('now'))
                ''', (ip, port, pool))
                
                updated_count += 1
                
        await db.commit()
        print(f"✅ Segmented {updated_count} proxies into Fast/Medium/Slow pools.")

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(segment_pool())
