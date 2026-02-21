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
        self._proxy_pool = []
        self._pool_lock = asyncio.Lock()
        self._failed_attempts = {}

    async def _health_monitor(self):
        """Background task that pings active gateway proxies."""
        while True:
            try:
                # 1. Fill pool if empty
                async with self._pool_lock:
                    if not self._proxy_pool:
                        proxies = await self.storage.get_proxies(limit=10) # Top 10 Elite
                        self._proxy_pool = [p for p in proxies if p['health_score'] > 50]
                        logger.info(f"Loaded {len(self._proxy_pool)} proxies into active gateway pool.")

                # 2. Check health of current pool
                async with self._pool_lock:
                    pool_copy = list(self._proxy_pool)
                
                for proxy in pool_copy:
                    proxy_url = f"{proxy['protocol']}://{proxy['ip']}:{proxy['port']}"
                    is_alive = await self._ping_proxy(proxy_url)
                    
                    if not is_alive:
                        self._failed_attempts[proxy_url] = self._failed_attempts.get(proxy_url, 0) + 1
                        if self._failed_attempts[proxy_url] >= 3:
                            logger.warning(f"Evicting DEAD proxy from gateway: {proxy_url} (3 consecutive failures)")
                            async with self._pool_lock:
                                if proxy in self._proxy_pool:
                                    self._proxy_pool.remove(proxy)
                            # Update DB health negatively
                            await self.storage.update_health(proxy['ip'], proxy['port'], working=False)
                    else:
                        self._failed_attempts[proxy_url] = 0 # reset on success
                
            except Exception as e:
                logger.error(f"Gateway health monitor error: {e}")
            
            await asyncio.sleep(15) # Check every 15s

    async def _ping_proxy(self, proxy_url):
        """Strict CONNECT ping to ensure proxy is still routing."""
        try:
             from curl_cffi.requests import AsyncSession
             proxies = {"http": proxy_url, "https": proxy_url}
             async with AsyncSession(proxies=proxies, impersonate="chrome120", timeout=5) as session:
                 res = await session.get("https://www.google.com")
                 return res.status_code == 200
        except Exception:
             return False

    async def get_best_proxy(self):
        """Get a proxy from the pre-validated healthy pool."""
        async with self._pool_lock:
            if not self._proxy_pool:
                return None
            return random.choice(self._proxy_pool)

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
        
        # Start health monitor background task
        asyncio.create_task(self._health_monitor())
        
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
