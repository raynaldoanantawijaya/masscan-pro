import yaml
from pydantic import BaseModel
from typing import List, Optional
import os

class DatabaseConfig(BaseModel):
    type: str
    path: str

class ScanningConfig(BaseModel):
    masscan_bin: str
    rate: int
    interface: str
    default_ports: str

class VerificationConfig(BaseModel):
    timeout: int
    judges: List[str]
    max_concurrent: int

class RotationConfig(BaseModel):
    strategy: str

class Settings(BaseModel):
    database: DatabaseConfig
    scanning: ScanningConfig
    verification: VerificationConfig
    rotation: RotationConfig

def load_settings(path: str = None) -> Settings:
    if path is None:
        # Resolve relative to this file (core/config.py -> ../config/settings.yaml)
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        path = os.path.join(base_dir, "config", "settings.yaml")

    if not os.path.exists(path):
        # Fallback to CWD relative
        if os.path.exists("proxy_manager/config/settings.yaml"):
             path = "proxy_manager/config/settings.yaml"
        elif os.path.exists("config/settings.yaml"):
             path = "config/settings.yaml"
        else:
            raise FileNotFoundError(f"Settings file not found at {path}")
    
    with open(path, "r") as f:
        config_data = yaml.safe_load(f)
    
    return Settings(**config_data)

# Global settings instance
try:
    settings = load_settings()
except Exception as e:
    print(f"Error loading settings: {e}")
    settings = None
