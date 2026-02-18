import asyncio
import logging
import sys
import aiohttp
from aiohttp import web
from proxy_manager.core.storage import StorageManager
import aiohttp_socks
from aiohttp_socks import ProxyConnector, ProxyType
import random

logger = logging.getLogger(__name__)

class ProxyGateway:
    def __init__(self, host: str = "127.0.0.1", port: int = 8888):
        self.host = host
        self.port = port
        self.storage = StorageManager()
        self.app = web.Application()
        self.app.router.add_route('*', '/{tail:.*}', self.handle_request)
        self.runner = None
        self.site = None

    async def get_best_proxy(self):
        # Fetch active proxies from DB
        # Ideally cache this or fetch periodically
        proxies = await self.storage.get_proxies(limit=50) # Top 50 healthy
        # Filter for high health?
        valid = [p for p in proxies if p['health_score'] > 50]
        if not valid:
            return None
        return random.choice(valid)

    async def handle_request(self, request):
        # This is a simple HTTP forwarder. 
        # For full proxy support (CONNECT method for HTTPS), aiohttp web server is tricky.
        # But let's implement a basic forwarder for HTTP requests.
        # For CONNECT (HTTPS), we need to hijack the socket.
        
        proxy_data = await self.get_best_proxy()
        if not proxy_data:
            return web.Response(status=503, text="No proxies available")

        target_url = str(request.url)
        method = request.method
        
        # Construct proxy URL
        pk_proto = proxy_data['protocol']
        pk_ip = proxy_data['ip']
        pk_port = proxy_data['port']
        proxy_address = f"{pk_proto}://{pk_ip}:{pk_port}"
        
        logger.info(f"Forwarding {method} {target_url} via {proxy_address}")

        try:
            connector = ProxyConnector.from_url(proxy_address)
            async with aiohttp.ClientSession(connector=connector) as session:
                # Reconstruct headers (excluding hop-by-hop)
                headers = {k: v for k, v in request.headers.items() if k.lower() not in ['host', 'connection', 'upgrade', 'proxy-connection']}
                
                # Stream body if POST
                data = await request.read()
                
                async with session.request(method, target_url, headers=headers, data=data) as resp:
                    # Stream response back
                    response = web.StreamResponse(status=resp.status, reason=resp.reason)
                    # Forward headers
                    for k, v in resp.headers.items():
                        if k.lower() not in ['content-encoding', 'content-length', 'transfer-encoding', 'connection']:
                            response.headers[k] = v
                    
                    await response.prepare(request)
                    
                    async for chunk in resp.content.iter_chunked(1024):
                        await response.write(chunk)
                        
                    await response.write_eof()
                    return response

        except Exception as e:
            logger.error(f"Gateway error: {e}")
            return web.Response(status=502, text=f"Bad Gateway: {e}")

    async def start(self):
        logger.info(f"Starting Local Proxy Gateway on {self.host}:{self.port}")
        self.runner = web.AppRunner(self.app)
        await self.runner.setup()
        self.site = web.TCPSite(self.runner, self.host, self.port)
        await self.site.start()
        
        # Keep running
        while True:
            await asyncio.sleep(3600)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    gateway = ProxyGateway()
    try:
        if sys.platform == 'win32':
             asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        asyncio.run(gateway.start())
    except KeyboardInterrupt:
        pass
