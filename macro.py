"""Macro functionality for auto-forging"""

import threading
import time
import ctypes
from ctypes import wintypes

# Windows API for mouse and keyboard
user32 = ctypes.windll.user32

# Virtual key codes
VK_F6 = 0x75
VK_ESCAPE = 0x1B

# Input type constants
INPUT_MOUSE = 0
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
MOUSEEVENTF_ABSOLUTE = 0x8000
MOUSEEVENTF_MOVE = 0x0001

# Window constants
SW_RESTORE = 9
SW_SHOW = 5


def find_roblox_window():
    """Find the Roblox window handle"""
    # Try different window class names Roblox uses
    hwnd = user32.FindWindowW("WINDOWSCLIENT", None)  # Roblox UWP
    if not hwnd:
        hwnd = user32.FindWindowW("RobloxPlayerBeta", None)  # Roblox Player
    if not hwnd:
        # Search by title
        hwnd = user32.FindWindowW(None, "Roblox")
    return hwnd


def focus_roblox():
    """Focus the Roblox window"""
    hwnd = find_roblox_window()
    if hwnd:
        # Restore if minimized
        user32.ShowWindow(hwnd, SW_RESTORE)
        # Bring to foreground
        user32.SetForegroundWindow(hwnd)
        time.sleep(0.3)  # Wait for window to focus
        return True
    return False


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
            "break_position": get_macro_button("break_position"),
            "inventory": get_macro_button("inventory"),
            "sell_tab": get_macro_button("sell_tab"),
            "select_all": get_macro_button("select_all"),
            "accept": get_macro_button("accept"),
            "close_menu": get_macro_button("close_menu"),
        }
    
    def reload_settings(self):
        """Reload button positions and settings"""
        from config import get_macro_button, get_macro_settings
        self.settings = get_macro_settings()
        self.buttons = {
            "break_position": get_macro_button("break_position"),
            "inventory": get_macro_button("inventory"),
            "sell_tab": get_macro_button("sell_tab"),
            "select_all": get_macro_button("select_all"),
            "accept": get_macro_button("accept"),
            "close_menu": get_macro_button("close_menu"),
        }
    
    def update_status(self, status):
        if self.on_status_change:
            self.on_status_change(status)
        print(f"[macro] {status}")
    
    def check_stop_hotkey(self):
        """Check if F6 or Escape is pressed to stop macro"""
        # GetAsyncKeyState returns negative if key is pressed
        if user32.GetAsyncKeyState(VK_F6) & 0x8000:
            return True
        if user32.GetAsyncKeyState(VK_ESCAPE) & 0x8000:
            return True
        return False
    
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
        """Main macro loop - runs until stopped with F6 or Escape"""
        hold_minutes = self.settings.get("hold_duration", 5)
        hold_seconds = hold_minutes * 60
        cycle = 1
        
        self.update_status(f"Macro started - Press F6 or ESC to stop")
        
        while self.running:
            # Check for stop hotkey
            if self.check_stop_hotkey():
                self.update_status("Hotkey pressed - stopping...")
                self.running = False
                break
            
            if self.paused:
                time.sleep(0.5)
                continue
            
            try:
                # Step 1: Focus Roblox and move to break position
                self.update_status(f"Cycle {cycle}: Focusing Roblox...")
                
                if not focus_roblox():
                    self.update_status("Error: Could not find Roblox window!")
                    time.sleep(2)
                    continue
                
                # Move mouse to break position
                break_pos = self.buttons["break_position"]
                self.update_status(f"Cycle {cycle}: Moving to break position...")
                user32.SetCursorPos(break_pos["x"], break_pos["y"])
                time.sleep(0.2)
                
                # Step 2: Hold M1 to break rocks for the set duration
                self.update_status(f"Cycle {cycle}: Breaking rocks for {hold_minutes}min...")
                
                # Press and HOLD left mouse button
                user32.mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
                
                # Wait in small increments so we can check for stop/hotkey
                elapsed = 0
                while elapsed < hold_seconds and self.running and not self.paused:
                    # Check hotkey every second
                    if self.check_stop_hotkey():
                        self.update_status("Stopping...")
                        self.running = False
                        break
                    
                    time.sleep(1)
                    elapsed += 1
                    
                    # Update status every second with realtime countdown
                    remaining = hold_seconds - elapsed
                    mins = remaining // 60
                    secs = remaining % 60
                    self.update_status(f"Cycle {cycle}: {mins}:{secs:02d}")
                
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
                    
                    if self.check_stop_hotkey():
                        self.running = False
                        break
                    
                    # Click Sell tab
                    self.update_status("Opening sell tab...")
                    sell_tab_pos = self.buttons["sell_tab"]
                    click_at(sell_tab_pos["x"], sell_tab_pos["y"])
                    time.sleep(0.4)
                    
                    if self.check_stop_hotkey():
                        self.running = False
                        break
                    
                    # Click Select All
                    self.update_status("Selecting all...")
                    select_pos = self.buttons["select_all"]
                    click_at(select_pos["x"], select_pos["y"])
                    time.sleep(0.3)
                    
                    if self.check_stop_hotkey():
                        self.running = False
                        break
                    
                    # Click Accept
                    self.update_status("Accepting...")
                    accept_pos = self.buttons["accept"]
                    click_at(accept_pos["x"], accept_pos["y"])
                    time.sleep(0.5)
                    
                    if self.check_stop_hotkey():
                        self.running = False
                        break
                    
                    # Click X to close menu
                    self.update_status("Closing menu...")
                    close_pos = self.buttons["close_menu"]
                    click_at(close_pos["x"], close_pos["y"])
                    time.sleep(0.3)
                    
                    self.update_status(f"Cycle {cycle} complete! Starting next...")
                
                cycle += 1
                time.sleep(0.5)
                
            except Exception as e:
                self.update_status(f"Macro error: {e}")
                # Release mouse in case of error
                user32.mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
                time.sleep(1)
        
        # Make sure mouse is released when stopping
        user32.mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
        self.update_status("Macro stopped")
