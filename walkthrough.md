# Indonesian Proxy Hunter - Walkthrough

## Overview
This system is designed to acquire, filter, and utilize high-quality Indonesian proxies. It combines public list scraping with targeted IP scanning to build a robust proxy pool.

## Key Features

### 1. Hybrid Acquisition Strategy
- **Public Lists**: Automatically scrapes thousands of public proxies and filters them for Indonesian IPs using GeoIP.
- **Targeted Scanning**: Uses APNIC data to identify all Indonesian IP ranges and scans them for open proxy ports.
- **Python Fallback**: If `masscan` is missing, the system automatically uses a built-in Python async scanner.

### 2. Advanced Validation
- **GeoIP Integration**: Enriches every proxy with Country, Region, and ISP data.
- **Anonymity Judge**: Detects "Transparent" proxies that leak your real IP and prioritizes "Elite" proxies.
- **Health Monitoring**: Background process (`LifecycleManager`) re-checks proxies every 5 minutes and removes dead ones.

### 3. Local Gateway
- **`localhost:8888`**: A local proxy server that forwards your traffic through the best available Indonesian proxy.
- **Auto-Rotation**: Automatically rotates through healthy proxies for every request.

## How to Use

### 1. Full Pipeline (Auto-Pilot)
To fetch public proxies, scan (if masscan installed), and validate everything:
```bash
python indonesia_pipeline.py
```

### 2. Manual Masscan (Recommended for Speed)
Creating the target list:
```bash
python utils/apnic_parser.py
```
Running Masscan (if installed):
```bash
masscan -c masscan_indonesia.conf
```
Importing results:
```bash
python -m proxy_manager.main --import-file masscan_results.txt
```

### 3. Using the Proxy Gateway
Start the gateway in a terminal:
```bash
python -m proxy_manager.main --serve
```
Configure your browser/tool to use `http://127.0.0.1:8888`.

### 4. Background Monitoring
Keep your proxy pool fresh:
```bash
python -m proxy_manager.main --monitor
```

## files
- `indonesia_pipeline.py`: Main orchestrator.
- `fetch_indonesia.py`: Scraper for public lists.
- `proxy_manager/core/scanner_py.py`: Python fallback scanner.
- `proxy_manager/core/judge.py`: Anonymity judge.
- `proxy_manager/core/gateway.py`: Local gateway server.

## Verification Results (Phase 6 - The "Golden" Scan)
We successfully executed a targeted scan on high-yield ISPs using the optimized 5000 pps rate.

### Key Achievements
- **Targets Hit:** Biznet, CBN, IndoInternet, ICON+, MyRepublic, FirstMedia.
- **New Findings:** 
    - **IndoInternet:** Found ultra-low latency proxies (46ms).
    - **ICON+:** Successfully penetrated PLN's subsidiary ISP.
    - **FirstMedia:** Unlocked residential proxies previously missed.
    - **MyRepublic:** Harvested a large cluster of high-bandwidth proxies.
- **Efficiency:** Zero crashes, high stability, vast improvement over legacy scans.

### Final Stats (Phase 6)
- **Top Speed:** 46ms (IndoInternet)
- **Total Elite Proxies:** 24+ New Elite Candidates (on top of previous pools).

We successfully scanned and verified a large pool of Indonesian proxies.

### Key Achievements
- **Turbo Mode Enabled:** Boosted Masscan rate to 10k pps (bridged adapter).
- **Import Fix:** Updated `main.py` to natively parse Masscan output.
- **Export Tool:** Created `export_proxies.py` for detailed inventory.
- **Total Proxies Found:** **252 Valid/Live Proxies**.
- **High Quality:** Found elite proxies from PT IndoInternet (46ms), CBN (78ms), and ICON+.

### Top Verified Proxies
| IP:Port | Speed | ISP |
| :--- | :--- | :--- |
| `202.159.35.236:8080` | **46ms** | PT IndoInternet |
| `202.158.11.125:80` | **78ms** | PT Cyberindo Aditama |
| `210.16.67.35:80` | 90ms | Shock Hosting LLC |
| `202.159.101.20:80` | 147ms | PT IndoInternet |
