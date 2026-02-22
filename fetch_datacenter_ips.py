import asyncio
import aiohttp
import os
import sys

# Windows asyncio bug workaround
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

ASNS = {
    "biznet_dc": "AS17451",
    "idcloudhost": "AS131612",
    "beon": "AS131759", # JagoanHosting
    "niagahoster": "AS133804",
    "masterweb": "AS55694",
    "jetdino": "AS131742",
    "cbn_cloud": "AS58591",
    "wowrack": "AS45672",
    "dtp": "AS45888",
    "qwords": "AS63858",
    "rackh": "AS131804",
    "republikhost": "AS136053",
    "awankilat": "AS136009",
    "hostinger_id": "AS132145",
    "dcloud": "AS138031"
}

OUTPUT_FILE = os.path.join(os.path.dirname(__file__), "proxy_manager", "ranges", "datacenter.txt")

async def fetch_asn_prefixes(session: aiohttp.ClientSession, name: str, asn: str) -> list[str]:
    print(f"Fetching prefixes for {name} ({asn})...")
    # Using RIPE Stat API, it's very reliable
    url = f"https://stat.ripe.net/data/announced-prefixes/data.json?resource={asn}"
    prefixes = []
    
    try:
        async with session.get(url, timeout=15) as response:
            if response.status == 200:
                data = await response.json()
                if "data" in data and "prefixes" in data["data"]:
                    for p in data["data"]["prefixes"]:
                        prefix = p.get("prefix")
                        # Only IPv4
                        if prefix and ":" not in prefix:
                            prefixes.append(prefix)
                    print(f" -> Found {len(prefixes)} IPv4 prefixes for {name}.")
                else:
                    print(f" -> API returned unexpected format for {asn}")
            else:
                print(f" -> HTTP {response.status} for {asn}")
    except Exception as e:
        print(f" -> Error fetching {asn}: {e}")
        
    return prefixes

async def main():
    print("Starting Datacenter ASN Fetcher (Powered by RIPE Stat)...")
    all_prefixes = []
    
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_asn_prefixes(session, name, asn) for name, asn in ASNS.items()]
        results = await asyncio.gather(*tasks)
        
        for prefixes in results:
            all_prefixes.extend(prefixes)
            
    all_prefixes = sorted(list(set(all_prefixes)))
    print(f"\nTotal unique Datacenter prefixes found: {len(all_prefixes)}")
    
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, "w") as f:
        f.write("# Indonesian Datacenter / Cloud / Server Subnets\n")
        f.write("# Target: Biznet DC, IDCloudHost, Niagahoster, Qwords, dsb.\n\n")
        for p in all_prefixes:
            f.write(f"{p}\n")
            
    print(f"✅ Saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    asyncio.run(main())
