import os
import argparse
import asyncio
from datetime import datetime

# Define project base paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PACKAGE_DIR = os.path.dirname(SCRIPT_DIR)
# PROJECT_ROOT = os.path.dirname(PACKAGE_DIR)

RANGES_DIR = os.path.join(PACKAGE_DIR, "ranges")
CONFIGS_DIR = os.path.join(PACKAGE_DIR, "configs")
RESULTS_DIR = os.path.join(PACKAGE_DIR, "results")

# Ensure directories exist
os.makedirs(CONFIGS_DIR, exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)

ISPS = {
    'firstmedia': {
        'ports': '1080,8080,23,4567,7547,80,3128',
        'rate': '5000'
    },
    'indihome_lama': {
        'ports': '1080,3128,7547,23,8080,80',
        'rate': '5000'
    },
    'biznet': {
        'ports': '8080,3128,80,1080,8888,9090,8118,3129',
        'rate': '10000'
    },
    'myrepublic': {
        'ports': '8080,3000,80,1080,8888,9090,8118,3129',
        'rate': '10000'
    },
    'cbn': {
        'ports': '8080,3128,80,1080,8888,9090,8118,3129',
        'rate': '10000'
    },
    'indointernet': {
        'ports': '8080,3128,80,1080,8888,9090,8118,3129',
        'rate': '10000'
    },
    'icon': {
        'ports': '8080,3128,80,1080,8888,9090,8118,3129',
        'rate': '10000'
    },
    # 'telkomsel': {
    #     'ports': '22,53,443,1194,4500',
    #     'rate': '5000'
    # },
    # 'xl': {
    #     'ports': '22,1080,8080,80',
    #     'rate': '5000'
    # },
    # 'tri': {
    #     'ports': '8799,22,443,1194',
    #     'rate': '5000'
    # },
    'isp_kecil': {
        'ports': '1080,3128,8080',
        'rate': '5000'
    }
}

def generate_configs(use_intel=False):
    print(f"Generating configurations in {CONFIGS_DIR}...")
    
    for isp, data in ISPS.items():
        # Read ranges from file
        range_file = os.path.join(RANGES_DIR, f"{isp}.txt")
        if not os.path.exists(range_file):
            print(f"⚠️ Warning: Range file for {isp} not found at {range_file}. Skipping.")
            continue
            
        with open(range_file, 'r') as f:
            # Filter empty lines and comments
            ranges = [line.strip() for line in f if line.strip() and not line.startswith('#')]
            
        ranges_str = ','.join(ranges)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        
        # Create Masscan Config
        config_content = f"""rate = {data['rate']}
output-format = list
output-filename = {RESULTS_DIR}/{isp}_{timestamp}.txt
ports = {data['ports']}
range = {ranges_str}
"""
        config_path = os.path.join(CONFIGS_DIR, f"{isp}.conf")
        with open(config_path, "w") as f:
            f.write(config_content)
        print(f"✅ Generated config for {isp}")
        
    if use_intel:
        if os.name == 'nt': # fallback for asyncio on windows
             asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        asyncio.run(generate_intel_configs())

async def generate_intel_configs():
    try:
        from proxy_manager.core.storage import StorageManager
        import sys
        if sys.platform == 'win32':
             asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        
        storage = StorageManager()
        top_subnets = await storage.get_top_subnets(limit=50) # top 50 /24s
        
        if not top_subnets:
            print("ℹ️ No subnet intel found yet. Run standard scans to gather data first.")
            return

        print(f"🧠 Generating Smart Intel Config for {len(top_subnets)} high-yield subnets...")
        ranges = [s['subnet_prefix'] for s in top_subnets]
        ranges_str = ','.join(ranges)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        
        # Super aggressive config for known good areas
        config_content = f"""rate = 15000
output-format = list
output-filename = {RESULTS_DIR}/intel_premium_{timestamp}.txt
ports = 8080,3128,80,1080,8888,9090,8118,3129
range = {ranges_str}
"""
        config_path = os.path.join(CONFIGS_DIR, "intel_premium.conf")
        with open(config_path, "w") as f:
            f.write(config_content)
        print("✅ Generated intel_premium.conf (Hyper-Targeted Scan)")
    except Exception as e:
        print(f"Error generating intel config: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--intel", action="store_true", help="Generate smart config based on past yields")
    args = parser.parse_args()
    
    generate_configs(args.intel)
