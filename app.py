"""Forger Companion - Overlay App with EasyOCR"""

import tkinter as tk
from tkinter import messagebox
import threading
import time
import sys
import platform

# Auth check before heavy imports
from auth import check_license, validate_key, get_license_info


# ============ UI STYLING ============

def set_dark_titlebar(window):
    """Set dark title bar on Windows 10/11"""
    if platform.system() != "Windows":
        return
    
    try:
        import ctypes
        window.update()
        
        # Get window handle
        hwnd = ctypes.windll.user32.GetParent(window.winfo_id())
        
        # DWMWA_USE_IMMERSIVE_DARK_MODE = 20 (Windows 10 build 18985+)
        # DWMWA_USE_IMMERSIVE_DARK_MODE = 19 (older Windows 10)
        DWMWA_USE_IMMERSIVE_DARK_MODE = 20
        
        # Enable dark mode for title bar
        ctypes.windll.dwmapi.DwmSetWindowAttribute(
            hwnd, 
            DWMWA_USE_IMMERSIVE_DARK_MODE,
            ctypes.byref(ctypes.c_int(1)), 
            ctypes.sizeof(ctypes.c_int)
        )
        
        # Force redraw
        window.withdraw()
        window.deiconify()
    except Exception as e:
        print(f"[ui] Could not set dark titlebar: {e}")


# Colors
BG_DARK = "#0d0d0d"
BG_CARD = "#1a1a1a"
BG_BUTTON = "#2a2a2a"
BG_BUTTON_HOVER = "#3a3a3a"
BG_PRIMARY = "#3d6b3d"
BG_PRIMARY_HOVER = "#4a7f4a"
BG_ACCENT = "#5a5a2d"
BG_DANGER = "#5a2d2d"
FG_WHITE = "#ffffff"
FG_DIM = "#9a9a9a"
FG_GOLD = "#ffdb4a"
FG_GREEN = "#4ade80"
FG_RED = "#ff6b6b"


class StyledButton(tk.Canvas):
    """Custom styled button with hover effects"""
    
    def __init__(self, parent, text, command=None, width=100, height=32, 
                 bg=BG_BUTTON, bg_hover=BG_BUTTON_HOVER, fg=FG_WHITE, 
                 font=("Arial", 10), bold=False, **kwargs):
        super().__init__(parent, width=width, height=height, 
                        bg=parent.cget("bg"), highlightthickness=0, **kwargs)
        
        self.command = command
        self.bg_normal = bg
        self.bg_hover = bg_hover
        self.fg = fg
        self.text = text
        self.font = (font[0], font[1], "bold") if bold else font
        self.width = width
        self.height = height
        
        self.draw_button(self.bg_normal)
        
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        self.bind("<Button-1>", self.on_click)
    
    def draw_button(self, bg_color):
        self.delete("all")
        # Rounded rectangle
        r = 6  # corner radius
        self.create_rounded_rect(2, 2, self.width-2, self.height-2, r, fill=bg_color, outline="")
        # Text
        self.create_text(self.width//2, self.height//2, text=self.text, 
                        fill=self.fg, font=self.font)
    
    def create_rounded_rect(self, x1, y1, x2, y2, r, **kwargs):
        points = [
            x1+r, y1, x2-r, y1, x2, y1, x2, y1+r,
            x2, y2-r, x2, y2, x2-r, y2, x1+r, y2,
            x1, y2, x1, y2-r, x1, y1+r, x1, y1
        ]
        return self.create_polygon(points, smooth=True, **kwargs)
    
    def on_enter(self, e):
        self.draw_button(self.bg_hover)
        self.config(cursor="hand2")
    
    def on_leave(self, e):
        self.draw_button(self.bg_normal)
    
    def on_click(self, e):
        if self.command:
            self.command()


class StyledCheckbox(tk.Canvas):
    """Custom styled checkbox"""
    
    def __init__(self, parent, text, variable=None, command=None, **kwargs):
        super().__init__(parent, width=200, height=24, 
                        bg=parent.cget("bg"), highlightthickness=0, **kwargs)
        
        self.variable = variable or tk.BooleanVar()
        self.command = command
        self.text = text
        self.parent_bg = parent.cget("bg")
        
        self.draw()
        
        self.bind("<Button-1>", self.toggle)
        self.bind("<Enter>", lambda e: self.config(cursor="hand2"))
    
    def draw(self):
        self.delete("all")
        checked = self.variable.get()
        
        # Box
        box_color = BG_PRIMARY if checked else BG_BUTTON
        self.create_rectangle(2, 4, 18, 20, fill=box_color, outline="#444", width=1)
        
        # Checkmark
        if checked:
            self.create_line(6, 12, 9, 16, fill=FG_WHITE, width=2)
            self.create_line(9, 16, 15, 7, fill=FG_WHITE, width=2)
        
        # Text
        self.create_text(26, 12, text=self.text, anchor=tk.W, fill=FG_WHITE, font=("Arial", 10))
    
    def toggle(self, e=None):
        self.variable.set(not self.variable.get())
        self.draw()
        if self.command:
            self.command()
    
    def get(self):
        return self.variable.get()


class AuthWindow:
    """License activation window"""
    
    def __init__(self, on_success):
        self.on_success = on_success
        self.activated = False
        
        self.root = tk.Tk()
        self.root.title("Forger Companion")
        self.root.geometry("420x320")
        self.root.resizable(False, False)
        self.root.configure(bg=BG_DARK)
        
        # Dark title bar
        set_dark_titlebar(self.root)
        
        # Center window
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() - 420) // 2
        y = (self.root.winfo_screenheight() - 320) // 2
        self.root.geometry(f"420x320+{x}+{y}")
        
        # Main container
        container = tk.Frame(self.root, bg=BG_DARK)
        container.pack(expand=True, fill=tk.BOTH, padx=40, pady=30)
        
        # Logo/Title
        tk.Label(container, text="⚒", font=("Arial", 36), bg=BG_DARK, fg=FG_GOLD).pack(pady=(0, 5))
        tk.Label(container, text="Forger Companion", font=("Arial", 20, "bold"), bg=BG_DARK, fg=FG_WHITE).pack(pady=(0, 5))
        tk.Label(container, text="Enter your license key", font=("Arial", 11), bg=BG_DARK, fg=FG_DIM).pack(pady=(0, 25))
        
        # Key entry with border frame
        entry_frame = tk.Frame(container, bg="#333", padx=2, pady=2)
        entry_frame.pack(fill=tk.X, pady=(0, 5))
        
        self.key_var = tk.StringVar()
        self.key_entry = tk.Entry(
            entry_frame,
            textvariable=self.key_var,
            font=("Consolas", 16),
            justify="center",
            bg=BG_CARD,
            fg=FG_WHITE,
            insertbackground=FG_WHITE,
            relief=tk.FLAT,
            bd=0
        )
        self.key_entry.pack(fill=tk.X, ipady=12)
        self.key_entry.focus()
        
        # Placeholder
        self.key_entry.insert(0, "FORGER-XXXXXX")
        self.key_entry.config(fg=FG_DIM)
        self.key_entry.bind("<FocusIn>", self.clear_placeholder)
        self.key_entry.bind("<Return>", lambda e: self.activate())
        
        # Status label
        self.status_label = tk.Label(container, text="", font=("Arial", 10), bg=BG_DARK, fg=FG_RED, height=2)
        self.status_label.pack(pady=(10, 10))
        
        # Activate button
        self.activate_btn = StyledButton(
            container, text="Activate", command=self.activate,
            width=160, height=40, bg=BG_PRIMARY, bg_hover=BG_PRIMARY_HOVER,
            font=("Arial", 12), bold=True
        )
        self.activate_btn.pack(pady=(0, 15))
        
        # Footer
        tk.Label(container, text="Get a key from the Forger Discord bot", font=("Arial", 9), bg=BG_DARK, fg="#555").pack(side=tk.BOTTOM)
    
    def clear_placeholder(self, event):
        if self.key_var.get() == "FORGER-XXXXXX":
            self.key_entry.delete(0, tk.END)
            self.key_entry.config(fg=FG_WHITE)
    
    def activate(self):
        key = self.key_var.get().strip().upper()
        
        if not key or key == "FORGER-XXXXXX":
            self.status_label.config(text="Please enter a license key")
            return
        
        if not key.startswith("FORGER-"):
            self.status_label.config(text="Invalid key format")
            return
        
        self.status_label.config(text="Validating...", fg="#ffdb4a")
        self.activate_btn.config(state=tk.DISABLED)
        self.root.update()
        
        # Validate in background
        def do_validate():
            result = validate_key(key)
            self.root.after(0, lambda: self.handle_result(result))
        
        threading.Thread(target=do_validate, daemon=True).start()
    
    def handle_result(self, result):
        self.activate_btn.config(state=tk.NORMAL)
        
        if result.get("valid"):
            self.status_label.config(text="✓ Activated!", fg="#4ade80")
            self.root.after(1000, self.success)
        else:
            error = result.get("error", "Activation failed")
            self.status_label.config(text=f"✗ {error}", fg="#ff4444")
    
    def success(self):
        self.activated = True
        self.root.destroy()
    
    def run(self):
        self.root.mainloop()
        # After mainloop ends, call on_success if activated
        if self.activated:
            self.on_success()


class ForgerCompanion:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Forger Companion")
        self.root.geometry("420x550")
        self.root.attributes("-topmost", True)
        self.root.attributes("-alpha", 0.95)
        self.root.resizable(False, False)
        
        # Remove default title bar
        self.root.overrideredirect(True)
        
        # Dark theme
        self.bg_color = BG_DARK
        self.fg_color = FG_WHITE
        self.dim_color = FG_DIM
        self.gold_color = FG_GOLD
        self.red_color = FG_RED
        
        self.root.configure(bg=self.bg_color)
        
        # UI state
        self.minimized = False
        self.drag_data = {"x": 0, "y": 0}
        
        # Load saved settings
        from config import load_settings, get_region
        self.settings = load_settings()
        
        # State
        self.scanning = False
        self.auto_mode = self.settings.get("preferences", {}).get("auto_mode", True)
        self.forge_ui_visible = False
        self.scan_region = get_region("forge_slots")
        self.ores_region = get_region("ores_panel")
        self.detected_ores = {}
        self.craft_type = "Weapon"
        self.enhancement_level = 0
        self.last_result = None
        
        self.setup_ui()
        
        # Center window on screen
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() - 420) // 2
        y = (self.root.winfo_screenheight() - 550) // 2
        self.root.geometry(f"+{x}+{y}")
        
        # Show tutorial on first run
        if not self.settings.get("setup_complete"):
            self.root.after(500, self.show_tutorial)
        
        # Start auto-detection in background
        if self.auto_mode:
            self.start_auto_detect()
    
    def setup_ui(self):
        # === CUSTOM TITLE BAR ===
        self.title_bar = tk.Frame(self.root, bg="#151515", height=36)
        self.title_bar.pack(fill=tk.X)
        self.title_bar.pack_propagate(False)
        
        # Make title bar draggable
        self.title_bar.bind("<Button-1>", self.start_drag)
        self.title_bar.bind("<B1-Motion>", self.do_drag)
        
        # App icon and title
        title_left = tk.Frame(self.title_bar, bg="#151515")
        title_left.pack(side=tk.LEFT, fill=tk.Y, padx=10)
        
        # Load logo
        try:
            from PIL import Image, ImageTk
            import os
            logo_path = os.path.join(os.path.dirname(__file__), "logo.png")
            logo_img = Image.open(logo_path)
            # Resize maintaining aspect ratio
            logo_img.thumbnail((20, 20), Image.Resampling.LANCZOS)
            self.logo_photo = ImageTk.PhotoImage(logo_img)
            logo_lbl = tk.Label(title_left, image=self.logo_photo, bg="#151515")
            logo_lbl.pack(side=tk.LEFT, pady=8)
        except:
            # Fallback to emoji if logo fails
            tk.Label(title_left, text="⚒", font=("Arial", 14), bg="#151515", fg=FG_GOLD).pack(side=tk.LEFT, pady=8)
        
        title_lbl = tk.Label(title_left, text="Forger Companion", font=("Arial", 10, "bold"), bg="#151515", fg=FG_WHITE)
        title_lbl.pack(side=tk.LEFT, padx=8, pady=8)
        title_lbl.bind("<Button-1>", self.start_drag)
        title_lbl.bind("<B1-Motion>", self.do_drag)
        
        # Window controls (right side)
        title_right = tk.Frame(self.title_bar, bg="#151515")
        title_right.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Minimize/collapse button
        self.collapse_btn = tk.Label(title_right, text="▼", font=("Arial", 10), bg="#151515", fg=FG_DIM, 
                                     width=4, cursor="hand2")
        self.collapse_btn.pack(side=tk.LEFT, fill=tk.Y)
        self.collapse_btn.bind("<Button-1>", lambda e: self.toggle_collapse())
        self.collapse_btn.bind("<Enter>", lambda e: self.collapse_btn.config(bg="#252525"))
        self.collapse_btn.bind("<Leave>", lambda e: self.collapse_btn.config(bg="#151515"))
        
        # Close button
        close_btn = tk.Label(title_right, text="✕", font=("Arial", 11), bg="#151515", fg=FG_DIM, 
                            width=4, cursor="hand2")
        close_btn.pack(side=tk.LEFT, fill=tk.Y)
        close_btn.bind("<Button-1>", lambda e: self.root.destroy())
        close_btn.bind("<Enter>", lambda e: close_btn.config(bg="#c42b1c", fg=FG_WHITE))
        close_btn.bind("<Leave>", lambda e: close_btn.config(bg="#151515", fg=FG_DIM))
        
        # === MAIN CONTENT (collapsible) ===
        self.main_content = tk.Frame(self.root, bg=self.bg_color)
        self.main_content.pack(fill=tk.BOTH, expand=True)
        
        # === TAB BAR ===
        tab_bar = tk.Frame(self.main_content, bg=BG_CARD, height=40)
        tab_bar.pack(fill=tk.X, padx=8, pady=(8, 0))
        tab_bar.pack_propagate(False)
        
        self.current_tab = "macro"
        
        # Tab buttons
        tab_frame = tk.Frame(tab_bar, bg=BG_CARD)
        tab_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        
        self.macro_tab_btn = StyledButton(tab_frame, text="Macro", command=lambda: self.switch_tab("macro"),
                                          width=70, height=28, bg=BG_PRIMARY, bg_hover=BG_PRIMARY_HOVER,
                                          font=("Arial", 9), bold=True)
        self.macro_tab_btn.pack(side=tk.LEFT, padx=2)
        
        self.calc_tab_btn = StyledButton(tab_frame, text="Calculator", command=lambda: self.switch_tab("calc"),
                                         width=80, height=28, bg=BG_BUTTON, bg_hover=BG_BUTTON_HOVER,
                                         font=("Arial", 9))
        self.calc_tab_btn.pack(side=tk.LEFT, padx=2)
        
        # Settings button on right
        settings_frame = tk.Frame(tab_bar, bg=BG_CARD)
        settings_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=5, pady=5)
        
        self.settings_btn = StyledButton(settings_frame, text="⚙", command=self.open_settings,
                                         width=30, height=28, bg=BG_BUTTON, bg_hover=BG_BUTTON_HOVER,
                                         font=("Arial", 10))
        self.settings_btn.pack(side=tk.RIGHT)
        
        # === PAGE CONTAINER ===
        self.page_container = tk.Frame(self.main_content, bg=self.bg_color)
        self.page_container.pack(fill=tk.BOTH, expand=True)
        
        # Create pages
        self.macro_page = tk.Frame(self.page_container, bg=self.bg_color)
        self.calc_page = tk.Frame(self.page_container, bg=self.bg_color)
        
        self.setup_macro_page()
        self.setup_calc_page()
        
        # Show macro page by default
        self.macro_page.pack(fill=tk.BOTH, expand=True)
    
    def switch_tab(self, tab):
        """Switch between tabs"""
        if tab == self.current_tab:
            return
        
        self.current_tab = tab
        
        # Update tab button styles
        if tab == "macro":
            self.macro_tab_btn.bg_normal = BG_PRIMARY
            self.macro_tab_btn.draw_button(BG_PRIMARY)
            self.calc_tab_btn.bg_normal = BG_BUTTON
            self.calc_tab_btn.draw_button(BG_BUTTON)
            self.calc_page.pack_forget()
            self.macro_page.pack(fill=tk.BOTH, expand=True)
        else:
            self.calc_tab_btn.bg_normal = BG_PRIMARY
            self.calc_tab_btn.draw_button(BG_PRIMARY)
            self.macro_tab_btn.bg_normal = BG_BUTTON
            self.macro_tab_btn.draw_button(BG_BUTTON)
            self.macro_page.pack_forget()
            self.calc_page.pack(fill=tk.BOTH, expand=True)
    
    def setup_macro_page(self):
        """Setup the macro control page"""
        from macro import MacroController
        
        self.macro_controller = MacroController(on_status_change=self.on_macro_status)
        
        # Center content
        content = tk.Frame(self.macro_page, bg=self.bg_color)
        content.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)
        
        # Status indicator
        self.macro_status_indicator = tk.Label(content, text="●", font=("Arial", 48), bg=self.bg_color, fg="#666")
        self.macro_status_indicator.pack(pady=(20, 10))
        
        self.macro_status_label = tk.Label(content, text="Macro Ready", font=("Arial", 14, "bold"), 
                                           bg=self.bg_color, fg=FG_WHITE)
        self.macro_status_label.pack(pady=(0, 5))
        
        self.macro_detail_label = tk.Label(content, text="Configure in Settings → Macro", font=("Arial", 10), 
                                           bg=self.bg_color, fg=FG_DIM)
        self.macro_detail_label.pack(pady=(0, 30))
        
        # Big start/stop button
        self.macro_btn = StyledButton(content, text="▶ Start Macro", command=self.toggle_macro,
                                      width=160, height=50, bg=BG_PRIMARY, bg_hover=BG_PRIMARY_HOVER,
                                      font=("Arial", 14), bold=True)
        self.macro_btn.pack(pady=10)
        
        # Timer display
        self.timer_label = tk.Label(content, text="", font=("Arial", 24, "bold"), bg=self.bg_color, fg=FG_GOLD)
        self.timer_label.pack(pady=20)
        
        # Info card
        info_card = tk.Frame(content, bg=BG_CARD, padx=20, pady=15)
        info_card.pack(fill=tk.X, pady=(20, 0))
        
        from config import get_macro_settings, is_macro_setup_complete
        settings = get_macro_settings()
        is_setup = is_macro_setup_complete()
        
        if is_setup:
            duration = settings.get("hold_duration", 5)
            auto_sell = "On" if settings.get("auto_sell", True) else "Off"
            info_text = f"Duration: {duration} min  •  Auto-sell: {auto_sell}"
            info_color = FG_DIM
        else:
            info_text = "⚠ Macro not configured - Go to Settings → Macro"
            info_color = FG_GOLD
        
        tk.Label(info_card, text=info_text, font=("Arial", 10), bg=BG_CARD, fg=info_color).pack()
    
    def toggle_macro(self):
        """Start or stop the macro"""
        if self.macro_controller.running:
            self.macro_controller.stop()
            self.macro_btn.text = "▶ Start Macro"
            self.macro_btn.bg_normal = BG_PRIMARY
            self.macro_btn.draw_button(BG_PRIMARY)
            self.macro_status_indicator.config(fg="#666")
        else:
            from config import is_macro_setup_complete
            if not is_macro_setup_complete():
                self.macro_status_label.config(text="Configure macro first!")
                self.macro_detail_label.config(text="Go to Settings → Macro → Configure")
                return
            
            if self.macro_controller.start():
                self.macro_btn.text = "⏹ Stop Macro"
                self.macro_btn.bg_normal = BG_DANGER
                self.macro_btn.draw_button(BG_DANGER)
                self.macro_status_indicator.config(fg=FG_GREEN)
    
    def on_macro_status(self, status):
        """Called when macro status changes"""
        self.root.after(0, lambda: self.macro_status_label.config(text=status))
    
    def setup_calc_page(self):
        """Setup the calculator page (auto-detection)"""
        # Controls bar
        controls = tk.Frame(self.calc_page, bg=BG_CARD, height=44)
        controls.pack(fill=tk.X, padx=8, pady=(8, 4))
        controls.pack_propagate(False)
        
        # Left side controls
        left_controls = tk.Frame(controls, bg=BG_CARD)
        left_controls.pack(side=tk.LEFT, fill=tk.Y, padx=8, pady=7)
        
        # Auto mode indicator + button
        self.auto_indicator = tk.Label(left_controls, text="●", font=("Arial", 12), bg=BG_CARD, fg="#666")
        self.auto_indicator.pack(side=tk.LEFT, padx=(0, 4))
        
        self.auto_btn = StyledButton(left_controls, text="Auto", command=self.toggle_auto_mode,
                                     width=50, height=28, bg=BG_PRIMARY, bg_hover=BG_PRIMARY_HOVER,
                                     font=("Arial", 9), bold=True)
        self.auto_btn.pack(side=tk.LEFT, padx=2)
        
        # Right side - Enhancement controls
        right_controls = tk.Frame(controls, bg=BG_CARD)
        right_controls.pack(side=tk.RIGHT, fill=tk.Y, padx=8, pady=7)
        
        self.enh_minus_btn = StyledButton(right_controls, text="−", command=self.decrease_enhancement,
                                          width=26, height=26, bg=BG_BUTTON, bg_hover=BG_BUTTON_HOVER,
                                          font=("Arial", 11), bold=True)
        self.enh_minus_btn.pack(side=tk.LEFT, padx=2)
        
        self.enh_label = tk.Label(right_controls, text="+0", font=("Arial", 11, "bold"), bg=BG_CARD, fg=FG_GOLD, width=3)
        self.enh_label.pack(side=tk.LEFT, padx=2)
        
        self.enh_plus_btn = StyledButton(right_controls, text="+", command=self.increase_enhancement,
                                         width=26, height=26, bg=BG_BUTTON, bg_hover=BG_BUTTON_HOVER,
                                         font=("Arial", 11), bold=True)
        self.enh_plus_btn.pack(side=tk.LEFT, padx=2)
        
        # Main content area for calculator
        self.content = tk.Frame(self.calc_page, bg=self.bg_color)
        self.content.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.setup_calc_content()
    
    def start_drag(self, event):
        self.drag_data["x"] = event.x
        self.drag_data["y"] = event.y
    
    def do_drag(self, event):
        x = self.root.winfo_x() + event.x - self.drag_data["x"]
        y = self.root.winfo_y() + event.y - self.drag_data["y"]
        self.root.geometry(f"+{x}+{y}")
    
    def toggle_collapse(self):
        if self.minimized:
            # Expand
            self.main_content.pack(fill=tk.BOTH, expand=True)
            self.collapse_btn.config(text="▼")
            self.root.geometry("420x550")
            self.minimized = False
        else:
            # Collapse
            self.main_content.pack_forget()
            self.collapse_btn.config(text="▲")
            self.root.geometry("420x36")
            self.minimized = True
    
    def setup_calc_content(self):
        """Setup calculator content (ore slots, results, etc.)"""
        # === MULTI LABEL ===
        tk.Label(self.content, text="MULTI", font=("Arial", 9), bg=self.bg_color, fg=self.dim_color).pack()
        self.multiplier_label = tk.Label(self.content, text="0.00x", font=("Arial", 28, "bold"), bg=self.bg_color, fg=self.fg_color)
        self.multiplier_label.pack()
        
        # === ORE BOXES ===
        self.ores_frame = tk.Frame(self.content, bg=self.bg_color)
        self.ores_frame.pack(pady=10)
        
        # Create 4 ore slot frames
        self.ore_slots = []
        for i in range(4):
            slot = tk.Frame(self.ores_frame, bg="#1a1a1a", width=80, height=80, highlightbackground="#444", highlightthickness=2)
            slot.pack(side=tk.LEFT, padx=5)
            slot.pack_propagate(False)
            
            name_lbl = tk.Label(slot, text="Empty", font=("Arial", 9, "bold"), bg="#1a1a1a", fg="#444")
            name_lbl.pack(pady=(8, 0))
            
            amt_lbl = tk.Label(slot, text="", font=("Arial", 14, "bold"), bg="#1a1a1a", fg="white")
            amt_lbl.pack(expand=True)
            
            pct_lbl = tk.Label(self.ores_frame, text="", font=("Arial", 12, "bold"), bg=self.bg_color, fg="white")
            
            self.ore_slots.append({"frame": slot, "name": name_lbl, "amount": amt_lbl, "pct": pct_lbl})
        
        # Percentage labels below boxes
        self.pct_frame = tk.Frame(self.content, bg=self.bg_color)
        self.pct_frame.pack()
        for i in range(4):
            lbl = tk.Label(self.pct_frame, text="", font=("Arial", 12, "bold"), bg=self.bg_color, fg="white", width=8)
            lbl.pack(side=tk.LEFT, padx=5)
            self.ore_slots[i]["pct"] = lbl
        
        # === WEAPON RESULT ===
        self.weapon_frame = tk.Frame(self.content, bg=self.bg_color)
        self.weapon_frame.pack(pady=(15, 5))
        
        self.weapon_name_label = tk.Label(self.weapon_frame, text="", font=("Arial", 18, "bold"), bg=self.bg_color, fg="white")
        self.weapon_name_label.pack()
        
        self.weapon_stats_label = tk.Label(self.weapon_frame, text="", font=("Arial", 11, "bold"), bg=self.bg_color, fg=self.gold_color)
        self.weapon_stats_label.pack()
        
        # === WEAPON TRAITS ===
        self.weapon_traits_label = tk.Label(self.content, text="", font=("Arial", 9), bg=self.bg_color, fg="#ccc", wraplength=380)
        self.weapon_traits_label.pack(pady=2)
        
        # === ARMOR RESULT ===
        self.armor_frame = tk.Frame(self.content, bg=self.bg_color)
        self.armor_frame.pack(pady=(10, 5))
        
        self.armor_name_label = tk.Label(self.armor_frame, text="", font=("Arial", 18, "bold"), bg=self.bg_color, fg="white")
        self.armor_name_label.pack()
        
        self.armor_stats_label = tk.Label(self.armor_frame, text="", font=("Arial", 11, "bold"), bg=self.bg_color, fg=self.gold_color)
        self.armor_stats_label.pack()
        
        # === ARMOR TRAITS ===
        self.armor_traits_label = tk.Label(self.content, text="", font=("Arial", 9), bg=self.bg_color, fg="#ccc", wraplength=380)
        self.armor_traits_label.pack(pady=2)
        
        # Status bar at bottom of calc page
        status_frame = tk.Frame(self.calc_page, bg=BG_CARD)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=8, pady=8)
        
        self.status_label = tk.Label(status_frame, text="Waiting for Forge UI...", font=("Arial", 9), bg=BG_CARD, fg=FG_DIM, anchor=tk.W)
        self.status_label.pack(side=tk.LEFT, padx=10, pady=6)
        
        # License info
        info = get_license_info()
        if info.get("active"):
            days = info.get("days_left", 0)
            color = FG_GREEN if days > 7 else FG_GOLD if days > 1 else FG_RED
            tk.Label(status_frame, text=f"License: {days}d", font=("Arial", 9), bg=BG_CARD, fg=color).pack(side=tk.RIGHT, padx=10, pady=6)
        
        # Debug (hidden by default)
        self.debug_frame = tk.Frame(self.root, bg=self.bg_color)
        self.debug_text = tk.Text(self.debug_frame, height=2, bg="#111", fg="#666", font=("Consolas", 8), wrap=tk.WORD)
        self.debug_text.pack(fill=tk.X, padx=5)
        self.debug_visible = False
        
        # Right-click to toggle debug
        self.root.bind("<Button-3>", lambda e: self.toggle_debug())
    
    def start_auto_detect(self):
        """Start background thread for auto-detecting forge UI"""
        self.waiting_for_ores = False
        
        def auto_detect_loop():
            while self.auto_mode:
                try:
                    from ocr_scanner import detect_forge_ui
                    is_forge, has_ores, _ = detect_forge_ui(self.scan_region)
                    
                    # Update UI in main thread
                    self.root.after(0, lambda f=is_forge, o=has_ores: self.on_forge_ui_detected(f, o))
                    
                except Exception as e:
                    print(f"[auto] Detection error: {e}")
                
                # Faster polling when waiting for ores, slower otherwise
                sleep_time = 1.0 if self.waiting_for_ores else 2.0
                time.sleep(sleep_time)
        
        threading.Thread(target=auto_detect_loop, daemon=True).start()
    
    def on_forge_ui_detected(self, visible, has_ores):
        """Called when forge UI detection state changes"""
        prev_visible = self.forge_ui_visible
        self.forge_ui_visible = visible
        
        if visible:
            if has_ores:
                # Ores are placed - start scanning!
                self.waiting_for_ores = False
                self.auto_indicator.config(fg=FG_GREEN)
                self.status_label.config(text="Scanning ores...")
                if not self.scanning:
                    self.scanning = True
                    threading.Thread(target=self.scan_loop, daemon=True).start()
            else:
                # Forge UI open but no ores yet - waiting
                self.waiting_for_ores = True
                self.auto_indicator.config(fg=FG_GOLD)  # Yellow - waiting
                self.status_label.config(text="Forge UI open - place ores...")
                self.scanning = False
                self.clear_display()
        else:
            # Forge UI closed
            self.waiting_for_ores = False
            self.auto_indicator.config(fg="#666")
            self.status_label.config(text="Waiting for Forge UI...")
            self.scanning = False
            self.clear_display()
    
    def toggle_auto_mode(self):
        """Toggle auto-detection mode"""
        self.auto_mode = not self.auto_mode
        
        if self.auto_mode:
            self.auto_btn.config(bg="#2d5a2d")
            self.status_label.config(text="Auto mode: ON")
            self.start_auto_detect()
        else:
            self.auto_btn.config(bg="#333")
            self.auto_indicator.config(fg="#666")
            self.status_label.config(text="Auto mode: OFF")
        
    def scan_loop(self):
        while self.scanning:
            try:
                detected, raw_text = scan_for_ores(self.scan_region)
                self.detected_ores = detected
                
                # Update UI in main thread
                self.root.after(0, lambda d=detected, r=raw_text: self.update_results(d, r))
                
            except Exception as e:
                self.root.after(0, lambda err=str(e): self.status_label.config(text=f"Error: {err}"))
            
            time.sleep(2)  # Scan every 2 seconds
    
    def update_results(self, detected, raw_text):
        # Update debug
        self.debug_text.delete(1.0, tk.END)
        self.debug_text.insert(tk.END, raw_text[:500])
        
        # Update status
        self.status_label.config(text=f"Found {len(detected)} ores")
        
        # Calculate BOTH weapon and armor results
        weapon_result = calculate_forge(detected, "Weapon")
        armor_result = calculate_forge(detected, "Armor")
        self.last_result = weapon_result  # Store for enhancement updates
        
        if not weapon_result:
            self.multiplier_label.config(text="0.00x")
            self.clear_display()
            return
        
        # Update multiplier
        self.multiplier_label.config(text=f"{weapon_result['multiplier']:.2f}x")
        
        # Update ore slots (up to 4)
        ore_list = list(weapon_result['composition'].items())
        for i in range(4):
            slot = self.ore_slots[i]
            if i < len(ore_list):
                ore_name, pct = ore_list[i]
                ore_data = ORES.get(ore_name, {})
                rarity = ore_data.get("rarity", "Common")
                color = RARITY_COLORS.get(rarity, "#808080")
                
                # Get amount from detected
                amount = detected.get(ore_name, {}).get("count", 0)
                
                # Update slot
                display_name = ore_name.replace(" Ore", "").replace(" Crystal", "")
                slot["name"].config(text=display_name, fg="white")
                slot["amount"].config(text=f"{amount}x")
                slot["frame"].config(highlightbackground=color)
                slot["pct"].config(text=f"{pct:.0f}%")
            else:
                # Empty slot
                slot["name"].config(text="Empty", fg="#444")
                slot["amount"].config(text="")
                slot["frame"].config(highlightbackground="#444")
                slot["pct"].config(text="")
        
        # Find top weapon
        top_weapon = None
        top_weapon_odds = 0
        for item, stats in weapon_result['item_stats'].items():
            if stats['odds'] > top_weapon_odds:
                top_weapon_odds = stats['odds']
                top_weapon = item
                top_weapon_stats = stats
        
        # Find top armor
        top_armor = None
        top_armor_odds = 0
        for item, stats in armor_result['item_stats'].items():
            if stats['odds'] > top_armor_odds:
                top_armor_odds = stats['odds']
                top_armor = item
                top_armor_stats = stats
        
        # Update weapon display
        if top_weapon:
            enh_mult = 1 + (self.enhancement_level * 0.05)
            base_dmg = top_weapon_stats.get('damage', 0) or 0
            enh_dmg = base_dmg * enh_mult
            mw_price = top_weapon_stats.get('mw_price', 0) or 0
            
            self.weapon_name_label.config(text=f"{top_weapon} ({int(top_weapon_odds * 100)}%)")
            
            enh_text = f" (+{self.enhancement_level})" if self.enhancement_level > 0 else ""
            stats_text = f"Masterwork {mw_price:,}$  •  {enh_dmg:.2f} DMG{enh_text}"
            self.weapon_stats_label.config(text=stats_text)
        
        # Weapon traits
        weapon_traits = [t['text'] for t in weapon_result['traits'] if t.get('source')]
        self.weapon_traits_label.config(text="  |  ".join(weapon_traits) if weapon_traits else "")
        
        # Update armor display
        if top_armor:
            mw_price = top_armor_stats.get('mw_price', 0) or 0
            self.armor_name_label.config(text=f"{top_armor} ({int(top_armor_odds * 100)}%)")
            self.armor_stats_label.config(text=f"Masterwork {mw_price:,}$")
        
        # Armor traits
        armor_traits = [t['text'] for t in armor_result['traits'] if t.get('source')]
        self.armor_traits_label.config(text="  |  ".join(armor_traits) if armor_traits else "")
    
    def clear_display(self):
        """Reset all display elements to default state"""
        # Reset multiplier
        self.multiplier_label.config(text="0.00x", fg=self.fg_color)
        
        # Reset ore slots
        for slot in self.ore_slots:
            slot["name"].config(text="Empty", fg="#444")
            slot["amount"].config(text="")
            slot["frame"].config(highlightbackground="#444")
            slot["pct"].config(text="")
        
        # Reset weapon display
        self.weapon_name_label.config(text="")
        self.weapon_stats_label.config(text="")
        self.weapon_traits_label.config(text="")
        
        # Reset armor display
        self.armor_name_label.config(text="")
        self.armor_stats_label.config(text="")
        self.armor_traits_label.config(text="")
        
        # Clear last result
        self.last_result = None
        self.detected_ores = {}
    
    def toggle_craft_type(self):
        if self.craft_type == "Weapon":
            self.craft_type = "Armor"
            self.craft_btn.config(text="Armor")
        else:
            self.craft_type = "Weapon"
            self.craft_btn.config(text="Weapon")
    
    def increase_enhancement(self):
        if self.enhancement_level < 9:
            self.enhancement_level += 1
            self.enh_label.config(text=f"+{self.enhancement_level}")
            self.update_enhancement_display()
    
    def decrease_enhancement(self):
        if self.enhancement_level > 0:
            self.enhancement_level -= 1
            self.enh_label.config(text=f"+{self.enhancement_level}")
            self.update_enhancement_display()
    
    def update_enhancement_display(self):
        """Update damage display with current enhancement level"""
        if not self.last_result:
            return
        
        # Find best weapon
        best_item = None
        best_odds = 0
        for item_type, stats in self.last_result['item_stats'].items():
            if stats['odds'] > best_odds:
                best_odds = stats['odds']
                best_item = item_type
                best_stats = stats
        
        if best_item and best_stats.get('damage'):
            base_dmg = best_stats['damage']
            enh_mult = 1 + (self.enhancement_level * 0.05)
            enh_dmg = base_dmg * enh_mult
            mw_price = best_stats.get('mw_price', 0) or 0
            
            enh_text = f" (+{self.enhancement_level})" if self.enhancement_level > 0 else ""
            stats_text = f"Masterwork {mw_price:,}$  •  {enh_dmg:.2f} DMG{enh_text}"
            self.weapon_stats_label.config(text=stats_text)
    
    def toggle_debug(self):
        self.debug_visible = not self.debug_visible
        if self.debug_visible:
            self.debug_frame.pack(fill=tk.X, before=self.status_label)
        else:
            self.debug_frame.pack_forget()
    
    def open_settings(self):
        """Open settings window"""
        SettingsWindow(self.root, self.on_settings_changed)
    
    def on_settings_changed(self):
        """Called when settings are updated"""
        from config import load_settings, get_region
        self.settings = load_settings()
        self.scan_region = get_region("forge_slots")
        self.ores_region = get_region("ores_panel")
        self.status_label.config(text="Settings updated")
    
    def show_tutorial(self):
        """Show first-time tutorial overlay"""
        # Create overlay frame
        self.tutorial_frame = tk.Frame(self.root, bg=BG_DARK)
        self.tutorial_frame.place(relx=0, rely=0, relwidth=1, relheight=1)
        
        # Content container
        content = tk.Frame(self.tutorial_frame, bg=BG_DARK)
        content.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        tk.Label(content, text="⚒", font=("Arial", 44), bg=BG_DARK, fg=FG_GOLD).pack(pady=(0, 10))
        tk.Label(content, text="Welcome!", font=("Arial", 22, "bold"), bg=BG_DARK, fg=FG_WHITE).pack(pady=(0, 5))
        tk.Label(content, text="How it works", font=("Arial", 11), bg=BG_DARK, fg=FG_DIM).pack(pady=(0, 25))
        
        # Instructions in a card
        card = tk.Frame(content, bg=BG_CARD, padx=25, pady=20)
        card.pack(pady=(0, 25))
        
        steps = [
            ("1.", "Open the Forge UI in Roblox"),
            ("2.", "Place ores in the forge slots"),
            ("3.", "Results appear automatically!")
        ]
        
        for num, text in steps:
            step_frame = tk.Frame(card, bg=BG_CARD)
            step_frame.pack(fill=tk.X, pady=6)
            tk.Label(step_frame, text=num, font=("Arial", 11, "bold"), bg=BG_CARD, fg=FG_GOLD, width=2).pack(side=tk.LEFT)
            tk.Label(step_frame, text=text, font=("Arial", 11), bg=BG_CARD, fg=FG_WHITE, anchor=tk.W).pack(side=tk.LEFT, padx=5)
        
        # Status indicators explanation
        indicator_frame = tk.Frame(content, bg=BG_DARK)
        indicator_frame.pack(pady=(0, 20))
        
        tk.Label(indicator_frame, text="●", font=("Arial", 12), bg=BG_DARK, fg="#666").pack(side=tk.LEFT)
        tk.Label(indicator_frame, text="Waiting  ", font=("Arial", 9), bg=BG_DARK, fg=FG_DIM).pack(side=tk.LEFT)
        tk.Label(indicator_frame, text="●", font=("Arial", 12), bg=BG_DARK, fg=FG_GOLD).pack(side=tk.LEFT)
        tk.Label(indicator_frame, text="Forge Open  ", font=("Arial", 9), bg=BG_DARK, fg=FG_DIM).pack(side=tk.LEFT)
        tk.Label(indicator_frame, text="●", font=("Arial", 12), bg=BG_DARK, fg=FG_GREEN).pack(side=tk.LEFT)
        tk.Label(indicator_frame, text="Scanning", font=("Arial", 9), bg=BG_DARK, fg=FG_DIM).pack(side=tk.LEFT)
        
        # Buttons
        btn_frame = tk.Frame(content, bg=BG_DARK)
        btn_frame.pack(pady=(0, 10))
        
        StyledButton(btn_frame, text="Got it!", command=self.close_tutorial,
                    width=120, height=38, bg=BG_PRIMARY, bg_hover=BG_PRIMARY_HOVER,
                    font=("Arial", 11), bold=True).pack(side=tk.LEFT, padx=8)
        
        StyledButton(btn_frame, text="Set Region", command=self.tutorial_set_region,
                    width=100, height=38, bg=BG_BUTTON, bg_hover=BG_BUTTON_HOVER,
                    font=("Arial", 10)).pack(side=tk.LEFT, padx=8)
    
    def tutorial_set_region(self):
        """Set region from tutorial (optional - for advanced users)"""
        self.tutorial_frame.destroy()
        
        def on_region(region):
            if region:
                from config import set_region, save_settings, load_settings
                set_region("forge_slots", region)
                self.scan_region = region
                
                # Mark setup complete
                settings = load_settings()
                settings["setup_complete"] = True
                save_settings(settings)
                
                self.status_label.config(text="Region saved!")
            else:
                # Mark complete anyway
                from config import save_settings, load_settings
                settings = load_settings()
                settings["setup_complete"] = True
                save_settings(settings)
                self.status_label.config(text="Waiting for Forge UI...")
        
        RegionSelector(self.root, on_region)
    
    def close_tutorial(self):
        """Close tutorial"""
        self.tutorial_frame.destroy()
        
        # Mark setup complete
        from config import save_settings, load_settings
        settings = load_settings()
        settings["setup_complete"] = True
        save_settings(settings)
        
        self.status_label.config(text="Waiting for Forge UI...")
    
    def run(self):
        self.root.mainloop()


class SettingsWindow:
    """Settings configuration window"""
    
    def __init__(self, parent, on_save):
        self.parent = parent
        self.on_save = on_save
        
        self.window = tk.Toplevel(parent)
        self.window.title("Settings")
        self.window.geometry("380x420")
        self.window.resizable(False, False)
        self.window.configure(bg=BG_DARK)
        self.window.transient(parent)
        # Don't use grab_set - it blocks child windows
        
        # Dark title bar
        set_dark_titlebar(self.window)
        
        # Center on screen
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() - 380) // 2
        y = (self.window.winfo_screenheight() - 420) // 2
        self.window.geometry(f"380x420+{x}+{y}")
        
        self.setup_ui()
    
    def setup_ui(self):
        from config import load_settings, get_region
        self.settings = load_settings()
        
        # Title
        tk.Label(self.window, text="Settings", font=("Arial", 18, "bold"), bg=BG_DARK, fg=FG_WHITE).pack(pady=(25, 20))
        
        # Main content frame
        content = tk.Frame(self.window, bg=BG_DARK)
        content.pack(fill=tk.BOTH, expand=True, padx=30)
        
        # Screen Regions section
        tk.Label(content, text="Screen Regions", font=("Arial", 11, "bold"), bg=BG_DARK, fg=FG_GOLD).pack(anchor=tk.W, pady=(0, 12))
        
        # Forge Slots row in a card
        slots_card = tk.Frame(content, bg=BG_CARD, padx=15, pady=12)
        slots_card.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(slots_card, text="Forge Slots", font=("Arial", 11), bg=BG_CARD, fg=FG_WHITE).pack(side=tk.LEFT)
        
        slots_region = get_region("forge_slots")
        slots_text = f"{slots_region['width']}×{slots_region['height']}" if slots_region else "Not configured"
        slots_color = FG_GREEN if slots_region else FG_DIM
        self.slots_label = tk.Label(slots_card, text=slots_text, font=("Arial", 10), bg=BG_CARD, fg=slots_color)
        self.slots_label.pack(side=tk.LEFT, padx=15)
        
        StyledButton(slots_card, text="Set", command=lambda: self.set_region("forge_slots"),
                    width=60, height=28, bg=BG_BUTTON, bg_hover=BG_BUTTON_HOVER,
                    font=("Arial", 9)).pack(side=tk.RIGHT)
        
        # Preferences section
        tk.Label(content, text="Preferences", font=("Arial", 11, "bold"), bg=BG_DARK, fg=FG_GOLD).pack(anchor=tk.W, pady=(5, 12))
        
        prefs_card = tk.Frame(content, bg=BG_CARD, padx=15, pady=12)
        prefs_card.pack(fill=tk.X)
        
        # Auto mode
        self.auto_var = tk.BooleanVar(value=self.settings.get("preferences", {}).get("auto_mode", True))
        self.auto_cb = StyledCheckbox(prefs_card, text="Auto-detect Forge UI", variable=self.auto_var)
        self.auto_cb.pack(anchor=tk.W, pady=4)
        
        # Always on top
        self.topmost_var = tk.BooleanVar(value=self.settings.get("preferences", {}).get("always_on_top", True))
        self.top_cb = StyledCheckbox(prefs_card, text="Always on top", variable=self.topmost_var)
        self.top_cb.pack(anchor=tk.W, pady=4)
        
        # Macro section
        tk.Label(content, text="Macro", font=("Arial", 11, "bold"), bg=BG_DARK, fg=FG_GOLD).pack(anchor=tk.W, pady=(15, 12))
        
        macro_card = tk.Frame(content, bg=BG_CARD, padx=15, pady=12)
        macro_card.pack(fill=tk.X)
        
        tk.Label(macro_card, text="Auto-forge & sell macro", font=("Arial", 10), bg=BG_CARD, fg=FG_DIM).pack(side=tk.LEFT)
        
        StyledButton(macro_card, text="Configure", command=self.open_macro_settings,
                    width=80, height=28, bg=BG_BUTTON, bg_hover=BG_BUTTON_HOVER,
                    font=("Arial", 9)).pack(side=tk.RIGHT)
        
        # Buttons at bottom
        btn_frame = tk.Frame(self.window, bg=BG_DARK)
        btn_frame.pack(fill=tk.X, padx=30, pady=15)
        
        StyledButton(btn_frame, text="Cancel", command=self.window.destroy,
                    width=90, height=34, bg=BG_BUTTON, bg_hover=BG_BUTTON_HOVER,
                    font=("Arial", 10)).pack(side=tk.LEFT)
        
        StyledButton(btn_frame, text="Save", command=self.save,
                    width=90, height=34, bg=BG_PRIMARY, bg_hover=BG_PRIMARY_HOVER,
                    font=("Arial", 10), bold=True).pack(side=tk.RIGHT)
    
    def set_region(self, region_name):
        """Open region selector for a specific region"""
        self.window.withdraw()
        
        def on_selected(region):
            self.window.deiconify()
            if region:
                from config import set_region
                set_region(region_name, region)
                
                # Update label
                text = f"{region['width']}x{region['height']}"
                self.slots_label.config(text=text, fg="#4ade80")
        
        RegionSelector(self.parent, on_selected)
    
    def open_macro_settings(self):
        """Open macro configuration window"""
        MacroSettingsWindow(self.window)
    
    def save(self):
        """Save settings and close"""
        from config import save_settings
        
        self.settings["preferences"]["auto_mode"] = self.auto_var.get()
        self.settings["preferences"]["always_on_top"] = self.topmost_var.get()
        save_settings(self.settings)
        
        self.on_save()
        self.window.destroy()


class RegionSelector:
    """Fullscreen overlay for selecting scan region"""
    
    def __init__(self, parent, callback):
        self.callback = callback
        self.start_x = 0
        self.start_y = 0
        self.rect = None
        
        # Create fullscreen window
        self.window = tk.Toplevel(parent)
        self.window.attributes("-fullscreen", True)
        self.window.attributes("-alpha", 0.3)
        self.window.attributes("-topmost", True)
        self.window.configure(bg="black")
        
        # Canvas for drawing
        self.canvas = tk.Canvas(
            self.window,
            highlightthickness=0,
            bg="black"
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Instructions
        self.canvas.create_text(
            self.window.winfo_screenwidth() // 2,
            50,
            text="Click and drag to select region. Press ESC to cancel.",
            fill="white",
            font=("Segoe UI", 14)
        )
        
        # Bindings
        self.canvas.bind("<Button-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.window.bind("<Escape>", self.on_cancel)
        
    def on_press(self, event):
        self.start_x = event.x
        self.start_y = event.y
        if self.rect:
            self.canvas.delete(self.rect)
        self.rect = self.canvas.create_rectangle(
            self.start_x, self.start_y, self.start_x, self.start_y,
            outline="#7aa2f7",
            width=2
        )
    
    def on_drag(self, event):
        self.canvas.coords(self.rect, self.start_x, self.start_y, event.x, event.y)
    
    def on_release(self, event):
        x1, y1 = min(self.start_x, event.x), min(self.start_y, event.y)
        x2, y2 = max(self.start_x, event.x), max(self.start_y, event.y)
        
        width = x2 - x1
        height = y2 - y1
        
        if width > 50 and height > 50:
            region = {"x": x1, "y": y1, "width": width, "height": height}
            self.callback(region)
        else:
            self.callback(None)
        
        self.window.destroy()
    
    def on_cancel(self, event):
        self.callback(None)
        self.window.destroy()


class PointPicker:
    """Fullscreen overlay for picking a single point (button position)"""
    
    def __init__(self, parent, callback, instruction="Click on the button"):
        self.callback = callback
        
        self.window = tk.Toplevel(parent)
        self.window.attributes("-fullscreen", True)
        self.window.attributes("-alpha", 0.4)
        self.window.attributes("-topmost", True)
        self.window.configure(bg="black")
        
        # Instruction label
        self.label = tk.Label(
            self.window,
            text=instruction + "\n\nPress ESC to cancel",
            font=("Arial", 18, "bold"),
            bg="black",
            fg="white"
        )
        self.label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        # Crosshair canvas
        self.canvas = tk.Canvas(self.window, highlightthickness=0, bg="black")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        self.window.bind("<Button-1>", self.on_click)
        self.window.bind("<Escape>", self.on_cancel)
        self.window.bind("<Motion>", self.on_motion)
        
        self.crosshair_h = None
        self.crosshair_v = None
    
    def on_motion(self, event):
        # Draw crosshair
        if self.crosshair_h:
            self.canvas.delete(self.crosshair_h)
            self.canvas.delete(self.crosshair_v)
        
        self.crosshair_h = self.canvas.create_line(0, event.y, self.window.winfo_width(), event.y, fill="#7aa2f7", width=1)
        self.crosshair_v = self.canvas.create_line(event.x, 0, event.x, self.window.winfo_height(), fill="#7aa2f7", width=1)
    
    def on_click(self, event):
        position = {"x": event.x, "y": event.y}
        self.callback(position)
        self.window.destroy()
    
    def on_cancel(self, event):
        self.callback(None)
        self.window.destroy()


class MacroSettingsWindow:
    """Macro configuration window"""
    
    def __init__(self, parent):
        self.parent = parent
        
        self.window = tk.Toplevel(parent)
        self.window.title("Macro Settings")
        self.window.geometry("400x480")
        self.window.resizable(False, False)
        self.window.configure(bg=BG_DARK)
        self.window.transient(parent)
        # Don't use grab_set - it blocks child windows
        
        set_dark_titlebar(self.window)
        
        # Center
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() - 400) // 2
        y = (self.window.winfo_screenheight() - 480) // 2
        self.window.geometry(f"400x480+{x}+{y}")
        
        self.setup_ui()
    
    def setup_ui(self):
        from config import get_macro_button, get_macro_settings
        self.macro_settings = get_macro_settings()
        
        # Title
        tk.Label(self.window, text="Macro Settings", font=("Arial", 18, "bold"), bg=BG_DARK, fg=FG_WHITE).pack(pady=(20, 15))
        
        # Content
        content = tk.Frame(self.window, bg=BG_DARK)
        content.pack(fill=tk.BOTH, expand=True, padx=25)
        
        # Button positions section
        tk.Label(content, text="Button Positions", font=("Arial", 11, "bold"), bg=BG_DARK, fg=FG_GOLD).pack(anchor=tk.W, pady=(0, 10))
        
        tk.Label(content, text="Click 'Set' then click on the button in-game", font=("Arial", 9), bg=BG_DARK, fg=FG_DIM).pack(anchor=tk.W, pady=(0, 10))
        
        buttons_card = tk.Frame(content, bg=BG_CARD, padx=15, pady=10)
        buttons_card.pack(fill=tk.X, pady=(0, 15))
        
        # Forge button
        self.forge_label = self._create_button_row(buttons_card, "Forge Button", "forge_button")
        
        # Select All button
        self.select_label = self._create_button_row(buttons_card, "Select All", "select_all")
        
        # Sell button
        self.sell_label = self._create_button_row(buttons_card, "Sell Button", "sell_button")
        
        # Duration section
        tk.Label(content, text="Settings", font=("Arial", 11, "bold"), bg=BG_DARK, fg=FG_GOLD).pack(anchor=tk.W, pady=(10, 10))
        
        settings_card = tk.Frame(content, bg=BG_CARD, padx=15, pady=12)
        settings_card.pack(fill=tk.X)
        
        # Duration row
        dur_frame = tk.Frame(settings_card, bg=BG_CARD)
        dur_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(dur_frame, text="Hold duration (minutes)", font=("Arial", 10), bg=BG_CARD, fg=FG_WHITE).pack(side=tk.LEFT)
        
        self.duration_var = tk.IntVar(value=self.macro_settings.get("hold_duration", 5))
        
        dur_controls = tk.Frame(dur_frame, bg=BG_CARD)
        dur_controls.pack(side=tk.RIGHT)
        
        StyledButton(dur_controls, text="−", command=self.dec_duration,
                    width=26, height=24, bg=BG_BUTTON, bg_hover=BG_BUTTON_HOVER,
                    font=("Arial", 10), bold=True).pack(side=tk.LEFT, padx=2)
        
        self.dur_label = tk.Label(dur_controls, text=str(self.duration_var.get()), font=("Arial", 11, "bold"), 
                                  bg=BG_CARD, fg=FG_GOLD, width=3)
        self.dur_label.pack(side=tk.LEFT, padx=5)
        
        StyledButton(dur_controls, text="+", command=self.inc_duration,
                    width=26, height=24, bg=BG_BUTTON, bg_hover=BG_BUTTON_HOVER,
                    font=("Arial", 10), bold=True).pack(side=tk.LEFT, padx=2)
        
        # Auto-sell checkbox
        self.autosell_var = tk.BooleanVar(value=self.macro_settings.get("auto_sell", True))
        self.autosell_cb = StyledCheckbox(settings_card, text="Auto-sell after forging", variable=self.autosell_var)
        self.autosell_cb.pack(anchor=tk.W, pady=8)
        
        # Buttons
        btn_frame = tk.Frame(self.window, bg=BG_DARK)
        btn_frame.pack(fill=tk.X, padx=25, pady=20)
        
        StyledButton(btn_frame, text="Close", command=self.window.destroy,
                    width=90, height=34, bg=BG_BUTTON, bg_hover=BG_BUTTON_HOVER,
                    font=("Arial", 10)).pack(side=tk.LEFT)
        
        StyledButton(btn_frame, text="Save", command=self.save,
                    width=90, height=34, bg=BG_PRIMARY, bg_hover=BG_PRIMARY_HOVER,
                    font=("Arial", 10), bold=True).pack(side=tk.RIGHT)
    
    def _create_button_row(self, parent, label, button_name):
        from config import get_macro_button
        
        frame = tk.Frame(parent, bg=BG_CARD)
        frame.pack(fill=tk.X, pady=4)
        
        tk.Label(frame, text=label, font=("Arial", 10), bg=BG_CARD, fg=FG_WHITE).pack(side=tk.LEFT)
        
        pos = get_macro_button(button_name)
        pos_text = f"({pos['x']}, {pos['y']})" if pos else "Not set"
        pos_color = FG_GREEN if pos else FG_DIM
        
        pos_label = tk.Label(frame, text=pos_text, font=("Arial", 9), bg=BG_CARD, fg=pos_color)
        pos_label.pack(side=tk.LEFT, padx=15)
        
        StyledButton(frame, text="Set", command=lambda: self.pick_button(button_name, pos_label),
                    width=50, height=24, bg=BG_BUTTON, bg_hover=BG_BUTTON_HOVER,
                    font=("Arial", 9)).pack(side=tk.RIGHT)
        
        return pos_label
    
    def pick_button(self, button_name, label):
        """Open point picker for a button"""
        self.window.withdraw()
        
        instructions = {
            "forge_button": "Click on the FORGE button",
            "select_all": "Click on the SELECT ALL button",
            "sell_button": "Click on the SELL button"
        }
        
        def on_picked(position):
            self.window.deiconify()
            if position:
                from config import set_macro_button
                set_macro_button(button_name, position)
                label.config(text=f"({position['x']}, {position['y']})", fg=FG_GREEN)
        
        PointPicker(self.parent, on_picked, instructions.get(button_name, "Click on the button"))
    
    def inc_duration(self):
        val = self.duration_var.get()
        if val < 15:
            self.duration_var.set(val + 1)
            self.dur_label.config(text=str(val + 1))
    
    def dec_duration(self):
        val = self.duration_var.get()
        if val > 1:
            self.duration_var.set(val - 1)
            self.dur_label.config(text=str(val - 1))
    
    def save(self):
        from config import set_macro_settings
        
        settings = {
            "enabled": True,
            "hold_duration": self.duration_var.get(),
            "auto_sell": self.autosell_var.get()
        }
        set_macro_settings(settings)
        self.window.destroy()


def start_app():
    """Start the main application after auth and setup"""
    # Import heavy modules only after auth
    global scan_for_ores, calculate_forge, ORES, RARITY_COLORS
    from ocr_scanner import scan_for_ores
    from calculator import calculate_forge
    from data import ORES, RARITY_COLORS
    
    app = ForgerCompanion()
    app.run()


def main():
    """Main entry point with auth check"""
    print("Starting Forger Companion...")
    
    # Check for existing valid license
    print("Checking license...")
    result = check_license()
    
    if result.get("valid"):
        # License valid, start app directly
        info = get_license_info()
        print(f"License active - {info.get('days_left', '?')} days remaining")
        start_app()
    else:
        # Show activation window
        print(f"License check: {result.get('error', 'Not activated')}")
        auth = AuthWindow(on_success=start_app)
        auth.run()


if __name__ == "__main__":
    main()
