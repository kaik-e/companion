"""Forger Companion - Overlay App with EasyOCR"""

import tkinter as tk
from tkinter import ttk
import threading
import time
from ocr_scanner import scan_for_ores
from calculator import calculate_forge
from ores import ORES, RARITY_COLORS


class ForgerCompanion:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Forger Companion")
        self.root.geometry("320x550")
        self.root.attributes("-topmost", True)
        self.root.attributes("-alpha", 0.9)
        
        # Dark theme colors
        self.bg_color = "#1a1b26"
        self.fg_color = "#c0caf5"
        self.accent_color = "#7aa2f7"
        self.dim_color = "#565f89"
        
        self.root.configure(bg=self.bg_color)
        
        # State
        self.scanning = False
        self.scan_region = None
        self.detected_ores = {}
        self.craft_type = "Weapon"
        self.opacity = 0.9
        
        self.setup_ui()
        
    def setup_ui(self):
        # Title bar
        title_frame = tk.Frame(self.root, bg=self.bg_color)
        title_frame.pack(fill=tk.X, padx=5, pady=5)
        
        tk.Label(
            title_frame, 
            text="⚒ Forger Companion", 
            font=("Segoe UI", 11, "bold"),
            bg=self.bg_color, 
            fg=self.fg_color
        ).pack(side=tk.LEFT)
        
        # Controls frame
        controls = tk.Frame(self.root, bg=self.bg_color)
        controls.pack(fill=tk.X, padx=5, pady=2)
        
        # Scan button
        self.scan_btn = tk.Button(
            controls,
            text="▶ Start Scan",
            command=self.toggle_scan,
            bg=self.accent_color,
            fg="white",
            font=("Segoe UI", 9),
            relief=tk.FLAT,
            padx=10
        )
        self.scan_btn.pack(side=tk.LEFT, padx=2)
        
        # Set region button
        tk.Button(
            controls,
            text="📐 Region",
            command=self.set_region,
            bg="#414868",
            fg=self.fg_color,
            font=("Segoe UI", 9),
            relief=tk.FLAT,
            padx=10
        ).pack(side=tk.LEFT, padx=2)
        
        # Craft type toggle
        self.craft_btn = tk.Button(
            controls,
            text="⚔ Weapon",
            command=self.toggle_craft_type,
            bg="#414868",
            fg=self.fg_color,
            font=("Segoe UI", 9),
            relief=tk.FLAT,
            padx=10
        )
        self.craft_btn.pack(side=tk.LEFT, padx=2)
        
        # Opacity slider
        opacity_frame = tk.Frame(self.root, bg=self.bg_color)
        opacity_frame.pack(fill=tk.X, padx=5, pady=2)
        
        tk.Label(
            opacity_frame,
            text="Opacity:",
            bg=self.bg_color,
            fg=self.dim_color,
            font=("Segoe UI", 8)
        ).pack(side=tk.LEFT)
        
        self.opacity_slider = tk.Scale(
            opacity_frame,
            from_=0.3,
            to=1.0,
            resolution=0.05,
            orient=tk.HORIZONTAL,
            command=self.set_opacity,
            bg=self.bg_color,
            fg=self.fg_color,
            highlightthickness=0,
            troughcolor="#414868",
            length=150
        )
        self.opacity_slider.set(0.9)
        self.opacity_slider.pack(side=tk.LEFT, padx=5)
        
        # Status
        self.status_label = tk.Label(
            self.root,
            text="Ready - Click Start Scan",
            bg=self.bg_color,
            fg=self.dim_color,
            font=("Segoe UI", 8)
        )
        self.status_label.pack(fill=tk.X, padx=5)
        
        # Results frame with scrollable canvas
        results_container = tk.Frame(self.root, bg="#24283b")
        results_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Top stats row
        stats_frame = tk.Frame(results_container, bg="#24283b")
        stats_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Multiplier
        mult_frame = tk.Frame(stats_frame, bg="#24283b")
        mult_frame.pack(side=tk.LEFT, expand=True)
        self.multiplier_label = tk.Label(
            mult_frame,
            text="--",
            font=("Segoe UI", 20, "bold"),
            bg="#24283b",
            fg=self.accent_color
        )
        self.multiplier_label.pack()
        tk.Label(mult_frame, text="Multiplier", font=("Segoe UI", 8), bg="#24283b", fg=self.dim_color).pack()
        
        # Rarity
        rarity_frame = tk.Frame(stats_frame, bg="#24283b")
        rarity_frame.pack(side=tk.LEFT, expand=True)
        self.rarity_label = tk.Label(
            rarity_frame,
            text="--",
            font=("Segoe UI", 12, "bold"),
            bg="#24283b",
            fg="#FFFFFF"
        )
        self.rarity_label.pack()
        tk.Label(rarity_frame, text="Rarity", font=("Segoe UI", 8), bg="#24283b", fg=self.dim_color).pack()
        
        # Masterwork
        mw_frame = tk.Frame(stats_frame, bg="#24283b")
        mw_frame.pack(side=tk.LEFT, expand=True)
        self.masterwork_label = tk.Label(
            mw_frame,
            text="--",
            font=("Segoe UI", 12, "bold"),
            bg="#24283b",
            fg="#FFD700"
        )
        self.masterwork_label.pack()
        tk.Label(mw_frame, text="Total Ores", font=("Segoe UI", 8), bg="#24283b", fg=self.dim_color).pack()
        
        # Separator
        tk.Frame(results_container, bg=self.dim_color, height=1).pack(fill=tk.X, padx=10, pady=5)
        
        # Item odds section
        self.items_label = tk.Label(
            results_container,
            text="Possible Items",
            font=("Segoe UI", 9, "bold"),
            bg="#24283b",
            fg=self.fg_color
        )
        self.items_label.pack(anchor=tk.W, padx=10)
        
        self.items_frame = tk.Frame(results_container, bg="#24283b")
        self.items_frame.pack(fill=tk.X, padx=10, pady=2)
        
        # Separator
        tk.Frame(results_container, bg=self.dim_color, height=1).pack(fill=tk.X, padx=10, pady=5)
        
        # Detected ores section
        tk.Label(
            results_container,
            text="Detected Ores",
            font=("Segoe UI", 9, "bold"),
            bg="#24283b",
            fg=self.fg_color
        ).pack(anchor=tk.W, padx=10)
        
        self.ores_frame = tk.Frame(results_container, bg="#24283b")
        self.ores_frame.pack(fill=tk.X, padx=10, pady=2)
        
        # Separator
        tk.Frame(results_container, bg=self.dim_color, height=1).pack(fill=tk.X, padx=10, pady=5)
        
        # Traits section
        self.traits_header = tk.Label(
            results_container,
            text="Traits",
            font=("Segoe UI", 9, "bold"),
            bg="#24283b",
            fg=self.fg_color
        )
        self.traits_header.pack(anchor=tk.W, padx=10)
        
        self.traits_frame = tk.Frame(results_container, bg="#24283b")
        self.traits_frame.pack(fill=tk.X, padx=10, pady=2)
        
        # Debug text
        self.debug_frame = tk.Frame(self.root, bg=self.bg_color)
        self.debug_text = tk.Text(
            self.debug_frame,
            height=3,
            bg="#1f2335",
            fg=self.dim_color,
            font=("Consolas", 8),
            wrap=tk.WORD
        )
        self.debug_text.pack(fill=tk.X, padx=5, pady=2)
        
        # Debug toggle
        self.debug_visible = False
        debug_btn = tk.Button(
            self.root,
            text="Show Debug",
            command=self.toggle_debug,
            bg=self.bg_color,
            fg=self.dim_color,
            font=("Segoe UI", 8),
            relief=tk.FLAT
        )
        debug_btn.pack(pady=2)
        
    def toggle_scan(self):
        self.scanning = not self.scanning
        if self.scanning:
            self.scan_btn.config(text="⏸ Stop", bg="#f7768e")
            self.status_label.config(text="Scanning...")
            threading.Thread(target=self.scan_loop, daemon=True).start()
        else:
            self.scan_btn.config(text="▶ Start Scan", bg=self.accent_color)
            self.status_label.config(text="Stopped")
    
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
        
        # Calculate forge
        result = calculate_forge(detected, self.craft_type)
        
        if result:
            # Update top stats
            self.multiplier_label.config(text=f"{result['multiplier']}x")
            self.rarity_label.config(text=result['rarity'], fg=result['rarity_color'])
            self.masterwork_label.config(text=f"{result['total_ores']}")
            
            # Update item odds with damage and MW price
            for widget in self.items_frame.winfo_children():
                widget.destroy()
            
            for item_type, stats in result['item_stats'].items():
                pct = int(stats['odds'] * 100)
                
                item_row = tk.Frame(self.items_frame, bg="#24283b")
                item_row.pack(fill=tk.X, pady=1)
                
                tk.Label(
                    item_row,
                    text=f"{item_type}",
                    font=("Segoe UI", 8),
                    bg="#24283b",
                    fg=self.fg_color,
                    anchor=tk.W,
                    width=14
                ).pack(side=tk.LEFT)
                
                tk.Label(
                    item_row,
                    text=f"{pct}%",
                    font=("Segoe UI", 8, "bold"),
                    bg="#24283b",
                    fg=self.accent_color,
                    width=4
                ).pack(side=tk.LEFT)
                
                # Damage (weapons only)
                if stats.get('damage'):
                    tk.Label(
                        item_row,
                        text=f"{stats['damage']:.1f}dmg",
                        font=("Segoe UI", 8),
                        bg="#24283b",
                        fg="#9ece6a",
                        width=7
                    ).pack(side=tk.LEFT)
                
                # Masterwork price
                if stats.get('mw_price'):
                    from data import format_price
                    tk.Label(
                        item_row,
                        text=f"MW:{format_price(stats['mw_price'])}",
                        font=("Segoe UI", 8),
                        bg="#24283b",
                        fg="#FFD700",
                        width=8
                    ).pack(side=tk.LEFT)
            
            # Update ores list
            for widget in self.ores_frame.winfo_children():
                widget.destroy()
            
            for ore_id, ore_data in detected.items():
                color = RARITY_COLORS.get(ore_data["rarity"], "#FFFFFF")
                tk.Label(
                    self.ores_frame,
                    text=f"• {ore_data['name']} x{ore_data['count']}",
                    font=("Segoe UI", 8),
                    bg="#24283b",
                    fg=color,
                    anchor=tk.W
                ).pack(fill=tk.X)
            
            # Update traits
            for widget in self.traits_frame.winfo_children():
                widget.destroy()
            
            for trait in result["traits"]:
                if trait.get("source"):
                    tk.Label(
                        self.traits_frame,
                        text=f"✦ {trait['text']}",
                        font=("Segoe UI", 8),
                        bg="#24283b",
                        fg="#bb9af7",
                        anchor=tk.W,
                        wraplength=280
                    ).pack(fill=tk.X)
                    tk.Label(
                        self.traits_frame,
                        text=f"   ({trait['source']})",
                        font=("Segoe UI", 7),
                        bg="#24283b",
                        fg=self.dim_color,
                        anchor=tk.W
                    ).pack(fill=tk.X)
                else:
                    tk.Label(
                        self.traits_frame,
                        text=trait['text'],
                        font=("Segoe UI", 8),
                        bg="#24283b",
                        fg=self.dim_color
                    ).pack(fill=tk.X)
        else:
            self.multiplier_label.config(text="--")
            self.rarity_label.config(text="--", fg="#FFFFFF")
            self.masterwork_label.config(text="--")
    
    def toggle_craft_type(self):
        if self.craft_type == "Weapon":
            self.craft_type = "Armor"
            self.craft_btn.config(text="🛡 Armor")
        else:
            self.craft_type = "Weapon"
            self.craft_btn.config(text="⚔ Weapon")
    
    def set_opacity(self, value):
        self.root.attributes("-alpha", float(value))
    
    def set_region(self):
        """Open region selector"""
        self.scanning = False
        self.scan_btn.config(text="▶ Start Scan", bg=self.accent_color)
        
        selector = RegionSelector(self.root, self.on_region_selected)
        
    def on_region_selected(self, region):
        if region:
            self.scan_region = region
            self.status_label.config(
                text=f"Region: {region['width']}x{region['height']} at ({region['x']}, {region['y']})"
            )
        else:
            self.scan_region = None
            self.status_label.config(text="Using full screen")
    
    def toggle_debug(self):
        self.debug_visible = not self.debug_visible
        if self.debug_visible:
            self.debug_frame.pack(fill=tk.X, before=self.status_label)
        else:
            self.debug_frame.pack_forget()
    
    def run(self):
        self.root.mainloop()


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


if __name__ == "__main__":
    print("Starting Forger Companion...")
    app = ForgerCompanion()
    app.run()
