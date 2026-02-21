import os
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

def generate_configs():
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
        
        # Create Masscan Config
        config_content = f"""rate = {data['rate']}
output-format = list
output-filename = {RESULTS_DIR}/{isp}_$(date +%Y%m%d_%H%M).txt
ports = {data['ports']}
range = {ranges_str}
"""
        config_path = os.path.join(CONFIGS_DIR, f"{isp}.conf")
        with open(config_path, "w") as f:
            f.write(config_content)
        print(f"✅ Generated config for {isp}")

if __name__ == "__main__":
    generate_configs()
