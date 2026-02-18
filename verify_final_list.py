import asyncio
import sys
import os
import aiohttp
import time
from aiohttp_socks import ProxyConnector

# Specific list from user
STOP_LIST = [
    "http://8.215.15.163:3129",
    "http://8.215.12.103:8004",
    "http://150.107.140.238:3128",
    "http://202.152.44.18:8081",
    "socks4://8.215.12.103:8001",
    "http://149.129.255.179:119"
]

async def test_proxy(proxy_url):
    print(f"\n🕵️ PROBE: {proxy_url}")
    print("-" * 40)
    
    start = time.time()
    try:
        connector = ProxyConnector.from_url(proxy_url)
        timeout = aiohttp.ClientTimeout(total=10)
        
        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            # 1. Connectivity & Latency
            s_conn = time.time()
            async with session.get("http://httpbin.org/ip") as resp:
                latency = int((time.time() - s_conn) * 1000)
                status = resp.status
                
                if status == 200:
                    data = await resp.json()
                    origin = data.get('origin', 'Unknown')
                    
                    # 2. ISP/Org Check (Simple heuristic or based on known list)
                    # For this script we just verify UP/DOWN and Anonymity
                    
                    print(f"✅ STATUS: ONLINE (HTTP 200)")
                    print(f"⏱️ LATENCY: {latency}ms")
                    print(f"🌍 PUBLIC IP: {origin}")
                    
                    # 3. Anonymity Check
                    async with session.get("http://httpbin.org/headers") as h_resp:
                        h_data = await h_resp.json()
                        headers = h_data.get('headers', {})
                        leaks = [k for k in ['Via', 'X-Forwarded-For', 'X-Proxy-Id'] if k in headers]
                        
                        if leaks:
                            print(f"⚠️ ANONYMITY: Transparent (Leaks: {leaks})")
                        else:
                            print(f"🛡️ ANONYMITY: Elite/Anonymous")
                else:
                    print(f"⚠️ STATUS: HTTP {status}")

    except Exception as e:
        print(f"❌ FAILED: {str(e)}")

async def main():
    print("🚀 FINAL QUALITY CHECK (User Selected List)")
    print("="*50)
    for proxy in STOP_LIST:
        await test_proxy(proxy)
    print("="*50)

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
