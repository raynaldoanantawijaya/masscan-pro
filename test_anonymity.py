import asyncio
from proxy_manager.core.validator import ProxyValidator

async def test_proxy():
    validator = ProxyValidator()
    # Test one of the recent unknown proxies to see anonymity output
    res = await validator.check_proxy("195.158.8.123", 3128, "http")
    print(res)

if __name__ == "__main__":
    asyncio.run(test_proxy())
