import asyncio
import aiohttp
import requests
import re
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))

from proxy_manager.core.geoip import GeoIPManager

SOURCES = [
    "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/socks5.txt",
    "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/http.txt",
    "https://raw.githubusercontent.com/Hookzof/socks5-list/master/proxy.txt",
    "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/socks5.txt",
    "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt",
    "https://www.proxy-list.download/api/v1/get?type=socks5",
    "https://www.proxy-list.download/api/v1/get?type=http",
]

OUTPUT_FILE = "indonesia_proxies.txt"

async def fetch_and_filter():
    print(f"Fetching from {len(SOURCES)} sources...")
    all_proxies = set()
    
    # 1. Fetch
    for url in SOURCES:
        try:
            print(f"Downloading {url}...")
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10) as response:
                    if response.status == 200:
                        text = await response.text()
                        lines = text.strip().split("\n")
                        for line in lines:
                            line = line.strip()
                            # Extract IP:Port
                            match = re.search(r'(\d+\.\d+\.\d+\.\d+):(\d+)', line)
                            if match:
                                all_proxies.add(f"{match.group(1)}:{match.group(2)}")
        except Exception as e:
            print(f"  -> Error: {e}")

    print(f"Total raw proxies found: {len(all_proxies)}")
    
    # 2. Filter by GeoIP (Batch)
    print("Filtering for Indonesia (ID)... this may take a moment...")
    geoip = GeoIPManager()
    id_proxies = []
    
    # Convert set to list for indexing
    proxy_list = list(all_proxies)
    
    # We need to query IPs, then map back to IP:Port
    # IP -> [Port1, Port2] map
    ip_map = {}
    for p in proxy_list:
        ip, port = p.split(":")
        if ip not in ip_map:
            ip_map[ip] = []
        ip_map[ip].append(port)
        
    unique_ips = list(ip_map.keys())
    print(f"Unique IPs to check: {len(unique_ips)}")
    
    # Batch lookup
    results = await geoip.lookup_batch(unique_ips)
    
    for ip, data in results.items():
        if data.get("country") == "ID":
            # Add all ports for this IP
            for port in ip_map[ip]:
                id_proxies.append(f"{ip}:{port}")
                
    print(f"✅ Found {len(id_proxies)} Indonesian proxies.")
    
    with open(OUTPUT_FILE, "w") as f:
        f.write("\n".join(id_proxies))
    
    print(f"Saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(fetch_and_filter())
