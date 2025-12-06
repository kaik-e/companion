"""Forger Companion - Overlay App with EasyOCR"""

import tkinter as tk
from tkinter import ttk
import threading
import time
from ocr_scanner import scan_for_ores
from calculator import calculate_forge
from data import ORES, RARITY_COLORS, calculate_weapon_damage, calculate_masterwork_price, format_price


class ForgerCompanion:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Forger Companion")
        self.root.geometry("340x620")
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
        self.enhancement_level = 0
        self.last_result = None
        
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
        
        # Results frame
        results_container = tk.Frame(self.root, bg="#24283b")
        results_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # === MAIN RESULT SECTION ===
        main_result_frame = tk.Frame(results_container, bg="#1f2335")
        main_result_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Top row: Multiplier | Rarity | Total Ores
        stats_frame = tk.Frame(main_result_frame, bg="#1f2335")
        stats_frame.pack(fill=tk.X, padx=5, pady=3)
        
        # Multiplier
        mult_frame = tk.Frame(stats_frame, bg="#1f2335")
        mult_frame.pack(side=tk.LEFT, expand=True)
        self.multiplier_label = tk.Label(mult_frame, text="--", font=("Segoe UI", 18, "bold"), bg="#1f2335", fg=self.accent_color)
        self.multiplier_label.pack()
        tk.Label(mult_frame, text="Multiplier", font=("Segoe UI", 7), bg="#1f2335", fg=self.dim_color).pack()
        
        # Rarity
        rarity_frame = tk.Frame(stats_frame, bg="#1f2335")
        rarity_frame.pack(side=tk.LEFT, expand=True)
        self.rarity_label = tk.Label(rarity_frame, text="--", font=("Segoe UI", 11, "bold"), bg="#1f2335", fg="#FFFFFF")
        self.rarity_label.pack()
        tk.Label(rarity_frame, text="Rarity", font=("Segoe UI", 7), bg="#1f2335", fg=self.dim_color).pack()
        
        # Total Ores
        ores_count_frame = tk.Frame(stats_frame, bg="#1f2335")
        ores_count_frame.pack(side=tk.LEFT, expand=True)
        self.total_ores_label = tk.Label(ores_count_frame, text="--", font=("Segoe UI", 11, "bold"), bg="#1f2335", fg="#FFD700")
        self.total_ores_label.pack()
        tk.Label(ores_count_frame, text="Total Ores", font=("Segoe UI", 7), bg="#1f2335", fg=self.dim_color).pack()
        
        # === HIGHEST % WEAPON/ARMOR ===
        tk.Frame(main_result_frame, bg=self.dim_color, height=1).pack(fill=tk.X, padx=5, pady=3)
        
        self.best_item_frame = tk.Frame(main_result_frame, bg="#1f2335")
        self.best_item_frame.pack(fill=tk.X, padx=5, pady=3)
        
        self.best_item_label = tk.Label(self.best_item_frame, text="Best: --", font=("Segoe UI", 10, "bold"), bg="#1f2335", fg=self.fg_color)
        self.best_item_label.pack(anchor=tk.W)
        
        self.best_damage_label = tk.Label(self.best_item_frame, text="Damage: --", font=("Segoe UI", 9), bg="#1f2335", fg="#9ece6a")
        self.best_damage_label.pack(anchor=tk.W)
        
        self.best_mw_label = tk.Label(self.best_item_frame, text="MW Price: --", font=("Segoe UI", 9), bg="#1f2335", fg="#FFD700")
        self.best_mw_label.pack(anchor=tk.W)
        
        # === ENHANCEMENT CONTROLS ===
        tk.Frame(main_result_frame, bg=self.dim_color, height=1).pack(fill=tk.X, padx=5, pady=3)
        
        enh_frame = tk.Frame(main_result_frame, bg="#1f2335")
        enh_frame.pack(fill=tk.X, padx=5, pady=3)
        
        tk.Label(enh_frame, text="Enhancement:", font=("Segoe UI", 9), bg="#1f2335", fg=self.fg_color).pack(side=tk.LEFT)
        
        tk.Button(enh_frame, text="-", command=self.decrease_enhancement, bg="#414868", fg=self.fg_color, font=("Segoe UI", 9, "bold"), width=2, relief=tk.FLAT).pack(side=tk.LEFT, padx=2)
        
        self.enh_label = tk.Label(enh_frame, text="+0", font=("Segoe UI", 10, "bold"), bg="#1f2335", fg="#ff9e64", width=3)
        self.enh_label.pack(side=tk.LEFT, padx=2)
        
        tk.Button(enh_frame, text="+", command=self.increase_enhancement, bg="#414868", fg=self.fg_color, font=("Segoe UI", 9, "bold"), width=2, relief=tk.FLAT).pack(side=tk.LEFT, padx=2)
        
        # Enhanced damage display
        self.enh_damage_label = tk.Label(enh_frame, text="", font=("Segoe UI", 9), bg="#1f2335", fg="#9ece6a")
        self.enh_damage_label.pack(side=tk.LEFT, padx=10)
        
        # === ORE COMPOSITION ===
        tk.Frame(results_container, bg=self.dim_color, height=1).pack(fill=tk.X, padx=10, pady=3)
        
        tk.Label(results_container, text="Ore Composition", font=("Segoe UI", 9, "bold"), bg="#24283b", fg=self.fg_color).pack(anchor=tk.W, padx=10)
        
        self.ores_frame = tk.Frame(results_container, bg="#24283b")
        self.ores_frame.pack(fill=tk.X, padx=10, pady=2)
        
        # === ITEM ODDS ===
        tk.Frame(results_container, bg=self.dim_color, height=1).pack(fill=tk.X, padx=10, pady=3)
        
        tk.Label(results_container, text="Item Odds", font=("Segoe UI", 9, "bold"), bg="#24283b", fg=self.fg_color).pack(anchor=tk.W, padx=10)
        
        self.items_frame = tk.Frame(results_container, bg="#24283b")
        self.items_frame.pack(fill=tk.X, padx=10, pady=2)
        
        # === TRAITS ===
        tk.Frame(results_container, bg=self.dim_color, height=1).pack(fill=tk.X, padx=10, pady=3)
        
        tk.Label(results_container, text="Traits", font=("Segoe UI", 9, "bold"), bg="#24283b", fg=self.fg_color).pack(anchor=tk.W, padx=10)
        
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
        self.last_result = result
        
        if result:
            # Update top stats
            self.multiplier_label.config(text=f"{result['multiplier']}x")
            self.rarity_label.config(text=result['rarity'], fg=result['rarity_color'])
            self.total_ores_label.config(text=f"{result['total_ores']}")
            
            # Find best item (highest odds)
            best_item = None
            best_odds = 0
            for item_type, stats in result['item_stats'].items():
                if stats['odds'] > best_odds:
                    best_odds = stats['odds']
                    best_item = item_type
                    best_stats = stats
            
            if best_item:
                self.best_item_label.config(text=f"Best: {best_item} ({int(best_odds * 100)}%)")
                
                # Calculate damage with enhancement
                if self.craft_type == "Weapon" and best_stats.get('damage'):
                    base_dmg = best_stats['damage']
                    enh_mult = 1 + (self.enhancement_level * 0.05)
                    enh_dmg = base_dmg * enh_mult
                    self.best_damage_label.config(text=f"Damage: {enh_dmg:.1f}")
                    self.enh_damage_label.config(text=f"(+{self.enhancement_level}: {enh_dmg:.1f})")
                else:
                    self.best_damage_label.config(text="")
                    self.enh_damage_label.config(text="")
                
                if best_stats.get('mw_price'):
                    self.best_mw_label.config(text=f"MW Price: {format_price(best_stats['mw_price'])}")
                else:
                    self.best_mw_label.config(text="")
            
            # Update ore composition with %
            for widget in self.ores_frame.winfo_children():
                widget.destroy()
            
            for ore_name, pct in result['composition'].items():
                ore_data = ORES.get(ore_name, {})
                color = RARITY_COLORS.get(ore_data.get("rarity"), "#FFFFFF")
                
                ore_row = tk.Frame(self.ores_frame, bg="#24283b")
                ore_row.pack(fill=tk.X, pady=1)
                
                tk.Label(ore_row, text=f"{pct:.1f}%", font=("Segoe UI", 8, "bold"), bg="#24283b", fg=self.accent_color, width=6).pack(side=tk.LEFT)
                tk.Label(ore_row, text=ore_name, font=("Segoe UI", 8), bg="#24283b", fg=color, anchor=tk.W).pack(side=tk.LEFT)
            
            # Update item odds
            for widget in self.items_frame.winfo_children():
                widget.destroy()
            
            for item_type, stats in result['item_stats'].items():
                pct = int(stats['odds'] * 100)
                
                item_row = tk.Frame(self.items_frame, bg="#24283b")
                item_row.pack(fill=tk.X, pady=1)
                
                tk.Label(item_row, text=f"{item_type}", font=("Segoe UI", 8), bg="#24283b", fg=self.fg_color, anchor=tk.W, width=14).pack(side=tk.LEFT)
                tk.Label(item_row, text=f"{pct}%", font=("Segoe UI", 8, "bold"), bg="#24283b", fg=self.accent_color, width=4).pack(side=tk.LEFT)
                
                if stats.get('damage'):
                    tk.Label(item_row, text=f"{stats['damage']:.1f}dmg", font=("Segoe UI", 8), bg="#24283b", fg="#9ece6a", width=7).pack(side=tk.LEFT)
                
                if stats.get('mw_price'):
                    tk.Label(item_row, text=f"MW:{format_price(stats['mw_price'])}", font=("Segoe UI", 8), bg="#24283b", fg="#FFD700", width=8).pack(side=tk.LEFT)
            
            # Update traits
            for widget in self.traits_frame.winfo_children():
                widget.destroy()
            
            for trait in result["traits"]:
                if trait.get("source"):
                    tk.Label(self.traits_frame, text=f"✦ {trait['text']}", font=("Segoe UI", 8), bg="#24283b", fg="#bb9af7", anchor=tk.W, wraplength=300).pack(fill=tk.X)
                    tk.Label(self.traits_frame, text=f"   ({trait['source']})", font=("Segoe UI", 7), bg="#24283b", fg=self.dim_color, anchor=tk.W).pack(fill=tk.X)
                else:
                    tk.Label(self.traits_frame, text=trait['text'], font=("Segoe UI", 8), bg="#24283b", fg=self.dim_color).pack(fill=tk.X)
        else:
            self.multiplier_label.config(text="--")
            self.rarity_label.config(text="--", fg="#FFFFFF")
            self.total_ores_label.config(text="--")
            self.best_item_label.config(text="Best: --")
            self.best_damage_label.config(text="Damage: --")
            self.best_mw_label.config(text="MW Price: --")
            self.enh_damage_label.config(text="")
    
    def toggle_craft_type(self):
        if self.craft_type == "Weapon":
            self.craft_type = "Armor"
            self.craft_btn.config(text="🛡 Armor")
        else:
            self.craft_type = "Weapon"
            self.craft_btn.config(text="⚔ Weapon")
    
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
        if not self.last_result or self.craft_type != "Weapon":
            return
        
        # Find best item
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
            self.best_damage_label.config(text=f"Damage: {enh_dmg:.1f}")
            self.enh_damage_label.config(text=f"(+{self.enhancement_level}: {enh_dmg:.1f})")
    
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
