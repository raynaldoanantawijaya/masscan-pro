import asyncio
import time
import traceback
from curl_cffi.requests import AsyncSession

async def main():
    proxy_url = "http://103.26.208.162:8080"
    proxies = {"http": proxy_url, "https": proxy_url}
    
    print("Testing connection...")
    try:
        async with AsyncSession(proxies=proxies, impersonate="chrome120", timeout=15.0) as session:
            t1 = time.time()
            resp = await session.get("https://www.google.com")
            print(f"Google: {resp.status_code} in {time.time()-t1:.2f}s")
            
            try:
                t2 = time.time()
                resp2 = await session.get("http://httpbin.org/get")
                print(f"Httpbin: {resp2.status_code} in {time.time()-t2:.2f}s")
            except Exception as e:
                print("Httpbin failed")
                traceback.print_exc()
                
            try:
                t3 = time.time()
                resp3 = await session.get("https://api.ipify.org?format=json")
                print(f"Ipify: {resp3.status_code} in {time.time()-t3:.2f}s")
            except Exception as e:
                print("Ipify failed")
                traceback.print_exc()
                
            try:
                t4 = time.time()
                resp4 = await session.get("https://ifconfig.me/ip")
                print(f"ifconfig: {resp4.status_code} in {time.time()-t4:.2f}s")
            except Exception as e:
                print("ifconfig failed")
                traceback.print_exc()
                
    except Exception as e:
        print("Overall failed")
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
