import aiohttp
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class GeoIPManager:
    def __init__(self):
        self.api_url = "http://ip-api.com/json/"
        # Rate limit for free API is 45 requests per minute.
        # We should probably use a batch endpoint or cache.
        # But for now, simple implementation.

    async def lookup(self, ip: str) -> Dict[str, Any]:
        """
        Resolve GeoIP data for a single IP.
        Returns dict with country, isp, etc.
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.api_url}{ip}?fields=status,country,countryCode,isp,org") as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get("status") == "success":
                            return {
                                "country": data.get("countryCode", "XX"),
                                "country_name": data.get("country", "Unknown"),
                                "isp": data.get("isp", "Unknown"),
                                "org": data.get("org", "")
                            }
        except Exception as e:
            logger.warning(f"GeoIP lookup failed for {ip}: {e}")
        
        return {
            "country": "XX",
            "country_name": "Unknown",
            "isp": "Unknown",
            "org": ""
        }

    async def lookup_batch(self, ips: list[str]) -> Dict[str, Dict[str, Any]]:
        """
        Resolve GeoIP data for a list of IPs using batch endpoint.
        Returns dict keyed by query IP.
        """
        results = {}
        # Chunk IPs into batches of 100 (API limit)
        chunks = [ips[i:i + 100] for i in range(0, len(ips), 100)]
        
        async with aiohttp.ClientSession() as session:
            for chunk in chunks:
                try:
                    # ip-api batch endpoint: POST /batch
                    # Body: [{"query": "1.1.1.1"}, ...] or just list of IPs if just fields?
                    # Batch format: JSON array of objects or strings? 
                    # Doc: http://ip-api.com/batch -> supports list of dicts.
                    # payload = [{"query": ip, "fields": "query,status,country,countryCode,isp,org"} for ip in chunk]
                    
                    payload = [{"query": ip, "fields": "query,status,country,countryCode,isp,org"} for ip in chunk]
                    
                    async with session.post("http://ip-api.com/batch", json=payload) as response:
                        if response.status == 200:
                            data = await response.json()
                            for item in data:
                                original_ip = item.get("query")
                                if item.get("status") == "success":
                                    results[original_ip] = {
                                        "country": item.get("countryCode", "XX"),
                                        "country_name": item.get("country", "Unknown"),
                                        "isp": item.get("isp", "Unknown"),
                                        "org": item.get("org", "")
                                    }
                                else:
                                    results[original_ip] = {"country": "XX"}
                        else:
                             logger.warning(f"Batch lookup failed: {response.status}")
                             
                except Exception as e:
                    logger.warning(f"Batch lookup exception: {e}")
        
        return results
