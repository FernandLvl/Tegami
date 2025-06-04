import json
from pathlib import Path

CONFIG_FILE = Path("config/default_config.json")

def load_config():
    with open(CONFIG_FILE, encoding="utf-8") as f:
        return json.load(f)

def get_setting(key):
    return load_config().get(key)

def get_current_language():
    return get_setting("language")

def save_setting(key, value):
    config = {}
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, encoding="utf-8") as f:
            config = json.load(f)
    config[key] = value
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4, ensure_ascii=False)

