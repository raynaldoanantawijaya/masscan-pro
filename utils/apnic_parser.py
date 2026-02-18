import requests
import os

APNIC_URL = "https://ftp.apnic.net/stats/apnic/delegated-apnic-latest"
OUTPUT_FILE = "id_ranges.txt"

def fetch_id_ranges():
    print(f"Downloading APNIC data from {APNIC_URL}...")
    try:
        response = requests.get(APNIC_URL, stream=True)
        response.raise_for_status()
        
        id_ranges = []
        
        for line in response.iter_lines():
            if not line: continue
            line = line.decode('utf-8')
            
            # Format: apnic|ID|ipv4|103.2.160.0|1024|20130527|allocated
            if "|ID|ipv4|" in line:
                parts = line.split("|")
                ip = parts[3]
                count = int(parts[4])
                
                # Convert count to CIDR
                # count = 2^(32 - cidr) => log2(count) = 32 - cidr => cidr = 32 - log2(count)
                import math
                cidr = 32 - int(math.log2(count))
                
                id_ranges.append(f"{ip}/{cidr}")

        print(f"Found {len(id_ranges)} Indonesian IPv4 ranges.")
        
        with open(OUTPUT_FILE, "w") as f:
            f.write("\n".join(id_ranges))
            
        print(f"Saved ranges to {OUTPUT_FILE}")
        return id_ranges

    except Exception as e:
        print(f"Error fetching APNIC data: {e}")
        return []

if __name__ == "__main__":
    fetch_id_ranges()
