import asyncio
import aiohttp
import time
import sys

# Top 25 Proxies from Phase 6
PROXIES = [
    "http://202.159.35.236:8080",
    "http://202.158.11.125:80",
    "http://210.16.67.35:80",
    "http://210.16.67.36:80",
    "http://124.158.165.12:80",
    "http://45.64.60.199:3000",
    "http://45.64.132.83:3000",
    "http://202.159.123.40:80",
    "http://202.159.101.20:80",
    "http://210.18.5.81:80",
    "http://210.18.5.80:80",
    "http://210.18.5.68:80",
    "http://210.18.5.87:80",
    "http://210.18.5.91:80",
    "http://210.18.5.86:80",
    "http://210.18.5.69:80",
    "http://210.16.67.34:80",
    "http://210.18.5.66:80",
    "http://210.18.5.88:80",
    "http://210.18.5.64:80",
    "http://210.16.67.37:80",
    "http://210.19.151.62:80",
    "http://210.18.5.93:80",
    "http://210.18.5.84:80",
    "http://124.81.6.123:8080"
]

async def check_proxy(proxy_url):
    start = time.time()
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("http://httpbin.org/ip", proxy=proxy_url, timeout=5) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    latency = int((time.time() - start) * 1000)
                    print(f"✅ ACTIVE: {proxy_url:<30} | {latency}ms | IP: {data['origin']}")
                    return True
                else:
                    print(f"⚠️  ERROR : {proxy_url:<30} | HTTP {resp.status}")
                    return False
    except Exception as e:
        print(f"❌ DEAD  : {proxy_url:<30} | {str(e)[:50]}")
        return False

async def main():
    print(f"🚀 Testing {len(PROXIES)} Top Elite Proxies...\n")
    print(f"{'STATUS':<8} | {'PROXY':<30} | {'LATENCY':<6} | {'VISIBLE IP'}")
    print("-" * 70)
    
    tasks = [check_proxy(p) for p in PROXIES]
    results = await asyncio.gather(*tasks)
    
    active_count = sum(results)
    print("\n" + "=" * 70)
    print(f"📊 SUMMARY: {active_count}/{len(PROXIES)} Proxies are LIVE right now.")
    print("=" * 70)

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
