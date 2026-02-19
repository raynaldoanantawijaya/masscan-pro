import asyncio
import aiohttp
import time
import sys

# Top 25 Proxies from Phase 6 (Using the potentially problematic ones to filter)
PROXIES = [
    # Phase 6 Winners (Cyberindo & Sify)
    "http://202.158.11.125:80",
    "http://210.18.5.80:80",
    "http://210.18.5.81:80",
    "http://210.18.5.91:80",
    "http://210.18.5.68:80",
    "http://210.18.5.84:80",
    "http://210.18.5.93:80",
    "http://210.18.5.87:80",

    # Early Phase Findings (Jalamedia, Lintasarta, Alibaba)
    "http://150.107.140.238:3128", 
    "http://202.152.44.18:8081",
    "http://8.215.15.163:3129",
    "http://8.215.12.103:8004",
    "http://149.129.226.9:80"
]

TARGET_URL = "https://www.google.com"

async def check_connect_method(proxy_url):
    """
    Tries to CONNECT to google.com:443 through the proxy.
    This is the gold standard for HTTPS proxy verification.
    """
    start = time.time()
    try:
        # We use aiohttp with ssl=False to avoid certificate verification issues with some transparent proxies
        async with aiohttp.ClientSession() as session:
            # The 'get' request to an HTTPS URL via proxy triggers the CONNECT method implicitly in aiohttp
            async with session.get(TARGET_URL, proxy=proxy_url, timeout=10, ssl=False) as resp:
                if resp.status == 200:
                    latency = int((time.time() - start) * 1000)
                    print(f"✅ CONNECT OK: {proxy_url:<30} | {latency}ms | GENUINE HTTPS PROXY")
                    return True
                else:
                    # If we get here, the proxy might differ HTTP requests but fail CONNECT, or return a login page
                    print(f"❌ CONNECT FAIL: {proxy_url:<30} | Status: {resp.status} (Likely HTTP-only or Login Page)")
                    return False
    except Exception as e:
        # Connection reset, timeout, or proxy error
        # print(f"❌ DEAD/ERROR : {proxy_url:<30} | {str(e)[:50]}")
        print(f"❌ DEAD/ERROR : {proxy_url:<30}")
        return False

async def main():
    print(f"🔒 Testing STRICT CONNECT Method on {len(PROXIES)} Targets...\n")
    print(f"{'RESULT':<15} | {'PROXY':<30} | {'LATENCY':<6} | {'NOTES'}")
    print("-" * 80)
    
    tasks = [check_connect_method(p) for p in PROXIES]
    results = await asyncio.gather(*tasks)
    
    active_count = sum(results)
    print("\n" + "=" * 80)
    print(f"📊 STRICT SUMMARY: {active_count}/{len(PROXIES)} are REAL HTTPS PROXIES.")
    print("=" * 80)

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
