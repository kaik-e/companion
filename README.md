# Forger Companion

Screen overlay companion app that uses OCR to detect ores and calculate forge results.

## Requirements

- Python 3.10 or 3.11 (NOT 3.14 - EasyOCR doesn't support it yet)
- Windows 10/11

## Installation

1. Install Python 3.11 from https://python.org/downloads/release/python-3119/

2. Create virtual environment and install:
```bash
py -3.11 -m venv venv
.\venv\Scripts\activate
pip install easyocr mss pillow numpy
```

3. Run:
```bash
python app.py
```

## Usage

1. Click **Region** to select the area with your ore inventory
2. Click **Start Scan** to begin auto-scanning
3. View multiplier and detected ores in the overlay

## First Run

EasyOCR downloads ~100MB model on first run. This only happens once.
