import asyncio
import aiohttp
import sys
import os
import logging

# Add project root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))

from proxy_manager.core.gateway import ProxyGateway
from proxy_manager.core.storage import StorageManager

# Configure logging to see Gateway output
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TestGateway")

async def test_gateway():
    # 1. Start Gateway in background
    gateway = ProxyGateway(port=8899) # Use different port to avoid conflicts
    
    # We need to run gateway.start() but it blocks.
    # So we wrap it or use app runner directly.
    runner = aiohttp.web.AppRunner(gateway.app)
    await runner.setup()
    site = aiohttp.web.TCPSite(runner, '127.0.0.1', 8899)
    await site.start()
    
    print(">>> Gateway started on 127.0.0.1:8899")
    
    # 2. Check DB status
    storage = StorageManager()
    proxies = await storage.get_proxies()
    print(f">>> DB contains {len(proxies)} proxies.")
    
    if not proxies:
        print(">>> WARNING: DB is empty. Gateway will fail (503).")
    
    # 3. Make request through gateway
    target_url = "http://httpbin.org/ip"
    print(f">>> Sending request to {target_url} via Gateway...")
    
    for i in range(3):
        print(f"\n--- Attempt {i+1} ---")
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(target_url, proxy="http://127.0.0.1:8899", timeout=15) as resp:
                    print(f">>> Response Status: {resp.status}")
                    if resp.status == 200:
                        data = await resp.json()
                        print(f">>> Success! Origin IP: {data.get('origin')}")
                        break
                    elif resp.status == 503:
                        print(">>> Gateway returned 503 (No active proxies).")
                    else:
                        text = await resp.text()
                        print(f">>> Failed: {text}")
                        
        except Exception as e:
            print(f">>> Request failed: {e}")
        
        await asyncio.sleep(2)
        
    # Cleanup
    await runner.cleanup()

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    try:
        asyncio.run(test_gateway())
    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
