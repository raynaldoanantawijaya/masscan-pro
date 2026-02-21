import asyncio
import argparse
import logging
import sys
import os
from typing import List

from proxy_manager.core.config import settings
from proxy_manager.core.scanner import MasscanWrapper
from proxy_manager.core.verifier import LightweightVerifier
from proxy_manager.core.validator import ProxyValidator
from proxy_manager.core.storage import StorageManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("ProxyManager")

from proxy_manager.core.scanner_py import AsyncScanner

async def run_pipeline(targets: List[str], ports: str = None, skip_scan: bool = False, force_python_scanner: bool = False):
    # 1. Initialize DB
    storage = StorageManager()
    await storage.init_db()
    
    candidates = []

    if not skip_scan:
        # 2. Scanning
        if force_python_scanner:
            scanner = AsyncScanner()
            # Default ports if None
            ports_to_scan = ports if ports else "8080,80,3128,1080"
            logger.info(f"Scanning targets: {targets} ports: {ports_to_scan}")
            results = await scanner.scan(targets, ports_to_scan)
            candidates = results
        else:
            scanner = MasscanWrapper()
            logger.info(f"Starting scan on {len(targets)} targets/ranges...")
            scan_results = await scanner.scan(targets, ports=ports)
            logger.info(f"Scan complete. Found {len(scan_results)} potential hosts.")
            
            # Extract IP:Port pairs
            for host in scan_results:
                ip = host.get("ip")
                for port_info in host.get("ports", []):
                    candidates.append({"ip": ip, "port": port_info.get("port")})
    else:
        # Import mode
        logger.info(f"Importing targets from provided list. Skipping scan.")
        for target in targets:
            if ":" in target:
                parts = target.split(":")
                candidates.append({"ip": parts[0], "port": int(parts[1])})
            else:
                 # If just IP, what port? Masscan defaults? 
                 # For import, we expect IP:Port. If not, maybe use default ports?
                 # Let's skip for now or assume port 80?
                 pass 

    logger.info(f"Processing {len(candidates)} candidate proxies.")
    
    # 3. Lightweight Verification
    verifier = LightweightVerifier()
    validator = ProxyValidator()
    
    tasks = []
    
    async def process_candidate(ip, port):
        # Step 3.1: Lightweight check
        # For imported proxies, we might want to skip lightweight check or keep it?
        # Keep it to filter dead ones fast.
        if await verifier.verify(ip, port):
            # Step 3.2: Deep validation
            valid_configs = await validator.validate_all_protocols(ip, port)
            if valid_configs:
                logger.info(f"Verified proxy: {ip}:{port} - {len(valid_configs)} protocols")
                for config in valid_configs:
                    await storage.save_proxy(config)
            else:
                 pass # Open port but failed proxy check
        else:
            pass # Failed lightweight check

    # Concurrency control for validation
    sem = asyncio.Semaphore(settings.verification.max_concurrent)
    
    async def sem_process(ip, port):
        async with sem:
            await process_candidate(ip, port)
            
    # Launch tasks
    # Launch tasks
    validation_tasks = [sem_process(c["ip"], c["port"]) for c in candidates]
    if validation_tasks:
        await asyncio.gather(*validation_tasks)
        
    logger.info("Pipeline complete.")

from proxy_manager.core.lifecycle import LifecycleManager
from proxy_manager.core.gateway import ProxyGateway

def main():
    parser = argparse.ArgumentParser(description="Advanced Proxy Management System")
    parser.add_argument("--scan", action="store_true", help="Run scan and validation pipeline")
    parser.add_argument("--import-file", type=str, help="Import IP:Port list from file and validate")
    parser.add_argument("--monitor", action="store_true", help="Start background lifecycle manager (infinite loop)")
    parser.add_argument("--serve", action="store_true", help="Start local proxy gateway (localhost:8888)")
    parser.add_argument("--reverify", action="store_true", help="One-shot re-verification of all saved proxies")
    parser.add_argument("--targets", type=str, help="Comma separated list of IPs or CIDRs, or path to file")
    parser.add_argument("--ports", type=str, help="Comma separated list of ports (overrides config)")
    
    args = parser.parse_args()
    
    if args.serve:
        gateway = ProxyGateway()
        try:
             asyncio.run(gateway.start())
        except KeyboardInterrupt:
             logger.info("Gateway stopped.")
        return

    if args.monitor:
        logger.info("Starting Lifecycle Monitor...")
        # Since windows doesn't support easy background daemon without service, we run loop here.
        lifecycle = LifecycleManager()
        try:
             asyncio.run(lifecycle.start_monitor())
        except KeyboardInterrupt:
             logger.info("Monitor stopped.")
        return

    if args.reverify:
        logger.info("Starting One-Shot Re-verification of all proxies...")
        lifecycle = LifecycleManager()
        async def run_reverify():
            await lifecycle.reverify_proxies()
            await lifecycle.cleanup_dead_proxies(threshold=40)
        asyncio.run(run_reverify())
        logger.info("Re-verification complete.")
        return

    if args.scan:
        # ... (existing scan logic)
        if not args.targets:
            logger.error("--targets is required for scanning")
            return
            
        targets = []
        if "," in args.targets:
            targets = args.targets.split(",")
        elif "." in args.targets and not args.targets.endswith(".txt") and not "/" in args.targets and not os.path.exists(args.targets):
             # Heuristic for single IP vs file? 
             # If it looks like ID and file doesn't exist, assume IP
             targets = [args.targets]
        elif os.path.exists(args.targets):
             with open(args.targets, 'r') as f:
                 targets = [line.strip() for line in f if line.strip()]
        else:
             # Assume CIDR or IP
             targets = [args.targets]

        # Check for masscan
        use_masscan = False
        import shutil
        if shutil.which("masscan"):
             use_masscan = True
        
        # Override if user forces or masscan missing
        # For now, simplistic check.
        
        if use_masscan:
            logger.info("Using Masscan for scanning...")
             # call existing pipeline which uses MasscanWrapper
            asyncio.run(run_pipeline(targets, args.ports))
        else:
            logger.warning("Masscan not found. Falling back to Python AsyncScanner (Slower).")
            # We need to adapt run_pipeline to accept a scanner instance or handle the switch
            # Modifying run_pipeline is better.
            asyncio.run(run_pipeline(targets, args.ports, force_python_scanner=True))
    
    elif args.import_file:
        # ... (existing import logic)
        if not os.path.exists(args.import_file):
            logger.error(f"File not found: {args.import_file}")
            return
            
        targets = []
        with open(args.import_file, 'r') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                
                # Handle Masscan format: "open tcp 8080 1.2.3.4 ..."
                if line.startswith("open tcp"):
                    parts = line.split()
                    if len(parts) >= 4:
                        port = int(parts[2])
                        ip = parts[3]
                        targets.append(f"{ip}:{port}")
                # Handle simple IP:Port format
                elif ":" in line:
                    targets.append(line)
        
        asyncio.run(run_pipeline(targets, skip_scan=True))

    else:
        parser.print_help()

if __name__ == "__main__":
    main()
