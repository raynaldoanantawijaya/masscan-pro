# 🐉 Installer for Kali Linux

This guide will help you set up the Advanced Proxy Scanner on a fresh Kali Linux environment (VPS or Local).

## 1. Update System & Install Dependencies
First, ensure your system is up to date and has the necessary build tools.
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y git python3-pip python3-venv libpcap-dev gcc make masscan
```
*Note: Kali usually comes with `masscan` pre-installed. If not, the command above handles it.*

## 2. Clone the Repository
```bash
git clone https://github.com/raynaldoanantawijaya/masscan-pro.git
cd masscan-pro
```

## 3. Setup Python Environment
It is recommended to use a virtual environment to avoid conflicts.
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 4. Run the Automation
To start the automated scanning system (Scheduler):
```bash
# This runs in the background using nohup or screen
# Option A: Direct Run (for testing)
python3 -m proxy_manager.scripts.run_scans

# Option B: Run in background (Production)
nohup python3 -m proxy_manager.scripts.run_scans > scanner.log 2>&1 &
```

## 5. Verify Installation
Check if the system can generate a report (empty at first):
```bash
python3 -m proxy_manager.scripts.generate_report
```

## ❓ Troubleshooting
- **Masscan Permission Error**: Masscan requires root privileges. Ensure you run the script with `sudo` if prompted, or configure capabilities: `sudo setcap cap_net_raw=ep $(which masscan)`.
- **Python Imports**: If you see `ModuleNotFoundError`, ensure you are in the root `masscan-pro` directory and the virtual environment is active.
