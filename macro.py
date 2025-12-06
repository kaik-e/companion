"""Macro functionality for auto-forging"""

import threading
import time
import ctypes
from ctypes import wintypes

# Windows API for mouse simulation
user32 = ctypes.windll.user32

# Input type constants
INPUT_MOUSE = 0
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
MOUSEEVENTF_ABSOLUTE = 0x8000
MOUSEEVENTF_MOVE = 0x0001


class MOUSEINPUT(ctypes.Structure):
    _fields_ = [
        ("dx", wintypes.LONG),
        ("dy", wintypes.LONG),
        ("mouseData", wintypes.DWORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong))
    ]


class INPUT(ctypes.Structure):
    class _INPUT(ctypes.Union):
        _fields_ = [("mi", MOUSEINPUT)]
    _fields_ = [
        ("type", wintypes.DWORD),
        ("_input", _INPUT)
    ]


def click_at(x, y):
    """Click at specific screen coordinates"""
    # Move mouse
    user32.SetCursorPos(x, y)
    time.sleep(0.05)
    
    # Click
    user32.mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    time.sleep(0.05)
    user32.mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)


def hold_click(duration_seconds):
    """Hold left mouse button for specified duration"""
    user32.mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    time.sleep(duration_seconds)
    user32.mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)


class MacroController:
    """Controls the auto-forge macro loop"""
    
    def __init__(self, on_status_change=None):
        self.running = False
        self.paused = False
        self.on_status_change = on_status_change
        self.thread = None
        
        # Load settings
        from config import get_macro_button, get_macro_settings
        self.settings = get_macro_settings()
        self.buttons = {
            "forge": get_macro_button("forge_button"),
            "inventory": get_macro_button("inventory"),
            "sell_tab": get_macro_button("sell_tab"),
            "select_all": get_macro_button("select_all"),
            "accept": get_macro_button("accept"),
        }
    
    def reload_settings(self):
        """Reload button positions and settings"""
        from config import get_macro_button, get_macro_settings
        self.settings = get_macro_settings()
        self.buttons = {
            "forge": get_macro_button("forge_button"),
            "inventory": get_macro_button("inventory"),
            "sell_tab": get_macro_button("sell_tab"),
            "select_all": get_macro_button("select_all"),
            "accept": get_macro_button("accept"),
        }
    
    def update_status(self, status):
        if self.on_status_change:
            self.on_status_change(status)
        print(f"[macro] {status}")
    
    def start(self):
        """Start the macro loop"""
        if self.running:
            return
        
        self.reload_settings()
        
        # Validate buttons are set
        if not all(self.buttons.values()):
            self.update_status("Error: Macro buttons not configured")
            return False
        
        self.running = True
        self.paused = False
        self.thread = threading.Thread(target=self._macro_loop, daemon=True)
        self.thread.start()
        return True
    
    def stop(self):
        """Stop the macro loop"""
        self.running = False
        self.update_status("Macro stopped")
    
    def toggle_pause(self):
        """Pause/resume the macro"""
        self.paused = not self.paused
        if self.paused:
            self.update_status("Macro paused")
        else:
            self.update_status("Macro resumed")
    
    def _macro_loop(self):
        """Main macro loop"""
        hold_minutes = self.settings.get("hold_duration", 5)
        hold_seconds = hold_minutes * 60
        
        self.update_status(f"Macro started - {hold_minutes}min cycles")
        
        while self.running:
            if self.paused:
                time.sleep(0.5)
                continue
            
            try:
                # Step 1: Click and hold on forge button
                forge_pos = self.buttons["forge"]
                self.update_status(f"Holding forge for {hold_minutes}min...")
                
                # Move to forge button
                user32.SetCursorPos(forge_pos["x"], forge_pos["y"])
                time.sleep(0.2)
                
                # Hold click for duration
                user32.mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
                
                # Wait in small increments so we can check for stop
                elapsed = 0
                while elapsed < hold_seconds and self.running and not self.paused:
                    time.sleep(1)
                    elapsed += 1
                    
                    # Update status every 30 seconds
                    if elapsed % 30 == 0:
                        remaining = hold_seconds - elapsed
                        self.update_status(f"Forging... {remaining//60}:{remaining%60:02d} left")
                
                # Release click
                user32.mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
                
                if not self.running:
                    break
                
                # Step 2: Auto-sell sequence (Inventory > Sell > Select All > Accept)
                if self.settings.get("auto_sell", True):
                    # Click Inventory
                    self.update_status("Opening inventory...")
                    inv_pos = self.buttons["inventory"]
                    click_at(inv_pos["x"], inv_pos["y"])
                    time.sleep(0.5)
                    
                    # Click Sell tab
                    self.update_status("Opening sell tab...")
                    sell_tab_pos = self.buttons["sell_tab"]
                    click_at(sell_tab_pos["x"], sell_tab_pos["y"])
                    time.sleep(0.4)
                    
                    # Click Select All
                    self.update_status("Selecting all...")
                    select_pos = self.buttons["select_all"]
                    click_at(select_pos["x"], select_pos["y"])
                    time.sleep(0.3)
                    
                    # Click Accept
                    self.update_status("Accepting...")
                    accept_pos = self.buttons["accept"]
                    click_at(accept_pos["x"], accept_pos["y"])
                    time.sleep(0.5)
                    
                    self.update_status("Sold! Starting next cycle...")
                
                time.sleep(1)
                
            except Exception as e:
                self.update_status(f"Macro error: {e}")
                time.sleep(1)
        
        self.update_status("Macro stopped")
