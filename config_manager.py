"""
LagForge - Configuration & Persistent Settings Handler (v1.101)
Manages saving and loading user preferences and custom profiles to config.json.
"""

import os
import json
import logging
from typing import Dict, Any, List

logger = logging.getLogger("LagForge.Config")

DEFAULT_CONFIG: Dict[str, Any] = {
    "version": "1.101",
    "ping": 325,
    "jitter": 0.0,
    "loss": 0.0,
    "hotkey": "F8",
    "profiles": [
        {"name": "Competitive Shooter Lag", "ping": 65, "jitter": 15.0, "loss": 1.5},
        {"name": "Intercontinental Server", "ping": 180, "jitter": 25.0, "loss": 3.0},
        {"name": "Severe Packet Loss Test", "ping": 250, "jitter": 40.0, "loss": 12.0},
    ]
}


class ConfigManager:
    """Handles persistent configuration reading and writing to disk."""

    def __init__(self, config_path: str = "config.json"):
        self.config_path = config_path

    def load_config(self) -> Dict[str, Any]:
        if not os.path.exists(self.config_path):
            return DEFAULT_CONFIG.copy()

        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                # Merge with defaults
                cfg = DEFAULT_CONFIG.copy()
                cfg.update(data)
                return cfg
        except Exception as e:
            logger.warning(f"Failed to load config file: {e}. Using defaults.")
            return DEFAULT_CONFIG.copy()

    def save_config(self, config_data: Dict[str, Any]) -> bool:
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(config_data, f, indent=2)
            return True
        except Exception as e:
            logger.error(f"Failed to write config file: {e}")
            return False
