import subprocess
import os
import sys
import shutil

def run_step(description, command):
    print(f"\n{'='*50}")
    print(f"🚀 {description}")
    print(f"{'='*50}")
    try:
        subprocess.run(command, check=True, shell=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")

def main():
    print("🌏 INDONESIAN PROXY PIPELINE STARTED")
    
    # 1. Fetch APNIC Ranges
    run_step("Fetching ID IP Ranges (APNIC)", ["python", "utils/apnic_parser.py"])
    
    # 2. Fetch Public Proxies
    run_step("Fetching & Filtering Public ID Proxies", ["python", "fetch_indonesia.py"])
    
    # 3. Generate Masscan Config (Prep only)
    print(f"\n{'='*50}")
    print(f"🛠️  MASSCAN PREPARATION")
    print(f"{'='*50}")
    if os.path.exists("id_ranges.txt"):
        # Create a simple list format for masscan if needed, or just refer to the file
        # Masscan can take -iL id_ranges.txt directly if format is IP/CIDR
        
        # Create config file
        with open("masscan_indonesia.conf", "w") as f:
            f.write("rate = 1000\n")
            f.write("output-format = list\n")
            f.write("output-filename = masscan_results.txt\n")
            f.write("ports = 1080,8080,3128,80,443\n")
            f.write("range-file = id_ranges.txt\n") # Use range-file for reading from file
        
        print("✅ Created 'masscan_indonesia.conf'.")
        print("⚠️  ACTION REQUIRED: Run this command in a terminal with Masscan installed:")
        print("   sudo masscan -c masscan_indonesia.conf")
    else:
        print("❌ id_ranges.txt missing. Skipping Masscan prep.")

    # 4. Import & Validate (if files exist)
    files_to_import = []
    
    if os.path.exists("indonesia_proxies.txt"):
        files_to_import.append("indonesia_proxies.txt")
        
    if os.path.exists("masscan_results.txt"):
        # Needs parsing first? 
        # Masscan list output: "open tcp 80 1.2.3.4 123456"
        # We need to parse it to IP:Port
        print("Parsing Masscan results...")
        proxies = []
        with open("masscan_results.txt", "r") as f:
            for line in f:
                parts = line.strip().split()
                # flexible parsing: look for 'open'
                if len(parts) >= 4 and parts[0] == "open":
                    # masscan default list format: open tcp <port> <ip> <timestamp>
                    port = parts[2]
                    ip = parts[3]
                    proxies.append(f"{ip}:{port}")
        
        with open("masscan_imported.txt", "w") as f:
            f.write("\n".join(proxies))
            
        files_to_import.append("masscan_imported.txt")

    if files_to_import:
        for file in files_to_import:
            run_step(f"Validating {file}", ["python", "-m", "proxy_manager.main", "--import-file", file])
            
        # 5. Query Results
        run_step("Displaying Valid Indonesian Proxies", ["python", "query_db.py"])
        
    else:
        print("\n❌ No proxy files found to import.")

if __name__ == "__main__":
    main()
