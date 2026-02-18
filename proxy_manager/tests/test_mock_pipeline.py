import asyncio
import sys
import os
import logging
from unittest.mock import MagicMock, patch

# Add project root to path to import proxy_manager modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from proxy_manager.core.storage import StorageManager
from proxy_manager.core.scanner import MasscanWrapper
from proxy_manager.core.verifier import LightweightVerifier
from proxy_manager.core.validator import ProxyValidator
from proxy_manager.main import run_pipeline

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TestPipeline")

async def test_pipeline_mocked():
    print(">>> Starting Mock Pipeline Test")

    # Mock Data
    MOCK_SCAN_RESULT = [
        {"ip": "192.168.1.100", "ports": [{"port": 8080, "proto": "tcp", "status": "open"}]},
        {"ip": "192.168.1.101", "ports": [{"port": 1080, "proto": "tcp", "status": "open"}]}
    ]

    # Mock Scanner
    with patch('proxy_manager.core.scanner.MasscanWrapper.scan', new_callable=MagicMock) as mock_scan:
        mock_scan.return_value = asyncio.Future()
        mock_scan.return_value.set_result(MOCK_SCAN_RESULT)
        
        # Mock Verifier (Lightweight)
        # 192.168.1.100 -> Open (True)
        # 192.168.1.101 -> Closed (False)
        async def mock_verify(self, ip, port):
            if ip == "192.168.1.100":
                return True
            return False
            
        with patch('proxy_manager.core.verifier.LightweightVerifier.verify', side_effect=mock_verify, autospec=True):
            
            # Mock Validator (Deep Check)
            # 192.168.1.100 -> Returns Valid Config
            async def mock_validate(self, ip, port):
                if ip == "192.168.1.100":
                    return [{
                        "ip": ip,
                        "port": port,
                        "protocol": "http",
                        "anonymity": "elite",
                        "country": "ID",
                        "response_time_ms": 150,
                        "health_score": 100
                    }]
                return []

            with patch('proxy_manager.core.validator.ProxyValidator.validate_all_protocols', side_effect=mock_validate, autospec=True):
                
                # Run the pipeline
                print(">>> Running pipeline with mocked components...")
                await run_pipeline(["192.168.1.0/24"], ports="8080,1080")
                
                # Check Database
                print(">>> Checking Database...")
                storage = StorageManager()
                proxies = await storage.get_proxies()
                
                print(f">>> Proxies found in DB: {len(proxies)}")
                for p in proxies:
                    print(f"    - {p['ip']}:{p['port']} [{p['protocol']}] - Latency: {p['response_time_ms']}ms")
                
                if len(proxies) == 1 and proxies[0]['ip'] == "192.168.1.100":
                    print(">>> TEST SUCCESS: Pipeline logic verified.")
                else:
                    print(">>> TEST FAILED: DB state mismatch.")

if __name__ == "__main__":
    try:
        if sys.platform == 'win32':
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        asyncio.run(test_pipeline_mocked())
    except Exception as e:
        logger.exception("Test failed with exception")
