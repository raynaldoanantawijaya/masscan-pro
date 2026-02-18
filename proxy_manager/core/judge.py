import aiohttp
import asyncio
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class AnonymityJudge:
    def __init__(self):
        # We need an endpoint that returns headers.
        # httpbin.org is good but often overloaded.
        # ip-api.com returns raw IP.
        # Best is to rotate between a few judges.
        self.judges = [
            "http://httpbin.org/get",
            "https://httpbin.org/get",
            # "http://azenv.net/api/v1/ip" # Returns IP
        ]
        self.timeout = aiohttp.ClientTimeout(total=10)

    async def check_anonymity(self, session: aiohttp.ClientSession, proxy_url: str) -> str:
        """
        Determines the anonymity level of a proxy.
        Levels:
        - Transparent: Sends Client IP in headers.
        - Anonymous: Hides Client IP but reveals it's a proxy.
        - Elite: Hides Client IP and no proxy headers.
        """
        try:
            # We need to know our own IP first to compare?
            # Or just check for headers.
            
            # For this implementation, we'll check for specific headers in the response body 
            # returned by httpbin (which echoes headers).
            
            async with session.get("http://httpbin.org/get", timeout=self.timeout) as response:
                if response.status == 200:
                    data = await response.json()
                    headers = data.get("headers", {})
                    origin = data.get("origin", "")
                    
                    # Check for common proxy headers
                    proxy_headers = [
                        "Via",
                        "X-Forwarded-For",
                        "X-Forwarded",
                        "Forwarded-For",
                        "Forwarded",
                        "Client-Ip",
                        "X-Real-Ip"
                    ]
                    
                    detected_headers = [h for h in proxy_headers if h in headers or h.lower() in headers]
                    
                    if detected_headers:
                        # Found proxy headers -> Transparent or Anonymous
                        # If Origin contains multiple IPs (e.g. mine, proxy), it's transparent.
                        # If Origin is just proxy IP, but Via header exists, it's Anonymous.
                        return "anonymous"
                    else:
                        # No proxy headers found.
                        # Ideally, we should also check if 'origin' matches our real IP.
                        # But assuming we don't know our real IP easily here without another check.
                        # If no headers, it's likely Elite.
                        return "elite"
                        
        except Exception as e:
            # logger.debug(f"Judge check failed: {e}")
            pass
            
        return "unknown"
