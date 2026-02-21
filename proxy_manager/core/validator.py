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
        start_time = time.time()
        
        try:
            from curl_cffi.requests import AsyncSession
            proxies = {"http": proxy_url, "https": proxy_url}
            
            # Increase timeout for TLS emulation. Indonesian proxies frequently need 5-8s for initial handshake
            check_timeout = max(self.timeout.total, 8.0) 
            
            async with AsyncSession(proxies=proxies, impersonate="chrome120", timeout=check_timeout) as session:
                is_valid = False
                latency = 0
                
                # Pass 1: Strict HTTPS CONNECT to a major site
                try:
                    t1 = time.time()
                    response = await session.get("https://www.google.com")
                    if response.status_code in [200, 301, 302]: # Allow redirects
                        latency = int((time.time() - t1) * 1000)
                        is_valid = True
                except Exception:
                    pass
                
                # Pass 2: Fallback to HTTP if HTTPS failed (some proxies block HTTPS or Google)
                if not is_valid:
                    try:
                        t2 = time.time()
                        # Use a different endpoint for HTTP pass to avoid cached failure modes
                        http_resp = await session.get("http://httpbin.org/get")
                        if http_resp.status_code == 200:
                            latency = int((time.time() - t2) * 1000)
                            is_valid = True
                    except Exception:
                        pass

                if is_valid:
                    
                    # Anonymity Check using curl_cffi
                    anonymity = "unknown"
                    try:
                        anon_resp = await session.get("http://httpbin.org/get", timeout=5)
                        if anon_resp.status_code == 200:
                            data = anon_resp.json()
                            headers = data.get("headers", {})
                            proxy_headers = ["Via", "X-Forwarded-For", "X-Forwarded", "Forwarded-For", "Forwarded", "Client-Ip", "X-Real-Ip"]
                            detected_headers = [h for h in proxy_headers if h in headers or h.lower() in headers]
                            if detected_headers:
                                anonymity = "anonymous"
                            else:
                                anonymity = "elite"
                    except Exception:
                        pass
                    
                    geo_data = await self.geoip.lookup(ip)

                    return {
                        "ip": ip,
                        "port": port,
                        "protocol": protocol,
                        "anonymity": anonymity,
                        "country": geo_data.get("country", "XX"),
                        "region": "", 
                        "city": "",
                        "isp": geo_data.get("isp", "Unknown"),
                        "response_time_ms": latency,
                        "health_score": 100,
                        "success_count": 1,
                        "fail_count": 0
                    }
        except Exception as e:
            # logger.debug(f"Strict Proxy check failed for {proxy_url}: {e}")
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
