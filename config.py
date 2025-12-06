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
    "macro_buttons": {
        "forge_button": None,    # Click position for FORGE! button
        "select_all": None,      # Click position for Select All button
        "sell_button": None,     # Click position for Sell button
    },
    "macro_settings": {
        "enabled": False,
        "hold_duration": 5,      # Minutes to hold M1
        "auto_sell": True,
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
                # Deep merge nested dicts
                if "regions" in saved:
                    settings["regions"] = {**DEFAULT_SETTINGS["regions"], **saved["regions"]}
                if "preferences" in saved:
                    settings["preferences"] = {**DEFAULT_SETTINGS["preferences"], **saved["preferences"]}
                if "macro_buttons" in saved:
                    settings["macro_buttons"] = {**DEFAULT_SETTINGS["macro_buttons"], **saved["macro_buttons"]}
                if "macro_settings" in saved:
                    settings["macro_settings"] = {**DEFAULT_SETTINGS["macro_settings"], **saved["macro_settings"]}
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


def get_macro_button(name: str) -> dict | None:
    """Get a macro button position by name"""
    settings = load_settings()
    return settings.get("macro_buttons", {}).get(name)


def set_macro_button(name: str, position: dict):
    """Set a macro button position (x, y coordinates)"""
    settings = load_settings()
    if "macro_buttons" not in settings:
        settings["macro_buttons"] = {}
    settings["macro_buttons"][name] = position
    save_settings(settings)


def get_macro_settings() -> dict:
    """Get macro settings"""
    settings = load_settings()
    return settings.get("macro_settings", DEFAULT_SETTINGS["macro_settings"])


def set_macro_settings(macro_settings: dict):
    """Update macro settings"""
    settings = load_settings()
    settings["macro_settings"] = macro_settings
    save_settings(settings)


def is_macro_setup_complete() -> bool:
    """Check if all macro buttons are configured"""
    settings = load_settings()
    buttons = settings.get("macro_buttons", {})
    return all([
        buttons.get("forge_button"),
        buttons.get("select_all"),
        buttons.get("sell_button")
    ])
