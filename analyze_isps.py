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
            # Get count of proxies per ISP
            query = """
                SELECT isp, COUNT(*) as count 
                FROM proxies 
                WHERE country='ID' 
                GROUP BY isp 
                ORDER BY count DESC
            """
            async with db.execute(query) as cursor:
                results = await cursor.fetchall()
                
                print(f"\n📊 **ISP DISTRIBUTION (Indonesian Proxies)**")
                print("="*60)
                print(f"{'ISP Name':<40} | {'Count':<5}")
                print("-" * 60)
                
                for row in results:
                    isp, count = row
                    # Handle None ISP
                    isp_name = isp if isp else "Unknown"
                    print(f"{isp_name:<40} | {str(count):<5}")
                    
                print("-" * 60)
                
            # Filter for likely residential (exclude common cloud/hosting keywords)
            print("\n🏠 **POTENTIAL RESIDENTIAL CANDIDATES (Non-Cloud/Hosting)**")
            keywords = ['Cloud', 'Hosting', 'Data Center', 'DigitalOcean', 'Amazon', 'Google', 'Microsoft', 'Alibaba', 'Choopa', 'Vultr']
            
            query_all = "SELECT ip, port, isp FROM proxies WHERE country='ID'"
            async with db.execute(query_all) as cursor:
                all_proxies = await cursor.fetchall()
                
                found = 0
                for p in all_proxies:
                    ip, port, isp = p
                    # Handle None
                    isp_clean = isp if isp else "Unknown"
                    
                    is_datacenter = any(k.lower() in isp_clean.lower() for k in keywords)
                    if not is_datacenter:
                        print(f"   📍 {ip}:{port} - {isp_clean}")
                        found += 1
                        
                if found == 0:
                    print("   (None found. All current proxies appear to be Datacenter/Business)")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
