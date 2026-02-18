import subprocess
import time
import sys
import os
import shutil
from datetime import datetime

# Project Paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PACKAGE_DIR = os.path.dirname(SCRIPT_DIR)
PROJECT_ROOT = os.path.dirname(PACKAGE_DIR)

# sys.path.append(PROJECT_ROOT) # Not strictly needed if running as module, but good for direct exec

SCRIPTS_DIR = os.path.join(PACKAGE_DIR, "scripts")
LOGS_DIR = os.path.join(PACKAGE_DIR, "logs")
RESULTS_DIR = os.path.join(PACKAGE_DIR, "results")
CONFIGS_DIR = os.path.join(PACKAGE_DIR, "configs")
RANGES_DIR = os.path.join(PACKAGE_DIR, "ranges")

# Ensure logs and results directories exist
os.makedirs(LOGS_DIR, exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)
os.makedirs(CONFIGS_DIR, exist_ok=True)

# Schedule (Start Hour, End Hour)
ISP_SCHEDULE = {
    'firstmedia': (0, 5),     
    'indihome_lama': (1, 5),   
    'biznet': (18, 23),        
    'myrepublic': (18, 23),    
    'cbn': (20, 23),           
    'telkomsel': (0, 5),       
    'xl': (0, 5),              
    'tri': (0, 5),             
    'isp_kecil': (1, 5),       
}

# Config Data (Mirrored for Python Scanner params)
ISP_CONFIGS = {
    'firstmedia': {'ports': '1080,8080,23,4567,7547,80,3128'},
    'indihome_lama': {'ports': '1080,3128,7547,23,8080,80'},
    'biznet': {'ports': '3128,8291,8080,1080,22'},
    'myrepublic': {'ports': '3000,8000,8080,1080,22'},
    'cbn': {'ports': '3128,8080,1080,3389,5900'},
    'telkomsel': {'ports': '22,53,443,1194,4500'},
    'xl': {'ports': '22,1080,8080,80'},
    'tri': {'ports': '8799,22,443,1194'},
    'isp_kecil': {'ports': '1080,3128,8080'}
}

def log(msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {msg}")
    with open(os.path.join(LOGS_DIR, "runner.log"), "a") as f:
        f.write(f"[{timestamp}] {msg}\n")

def check_masscan():
    return shutil.which("masscan") is not None

def run_scan(isp):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # 1. Check if Masscan is available
    has_masscan = check_masscan()
    
    if has_masscan:
        # --- MASSCAN MODE ---
        config_file = os.path.join(CONFIGS_DIR, f"{isp}.conf")
        output_file = os.path.join(RESULTS_DIR, f"{isp}_{timestamp}.txt")
        
        # We need to manually inject output filename since .conf has variable
        # Actually, let's just build the command arguments directly to be safe
        # Read range from file
        range_file = os.path.join(RANGES_DIR, f"{isp}.txt")
        ports = ISP_CONFIGS[isp]['ports']
        
        log(f"Starting MASSCAN for {isp}...")
        cmd = [
            "masscan",
            "--conf", config_file, 
            "--output-filename", output_file,
            "--output-format", "list"
        ]
        
        try:
            subprocess.run(cmd, check=True)
            log(f"Masscan finished. Importing results from {output_file}...")
            
            # Import
            import_cmd = [sys.executable, "-m", "proxy_manager.main", "--import", output_file]
            subprocess.run(import_cmd, check=True)
            log("Import complete.")
            
        except Exception as e:
            log(f"Masscan failed: {e}")
            
    else:
        # --- PYTHON FALLBACK MODE ---
        log(f"Masscan not found. Using PYTHON SCANNER for {isp}...")
        range_file = os.path.join(RANGES_DIR, f"{isp}.txt")
        ports = ISP_CONFIGS[isp]['ports']
        
        if not os.path.exists(range_file):
            log(f"Range file not found: {range_file}")
            return

        # Call main.py with --scan --targets --ports
        # Note: The Python scanner currently takes a file of targets. 
        # Ideally we pass 'range_file' directly.
        
        cmd = [
            sys.executable, "-m", "proxy_manager.main", 
            "--scan", 
            "--targets", range_file, 
            "--ports", ports
        ]
        
        try:
            subprocess.run(cmd, check=True)
            log(f"Python scan for {isp} completed.")
        except Exception as e:
            log(f"Python scan failed: {e}")

def main():
    log("🚀 PROXY SCAN SCHEDULER STARTED")
    log("Checking schedule every 60 minutes...")
    
    # Run loop
    while True:
        now = datetime.now()
        current_hour = now.hour
        
        ran_any = False
        
        for isp, (start, end) in ISP_SCHEDULE.items():
            # Check if current hour is within range
            # Handle wrapping (e.g. 22 to 02)
            is_time = False
            if start <= end:
                is_time = start <= current_hour < end
            else: # Crosses midnight
                is_time = start <= current_hour or current_hour < end
                
            # To avoid running every minute of the hour, we track if we ran today?
            # Or simpler: The user script just checks "if current_hour == start".
            # Let's stick to the user's logic: Run once at the START hour.
            
            if current_hour == start:
                log(f"Triggering scheduled scan for {isp}")
                run_scan(isp)
                ran_any = True
                
        if not ran_any:
            log(f"No scheduled scans for hour {current_hour}. Sleeping...")
            
        # Sleep 1 hour
        time.sleep(3600)

if __name__ == "__main__":
    # If run with --now, just run everything once (for testing)
    if "--now" in sys.argv:
        log("Force running ALL scans immediately...")
        for isp in ISP_SCHEDULE.keys():
            run_scan(isp)
    else:
        main()
