import asyncio
import sys
import os
import aiosqlite

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))

from proxy_manager.core.storage import StorageManager

async def main():
    try:
        # Force UTF-8
        sys.stdout.reconfigure(encoding='utf-8')
        
        storage = StorageManager()
        db_path = storage.db_path
        
        async with aiosqlite.connect(db_path) as db:
            # Query specifically for Residential ISPs
            query = """
                SELECT ip, port, protocol, response_time_ms, health_score, isp 
                FROM proxies 
                WHERE country='ID' 
                AND (
                    isp LIKE '%Telkom%' OR 
                    isp LIKE '%Biznet%' OR 
                    isp LIKE '%Indosat%' OR
                    isp LIKE '%XL Axiata%'
                )
                ORDER BY response_time_ms ASC
            """
            async with db.execute(query) as cursor:
                proxies = await cursor.fetchall()
                
                print(f"\n🔍 **RESIDENTIAL / TARGET ISP PROXIES FOUND: {len(proxies)}**")
                print("="*60)
                
                for p in proxies:
                    ip, port, proto, lat, score, isp = p
                    print(f"📍 {ip}:{port} | {proto} | {lat}ms | Score: {score} | ISP: {isp}")
                
                if not proxies:
                    print("❌ No proxies found from Telkom/Biznet/Indosat yet.")
                    print("   The random scanner is still hunting. These ranges are huge!")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
