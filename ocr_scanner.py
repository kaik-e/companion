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
    
    # Run OCR - get bounding boxes too for position-based matching
    results = reader.readtext(img)
    
    # Build list of detected text with positions
    text_items = []
    for bbox, text, conf in results:
        # Get center position of text
        x_center = (bbox[0][0] + bbox[2][0]) / 2
        y_center = (bbox[0][1] + bbox[2][1]) / 2
        text_items.append({
            "text": text,
            "x": x_center,
            "y": y_center,
            "conf": conf
        })
    
    raw_text = " ".join([item["text"] for item in text_items])
    print(f"OCR Text: {raw_text}")
    print(f"Items with positions: {[(i['text'], i['x'], i['y']) for i in text_items]}")
    
    # First pass: find all ore names and their positions
    ore_items = []
    for item in text_items:
        text_lower = item["text"].lower().strip()
        
        # Find the BEST (longest) matching pattern
        best_match = None
        best_match_len = 0
        
        for pattern, ore_id in ORE_PATTERNS.items():
            if pattern in text_lower:
                # Prefer longer pattern matches (magmaite > aite)
                if len(pattern) > best_match_len:
                    best_match = ore_id
                    best_match_len = len(pattern)
            elif text_lower in pattern and len(text_lower) >= 4:
                # OCR text is substring of pattern (partial read)
                if len(text_lower) > best_match_len:
                    best_match = ore_id
                    best_match_len = len(text_lower)
        
        if best_match:
            ore_items.append({
                "ore_id": best_match,
                "x": item["x"],
                "y": item["y"],
                "text": item["text"]
            })
            print(f"Matched '{item['text']}' -> {best_match} (len={best_match_len})")
    
    # Second pass: find all count patterns (x#)
    count_items = []
    for item in text_items:
        text = item["text"].strip()
        match = re.search(r'x\s*(\d+)', text, re.IGNORECASE)
        if match:
            count = int(match.group(1))
            if 0 < count < 100:
                count_items.append({
                    "count": count,
                    "x": item["x"],
                    "y": item["y"],
                    "text": item["text"],
                    "used": False
                })
    
    print(f"Ore items: {[(o['ore_id'], o['x']) for o in ore_items]}")
    print(f"Count items: {[(c['count'], c['x']) for c in count_items]}")
    
    # Match each ore with its closest count (must be below and horizontally close)
    detected = {}
    for ore in ore_items:
        if ore["ore_id"] in detected:
            continue
        
        best_count = 1
        best_count_item = None
        best_distance = float('inf')
        
        for count_item in count_items:
            if count_item["used"]:
                continue
            
            dx = abs(count_item["x"] - ore["x"])
            dy = count_item["y"] - ore["y"]  # Positive = below
            
            # Count must be below the ore name (dy > 0) and horizontally close
            if dy > 0 and dy < 80 and dx < 60:
                distance = dx + dy * 0.5  # Prefer horizontally aligned
                
                if distance < best_distance:
                    best_distance = distance
                    best_count = count_item["count"]
                    best_count_item = count_item
        
        # Mark this count as used so it's not assigned to another ore
        if best_count_item:
            best_count_item["used"] = True
        
        ore_id = ore["ore_id"]
        detected[ore_id] = {
            "id": ore_id,
            "name": ORES[ore_id]["name"],
            "count": best_count,
            "rarity": ORES[ore_id]["rarity"],
            "multiplier": ORES[ore_id]["multiplier"]
        }
        print(f"Found: {ORES[ore_id]['name']} x{best_count} (ore_x={ore['x']:.0f})")
    
    return detected, raw_text


if __name__ == "__main__":
    # Test scan
    from calculator import calculate_forge, format_results
    
    print("\nScanning screen in 3 seconds...")
    import time
    time.sleep(3)
    
    detected, raw = scan_for_ores()
    print(f"\nDetected {len(detected)} ores")
    
    result = calculate_forge(detected)
    print(format_results(result))
