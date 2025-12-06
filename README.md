# Forger Companion

A screen overlay companion app for the Forger game that uses OCR to automatically detect ores and calculate forge results.

## Features

- **EasyOCR** - Accurate text detection for game fonts
- **Always-on-top overlay** - Stays visible while playing
- **Auto-scanning** - Continuously scans for ores
- **Region selection** - Focus on specific screen area
- **Forge calculator** - Shows multiplier and traits

## Installation

### Windows

1. Install Python 3.10+ from https://python.org

2. Install dependencies:
```bash
pip install easyocr mss pillow numpy
```

3. Run the app:
```bash
python app.py
```

### First Run

On first run, EasyOCR will download the text detection model (~100MB). This only happens once.

## Usage

1. **Start the app** - Run `python app.py`
2. **Click "Region"** - Draw a box around your forge inventory area
3. **Click "Start Scan"** - App will scan every 2 seconds
4. **View results** - Multiplier and detected ores shown in overlay

## Tips

- Set a region around just the ore inventory for faster/more accurate scanning
- Adjust opacity slider to see through the overlay
- Toggle between Weapon/Armor to see relevant traits

## Requirements

- Python 3.10+
- Windows 10/11 (for screen capture)
- ~2GB RAM for EasyOCR model
- GPU recommended but not required
