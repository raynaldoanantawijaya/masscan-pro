import asyncio
import sys
import os
import random
import ipaddress
import subprocess

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))

# TARGET RANGES (Hardcoded for now based on research)
ISP_RANGES = {
    "Telkom_Indihome": [
        "125.160.0.0/13", 
        "36.64.0.0/11",   
        "180.240.0.0/12", 
        "110.136.0.0/13",
        "202.134.0.0/16"
    ],
    "Biznet": [
        "101.255.0.0/16",
        "112.78.160.0/19",
        "202.169.32.0/19"
    ],
    "Indosat": [
        "114.0.0.0/11",
        "124.195.0.0/16",
        "103.10.64.0/22"
    ]
}

def get_random_subnets(cidr: str, count: int = 5) -> list:
    """
    Pick 'count' random /24 subnets from a larger CIDR block.
    """
    try:
        net = ipaddress.ip_network(cidr, strict=False)
        if net.prefixlen >= 24:
            return [str(net)]
            
        prefix_diff = 24 - net.prefixlen
        num_subnets = 2**prefix_diff
        
        selected = []
        count = min(count, num_subnets)
        
        # Limit safety (max 50 to avoid slow generation on huge blocks)
        if num_subnets > 100000:
             # Just pick random numbers
             indices = [random.randint(0, num_subnets-1) for _ in range(count)]
        else:
             indices = random.sample(range(num_subnets), count)
        
        base_int = int(net.network_address)
        
        for idx in indices:
            subnet_int = base_int + (idx * 256)
            subnet_addr = ipaddress.IPv4Address(subnet_int)
            # Create /24
            selected.append(f"{subnet_addr}/24")
            
        return selected
    except Exception as e:
        print(f"Error parsing {cidr}: {e}")
        return []

def main():
    print("🚀 TARGETED ISP SCANNING (Sampling Mode)")
    print("Scanning specific subnets from Telkom, Biznet, Indosat...")
    
    all_targets = []
    
    for isp, ranges in ISP_RANGES.items():
        print(f"\nGenerating targets for {isp}...")
        for r in ranges:
            # Get 5 random /24 subnets from each large block to scan quickly
            subnets = get_random_subnets(r, count=5)
            print(f"  - {r} -> Selected {len(subnets)} subnets")
            all_targets.extend(subnets)
            
    target_file = "isp_targets.txt"
    with open(target_file, "w") as f:
        f.write("\n".join(all_targets))
        
    print(f"\nTotal Targets: {len(all_targets)} subnets. Saved to {target_file}")
    print("Starting Scan Pipeline...")
    
    # Run main.py via subprocess to avoid asyncio loop issues and ensure clean state
    # We use comma separated targets if list is small, or file if large
    # Here file is better.
    
    cmd = [sys.executable, "-m", "proxy_manager.main", "--scan", "--targets", target_file, "--ports", "8080,80,3128,8000"]
    subprocess.run(cmd)

if __name__ == "__main__":
    main()
