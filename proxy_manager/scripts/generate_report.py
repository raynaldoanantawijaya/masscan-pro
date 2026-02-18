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

async def generate_report():
    print(f"📊 PROXY REPORT - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("="*60)
    
    storage = StorageManager()
    db_path = storage.db_path
    
    async with aiosqlite.connect(db_path) as db:
        # 1. Total Active
        async with db.execute("SELECT COUNT(*) FROM proxies WHERE health_score > 0") as cursor:
            total_active = (await cursor.fetchone())[0]
            
        print(f"✅ TOTAL ACTIVE PROXIES: {total_active}")
        print("-" * 60)
        
        # 2. By ISP (Top 10)
        print("🏢 TOP ISPs:")
        query_isp = """
            SELECT isp, COUNT(*) as cnt 
            FROM proxies 
            WHERE health_score > 0 
            GROUP BY isp 
            ORDER BY cnt DESC 
            LIMIT 10
        """
        async with db.execute(query_isp) as cursor:
            async for row in cursor:
                isp, count = row
                isp_name = isp if isp else "Unknown"
                print(f"   - {isp_name:<40} : {count}")
        print("-" * 60)
        
        # 3. By Port (Top 5)
        print("🔌 TOP PORTS:")
        query_port = """
            SELECT port, COUNT(*) as cnt 
            FROM proxies 
            WHERE health_score > 0 
            GROUP BY port 
            ORDER BY cnt DESC 
            LIMIT 5
        """
        async with db.execute(query_port) as cursor:
            async for row in cursor:
                port, count = row
                print(f"   - {port:<40} : {count}")
        print("-" * 60)
        
        # 4. By Type/Protocol
        print("🌐 PROTOCOLS:")
        query_proto = """
            SELECT protocol, COUNT(*) as cnt 
            FROM proxies 
            WHERE health_score > 0 
            GROUP BY protocol
        """
        async with db.execute(query_proto) as cursor:
            async for row in cursor:
                proto, count = row
                print(f"   - {proto:<10} : {count}")
        print("-" * 60)
        
        # 5. Pool Distribution (if exists)
        try:
            print("🏊 POOL SEGMENTATION:")
            query_pool = """
                SELECT pool_name, COUNT(*) as cnt 
                FROM pool_assignments 
                GROUP BY pool_name
            """
            async with db.execute(query_pool) as cursor:
                rows = await cursor.fetchall()
                if not rows:
                    print("   (No segmentation data defined yet. Run segment_pool.py)")
                for row in rows:
                    pool, count = row
                    print(f"   - {pool.upper():<10} : {count}")
        except Exception:
            print("   (Pool table not found)")
            
    print("="*60)

if __name__ == "__main__":
    # Force UTF-8 for Windows console
    sys.stdout.reconfigure(encoding='utf-8')
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(generate_report())
