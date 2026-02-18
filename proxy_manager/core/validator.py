import asyncio
import logging
import time
import aiohttp
from typing import Dict, Optional, List, Any
from aiohttp_socks import ProxyConnector
from proxy_manager.core.config import settings

logger = logging.getLogger(__name__)

from proxy_manager.core.geoip import GeoIPManager
from proxy_manager.core.judge import AnonymityJudge

class ProxyValidator:
    def __init__(self):
        self.judges = settings.verification.judges
        self.timeout = aiohttp.ClientTimeout(total=settings.verification.timeout)
        self.geoip = GeoIPManager()
        self.judge = AnonymityJudge()

    async def check_proxy(self, ip: str, port: int, protocol: str) -> Optional[Dict[str, Any]]:
        """
        Validates a specific proxy protocol (http, socks4, socks5).
        Returns dict with metadata if working, None if failed.
        """
        proxy_url = f"{protocol}://{ip}:{port}"
        
        # Use simple judge first for speed/liveness
        judge_url = self.judges[0] 
        start_time = time.time()
        
        try:
            # Configure connector based on protocol
            connector = ProxyConnector.from_url(proxy_url)
            
            async with aiohttp.ClientSession(connector=connector, timeout=self.timeout) as session:
                async with session.get(judge_url) as response:
                    if response.status == 200:
                        # Success
                        latency = int((time.time() - start_time) * 1000)
                        
                        # Anonymity Check (Advanced)
                        anonymity = await self.judge.check_anonymity(session, proxy_url)
                        
                        # GeoIP Lookup
                        geo_data = await self.geoip.lookup(ip)

                        return {
                            "ip": ip,
                            "port": port,
                            "protocol": protocol,
                            "anonymity": anonymity,
                            "country": geo_data.get("country", "XX"),
                            "region": "", # GeoIP might parse this 
                            "city": "",
                            "isp": geo_data.get("isp", "Unknown"),
                            "response_time_ms": latency,
                            "health_score": 100,
                            "success_count": 1,
                            "fail_count": 0
                        }
        except Exception as e:
            # logger.debug(f"Proxy check failed for {proxy_url}: {e}")
            pass
        
        return None

    async def validate_all_protocols(self, ip: str, port: int) -> List[Dict[str, Any]]:
        """
        Checks all supported protocols for a given IP:Port.
        Returns list of working configurations.
        """
        valid_configs = []
        # Order makes sense: SOCKS5 is best, then SOCKS4, then HTTP
        protocols_to_test = ["socks5", "socks4", "http"]
        
        tasks = [self.check_proxy(ip, port, proto) for proto in protocols_to_test]
        results = await asyncio.gather(*tasks)
        
        for res in results:
            if res:
                valid_configs.append(res)
        
        return valid_configs
