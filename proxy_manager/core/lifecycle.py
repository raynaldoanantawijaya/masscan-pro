import aiosqlite
import asyncio
import logging
import time
from typing import List
from proxy_manager.core.storage import StorageManager
from proxy_manager.core.validator import ProxyValidator

logger = logging.getLogger(__name__)

class LifecycleManager:
    def __init__(self):
        self.storage = StorageManager()
        self.validator = ProxyValidator()
        self.running = False

    async def start_monitor(self, interval: int = 300):
        """
        Starts the background monitoring loop.
        Interval: Seconds between checks.
        """
        self.running = True
        logger.info(f"Lifecycle Manager started. Checking every {interval}s.")
        
        while self.running:
            try:
                await self.reverify_proxies()
                await self.cleanup_dead_proxies()
            except Exception as e:
                logger.error(f"Lifecycle error: {e}")
            
            await asyncio.sleep(interval)

    async def stop(self):
        self.running = False

    async def reverify_proxies(self):
        """
        Fetch proxies that haven't been checked recently and re-validate them.
        """
        proxies = await self.storage.get_proxies(limit=1000) # Fetch all for now
        # Ideally, fetch only those with last_checked > X minutes
        
        logger.info(f"Re-verifying {len(proxies)} proxies...")
        
        coros = []
        for proxy in proxies:
            coros.append(self._reverify_single(proxy))
        
        if coros:
            await asyncio.gather(*coros)

    async def _reverify_single(self, proxy):
        ip = proxy['ip']
        port = proxy['port']
        protocol = proxy['protocol']
        
        # Check current health
        current_health = proxy['health_score']
        
        result = await self.validator.check_proxy(ip, port, protocol)
        
        if result:
            # It's alive!
            # Boost health score (max 100)
            new_health = min(100, current_health + 10)
            result['health_score'] = new_health
            result['success_count'] = proxy['success_count'] + 1
            result['fail_count'] = proxy['fail_count']
            
            # Update DB
            await self.storage.save_proxy(result)
            # logger.debug(f"Proxy {ip}:{port} verified (Health: {new_health})")
        else:
            # It's dead!
            # Decrease health
            new_health = max(0, current_health - 20)
            
            # If health drops below threshold, we might rely on cleanup_dead_proxies to remove it
            # Or just update it here.
            # We need a method to UPDATE specific fields without overwriting everything if we don't have full object
            # But save_proxy does REPLACE. So we need full object.
            # Since check_proxy failed, we don't have new metadata.
            # We must manually update status in DB.
            
            async with aiosqlite.connect(self.storage.db_path) as db:
                await db.execute("""
                    UPDATE proxies 
                    SET health_score = ?, fail_count = fail_count + 1, last_checked = CURRENT_TIMESTAMP
                    WHERE ip = ? AND port = ?
                """, (new_health, ip, port))
                await db.commit()
            
            # logger.debug(f"Proxy {ip}:{port} failed (Health: {new_health})")

    async def cleanup_dead_proxies(self, threshold: int = 40):
        """
        Remove proxies with health_score below threshold.
        """
        async with aiosqlite.connect(self.storage.db_path) as db:
            await db.execute("DELETE FROM proxies WHERE health_score < ?", (threshold,))
            deleted = db.total_changes
            await db.commit()
        
        if deleted > 0:
            logger.info(f"Cleaned up {deleted} dead proxies.")
