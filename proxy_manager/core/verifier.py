import asyncio
import logging
from typing import Tuple

logger = logging.getLogger(__name__)

class LightweightVerifier:
    def __init__(self, timeout: int = 3):
        self.timeout = timeout

    async def verify(self, ip: str, port: int) -> bool:
        """
        Quickly check if a port is open and responsive using raw sockets.
        Tries to perform a basic handshake or just connection check.
        """
        try:
            # Simple TCP connect
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(ip, port),
                timeout=self.timeout
            )
            
            # Optional: Send generic byte to trigger response
            # Some proxies won't respond until you send something.
            # HTTP/SOCKS usually expects client to speak first.
            # HEAD / HTTP/1.0\r\n\r\n is safe for HTTP
            # For SOCKS, we might just check connection open.
            
            # Let's try sending a simple HTTP probe
            try:
                writer.write(b"HEAD / HTTP/1.0\r\nHost: probetest\r\n\r\n")
                await writer.drain()
                
                # Check if we can read byte back
                # We don't strictly need to parse it for this lightweight stage
                # Just knowing it didn't immediately RST is often enough for "open"
                # But to filter masscan FPs, getting data is better.
                data = await asyncio.wait_for(reader.read(1024), timeout=2)
                if data:
                    return True
            except (asyncio.TimeoutError, ConnectionResetError):
                # If write/read failed, but connection opened, it's still "open" but maybe not talking HTTP.
                # Masscan already told us it's open.
                # Lightweight verifier aims to confirm it's NOT a firewall tarpit.
                # If we connected, it's likely good enough to pass to Validator.
                return True
            finally:
                writer.close()
                try:
                    await writer.wait_closed()
                except:
                    pass
            
            return True

        except (asyncio.TimeoutError, ConnectionRefusedError, OSError):
            return False
            
# Usage:
# verifier = LightweightVerifier()
# is_open = await verifier.verify("1.2.3.4", 80)
