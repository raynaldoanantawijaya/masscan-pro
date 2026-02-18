import asyncio
import logging
import ipaddress
import random
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

class AsyncScanner:
    def __init__(self, concurrency: int = 1000, timeout: float = 2.0):
        self.concurrency = concurrency
        self.timeout = timeout
        self.semaphore = asyncio.Semaphore(concurrency)

    async def check_port(self, ip: str, port: int) -> Optional[Dict]:
        """
        Briefly attempts to connect to a port to see if it's open.
        """
        async with self.semaphore:
            try:
                conn = asyncio.open_connection(ip, port)
                reader, writer = await asyncio.wait_for(conn, timeout=self.timeout)
                writer.close()
                await writer.wait_closed()
                return {"ip": ip, "port": port}
            except (asyncio.TimeoutError, ConnectionRefusedError, OSError):
                return None
            except Exception as e:
                # logger.debug(f"Scan error {ip}:{port} - {e}")
                return None

    async def scan_range(self, cidr: str, ports: List[int]) -> List[Dict]:
        """
        Scans a CIDR range for specified ports.
        """
        logger.info(f"Starting async scan on {cidr} for ports {ports}")
        open_proxies = []
        
        try:
            network = ipaddress.ip_network(cidr, strict=False)
            # Shuffle IPs to avoid hitting one host sequentially if it's a large subnet
            ips = list(network.hosts())
            random.shuffle(ips)
            
            # Create tasks
            tasks = []
            for ip in ips:
                ip_str = str(ip)
                for port in ports:
                    tasks.append(self.check_port(ip_str, port))
            
            # Execute
            # For very large ranges, we might need batching to avoid creating millions of task objects at once
            # But python's asyncio can handle fairly large numbers. 
            # If cidr is too big (e.g. /16), we should chunk it.
            
            batch_size = 10000
            total_tasks = len(tasks)
            logger.info(f"Generated {total_tasks} scan tasks.")
            
            for i in range(0, total_tasks, batch_size):
                batch = tasks[i:i + batch_size]
                results = await asyncio.gather(*batch)
                
                for res in results:
                    if res:
                        logger.info(f"Found open port: {res['ip']}:{res['port']}")
                        open_proxies.append(res)
                        
        except ValueError as e:
            logger.error(f"Invalid CIDR {cidr}: {e}")
            
        return open_proxies

    async def scan(self, targets: List[str], ports: str = "8080") -> List[Dict]:
        """
        Main entry point for scanning multiple targets.
        """
        port_list = [int(p) for p in ports.split(",")]
        all_results = []
        
        for target in targets:
            # Check if target is CIDR or IP
            if "/" in target:
                results = await self.scan_range(target, port_list)
                all_results.extend(results)
            else:
                # Single IP
                for port in port_list:
                    res = await self.check_port(target, port)
                    if res:
                        all_results.append(res)
                        
        return all_results
