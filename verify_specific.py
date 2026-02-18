import asyncio
import sys
import os
import aiohttp
import time
from aiohttp_socks import ProxyConnector

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))

CANDIDATES = [
    "http://202.152.44.18:8081"
]

async def test_proxy(proxy_url):
    print(f"\n🕵️ PROBE: {proxy_url}")
    print("-" * 40)
    
    start = time.time()
    try:
        connector = ProxyConnector.from_url(proxy_url)
        timeout = aiohttp.ClientTimeout(total=10) # Give residential proxies more time
        
        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            # 1. Connectivity & Latency
            s_conn = time.time()
            async with session.get("http://httpbin.org/ip") as resp:
                latency = int((time.time() - s_conn) * 1000)
                status = resp.status
                
                if status == 200:
                    data = await resp.json()
                    origin = data.get('origin', 'Unknown')
                    print(f"✅ STATUS: ONLINE (HTTP 200)")
                    print(f"⏱️ LATENCY: {latency}ms")
                    print(f"🌍 PUBLIC IP: {origin}")
                    
                    # 2. Anonymity Check (Headers)
                    # We make a second request to check headers
                    async with session.get("http://httpbin.org/headers") as h_resp:
                        h_data = await h_resp.json()
                        headers = h_data.get('headers', {})
                        
                        # Check for leakage
                        leaks = []
                        for k in ['Via', 'X-Forwarded-For', 'X-Proxy-Id']:
                            if k in headers or k.lower() in headers:
                                leaks.append(k)
                                
                        if leaks:
                            print(f"⚠️ ANONYMITY: Transparent (Leaked headers: {', '.join(leaks)})")
                        else:
                            print(f"🛡️ ANONYMITY: Elite/Anonymous (No proxy headers detected)")
                            
                else:
                    print(f"⚠️ STATUS: HTTP {status}")

    except Exception as e:
        print(f"❌ FAILED: {str(e)}")

async def main():
    print("🚀 Verifying Residential Candidates...")
    for c in CANDIDATES:
        await test_proxy(c)

if __name__ == "__main__":
    # Force UTF-8 for Windows console
    sys.stdout.reconfigure(encoding='utf-8')
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
