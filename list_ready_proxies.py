import asyncio
import sys
import os
import aiosqlite
import aiohttp
from aiohttp_socks import ProxyConnector

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))

from proxy_manager.core.storage import StorageManager

async def test_proxy(proxy_url):
    print(f"   Testing connection via {proxy_url}...", end="", flush=True)
    try:
        connector = ProxyConnector.from_url(proxy_url)
        async with aiohttp.ClientSession(connector=connector, timeout=aiohttp.ClientTimeout(total=5)) as session:
            async with session.get("http://httpbin.org/ip") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    print(f" ✅ ONLINE (Origin: {data.get('origin')})")
                    return True
                else:
                    print(f" ❌ HTTP {resp.status}")
    except Exception as e:
        print(f" ❌ FAILED ({str(e)[:50]}...)")
    return False

async def main():
    try:
        # Force UTF-8
        sys.stdout.reconfigure(encoding='utf-8')
        
        storage = StorageManager()
        db_path = storage.db_path
        
        async with aiosqlite.connect(db_path) as db:
            # Query for Elite/Anonymous + Reasonable Latency
            query = """
                SELECT ip, port, protocol, response_time_ms, anonymity, isp 
                FROM proxies 
                WHERE country='ID' AND anonymity IN ('elite', 'anonymous') AND response_time_ms < 5000
                ORDER BY response_time_ms ASC
                LIMIT 10
            """
            async with db.execute(query) as cursor:
                proxies = await cursor.fetchall()
                
                print(f"\n🔥 **TOP RECOMMENDED PROXIES (Siap Pakai)** 🔥")
                print("="*60)
                
                valid_count = 0
                for p in proxies:
                    ip, port, proto, lat, anon, isp = p
                    proxy_url = f"{proto}://{ip}:{port}"
                    
                    print(f"\n📍 **{ip}:{port}**")
                    print(f"   - Type: {proto.upper()} ({anon.capitalize()})")
                    print(f"   - Latency: {lat}ms")
                    print(f"   - ISP: {isp}")
                    
                    # Test it immediately
                    if await test_proxy(proxy_url):
                        valid_count += 1
                        print(f"   - URI: `{proxy_url}`")
                
                if valid_count == 0:
                    print("\n⚠️  No 'Elite' proxies are currently responding fast enough.")
                    print("   Try running the pipeline again via `python indonesia_pipeline.py`")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
