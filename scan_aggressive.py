import asyncio
import sys
import os
import random
import ipaddress
import subprocess

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))

# TARGET: Indihome - 36.64.0.0/13 is huge.
# Let's focus on a smaller, often active block: 36.72.0.0/16 (example)
TARGET_CIDR = "36.72.0.0/16" 
# Scan 500 random subnets from this block = ~128,000 IPs checked
SUBNET_COUNT = 500

def get_random_subnets(cidr: str, count: int = 50) -> list:
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
        
        print(f"Generating {count} random subnets from {num_subnets} total in {cidr}...")
        
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
        print(f"Error parsing {cidr}: {e}")
        return []

def main():
    print("🚀 AGGRESSIVE INDIHOME SCAN (Phase 4.2)")
    print(f"Targeting: {TARGET_CIDR}")
    print(f"Strategy: Scan {SUBNET_COUNT} random /24 subnets.")
    
    subnets = get_random_subnets(TARGET_CIDR, count=SUBNET_COUNT)
    
    target_file = "aggressive_targets.txt"
    with open(target_file, "w") as f:
        f.write("\n".join(subnets))
        
    print(f"\nTargets saved to {target_file}")
    print("Starting Scan Pipeline... (This will take time!)")
    
    # Run main.py via subprocess
    cmd = [sys.executable, "-m", "proxy_manager.main", "--scan", "--targets", target_file, "--ports", "8080,80,3128,8000"]
    subprocess.run(cmd)

if __name__ == "__main__":
    main()
