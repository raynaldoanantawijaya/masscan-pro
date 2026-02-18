import asyncio
import sys
import os
import random
import ipaddress
import subprocess

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))

# TARGET RANGES: other big residential ISPs
ISP_RANGES = {
    "FirstMedia": [
        "111.94.0.0/15", # Large block
        "139.192.0.0/16",
        "118.136.0.0/16",
        "61.247.0.0/19"
    ],
    "MyRepublic": [
        "103.129.172.0/23", # Smaller blocks usually
        "103.47.132.0/22"   # Educated guess/sampling common ranges
    ],
    "MNC_Play": [
        "119.110.115.0/24",
        "202.150.128.0/19" # PT Infokom (associated)
    ],
     "Biznet_Home": [
        "112.78.160.0/20" # Specific biznet block
    ]
}

def get_random_subnets(cidr: str, count: int = 20) -> list:
    try:
        net = ipaddress.ip_network(cidr, strict=False)
        if net.prefixlen >= 24:
            return [str(net)]
            
        prefix_diff = 24 - net.prefixlen
        num_subnets = 2**prefix_diff
        
        selected = []
        count = min(count, num_subnets)
        
        if num_subnets > 100000:
             indices = [random.randint(0, num_subnets-1) for _ in range(count)]
        else:
             indices = random.sample(range(num_subnets), count)
        
        base_int = int(net.network_address)
        
        for idx in indices:
            subnet_int = base_int + (idx * 256)
            subnet_addr = ipaddress.IPv4Address(subnet_int)
            selected.append(f"{subnet_addr}/24")
            
        return selected
    except Exception as e:
        print(f"Error: {e}")
        return []

def main():
    print("🚀 BROAD RESIDENTIAL SCAN (First Media, MyRepublic, MNC)")
    
    all_targets = []
    
    for isp, ranges in ISP_RANGES.items():
        print(f"\nGenerating targets for {isp}...")
        for r in ranges:
            # First Media has huge blocks, verify 20 random subnets per block
            subnets = get_random_subnets(r, count=20)
            print(f"  - {r} -> Selected {len(subnets)} subnets")
            all_targets.extend(subnets)
            
    target_file = "broad_targets.txt"
    with open(target_file, "w") as f:
        f.write("\n".join(all_targets))
        
    print(f"\nTotal Targets: {len(all_targets)} subnets. Saved to {target_file}")
    
    # Run scan
    cmd = [sys.executable, "-m", "proxy_manager.main", "--scan", "--targets", target_file, "--ports", "8080,80,3128,8000,8081"]
    subprocess.run(cmd)

if __name__ == "__main__":
    main()
