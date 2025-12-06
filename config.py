"""Configuration management for Forger Companion"""

import json
from pathlib import Path

# Config directory (same as auth)
CONFIG_DIR = Path.home() / ".forger-companion"
SETTINGS_FILE = CONFIG_DIR / "settings.json"

DEFAULT_SETTINGS = {
    "setup_complete": False,
    "regions": {
        "ores_panel": None,      # Right side "Forge / Select Ores" panel
        "forge_slots": None,     # The 4 ore slots in the middle
        "forge_button": None,    # FORGE! button area (for detection)
    },
    "preferences": {
        "auto_mode": True,
        "always_on_top": True,
        "opacity": 0.95,
        "scan_interval": 2.0,    # seconds
    }
}


def load_settings() -> dict:
    """Load settings from file"""
    try:
        if SETTINGS_FILE.exists():
            with open(SETTINGS_FILE) as f:
                saved = json.load(f)
                # Merge with defaults (in case new settings added)
                settings = DEFAULT_SETTINGS.copy()
                settings.update(saved)
                # Deep merge regions
                if "regions" in saved:
                    settings["regions"] = {**DEFAULT_SETTINGS["regions"], **saved["regions"]}
                if "preferences" in saved:
                    settings["preferences"] = {**DEFAULT_SETTINGS["preferences"], **saved["preferences"]}
                return settings
    except Exception as e:
        print(f"[config] Load error: {e}")
    return DEFAULT_SETTINGS.copy()


def save_settings(settings: dict):
    """Save settings to file"""
    try:
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        with open(SETTINGS_FILE, "w") as f:
            json.dump(settings, f, indent=2)
        print(f"[config] Settings saved")
    except Exception as e:
        print(f"[config] Save error: {e}")


def get_region(name: str) -> dict | None:
    """Get a specific region by name"""
    settings = load_settings()
    return settings.get("regions", {}).get(name)


def set_region(name: str, region: dict):
    """Set a specific region"""
    settings = load_settings()
    if "regions" not in settings:
        settings["regions"] = {}
    settings["regions"][name] = region
    save_settings(settings)


def is_setup_complete() -> bool:
    """Check if first-time setup has been completed"""
    settings = load_settings()
    return settings.get("setup_complete", False)


def mark_setup_complete():
    """Mark setup as complete"""
    settings = load_settings()
    settings["setup_complete"] = True
    save_settings(settings)


def reset_setup():
    """Reset setup (for testing)"""
    settings = load_settings()
    settings["setup_complete"] = False
    settings["regions"] = DEFAULT_SETTINGS["regions"].copy()
    save_settings(settings)
