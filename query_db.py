import asyncio
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))

from proxy_manager.core.storage import StorageManager

async def main():
    try:
        storage = StorageManager()
        proxies = await storage.get_proxies()
        print(f"Total proxies in DB: {len(proxies)}")
        for p in proxies:
            print(f"{p['ip']}:{p['port']} | {p['protocol']} | {p['country']} | {p['response_time_ms']}ms")
    except Exception as e:
        print(f"Error querying DB: {e}")

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
