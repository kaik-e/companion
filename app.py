"""Forger Companion - Overlay App with EasyOCR"""

import tkinter as tk
from tkinter import messagebox
import threading
import time
import sys

# Auth check before heavy imports
from auth import check_license, validate_key, get_license_info


class AuthWindow:
    """License activation window"""
    
    def __init__(self, on_success):
        self.on_success = on_success
        self.root = tk.Tk()
        self.root.title("Forger Companion - Activation")
        self.root.geometry("400x280")
        self.root.resizable(False, False)
        self.root.configure(bg="#0d0d0d")
        
        # Center window
        self.root.eval('tk::PlaceWindow . center')
        
        # Logo/Title
        tk.Label(
            self.root,
            text="⚒ Forger Companion",
            font=("Arial", 18, "bold"),
            bg="#0d0d0d",
            fg="#ffffff"
        ).pack(pady=(30, 5))
        
        tk.Label(
            self.root,
            text="Enter your license key to activate",
            font=("Arial", 10),
            bg="#0d0d0d",
            fg="#9a9a9a"
        ).pack(pady=(0, 20))
        
        # Key entry
        self.key_var = tk.StringVar()
        self.key_entry = tk.Entry(
            self.root,
            textvariable=self.key_var,
            font=("Consolas", 14),
            width=20,
            justify="center",
            bg="#1a1a1a",
            fg="#ffffff",
            insertbackground="#ffffff",
            relief=tk.FLAT,
            highlightthickness=1,
            highlightbackground="#333",
            highlightcolor="#ffdb4a"
        )
        self.key_entry.pack(pady=10, ipady=8)
        self.key_entry.focus()
        
        # Placeholder
        self.key_entry.insert(0, "FORGER-XXXXXX")
        self.key_entry.bind("<FocusIn>", self.clear_placeholder)
        self.key_entry.bind("<Return>", lambda e: self.activate())
        
        # Activate button
        self.activate_btn = tk.Button(
            self.root,
            text="Activate",
            command=self.activate,
            font=("Arial", 11, "bold"),
            bg="#2d5a2d",
            fg="#ffffff",
            relief=tk.FLAT,
            padx=30,
            pady=8,
            cursor="hand2"
        )
        self.activate_btn.pack(pady=15)
        
        # Status label
        self.status_label = tk.Label(
            self.root,
            text="",
            font=("Arial", 9),
            bg="#0d0d0d",
            fg="#ff4444"
        )
        self.status_label.pack(pady=5)
        
        # Footer
        tk.Label(
            self.root,
            text="Get a key from the Forger Discord bot",
            font=("Arial", 8),
            bg="#0d0d0d",
            fg="#666"
        ).pack(side=tk.BOTTOM, pady=10)
    
    def clear_placeholder(self, event):
        if self.key_var.get() == "FORGER-XXXXXX":
            self.key_entry.delete(0, tk.END)
    
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
        self.root.destroy()
        self.on_success()
    
    def run(self):
        self.root.mainloop()


class ForgerCompanion:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Forger Companion")
        self.root.geometry("400x520")
        self.root.attributes("-topmost", True)
        self.root.attributes("-alpha", 0.95)
        self.root.resizable(True, True)
        
        # Dark theme - matching forge result image
        self.bg_color = "#0d0d0d"
        self.fg_color = "#ffffff"
        self.dim_color = "#9a9a9a"
        self.gold_color = "#ffdb4a"
        self.red_color = "#ff4444"
        
        self.root.configure(bg=self.bg_color)
        
        # State
        self.scanning = False
        self.scan_region = None
        self.detected_ores = {}
        self.craft_type = "Weapon"
        self.enhancement_level = 0
        self.last_result = None
        
        self.setup_ui()
        
    def setup_ui(self):
        # Controls bar at top
        controls = tk.Frame(self.root, bg="#1a1a1a")
        controls.pack(fill=tk.X, padx=10, pady=8)
        
        self.scan_btn = tk.Button(controls, text="▶ Scan", command=self.toggle_scan, bg="#2d5a2d", fg="white", font=("Arial", 9, "bold"), relief=tk.FLAT, padx=12, pady=2)
        self.scan_btn.pack(side=tk.LEFT, padx=2)
        
        tk.Button(controls, text="Region", command=self.set_region, bg="#333", fg="#ccc", font=("Arial", 9), relief=tk.FLAT, padx=8, pady=2).pack(side=tk.LEFT, padx=2)
        
        self.craft_btn = tk.Button(controls, text="Weapon", command=self.toggle_craft_type, bg="#333", fg="#ccc", font=("Arial", 9), relief=tk.FLAT, padx=8, pady=2)
        self.craft_btn.pack(side=tk.LEFT, padx=2)
        
        # Enhancement controls
        tk.Button(controls, text="-", command=self.decrease_enhancement, bg="#333", fg="#ccc", font=("Arial", 9, "bold"), width=2, relief=tk.FLAT).pack(side=tk.RIGHT, padx=1)
        self.enh_label = tk.Label(controls, text="+0", font=("Arial", 10, "bold"), bg="#1a1a1a", fg="#ff9e64", width=3)
        self.enh_label.pack(side=tk.RIGHT)
        tk.Button(controls, text="+", command=self.increase_enhancement, bg="#333", fg="#ccc", font=("Arial", 9, "bold"), width=2, relief=tk.FLAT).pack(side=tk.RIGHT, padx=1)
        tk.Label(controls, text="Enh:", font=("Arial", 8), bg="#1a1a1a", fg="#666").pack(side=tk.RIGHT, padx=4)
        
        # Main content area
        self.content = tk.Frame(self.root, bg=self.bg_color)
        self.content.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
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
        
        # Status bar at bottom
        status_frame = tk.Frame(self.root, bg="#1a1a1a")
        status_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=10, pady=5)
        
        self.status_label = tk.Label(status_frame, text="Click Scan to start", font=("Arial", 8), bg="#1a1a1a", fg="#666", anchor=tk.W)
        self.status_label.pack(side=tk.LEFT)
        
        # License info
        info = get_license_info()
        if info.get("active"):
            days = info.get("days_left", 0)
            color = "#4ade80" if days > 7 else "#ffdb4a" if days > 1 else "#ff4444"
            tk.Label(status_frame, text=f"License: {days}d", font=("Arial", 8), bg="#1a1a1a", fg=color).pack(side=tk.RIGHT)
        
        # Debug (hidden by default)
        self.debug_frame = tk.Frame(self.root, bg=self.bg_color)
        self.debug_text = tk.Text(self.debug_frame, height=2, bg="#111", fg="#666", font=("Consolas", 8), wrap=tk.WORD)
        self.debug_text.pack(fill=tk.X, padx=5)
        self.debug_visible = False
        
        # Right-click to toggle debug
        self.root.bind("<Button-3>", lambda e: self.toggle_debug())
        
    def toggle_scan(self):
        self.scanning = not self.scanning
        if self.scanning:
            self.scan_btn.config(text="⏸ Stop", bg="#5a2d2d")
            self.status_label.config(text="Scanning...")
            threading.Thread(target=self.scan_loop, daemon=True).start()
        else:
            self.scan_btn.config(text="▶ Scan", bg="#2d5a2d")
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
        for slot in self.ore_slots:
            slot["name"].config(text="Empty", fg="#444")
            slot["amount"].config(text="")
            slot["frame"].config(highlightbackground="#444")
            slot["pct"].config(text="")
        self.weapon_name_label.config(text="")
        self.weapon_stats_label.config(text="")
        self.weapon_traits_label.config(text="")
        self.armor_name_label.config(text="")
        self.armor_stats_label.config(text="")
        self.armor_traits_label.config(text="")
    
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
    
    def set_region(self):
        """Open region selector"""
        self.scanning = False
        self.scan_btn.config(text="▶ Scan", bg="#2d5a2d")
        
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


def start_app():
    """Start the main application after auth"""
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
        # License valid, start app
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
