# 🤖 Advanced Proxy Automation System

## Overview
Based on your workflow design, this system automates the entire lifecycle of proxy hunting: from range targeting to reporting.

## 📂 Directory Structure
- `proxy_manager/ranges/` : Text files containing IP ranges for each ISP.
- `proxy_manager/configs/`: Generated configuration files.
- `proxy_manager/results/`: Scan output files.
- `proxy_manager/scripts/`: Automation scripts.

## 🚀 Key Scripts

### 1. Generate Configurations
Updates scanning targets based on `ranges/`.
```powershell
python -m proxy_manager.scripts.generate_configs
```

### 2. Run Scheduled Scans (The "Brain")
Checks the time and runs scans for the appropriate ISP.
*   **Dual Mode**: Uses `masscan` (if installed) or falls back to `Python Scanner`.
*   **Auto-Import**: Automatically adds results to the database.
```powershell
python -m proxy_manager.scripts.run_scans
```
*Run this in a separate terminal or screen session.*

### 3. Pool Segmentation
Tags proxies as `fast`, `medium`, or `slow` in the database.
```powershell
python -m proxy_manager.scripts.segment_pool
```

### 4. Generate Report
Shows detailed statistics: Active proxies, Top ISPs, Pool distribution.
```powershell
python -m proxy_manager.scripts.generate_report
```

## 📋 Recommended Workflow
1.  **Start the Scheduler**: `start python -m proxy_manager.scripts.run_scans`
2.  **Start the Cleaner**: `start python -m proxy_manager.main --monitor`
3.  **Check Reports**: Run `generate_report` daily.
