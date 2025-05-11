# modules/config.py

import json
import os

DEFAULT_CONFIG = {
    "weather_update_interval": 5,
    "stock_update_interval": 5,
    "logo_path": "assets/logo.bmp",
    "targets_path": "assets/targets.json"
}

CONFIG_PATH = os.path.join("assets", "config.json")

def load_config():
    try:
        with open(CONFIG_PATH, "r") as f:
            config = json.load(f)
            return {**DEFAULT_CONFIG, **config}
    except Exception:
        return DEFAULT_CONFIG

