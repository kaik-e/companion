"""First-time setup wizard for Forger Companion"""

import tkinter as tk
from tkinter import messagebox
from config import save_settings, load_settings, mark_setup_complete


class SetupWizard:
    """Step-by-step setup wizard for first-time users"""
    
    STEPS = [
        {
            "title": "Welcome to Forger Companion!",
            "description": "This quick setup will help you configure the app.\n\nWe'll ask you to select a few screen regions so the app can automatically detect when you're forging.",
            "region": None,
            "icon": "⚒"
        },
        {
            "title": "Step 1: Forge Slots",
            "description": "Open the Forge UI in-game, then click 'Select Region' and drag to select the 4 ORE SLOTS area in the middle.\n\nThis includes the slots where you place ores and the Multiplier display.",
            "region": "forge_slots",
            "icon": "🔲"
        },
        {
            "title": "Setup Complete!",
            "description": "You're all set! The app will now:\n\n• Auto-detect when you open the Forge UI\n• Scan your selected ores automatically\n• Show forge results in real-time\n\nYou can reconfigure regions anytime from Settings (⚙).",
            "region": None,
            "icon": "✓"
        }
    ]
    
    def __init__(self, on_complete):
        self.on_complete = on_complete
        self.current_step = 0
        self.settings = load_settings()
        self.completed = False
        
        self.root = tk.Tk()
        self.root.title("Forger Companion - Setup")
        self.root.geometry("500x380")
        self.root.resizable(False, False)
        self.root.configure(bg="#0d0d0d")
        
        # Center window
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() - 500) // 2
        y = (self.root.winfo_screenheight() - 380) // 2
        self.root.geometry(f"500x380+{x}+{y}")
        
        self.setup_ui()
        self.show_step(0)
        
        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
    
    def setup_ui(self):
        # Header
        self.header_frame = tk.Frame(self.root, bg="#0d0d0d")
        self.header_frame.pack(fill=tk.X, pady=(30, 10))
        
        self.icon_label = tk.Label(
            self.header_frame,
            text="⚒",
            font=("Arial", 48),
            bg="#0d0d0d",
            fg="#ffdb4a"
        )
        self.icon_label.pack()
        
        self.title_label = tk.Label(
            self.header_frame,
            text="",
            font=("Arial", 18, "bold"),
            bg="#0d0d0d",
            fg="#ffffff"
        )
        self.title_label.pack(pady=(10, 0))
        
        # Content
        self.content_frame = tk.Frame(self.root, bg="#0d0d0d")
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=40, pady=20)
        
        self.desc_label = tk.Label(
            self.content_frame,
            text="",
            font=("Arial", 11),
            bg="#0d0d0d",
            fg="#9a9a9a",
            wraplength=420,
            justify=tk.LEFT
        )
        self.desc_label.pack(fill=tk.X)
        
        # Region status
        self.region_status = tk.Label(
            self.content_frame,
            text="",
            font=("Arial", 10, "bold"),
            bg="#0d0d0d",
            fg="#4ade80"
        )
        self.region_status.pack(pady=(20, 0))
        
        # Buttons frame
        self.btn_frame = tk.Frame(self.root, bg="#0d0d0d")
        self.btn_frame.pack(fill=tk.X, padx=40, pady=(0, 30))
        
        self.skip_btn = tk.Button(
            self.btn_frame,
            text="Skip Setup",
            command=self.skip_setup,
            font=("Arial", 10),
            bg="#333",
            fg="#999",
            relief=tk.FLAT,
            padx=15,
            pady=8,
            cursor="hand2"
        )
        self.skip_btn.pack(side=tk.LEFT)
        
        self.next_btn = tk.Button(
            self.btn_frame,
            text="Next →",
            command=self.next_step,
            font=("Arial", 11, "bold"),
            bg="#2d5a2d",
            fg="#ffffff",
            relief=tk.FLAT,
            padx=25,
            pady=8,
            cursor="hand2"
        )
        self.next_btn.pack(side=tk.RIGHT)
        
        self.select_btn = tk.Button(
            self.btn_frame,
            text="Select Region",
            command=self.select_region,
            font=("Arial", 11, "bold"),
            bg="#5a5a2d",
            fg="#ffffff",
            relief=tk.FLAT,
            padx=20,
            pady=8,
            cursor="hand2"
        )
        # Will be shown/hidden per step
        
        # Progress dots
        self.progress_frame = tk.Frame(self.root, bg="#0d0d0d")
        self.progress_frame.pack(pady=(0, 20))
        
        self.dots = []
        for i in range(len(self.STEPS)):
            dot = tk.Label(
                self.progress_frame,
                text="●",
                font=("Arial", 12),
                bg="#0d0d0d",
                fg="#333"
            )
            dot.pack(side=tk.LEFT, padx=3)
            self.dots.append(dot)
    
    def show_step(self, step_idx):
        self.current_step = step_idx
        step = self.STEPS[step_idx]
        
        # Update content
        self.icon_label.config(text=step["icon"])
        self.title_label.config(text=step["title"])
        self.desc_label.config(text=step["description"])
        
        # Update progress dots
        for i, dot in enumerate(self.dots):
            if i < step_idx:
                dot.config(fg="#4ade80")  # Completed
            elif i == step_idx:
                dot.config(fg="#ffdb4a")  # Current
            else:
                dot.config(fg="#333")     # Pending
        
        # Show/hide region button
        if step["region"]:
            self.select_btn.pack(side=tk.RIGHT, padx=(0, 10))
            self.next_btn.config(state=tk.DISABLED, bg="#333")
            
            # Check if region already set
            region = self.settings.get("regions", {}).get(step["region"])
            if region:
                self.region_status.config(
                    text=f"✓ Region set: {region['width']}x{region['height']}",
                    fg="#4ade80"
                )
                self.next_btn.config(state=tk.NORMAL, bg="#2d5a2d")
            else:
                self.region_status.config(text="", fg="#4ade80")
        else:
            self.select_btn.pack_forget()
            self.next_btn.config(state=tk.NORMAL, bg="#2d5a2d")
            self.region_status.config(text="")
        
        # Update button text for last step
        if step_idx == len(self.STEPS) - 1:
            self.next_btn.config(text="Get Started!")
            self.skip_btn.pack_forget()
        else:
            self.next_btn.config(text="Next →")
            self.skip_btn.pack(side=tk.LEFT)
    
    def next_step(self):
        if self.current_step < len(self.STEPS) - 1:
            self.show_step(self.current_step + 1)
        else:
            self.complete()
    
    def select_region(self):
        step = self.STEPS[self.current_step]
        region_name = step["region"]
        
        if not region_name:
            return
        
        # Hide wizard temporarily
        self.root.withdraw()
        
        # Open region selector
        selector = RegionSelector(self.root, lambda r: self.on_region_selected(region_name, r))
    
    def on_region_selected(self, region_name, region):
        # Show wizard again
        self.root.deiconify()
        
        if region:
            # Save region
            if "regions" not in self.settings:
                self.settings["regions"] = {}
            self.settings["regions"][region_name] = region
            save_settings(self.settings)
            
            # Update UI
            self.region_status.config(
                text=f"✓ Region set: {region['width']}x{region['height']}",
                fg="#4ade80"
            )
            self.next_btn.config(state=tk.NORMAL, bg="#2d5a2d")
    
    def skip_setup(self):
        if messagebox.askyesno(
            "Skip Setup?",
            "You can always configure regions later from Settings.\n\nSkip setup for now?"
        ):
            self.complete()
    
    def on_close(self):
        """Handle window close button"""
        if messagebox.askyesno("Exit Setup?", "Exit setup and close the app?"):
            self.root.destroy()
            # Don't call on_complete - just exit
    
    def complete(self):
        self.completed = True
        mark_setup_complete()
        self.root.destroy()
    
    def run(self):
        self.root.mainloop()
        # After mainloop ends, call on_complete if setup was completed
        if self.completed:
            self.on_complete()


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
        
        # Instructions
        self.label = tk.Label(
            self.window,
            text="Click and drag to select region\nPress ESC to cancel",
            font=("Arial", 16),
            bg="black",
            fg="white"
        )
        self.label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        # Canvas for drawing
        self.canvas = tk.Canvas(
            self.window,
            highlightthickness=0,
            bg="black"
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Bindings
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.window.bind("<Escape>", self.on_cancel)
    
    def on_click(self, event):
        self.label.place_forget()
        self.start_x = event.x
        self.start_y = event.y
        self.rect = self.canvas.create_rectangle(
            self.start_x, self.start_y, self.start_x, self.start_y,
            outline="#ffdb4a",
            width=3
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
