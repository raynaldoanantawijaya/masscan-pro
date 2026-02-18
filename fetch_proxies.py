import requests
import os

SOURCES = [
    "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks5.txt",
    "https://raw.githubusercontent.com/hookzof/socks5_list/master/proxy.txt",
    "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/socks5.txt"
]

OUTPUT_FILE = "proxies.txt"

def fetch_proxies():
    unique_proxies = set()
    print(f"Fetching proxies from {len(SOURCES)} sources...")
    
    for url in SOURCES:
        try:
            print(f"Downloading {url}...")
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                lines = response.text.strip().split("\n")
                for line in lines:
                    line = line.strip()
                    if line and ":" in line:
                        unique_proxies.add(line)
                print(f"  -> Found {len(lines)} proxies.")
            else:
                print(f"  -> Failed: {response.status_code}")
        except Exception as e:
            print(f"  -> Error: {e}")

    print(f"Total unique proxies: {len(unique_proxies)}")
    
    with open(OUTPUT_FILE, "w") as f:
        f.write("\n".join(unique_proxies))
    
    print(f"Saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    fetch_proxies()
