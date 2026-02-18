# Premium Proxy Hunting Guide (Targeted ISP)

## Overview
This advanced module allows you to hunt for "Residential" proxies by scanning specific ISP ranges (Indihome, Biznet, Indosat) instead of random public lists. These proxies are often faster, cleaner, and less blocked.

## How to Use

### 1. Run the Targeted Scanner
The `scan_isps.py` script automatically:
1.  Selects valid IP ranges for major Indonesian ISPs.
2.  Generates random /24 subnets to sample (checking ~256 IPs at a time).
3.  Scans them using active probing.

**Command:**
```powershell
python scan_isps.py
```

### 2. Check Results
After the scan finishes (5-10 mins), active proxies are automatically added to your database.
Check them with:
```powershell
python find_best_proxies.py
```
Look for new entries with ISP "PT Telekomunikasi Indonesia" or "Biznet Networks".

## Strategy
- **Indihome**: High quantity, dynamic IPs. Good for rotation.
- **Biznet/Dedicated**: High stability, static IPs. Good for long sessions.
- The scanner currently samples about 5000 IPs per run. You can run it multiple times to scan different random subnets!
