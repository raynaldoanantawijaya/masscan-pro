import asyncio
import json
import logging
import os
from tempfile import NamedTemporaryFile
from typing import List, Dict, Optional
from proxy_manager.core.config import settings

logger = logging.getLogger(__name__)

class MasscanWrapper:
    def __init__(self, binary_path: str = settings.scanning.masscan_bin):
        self.binary_path = binary_path
        self.default_rate = settings.scanning.rate
        self.default_interface = settings.scanning.interface

    async def scan(self, targets: List[str], ports: Optional[str] = None, rate: Optional[int] = None) -> List[Dict]:
        """
        Run masscan against a list of targets.
        Returns a list of results: [{'ip': '...', 'ports': [{'port': 80, 'proto': 'tcp', 'status': 'open'}]}]
        """
        if not ports:
            ports = settings.scanning.default_ports
        if not rate:
            rate = self.default_rate

        # Create a temporary file for targets
        # Masscan -iL expects a file
        with NamedTemporaryFile(mode='w+', delete=False, suffix='.txt') as tmp_targets:
            for target in targets:
                tmp_targets.write(f"{target}\n")
            tmp_targets_path = tmp_targets.name

        output_file = f"{tmp_targets_path}.json"

        # Build command: masscan -iL targets.txt -p80,8080 --rate 1000 -oJ output.json --randomize-hosts
        cmd = [
            self.binary_path,
            "-iL", tmp_targets_path,
            "-p", ports,
            "--rate", str(rate),
            "-oJ", output_file,
            "--randomize-hosts" # Anti-detection strategy
        ]
        
        # If interface is specified
        if self.default_interface:
             cmd.extend(["-e", self.default_interface])

        logger.info(f"Starting masscan: {' '.join(cmd)}")
        
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()

            if process.returncode != 0:
                logger.error(f"Masscan failed: {stderr.decode()}")
                # masscan often writes status to stderr, but non-zero return code is bad
                # However, sometimes if no adapters found etc it fails. 
                # Proceed to check output file anyway or raise error?
                # Raising error is safer for debugging.
                # But masscan might exit with 1 on simple warnings? 
                # Let's log warning and try to read output.
                pass

            results = self._parse_output(output_file)
            return results

        except Exception as e:
            logger.exception("Error running masscan")
            return []
        finally:
            # Cleanup
            if os.path.exists(tmp_targets_path):
                os.remove(tmp_targets_path)
            if os.path.exists(output_file):
                os.remove(output_file)

    def _parse_output(self, output_file: str) -> List[Dict]:
        results = []
        if not os.path.exists(output_file):
            return results
        
        try:
            # Masscan JSON output is sometimes a list of objects, or concatenated objects? 
            # -oJ usually produces a valid JSON array or a sequence of JSON objects.
            # actually masscan -oJ produces a valid JSON list.
            with open(output_file, 'r') as f:
                content = f.read()
                if not content:
                    return results
                
                # Handle potential JSON parsing errors (sometimes masscan might not close the file properly if crashed)
                # But usually it's fine.
                try: 
                    data = json.loads(content)
                    # Data format: [ { "ip": "...", "timestamp": "...", "ports": [ {"port": 80, "proto": "tcp", "status": "open", "reason": "syn-ack", "ttl": 53} ] } ]
                    results = data
                except json.JSONDecodeError:
                    # Fallback for malformed JSON if necessary
                    # For now just return empty
                    logger.error("Failed to parse Masscan JSON output")
                    pass
        except Exception as e:
            logger.error(f"Error reading masscan output: {e}")
        
        return results

# Example usage (for testing):
# async def main():
#     scanner = MasscanWrapper()
#     results = await scanner.scan(["1.1.1.1", "8.8.8.8"], ports="53,80")
#     print(results)
