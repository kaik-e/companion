"""OCR Scanner using EasyOCR"""

import re
import easyocr
import mss
import numpy as np
from PIL import Image
from ores import ORES, ORE_PATTERNS

# Initialize EasyOCR reader (downloads model on first run)
print("Loading EasyOCR model...")
reader = easyocr.Reader(['en'], gpu=True)  # Set gpu=False if no CUDA
print("EasyOCR ready!")


def capture_screen(region=None):
    """Capture screen or specific region"""
    with mss.mss() as sct:
        if region:
            monitor = {
                "left": region["x"],
                "top": region["y"],
                "width": region["width"],
                "height": region["height"]
            }
        else:
            # Primary monitor
            monitor = sct.monitors[1]
        
        screenshot = sct.grab(monitor)
        img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
        return np.array(img)


def scan_for_ores(region=None):
    """Capture screen and detect ores using OCR"""
    # Capture screen
    img = capture_screen(region)
    
    # Run OCR
    results = reader.readtext(img)
    
    # Extract text
    raw_text = " ".join([text for _, text, _ in results])
    print(f"OCR Text: {raw_text}")
    
    # Find ores
    detected = {}
    text_lower = raw_text.lower()
    
    for pattern, ore_id in ORE_PATTERNS.items():
        if pattern in text_lower and ore_id not in detected:
            # Try to find count near the ore name
            count = extract_count_near(raw_text, pattern)
            detected[ore_id] = {
                "id": ore_id,
                "name": ORES[ore_id]["name"],
                "count": count,
                "rarity": ORES[ore_id]["rarity"],
                "multiplier": ORES[ore_id]["multiplier"]
            }
            print(f"Found: {ORES[ore_id]['name']} x{count}")
    
    return detected, raw_text


def extract_count_near(text, keyword):
    """Extract count number near a keyword"""
    text_lower = text.lower()
    idx = text_lower.find(keyword.lower())
    
    if idx == -1:
        return 1
    
    # Look for numbers within 20 chars before/after
    start = max(0, idx - 20)
    end = min(len(text), idx + len(keyword) + 20)
    context = text[start:end]
    
    # Patterns: x5, 5x, :5, just 5
    patterns = [
        r'[xX]\s*(\d+)',      # x5
        r'(\d+)\s*[xX]',      # 5x
        r':\s*(\d+)',         # :5
        r'\s(\d{1,3})\s',     # standalone number
    ]
    
    for pattern in patterns:
        match = re.search(pattern, context)
        if match:
            num = int(match.group(1))
            if 0 < num < 1000:
                return num
    
    return 1


def calculate_forge(ores_dict, craft_type="Weapon"):
    """Calculate forge results from detected ores"""
    if not ores_dict:
        return None
    
    total_multiplier = 0
    total_count = 0
    traits = []
    
    for ore_id, ore_data in ores_dict.items():
        count = ore_data["count"]
        multiplier = ore_data["multiplier"]
        total_multiplier += multiplier * count
        total_count += count
        
        # Check for traits
        ore_info = ORES[ore_id]
        if "trait" in ore_info:
            trait_type = ore_info.get("trait_type", "All")
            if trait_type == "All" or trait_type == craft_type:
                traits.append(f"{ore_info['trait']} ({ore_info['name']})")
    
    if total_count == 0:
        return None
    
    avg_multiplier = total_multiplier / total_count
    
    return {
        "multiplier": round(avg_multiplier, 2),
        "total_ores": total_count,
        "traits": traits
    }


if __name__ == "__main__":
    # Test scan
    print("\nScanning screen in 3 seconds...")
    import time
    time.sleep(3)
    
    detected, raw = scan_for_ores()
    print(f"\nDetected {len(detected)} ores")
    
    result = calculate_forge(detected)
    if result:
        print(f"Multiplier: {result['multiplier']}x")
        print(f"Total ores: {result['total_ores']}")
        print(f"Traits: {result['traits']}")
