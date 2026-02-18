import asyncio
import sys
import os
import aiohttp
from aiohttp_socks import ProxyConnector

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))

from proxy_manager.core.judge import AnonymityJudge
from proxy_manager.core.scanner_py import AsyncScanner

async def test_scanner():
    print("\n>>> Testing Python Scanner...")
    scanner = AsyncScanner()
    # Scan Google DNS port 53 (always open)
    result = await scanner.scan(["8.8.8.8"], "53")
    print(f"Result: {result}")
    if result:
        print(">>> Scanner Success!")
    else:
        print(">>> Scanner Failed.")

async def test_judge():
    print("\n>>> Testing Anonymity Judge...")
    # We need a direct connection to test logic, or mocking?
    # Let's test checking logic without proxy (should be Transparent or Elite depending on how we see it)
    # Actually without proxy, we are just connecting directly.
    # The judge checks response headers.
    
    judge = AnonymityJudge()
    async with aiohttp.ClientSession() as session:
        # We can't easily test check_anonymity without a real proxy.
        # But we can verify the function runs.
        print("Skipping full integration test for Judge (requires live proxy).")
        print(">>> Judge instantiated.")

async def test_gateway_connectivity():
    print("\n>>> Gateway Start Test...")
    # We can't start gateway here easily as it blocks.
    # User should test manually.
    print("User must test 'python -m proxy_manager.main --serve'")

async def main():
    await test_scanner()
    await test_judge()
    await test_gateway_connectivity()

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
