"""Authentication module for Forger Companion"""

import os
import json
import hashlib
import platform
import subprocess
import urllib.request
import urllib.error
from pathlib import Path
from datetime import datetime

# API endpoint - update this to your Railway URL
API_URL = os.environ.get("FORGER_API_URL", "https://forger-production.up.railway.app")

# Local config file
CONFIG_DIR = Path.home() / ".forger-companion"
CONFIG_FILE = CONFIG_DIR / "config.json"


def get_hardware_id() -> str:
    """Generate a unique hardware ID for this PC"""
    try:
        system = platform.system()
        
        if system == "Windows":
            # Use Windows machine GUID
            result = subprocess.run(
                ["wmic", "csproduct", "get", "uuid"],
                capture_output=True, text=True, timeout=5
            )
            uuid = result.stdout.strip().split("\n")[-1].strip()
            if uuid and uuid != "UUID":
                return hashlib.sha256(uuid.encode()).hexdigest()[:32]
        
        elif system == "Darwin":  # macOS
            result = subprocess.run(
                ["ioreg", "-rd1", "-c", "IOPlatformExpertDevice"],
                capture_output=True, text=True, timeout=5
            )
            for line in result.stdout.split("\n"):
                if "IOPlatformUUID" in line:
                    uuid = line.split('"')[-2]
                    return hashlib.sha256(uuid.encode()).hexdigest()[:32]
        
        elif system == "Linux":
            # Try machine-id
            for path in ["/etc/machine-id", "/var/lib/dbus/machine-id"]:
                if os.path.exists(path):
                    with open(path) as f:
                        return hashlib.sha256(f.read().strip().encode()).hexdigest()[:32]
    except Exception as e:
        print(f"[auth] Hardware ID error: {e}")
    
    # Fallback: use hostname + username
    fallback = f"{platform.node()}-{os.getlogin()}"
    return hashlib.sha256(fallback.encode()).hexdigest()[:32]


def load_config() -> dict:
    """Load saved configuration"""
    try:
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE) as f:
                return json.load(f)
    except Exception as e:
        print(f"[auth] Config load error: {e}")
    return {}


def save_config(config: dict):
    """Save configuration"""
    try:
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f, indent=2)
    except Exception as e:
        print(f"[auth] Config save error: {e}")


def api_request(endpoint: str, data: dict) -> dict:
    """Make API request to the bot server"""
    try:
        url = f"{API_URL}{endpoint}"
        req = urllib.request.Request(
            url,
            data=json.dumps(data).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        
        with urllib.request.urlopen(req, timeout=10) as response:
            return json.loads(response.read().decode())
    
    except urllib.error.HTTPError as e:
        try:
            error_body = json.loads(e.read().decode())
            return error_body
        except:
            return {"valid": False, "error": f"HTTP {e.code}"}
    
    except urllib.error.URLError as e:
        return {"valid": False, "error": f"Connection failed: {e.reason}"}
    
    except Exception as e:
        return {"valid": False, "error": str(e)}


def validate_key(key: str) -> dict:
    """Validate a license key with the server"""
    hardware_id = get_hardware_id()
    result = api_request("/api/validate", {"key": key, "hardwareId": hardware_id})
    
    if result.get("valid"):
        # Save to config
        config = load_config()
        config["license_key"] = key
        config["hardware_id"] = hardware_id
        config["expires_at"] = result.get("license", {}).get("expiresAt")
        config["validated_at"] = datetime.now().isoformat()
        save_config(config)
    
    return result


def check_license() -> dict:
    """Check if this PC has a valid license"""
    hardware_id = get_hardware_id()
    
    # First check local config
    config = load_config()
    
    if config.get("hardware_id") == hardware_id:
        # Check expiration locally first
        expires_at = config.get("expires_at")
        if expires_at:
            try:
                exp_date = datetime.fromisoformat(expires_at.replace("Z", "+00:00"))
                if datetime.now(exp_date.tzinfo) > exp_date:
                    return {"valid": False, "error": "License expired"}
            except:
                pass
    
    # Verify with server
    result = api_request("/api/check", {"hardwareId": hardware_id})
    
    if result.get("valid"):
        # Update local config
        config["hardware_id"] = hardware_id
        config["expires_at"] = result.get("license", {}).get("expiresAt")
        config["last_check"] = datetime.now().isoformat()
        save_config(config)
    
    return result


def get_license_info() -> dict:
    """Get current license info from local config"""
    config = load_config()
    
    if not config.get("expires_at"):
        return {"active": False}
    
    try:
        expires_at = datetime.fromisoformat(config["expires_at"].replace("Z", "+00:00"))
        now = datetime.now(expires_at.tzinfo)
        
        return {
            "active": now < expires_at,
            "expires_at": config["expires_at"],
            "days_left": max(0, (expires_at - now).days),
            "key": config.get("license_key", "")[:12] + "..."  # Partial key for display
        }
    except:
        return {"active": False}


def clear_license():
    """Clear saved license (for testing/reset)"""
    try:
        if CONFIG_FILE.exists():
            CONFIG_FILE.unlink()
    except:
        pass
