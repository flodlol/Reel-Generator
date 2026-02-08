"""
Meme Video Generator - GUI Application

A professional GUI for generating meme videos with customization options.
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog, colorchooser
import os
import sys
import json
import threading
import shutil
import subprocess
import webbrowser
from datetime import datetime
from pathlib import Path

import requests
from packaging import version

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.niche_manager import NicheManager
from src.utils import get_config, init_config, setup_logger


class MemeGeneratorGUI:
    """Main GUI application for Meme Video Generator."""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Meme Video Generator")
        if sys.platform == 'darwin':
            try:
                self.root.tk.call('tk::mac::setAppName', 'Meme Video Generator')
            except Exception:
                pass
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        self.root.geometry(f"{screen_width}x{screen_height}")
        self.root.minsize(1100, 800)
        try:
            self.root.state('zoomed')
        except Exception:
            try:
                self.root.attributes('-zoomed', True)
            except Exception:
                pass
        self.root.resizable(True, True)
        self.apply_theme()
        
        # Set app icon
        try:
            logo_path = os.path.join(Path(__file__).parent.parent, "public", "logo", "1024.png")
            if os.path.exists(logo_path):
                icon = tk.PhotoImage(file=logo_path)
                self.root.iconphoto(True, icon)
        except Exception as e:
            print(f"Could not load icon: {e}")
        
        # Initialize
        try:
            init_config()
            self.niche_manager = NicheManager()
            self.logger = setup_logger('gui', log_file='logs/gui.log')
        except Exception as e:
            messagebox.showerror("Configuration Error", 
                               f"Failed to load configuration:\n{e}\n\nPlease check config/config.yaml")
            sys.exit(1)
        
        self.current_niche = None
        self.processing = False
        self.repo_slug = "flodlol/Reel-Generator"
        
        # Default video settings
        self.video_settings = {
            'font': 'Arial',
            'font_size': 72,
            'font_color': 'text_box_white',
            'fade_duration': 0.5,
            'fade_in_start': True,
            'fade_out_end': True,
            'sound_fade': 0.3,
            'text_position': 'above',
            'bg_color': '#000000',
            'part_enabled': False,
            'part_start_number': 1,
            'part_font': 'Arial',
            'part_font_size': 36,
            'part_color': 'white_outline',
            'part_text_position': 'below'
        }
        
        # Setup UI
        self.setup_ui()
        self.load_niches()
        self.root.after(1500, lambda: self.check_for_updates(show_up_to_date=False))

    def apply_theme(self):
        """Apply a cohesive dark UI theme."""
        colors = {
            "bg": "#1f2023",
            "card": "#2a2c31",
            "panel": "#24262b",
            "border": "#2a2c31",
            "fg": "#e9e9ee",
            "muted": "#b0b3bb",
            "accent": "#f5a623",
            "accent_hover": "#f7b64b",
            "accent_text": "#1a1a1a",
            "button": "#30343b",
            "button_hover": "#3a3f47",
            "outline": "#1f2023",
            "list_bg": "#1b1d21"
        }
        self.ui_colors = colors

        style = ttk.Style(self.root)
        try:
            style.theme_use("clam")
        except Exception:
            pass

        self.root.configure(bg=colors["bg"])

        style.configure("TFrame", background=colors["bg"])
        style.configure("Card.TFrame", background=colors["card"])
        style.configure("TLabel", background=colors["bg"], foreground=colors["fg"])
        style.configure("Title.TLabel", background=colors["bg"], foreground=colors["fg"], font=("Arial", 20, "bold"))
        style.configure("Subtitle.TLabel", background=colors["bg"], foreground=colors["muted"], font=("Arial", 10))
        style.configure("TLabelframe", background=colors["bg"], foreground=colors["fg"], bordercolor=colors["border"], relief="flat")
        style.configure("TLabelframe.Label", background=colors["bg"], foreground=colors["muted"], font=("Arial", 9, "bold"))
        style.configure("TButton", background=colors["button"], foreground=colors["fg"], bordercolor=colors["outline"], padding=(8, 4), borderwidth=0, relief="flat")
        style.map("TButton", background=[("active", colors["button_hover"])], bordercolor=[("active", colors["outline"])], relief=[("active", "flat"), ("pressed", "flat")])
        style.configure("Accent.TButton", background=colors["accent"], foreground=colors["accent_text"], bordercolor=colors["outline"], padding=(8, 4), borderwidth=0, relief="flat")
        style.map("Accent.TButton", background=[("active", colors["accent_hover"])], relief=[("active", "flat"), ("pressed", "flat")])
        style.configure("TEntry", fieldbackground=colors["panel"], foreground=colors["fg"], bordercolor=colors["outline"], padding=4)
        style.configure("TCombobox", fieldbackground=colors["panel"], foreground=colors["fg"], bordercolor=colors["outline"], padding=4, borderwidth=0, relief="flat")
        style.configure("Dark.TCombobox", fieldbackground=colors["panel"], foreground=colors["fg"], bordercolor=colors["outline"], padding=4, borderwidth=0, relief="flat")
        style.configure("TSpinbox", fieldbackground=colors["panel"], foreground=colors["fg"], bordercolor=colors["outline"], padding=4)
        style.configure("Dark.TSpinbox", fieldbackground=colors["panel"], foreground=colors["fg"], bordercolor=colors["outline"], padding=4)
        style.map("TCombobox", fieldbackground=[("readonly", colors["panel"])], foreground=[("readonly", colors["fg"])])
        style.map("TSpinbox", fieldbackground=[("readonly", colors["panel"])], foreground=[("readonly", colors["fg"])])
        style.configure("TSeparator", background=colors["bg"])
        style.configure("Status.TLabel", background=colors["bg"], foreground=colors["muted"])
        style.configure("TProgressbar", background=colors["accent"], troughcolor=colors["card"], bordercolor=colors["border"])

        style.configure(
            "TScrollbar",
            background=colors["card"],
            troughcolor=colors["bg"],
            bordercolor=colors["bg"],
            lightcolor=colors["bg"],
            darkcolor=colors["bg"],
            arrowcolor=colors["muted"],
            relief="flat",
            borderwidth=0
        )
        style.configure(
            "Horizontal.TScrollbar",
            background=colors["card"],
            troughcolor=colors["bg"],
            bordercolor=colors["bg"],
            lightcolor=colors["bg"],
            darkcolor=colors["bg"],
            arrowcolor=colors["muted"],
            relief="flat",
            borderwidth=0
        )
        style.configure(
            "Vertical.TScrollbar",
            background=colors["card"],
            troughcolor=colors["bg"],
            bordercolor=colors["bg"],
            lightcolor=colors["bg"],
            darkcolor=colors["bg"],
            arrowcolor=colors["muted"],
            relief="flat",
            borderwidth=0
        )
        style.map("TScrollbar", background=[("active", colors["button_hover"])])

        self.root.option_add("*TCombobox*Listbox*Background", colors["list_bg"])
        self.root.option_add("*TCombobox*Listbox*Foreground", colors["fg"])
        self.root.option_add("*TCombobox*Listbox*selectBackground", colors["accent"])
        self.root.option_add("*TCombobox*Listbox*selectForeground", colors["accent_text"])
        self.root.option_add("*Listbox*Background", colors["list_bg"])
        self.root.option_add("*Listbox*Foreground", colors["fg"])
        self.root.option_add("*Listbox*selectBackground", colors["accent"])
        self.root.option_add("*Listbox*selectForeground", colors["accent_text"])
        self.root.option_add("*Combobox*highlightThickness", 0)
    
    def setup_ui(self):
        """Setup the user interface."""
        # Menu bar
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New Niche", command=self.create_niche_dialog)
        file_menu.add_separator()
        file_menu.add_command(label="Open Output Folder", command=self.open_output_folder)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Import menu
        import_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Import", menu=import_menu)
        import_menu.add_command(label="Import Quotes", command=self.import_quotes)
        import_menu.add_command(label="Import Images", command=self.import_images)
        import_menu.add_command(label="Import Sounds List", command=self.import_sounds)
        import_menu.add_separator()
        import_menu.add_command(label="Download Sounds", command=self.download_sounds_menu)
        
        # Customize menu
        customize_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Customize", menu=customize_menu)
        customize_menu.add_command(label="Video Settings", command=self.show_video_settings)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="Check for Updates", command=self.check_for_updates)
        help_menu.add_command(label="About", command=self.show_about)
        
        # Header
        header_frame = ttk.Frame(self.root, padding="10")
        header_frame.pack(fill=tk.X)

        header_row = ttk.Frame(header_frame)
        header_row.pack()

        self.logo_image = None
        try:
            logo_path = os.path.join(Path(__file__).parent.parent, "public", "logo", "128.png")
            if os.path.exists(logo_path):
                self.logo_image = tk.PhotoImage(file=logo_path)
                ttk.Label(header_row, image=self.logo_image).pack(side=tk.LEFT, padx=(0, 10))
        except Exception:
            pass

        header_text = ttk.Frame(header_row)
        header_text.pack(side=tk.LEFT)

        title = ttk.Label(header_text, text="Meme Video Generator", style="Title.TLabel")
        title.pack(anchor=tk.W)

        subtitle = ttk.Label(header_text, text="Generate and Upload Meme Videos", style="Subtitle.TLabel")
        subtitle.pack(anchor=tk.W)
        
        # Separator
        ttk.Frame(self.root, height=8).pack(fill=tk.X)
        
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left panel - Niche selection and info
        left_panel = ttk.LabelFrame(main_frame, text="Niche Selection", padding="10")
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, 5))
        
        # Niche dropdown
        ttk.Label(left_panel, text="Select Niche:").pack(anchor=tk.W, pady=(0, 5))
        self.niche_var = tk.StringVar()
        self.niche_dropdown = ttk.Combobox(left_panel, textvariable=self.niche_var,
                          state='readonly', width=25)
        self.niche_dropdown.configure(style="Dark.TCombobox")
        self.niche_dropdown.configure(takefocus=False)
        self.niche_dropdown.pack(fill=tk.X, pady=(0, 10))
        self.niche_dropdown.bind('<<ComboboxSelected>>', self.on_niche_selected)
        
        # Niche info
        info_frame = ttk.LabelFrame(left_panel, text="Niche Info", padding="10")
        info_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        self.info_text = scrolledtext.ScrolledText(info_frame, height=15, width=30,
                                                   wrap=tk.WORD, state='disabled')
        self.info_text.config(
            bg=self.ui_colors["panel"],
            fg=self.ui_colors["fg"],
            insertbackground=self.ui_colors["fg"],
            highlightthickness=0,
            bd=0
        )
        self.info_text.pack(fill=tk.BOTH, expand=True)
        try:
            self.info_text.vbar.configure(
                bg=self.ui_colors["bg"],
                troughcolor=self.ui_colors["bg"],
                activebackground=self.ui_colors["button_hover"],
                highlightthickness=0,
                bd=0,
                borderwidth=0
            )
        except Exception:
            pass
        
        # Right panel - Actions
        right_panel = ttk.Frame(main_frame)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # Action buttons
        actions_frame = ttk.LabelFrame(right_panel, text="Actions", padding="10")
        actions_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Actions row
        actions_row = ttk.Frame(actions_frame)
        actions_row.pack(fill=tk.X, pady=5)

        left_actions = ttk.Frame(actions_row)
        left_actions.pack(side=tk.LEFT, fill=tk.X, expand=True)

        ttk.Label(left_actions, text="Generate Videos:").pack(side=tk.LEFT)
        self.gen_count = tk.IntVar(value=1)
        count_spin = ttk.Spinbox(left_actions, from_=1, to=20, textvariable=self.gen_count,
                    width=10)
        count_spin.configure(style="Dark.TSpinbox")
        count_spin.pack(side=tk.LEFT, padx=10)

        self.gen_btn = ttk.Button(left_actions, text="🎨 Generate Videos",
                     command=self.generate_memes, width=20, style="Accent.TButton")
        self.gen_btn.pack(side=tk.LEFT)

        right_actions = ttk.Frame(actions_row)
        right_actions.pack(side=tk.RIGHT)

        self.customize_btn = ttk.Button(right_actions, text="⚙️ Video Settings",
                           command=self.show_video_settings, width=20)
        self.customize_btn.pack(side=tk.LEFT, padx=(0, 8))

        self.folder_btn = ttk.Button(right_actions, text="📁 Open Output Folder",
                        command=self.open_output_folder, width=20)
        self.folder_btn.pack(side=tk.LEFT)
        
        # Log output
        log_frame = ttk.LabelFrame(right_panel, text="Activity Log", padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, wrap=tk.WORD)
        self.log_text.config(
            bg=self.ui_colors["panel"],
            fg=self.ui_colors["fg"],
            insertbackground=self.ui_colors["fg"],
            highlightthickness=0,
            bd=0
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)
        try:
            self.log_text.vbar.configure(
                bg=self.ui_colors["bg"],
                troughcolor=self.ui_colors["bg"],
                activebackground=self.ui_colors["button_hover"],
                highlightthickness=0,
                bd=0,
                borderwidth=0
            )
        except Exception:
            pass
        
        # Output preview
        preview_frame = ttk.LabelFrame(right_panel, text="Output Folder Preview", padding="10")
        preview_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))

        self.preview_canvas = tk.Canvas(preview_frame, highlightthickness=0, bg=self.ui_colors["card"], bd=0)
        self.preview_scrollbar = ttk.Scrollbar(preview_frame, orient="horizontal", command=self.preview_canvas.xview, style="Horizontal.TScrollbar")
        self.preview_canvas.configure(xscrollcommand=self.preview_scrollbar.set)

        self.preview_canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.preview_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

        self.preview_content = ttk.Frame(self.preview_canvas)
        self.preview_window = self.preview_canvas.create_window((0, 0), window=self.preview_content, anchor="nw")

        def update_preview_scroll(_event=None):
            self.preview_canvas.configure(scrollregion=self.preview_canvas.bbox("all"))

        self.preview_content.bind("<Configure>", update_preview_scroll)
        self.preview_thumbnails = []
        
        # Status bar
        status_frame = ttk.Frame(self.root)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.status_var = tk.StringVar(value="Ready")
        status_label = ttk.Label(status_frame, textvariable=self.status_var,
                    relief=tk.SUNKEN, anchor=tk.W, style="Status.TLabel")
        status_label.pack(fill=tk.X, padx=5, pady=2)
        
        # Progress bar
        self.progress = ttk.Progressbar(status_frame, mode='determinate', maximum=100)
        self.progress.pack(fill=tk.X, padx=5, pady=2)
    
    def load_niches(self):
        """Load available niches."""
        niches = self.niche_manager.list_niches()
        
        if not niches:
            self.log("⚠️  No niches found. Please create a niche first.")
            self.niche_dropdown['values'] = []
            return
        
        # Clean up niche names for display
        display_niches = []
        for niche in niches:
            display_name = niche[1:] if niche.startswith('!') else niche
            display_niches.append(display_name)
        
        self.niche_dropdown['values'] = display_niches
        
        # Select first niche by default
        if display_niches:
            self.niche_dropdown.current(0)
            self.on_niche_selected(None)
    
    def on_niche_selected(self, event):
        """Handle niche selection."""
        selected = self.niche_var.get()
        if not selected:
            return
        
        # Find actual niche path
        niches = self.niche_manager.list_niches()
        for niche in niches:
            display_name = niche[1:] if niche.startswith('!') else niche
            if display_name == selected:
                self.current_niche = os.path.join(self.niche_manager.niches_base_path, niche)
                break
        
        self.update_niche_info()
        self.update_output_preview()
        self.log(f"📁 Selected niche: {selected}")
    
    def update_niche_info(self):
        """Update niche information display."""
        if not self.current_niche:
            return
        
        self.info_text.config(state='normal')
        self.info_text.delete(1.0, tk.END)
        
        try:
            # Get niche info
            niche_name = os.path.basename(self.current_niche)
            if niche_name.startswith('!'):
                niche_name = niche_name[1:]
            
            # Get video counts
            final_videos_path = os.path.join(self.current_niche, 'Meme-Final')
            if os.path.exists(final_videos_path):
                videos = [f for f in os.listdir(final_videos_path) 
                         if f.endswith('.mp4')]
                total_videos = len(videos)
            else:
                total_videos = 0
            
            # Get content stats
            quotes_file = os.path.join(self.current_niche, 'Quotes.txt')
            images_folder = os.path.join(self.current_niche, 'Raw-Images')
            audio_folder = os.path.join(self.current_niche, 'TikTok-Sounds')
            
            quotes_count = 0
            if os.path.exists(quotes_file):
                with open(quotes_file, 'r') as f:
                    quotes_count = len([l for l in f if l.strip() and not l.startswith('#')])
            
            images_count = 0
            if os.path.exists(images_folder):
                images_count = len([f for f in os.listdir(images_folder) 
                                  if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp'))])
            
            audio_count = 0
            if os.path.exists(audio_folder):
                audio_count = len([f for f in os.listdir(audio_folder) 
                                 if f.lower().endswith('.mp3')])
            
            # Format info
            info = f"Niche: {niche_name}\n\n"
            info += f"📊 Content:\n"
            info += f"  Quotes: {quotes_count}\n"
            info += f"  Images: {images_count}\n"
            info += f"  Audio: {audio_count}\n\n"
            info += f"🎬 Videos Generated: {total_videos}\n"
            
            self.info_text.insert(1.0, info)
        except Exception as e:
            self.info_text.insert(1.0, f"Error loading info:\n{e}")
        finally:
            self.info_text.config(state='disabled')
    
    def _format_time(self, time_str):
        """Format datetime string."""
        if time_str == 'N/A' or not time_str:
            return 'N/A'
        try:
            dt = datetime.fromisoformat(time_str)
            return dt.strftime('%H:%M %d %b %Y')
        except:
            return time_str
    
    def log(self, message):
        """Add message to log."""
        timestamp = datetime.now().strftime('%H:%M:%S')
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.logger.info(message)
    
    def set_status(self, message, processing=False, progress=0):
        """Update status bar."""
        self.status_var.set(message)
        self.processing = processing
        
        if processing:
            self.progress['value'] = progress
            self.disable_buttons()
        else:
            self.progress['value'] = 0
            self.enable_buttons()
    
    def disable_buttons(self):
        """Disable action buttons."""
        self.gen_btn.config(state='disabled')
        self.customize_btn.config(state='disabled')
        self.folder_btn.config(state='disabled')
    
    def enable_buttons(self):
        """Enable action buttons."""
        self.gen_btn.config(state='normal')
        self.customize_btn.config(state='normal')
        self.folder_btn.config(state='normal')
    
    def generate_memes(self):
        """Generate memes."""
        if not self.current_niche:
            messagebox.showwarning("No Niche", "Please select a niche first.")
            return
        
        count = self.gen_count.get()
        self.log(f"🎨 Starting generation of {count} meme(s)...")
        self.set_status(f"Generating {count} meme(s)...", processing=True)
        
        # Run in thread to not block UI
        thread = threading.Thread(target=self._generate_thread, args=(count,))
        thread.daemon = True
        thread.start()
    
    def _generate_thread(self, count):
        """Thread for generation - runs in background to avoid UI blocking."""
        error_occurred = False
        error_str = ""
        success_count = 0
        try:
            # Import generator
            sys.path.insert(0, str(Path(__file__).parent.parent))
            from src.core import generator_engine
            
            # Set the base path for generator
            generator_engine.BASE_PATH = self.current_niche
            
            # Apply video settings to generator
            # TODO: Pass video_settings to generator_engine
            
            # Run generation
            for i in range(count):
                if not self.processing:
                    self.root.after(0, lambda: self.log("⚠️  Generation cancelled by user"))
                    break
                
                # Update progress
                progress_percent = int((i / count) * 100)
                self.root.after(0, lambda p=progress_percent, idx=i: 
                               self.set_status(f"Generating video {idx+1}/{count}...", processing=True, progress=p))
                self.root.after(0, lambda idx=i: self.log(f"🎨 Generating video {idx+1}/{count}..."))
                
                try:
                    # Pass auto_count=1 to generate 1 video at a time without prompting
                    generator_engine.main(self.current_niche, auto_count=1)
                    success_count += 1
                    self.root.after(0, lambda idx=i: self.log(f"✅ Video {idx+1}/{count} generated successfully"))
                except Exception as e:
                    self.root.after(0, lambda idx=i, err=str(e): self.log(f"⚠️  Error on video {idx+1}: {err}"))
            
            # Set progress to 100% when done
            if success_count > 0:
                self.root.after(0, lambda: self.set_status("Generation complete!", processing=True, progress=100))
                self.root.after(0, lambda: self.log(f"✅ Generation completed! Created {success_count}/{count} videos"))
        except Exception as e:
            import traceback
            error_msg = traceback.format_exc()
            error_str = str(e)
            error_occurred = True
            self.log(f"❌ Error generating videos: {error_str}")
            self.logger.error(error_msg)
        finally:
            # Schedule UI update on main thread (critical for thread safety)
            def final_update():
                try:
                    self.set_status("Ready", processing=False)
                    self.update_niche_info()
                    self.update_output_preview()
                    
                    if error_occurred:
                        messagebox.showerror("Error", f"Failed to generate videos:\n{error_str}")
                    elif success_count > 0:
                        messagebox.showinfo("Success", f"Generated {success_count}/{count} video(s)! Check the output folder.")
                    elif success_count == 0:
                        messagebox.showwarning("Warning", "No videos were generated.")
                except Exception as e:
                    print(f"Error in final_update: {e}")
            
            self.root.after(0, final_update)
    
    def update_output_preview(self):
        """Update the output folder preview."""
        if not self.current_niche:
            return

        for child in self.preview_content.winfo_children():
            child.destroy()
        self.preview_thumbnails = []

        try:
            output_folder = os.path.join(self.current_niche, "Meme-Final")
            if not os.path.exists(output_folder):
                ttk.Label(
                    self.preview_content,
                    text="No videos generated yet.\n\nClick 'Generate Videos' to create your first video!",
                    background=self.ui_colors["card"],
                    foreground=self.ui_colors["fg"]
                ).pack(anchor=tk.W)
                return
            
            files = [f for f in os.listdir(output_folder) if f.endswith('.mp4')]
            files.sort(reverse=True)  # Most recent first
            
            if not files:
                ttk.Label(
                    self.preview_content,
                    text="No videos in output folder.",
                    background=self.ui_colors["card"],
                    foreground=self.ui_colors["fg"]
                ).pack(anchor=tk.W)
            else:
                header = ttk.Label(
                    self.preview_content,
                    text=f"Output: Meme-Final/   Total: {len(files)}",
                    font=("Arial", 10, "bold")
                )
                header.pack(anchor=tk.W, pady=(0, 8))

                meme_images_folder = os.path.join(self.current_niche, "Meme-Images")
                try:
                    from PIL import Image, ImageTk, ImageOps
                except Exception as e:
                    ttk.Label(self.preview_content, text=f"Preview unavailable: {e}").pack(anchor=tk.W)
                    return

                strip_frame = ttk.Frame(self.preview_content)
                strip_frame.pack(fill=tk.BOTH, expand=True)

                thumb_width = 160
                thumb_height = 284

                for idx, file in enumerate(files):
                    file_path = os.path.join(output_folder, file)
                    size_mb = os.path.getsize(file_path) / (1024 * 1024)
                    mod_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                    base_name = os.path.splitext(file)[0]
                    image_path = os.path.join(meme_images_folder, f"{base_name}.jpg")

                    cell = ttk.Frame(strip_frame)
                    cell.grid(row=0, column=idx, padx=8, pady=6, sticky="n")

                    image_widget = None
                    image = None

                    if os.path.exists(image_path):
                        try:
                            image = Image.open(image_path)
                        except Exception:
                            image = None
                    else:
                        try:
                            from moviepy import VideoFileClip
                            clip = VideoFileClip(file_path)
                            frame = clip.get_frame(0.0)
                            clip.close()
                            image = Image.fromarray(frame)
                        except Exception:
                            image = None

                    if image:
                        image = ImageOps.pad(image, (thumb_width, thumb_height), color="black")
                        photo = ImageTk.PhotoImage(image)
                        image_widget = ttk.Label(cell, image=photo)
                        self.preview_thumbnails.append(photo)
                    else:
                        canvas = tk.Canvas(cell, width=thumb_width, height=thumb_height, bg="#222", highlightthickness=1, highlightbackground="#444")
                        canvas.create_text(thumb_width // 2, thumb_height // 2, text="No preview", fill="white")
                        image_widget = canvas

                    def open_in_finder(_event, path=file_path):
                        if sys.platform == 'darwin':
                            subprocess.run(['open', '-R', path])
                        elif sys.platform == 'win32':
                            os.startfile(os.path.dirname(path))
                        else:
                            subprocess.run(['xdg-open', os.path.dirname(path)])

                    image_widget.bind("<Double-Button-1>", open_in_finder)
                    image_widget.pack()

                    caption = ttk.Label(
                        cell,
                        text=f"{file}\n{size_mb:.1f} MB | {mod_time.strftime('%H:%M %d/%m')}",
                        justify="center"
                    )
                    caption.pack(pady=(4, 0))
        except Exception as e:
            ttk.Label(self.preview_content, text=f"Error loading preview:\n{e}").pack(anchor=tk.W)

        self.preview_canvas.xview_moveto(0)
    
    def open_output_folder(self):
        """Open the output folder in file explorer."""
        if not self.current_niche:
            messagebox.showwarning("No Niche", "Please select a niche first.")
            return
        
        output_folder = os.path.join(self.current_niche, "Meme-Final")
        if not os.path.exists(output_folder):
            messagebox.showinfo("No Output", "No output folder yet. Generate some videos first!")
            return
        
        # Open folder in system file explorer
        if sys.platform == 'darwin':  # macOS
            subprocess.run(['open', output_folder])
        elif sys.platform == 'win32':  # Windows
            os.startfile(output_folder)
        else:  # Linux
            subprocess.run(['xdg-open', output_folder])
        
        self.log(f"📁 Opened output folder")
    
    def show_video_settings(self):
        """Show video customization settings."""
        dialog = tk.Toplevel(self.root)
        dialog.title("Video Settings")
        dialog.geometry("1200x820")
        dialog.minsize(1200, 820)
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Main container with two panels
        main_container = ttk.Frame(dialog)
        main_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Left panel - All Settings
        left_panel = ttk.Frame(main_container)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=(0, 15))
        
        # Font Settings
        font_frame = ttk.LabelFrame(left_panel, text="Font Settings", padding=15)
        font_frame.pack(fill=tk.X, pady=(0, 10))

        color_options = {
            "White box (black text)": "text_box_white",
            "Black box (white text)": "text_box_black",
            "White text with outside black outline": "white_outline"
        }
        
        ttk.Label(font_frame, text="Font Family:").grid(row=0, column=0, sticky=tk.W, pady=5)
        font_var = tk.StringVar(value=self.video_settings['font'])
        font_combo = ttk.Combobox(font_frame, textvariable=font_var, width=25,
                                   values=['Arial', 'Impact', 'Comic Sans MS', 'Times New Roman', 'Courier New', 'Helvetica'])
        font_combo.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        
        ttk.Label(font_frame, text="Font Size:").grid(row=1, column=0, sticky=tk.W, pady=5)
        size_var = tk.IntVar(value=self.video_settings['font_size'])
        ttk.Spinbox(font_frame, from_=20, to=200, textvariable=size_var, width=10).grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(font_frame, text="Font Color:").grid(row=2, column=0, sticky=tk.W, pady=5)
        font_color_value = self.video_settings.get('font_color', 'text_box_white')
        font_color_label = next(
            (label for label, value in color_options.items() if value == font_color_value),
            "White box (black text)"
        )
        color_var = tk.StringVar(value=font_color_label)
        ttk.Combobox(font_frame, textvariable=color_var, width=25,
                    values=list(color_options.keys()), state='readonly').grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(font_frame, text="Text Position:").grid(row=3, column=0, sticky=tk.W, pady=5)
        pos_var = tk.StringVar(value=self.video_settings.get('text_position', 'above'))
        ttk.Combobox(font_frame, textvariable=pos_var, width=15,
                    values=['above', 'below'], state='readonly').grid(row=3, column=1, sticky=tk.W, padx=5, pady=5)

        # Part Number Settings
        part_frame = ttk.LabelFrame(left_panel, text="Part Number", padding=15)
        part_frame.pack(fill=tk.X, pady=(0, 10))

        part_enabled_var = tk.BooleanVar(value=self.video_settings.get('part_enabled', False))
        ttk.Checkbutton(part_frame, text="Enable part number",
                       variable=part_enabled_var).grid(row=0, column=0, columnspan=3, sticky=tk.W, pady=5)

        ttk.Label(part_frame, text="Start Number:").grid(row=1, column=0, sticky=tk.W, pady=5)
        part_start_var = tk.IntVar(value=self.video_settings.get('part_start_number', 1))
        ttk.Spinbox(part_frame, from_=1, to=9999, textvariable=part_start_var, width=10).grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)

        ttk.Label(part_frame, text="Font Family:").grid(row=2, column=0, sticky=tk.W, pady=5)
        part_font_var = tk.StringVar(value=self.video_settings.get('part_font', self.video_settings['font']))
        ttk.Combobox(part_frame, textvariable=part_font_var, width=25,
                    values=['Arial', 'Impact', 'Comic Sans MS', 'Times New Roman', 'Courier New', 'Helvetica']).grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)

        ttk.Label(part_frame, text="Font Size:").grid(row=3, column=0, sticky=tk.W, pady=5)
        part_size_var = tk.IntVar(value=self.video_settings.get('part_font_size', 36))
        ttk.Spinbox(part_frame, from_=12, to=120, textvariable=part_size_var, width=10).grid(row=3, column=1, sticky=tk.W, padx=5, pady=5)

        ttk.Label(part_frame, text="Font Color:").grid(row=4, column=0, sticky=tk.W, pady=5)
        part_color_value = self.video_settings.get('part_color', 'white_outline')
        part_color_label = next(
            (label for label, value in color_options.items() if value == part_color_value),
            "White text with outside black outline"
        )
        part_color_var = tk.StringVar(value=part_color_label)
        ttk.Combobox(part_frame, textvariable=part_color_var, width=25,
                    values=list(color_options.keys()), state='readonly').grid(row=4, column=1, sticky=tk.W, padx=5, pady=5)

        ttk.Label(part_frame, text="Text Position:").grid(row=5, column=0, sticky=tk.W, pady=5)
        part_pos_var = tk.StringVar(value=self.video_settings.get('part_text_position', 'below'))
        ttk.Combobox(part_frame, textvariable=part_pos_var, width=15,
                    values=['above', 'below'], state='readonly').grid(row=5, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Fade Settings
        fade_frame = ttk.LabelFrame(left_panel, text="Fade & Transition Settings", padding=15)
        fade_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(fade_frame, text="Fade Duration (sec):").grid(row=0, column=0, sticky=tk.W, pady=5)
        fade_dur_var = tk.DoubleVar(value=self.video_settings['fade_duration'])
        ttk.Spinbox(fade_frame, from_=0.1, to=5.0, increment=0.1, 
                   textvariable=fade_dur_var, width=10).grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        fade_in_var = tk.BooleanVar(value=self.video_settings['fade_in_start'])
        ttk.Checkbutton(fade_frame, text="Fade in at start", 
                       variable=fade_in_var).grid(row=1, column=0, columnspan=3, sticky=tk.W, pady=5)
        
        fade_out_var = tk.BooleanVar(value=self.video_settings['fade_out_end'])
        ttk.Checkbutton(fade_frame, text="Fade out at end", 
                       variable=fade_out_var).grid(row=2, column=0, columnspan=3, sticky=tk.W, pady=5)
        
        ttk.Label(fade_frame, text="Sound Fade (sec):").grid(row=3, column=0, sticky=tk.W, pady=5)
        sound_fade_var = tk.DoubleVar(value=self.video_settings['sound_fade'])
        ttk.Spinbox(fade_frame, from_=0.0, to=5.0, increment=0.1,
                   textvariable=sound_fade_var, width=10).grid(row=3, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Background Settings
        bg_settings_frame = ttk.LabelFrame(left_panel, text="Background", padding=15)
        bg_settings_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(bg_settings_frame, text="Background Color:").grid(row=0, column=0, sticky=tk.W, pady=5)
        bg_color_var = tk.StringVar(value=self.video_settings['bg_color'])
        bg_color_entry = ttk.Entry(bg_settings_frame, textvariable=bg_color_var, width=12)
        bg_color_entry.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        def choose_bg_color():
            color = colorchooser.askcolor(color=bg_color_var.get())[1]
            if color:
                bg_color_var.set(color)
        
        ttk.Button(bg_settings_frame, text="Choose", command=choose_bg_color).grid(row=0, column=2, padx=5)
        
        # Right panel - Live Preview
        preview_panel = ttk.LabelFrame(main_container, text="Live Preview (9:16 Portrait)", padding=15)
        preview_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Preview canvas (9:16 aspect ratio - matches actual meme generation 1080x1920)
        # Scaled to 360x640 so the full settings panel stays visible
        preview_canvas = tk.Canvas(preview_panel, width=360, height=640, bg='black', highlightthickness=1, highlightbackground='#555')
        preview_canvas.pack(pady=(0, 10))
        
        # Preview info
        preview_info_label = ttk.Label(preview_panel, text="Preview matches actual meme layout", 
                                       font=("Arial", 9, "italic"), foreground='#666')
        preview_info_label.pack()
        
        # Get sample image for realistic preview
        sample_image_pil = None
        if self.current_niche:
            images_folder = os.path.join(self.current_niche, 'Raw-Images')
            if os.path.exists(images_folder):
                images = [f for f in os.listdir(images_folder) 
                         if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
                if images:
                    try:
                        from PIL import Image, ImageTk, ImageDraw, ImageFont
                        img_path = os.path.join(images_folder, images[0])
                        img = Image.open(img_path)
                        # Don't resize yet - we'll do it in the preview function
                        sample_image_pil = img
                    except Exception as e:
                        print(f"Error loading sample image: {e}")
        
        def update_preview(*args):
            """Update preview to EXACTLY match generator: white text box + image on black background."""
            preview_canvas.delete("all")
            
            # Portrait canvas: 360x640 (9:16 ratio, scaled from 1080x1920)
            canvas_width = 360
            canvas_height = 640
            scale_factor = canvas_width / 1080
            
            if sample_image_pil:
                try:
                    from PIL import Image, ImageTk, ImageDraw, ImageFont
                    
                    # Create background (matching user setting)
                    bg_color_value = bg_color_var.get()
                    try:
                        bg = Image.new('RGB', (canvas_width, canvas_height), bg_color_value)
                    except ValueError:
                        bg_color_value = 'black'
                        bg = Image.new('RGB', (canvas_width, canvas_height), bg_color_value)
                    
                    # Resize image to fit (matching generator: leave ~112px for text/spacing)
                    img = sample_image_pil.copy()
                    img.thumbnail((canvas_width, canvas_height - 112), Image.Resampling.LANCZOS)
                    
                    # Create main text and font
                    text = "Sample Meme Text"
                    font_size = max(22, int(size_var.get() * scale_factor))
                    
                    # Load font
                    try:
                        font_name = font_var.get()
                        font_paths = [
                            f"/System/Library/Fonts/{font_name}.ttc",
                            f"/System/Library/Fonts/{font_name}.ttf",
                            f"/System/Library/Fonts/Supplemental/{font_name}.ttf",
                        ]
                        font = None
                        for path in font_paths:
                            if os.path.exists(path):
                                font = ImageFont.truetype(path, font_size)
                                break
                        if not font:
                            font = ImageFont.load_default()
                    except:
                        font = ImageFont.load_default()
                    
                    # Calculate text box dimensions
                    temp_draw = ImageDraw.Draw(Image.new('RGB', (1, 1)))
                    bbox = temp_draw.textbbox((0, 0), text, font=font)
                    text_width = bbox[2] - bbox[0]
                    text_height = bbox[3] - bbox[1]

                    box_padding = max(8, int(30 * scale_factor))
                    box_height = text_height + 2 * box_padding
                    text_box_width = img.width

                    font_color_style = color_options.get(color_var.get(), 'text_box_white')
                    stroke_width = max(1, int(2 * scale_factor))
                    
                    part_enabled = part_enabled_var.get()
                    part_text = f"part {part_start_var.get()}" if part_enabled else ""
                    part_font_size = max(14, int(part_size_var.get() * scale_factor))

                    try:
                        part_font_name = part_font_var.get()
                        part_font = None
                        for path in [
                            f"/System/Library/Fonts/{part_font_name}.ttc",
                            f"/System/Library/Fonts/{part_font_name}.ttf",
                            f"/System/Library/Fonts/Supplemental/{part_font_name}.ttf",
                        ]:
                            if os.path.exists(path):
                                part_font = ImageFont.truetype(path, part_font_size)
                                break
                        if not part_font:
                            part_font = ImageFont.load_default()
                    except Exception:
                        part_font = ImageFont.load_default()

                    part_color_style = color_options.get(part_color_var.get(), 'white_outline')
                    part_padding = max(6, int(20 * scale_factor))

                    if part_enabled:
                        part_bbox = temp_draw.textbbox((0, 0), part_text, font=part_font)
                        part_text_width = part_bbox[2] - part_bbox[0]
                        part_text_height = part_bbox[3] - part_bbox[1]
                        part_block_height = part_text_height + 2 * part_padding
                    else:
                        part_text_width = 0
                        part_text_height = 0
                        part_block_height = 0

                    blocks_above = []
                    blocks_below = []
                    if pos_var.get() == 'above':
                        blocks_above.append('main')
                    else:
                        blocks_below.append('main')

                    if part_enabled:
                        if part_pos_var.get() == 'above':
                            blocks_above.append('part')
                        else:
                            blocks_below.append('part')

                    total_content_height = box_height + img.height + part_block_height
                    vertical_center = (canvas_height - total_content_height) // 2
                    current_y = vertical_center

                    def draw_main_text(y_pos):
                        text_box_x = (canvas_width - text_box_width) // 2
                        text_x = text_box_x + (text_box_width - text_width) // 2
                        text_y = y_pos + box_padding

                        if font_color_style == 'white_outline':
                            draw = ImageDraw.Draw(bg)
                            draw.text(
                                (text_x, text_y),
                                text,
                                font=font,
                                fill='white',
                                stroke_width=stroke_width,
                                stroke_fill='black'
                            )
                            return

                        text_box_color = 'white' if font_color_style == 'text_box_white' else 'black'
                        text_color = 'black' if text_box_color == 'white' else 'white'
                        text_box = Image.new('RGB', (text_box_width, box_height), text_box_color)
                        text_draw = ImageDraw.Draw(text_box)
                        text_draw.text((text_x - text_box_x, text_y - y_pos), text, font=font, fill=text_color)
                        bg.paste(text_box, (text_box_x, y_pos))

                    def draw_part_text(y_pos):
                        if not part_enabled:
                            return
                        draw = ImageDraw.Draw(bg)
                        text_x = (canvas_width - part_text_width) // 2
                        text_y = y_pos + part_padding

                        if part_color_style == 'white_outline':
                            draw.text(
                                (text_x, text_y),
                                part_text,
                                font=part_font,
                                fill='white',
                                stroke_width=stroke_width,
                                stroke_fill='black'
                            )
                            return

                        part_box_color = 'white' if part_color_style == 'text_box_white' else 'black'
                        part_text_color = 'black' if part_box_color == 'white' else 'white'
                        part_box_width = part_text_width + 2 * part_padding
                        part_box_height = part_text_height + 2 * part_padding
                        part_box = Image.new('RGB', (part_box_width, part_box_height), part_box_color)
                        part_box_draw = ImageDraw.Draw(part_box)
                        part_box_draw.text((part_padding, part_padding), part_text, font=part_font, fill=part_text_color)
                        bg.paste(part_box, (text_x - part_padding, y_pos))

                    for block in blocks_above:
                        if block == 'main':
                            draw_main_text(current_y)
                            current_y += box_height
                        elif block == 'part':
                            draw_part_text(current_y)
                            current_y += part_block_height

                    img_x = (canvas_width - img.width) // 2
                    img_y = current_y
                    bg.paste(img, (img_x, img_y))
                    current_y += img.height

                    for block in blocks_below:
                        if block == 'main':
                            draw_main_text(current_y)
                            current_y += box_height
                        elif block == 'part':
                            draw_part_text(current_y)
                            current_y += part_block_height
                    
                    # Convert and display
                    photo = ImageTk.PhotoImage(bg)
                    preview_canvas.create_image(canvas_width//2, canvas_height//2, image=photo)
                    preview_canvas.image = photo
                    
                except Exception as e:
                    import traceback
                    print(f"Preview error: {e}")
                    traceback.print_exc()
                    # Fallback
                    preview_canvas.create_rectangle(0, 0, canvas_width, canvas_height, fill='black')
                    preview_canvas.create_text(canvas_width//2, canvas_height//2, 
                                             text="Preview Error\nCheck console",
                                             fill='white')
            else:
                # No image - show placeholder
                preview_canvas.create_rectangle(0, 0, canvas_width, canvas_height, fill='black')
                preview_canvas.create_text(canvas_width//2, canvas_height//2, 
                                         text="Import images to see preview",
                                         fill='white', font=('Arial', 12))
        
        # Auto-update preview when settings change
        font_var.trace_add('write', update_preview)
        size_var.trace_add('write', update_preview)
        color_var.trace_add('write', update_preview)
        pos_var.trace_add('write', update_preview)
        bg_color_var.trace_add('write', update_preview)
        part_enabled_var.trace_add('write', update_preview)
        part_start_var.trace_add('write', update_preview)
        part_font_var.trace_add('write', update_preview)
        part_size_var.trace_add('write', update_preview)
        part_color_var.trace_add('write', update_preview)
        part_pos_var.trace_add('write', update_preview)
        
        # Initial preview
        self.root.after(100, update_preview)
        
        # Save button at bottom
        button_frame = ttk.Frame(dialog)
        button_frame.pack(fill=tk.X, padx=15, pady=(10, 15))
        
        def save_settings():
            self.video_settings = {
                'font': font_var.get(),
                'font_size': size_var.get(),
                'font_color': color_options.get(color_var.get(), 'white_stroke'),
                'fade_duration': fade_dur_var.get(),
                'fade_in_start': fade_in_var.get(),
                'fade_out_end': fade_out_var.get(),
                'sound_fade': sound_fade_var.get(),
                'text_position': pos_var.get(),
                'bg_color': bg_color_var.get(),
                'part_enabled': part_enabled_var.get(),
                'part_start_number': part_start_var.get(),
                'part_font': part_font_var.get(),
                'part_font_size': part_size_var.get(),
                'part_color': color_options.get(part_color_var.get(), 'white_stroke'),
                'part_text_position': part_pos_var.get()
            }
            
            # Save to niche folder
            if self.current_niche:
                settings_file = os.path.join(self.current_niche, "video_settings.json")
                with open(settings_file, 'w') as f:
                    json.dump(self.video_settings, f, indent=2)
            
            messagebox.showinfo("Success", "Video settings saved!")
            self.log("✅ Video settings updated")
            dialog.destroy()
        
        ttk.Button(button_frame, text="💾 Save Settings", command=save_settings).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.RIGHT)
    
    def create_niche_dialog(self):
        """Show dialog to create a new niche."""
        dialog = tk.Toplevel(self.root)
        dialog.title("Create New Niche")
        dialog.geometry("500x400")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Niche name
        ttk.Label(dialog, text="Niche Name:", font=("Arial", 10, "bold")).pack(pady=(20, 5))
        name_var = tk.StringVar()
        name_entry = ttk.Entry(dialog, textvariable=name_var, width=40)
        name_entry.pack(pady=5)
        name_entry.focus()
        
        ttk.Label(dialog, text="(e.g., Dog, Cat, Tech, Motivation)", 
                 font=("Arial", 8, "italic")).pack()
        
        # Create button
        def create():
            niche_name = name_var.get().strip()
            if not niche_name:
                messagebox.showwarning("Invalid Name", "Please enter a niche name.")
                return
            
            # Create niche structure
            try:
                niche_path = os.path.join(self.niche_manager.niches_base_path, f"!{niche_name}")
                
                if os.path.exists(niche_path):
                    messagebox.showwarning("Exists", f"Niche '{niche_name}' already exists.")
                    return
                
                # Create folders
                os.makedirs(niche_path, exist_ok=True)
                os.makedirs(os.path.join(niche_path, "Raw-Images"), exist_ok=True)
                os.makedirs(os.path.join(niche_path, "Meme-Images"), exist_ok=True)
                os.makedirs(os.path.join(niche_path, "Meme-Fade"), exist_ok=True)
                os.makedirs(os.path.join(niche_path, "Meme-Final"), exist_ok=True)
                os.makedirs(os.path.join(niche_path, "Meme-Description"), exist_ok=True)
                os.makedirs(os.path.join(niche_path, "TikTok-Sounds"), exist_ok=True)
                
                # Copy templates
                config_path = os.path.join(Path(__file__).parent.parent, "config")
                
                # Credentials
                cred_template = os.path.join(config_path, "credentials.template.json")
                cred_dest = os.path.join(niche_path, "Credentials.json")
                if os.path.exists(cred_template):
                    shutil.copy(cred_template, cred_dest)
                
                # Quotes
                quotes_template = os.path.join(config_path, "quotes.template.txt")
                quotes_dest = os.path.join(niche_path, "Quotes.txt")
                if os.path.exists(quotes_template):
                    shutil.copy(quotes_template, quotes_dest)
                
                # Upload log
                upload_template = os.path.join(config_path, "upload_log.template.json")
                upload_dest = os.path.join(niche_path, "upload_log.json")
                if os.path.exists(upload_template):
                    shutil.copy(upload_template, upload_dest)
                
                # TikTok sounds list
                sounds_dest = os.path.join(niche_path, "TikTok-Sounds.txt")
                with open(sounds_dest, 'w') as f:
                    f.write("# Add TikTok sound URLs here (one per line)\n")
                
                # Upload logs
                open(os.path.join(niche_path, "tiktok_upload_log.txt"), 'w').close()
                open(os.path.join(niche_path, "youtube_upload_log.txt"), 'w').close()
                
                with open(os.path.join(niche_path, "youtube_upload_log.json"), 'w') as f:
                    json.dump({}, f, indent=2)
                
                dialog.destroy()
                messagebox.showinfo("Success", 
                                   f"Niche '{niche_name}' created successfully!\n\n"
                                   f"Next steps:\n"
                                   f"1. Import quotes (Import → Import Quotes)\n"
                                   f"2. Import images (Import → Import Images)\n"
                                   f"3. Configure credentials (File → Settings)")
                
                # Reload niches
                self.load_niches()
                self.log(f"✅ Created niche: {niche_name}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to create niche:\n{e}")
        
        ttk.Button(dialog, text="Create Niche", command=create, 
                  style="Accent.TButton").pack(pady=20)
        
        # Info
        info_frame = ttk.LabelFrame(dialog, text="What gets created:", padding=10)
        info_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        info_text = scrolledtext.ScrolledText(info_frame, height=8, wrap=tk.WORD)
        info_text.pack(fill=tk.BOTH, expand=True)
        info_text.insert(1.0, """✓ Folder structure for videos and images
✓ Credentials.json (template)
✓ Quotes.txt (template)
✓ TikTok-Sounds.txt (empty)
✓ Upload tracking files

After creation, you can:
• Import your quotes
• Import your images
• Add credentials in Settings
• Import TikTok sounds list""")
        info_text.config(state='disabled')
    
    def import_quotes(self):
        """Import quotes from a file."""
        if not self.current_niche:
            messagebox.showwarning("No Niche", "Please select a niche first.")
            return
        
        file_path = filedialog.askopenfilename(
            title="Select Quotes File",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        
        if not file_path:
            return
        
        try:
            dest = os.path.join(self.current_niche, "Quotes.txt")
            shutil.copy(file_path, dest)
            
            # Count quotes
            with open(dest, 'r') as f:
                quotes = [line.strip() for line in f if line.strip() and not line.startswith('#')]
            
            messagebox.showinfo("Success", f"Imported {len(quotes)} quotes successfully!")
            self.log(f"✅ Imported {len(quotes)} quotes")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to import quotes:\n{e}")
    
    def import_images(self):
        """Import images."""
        if not self.current_niche:
            messagebox.showwarning("No Niche", "Please select a niche first.")
            return
        
        # Ask for folder or files
        response = messagebox.askyesno("Import Images", 
                                      "Import entire folder?\n\n"
                                      "Yes = Select folder\n"
                                      "No = Select individual files")
        
        if response:
            # Folder
            folder_path = filedialog.askdirectory(title="Select Image Folder")
            if not folder_path:
                return
            
            try:
                dest_folder = os.path.join(self.current_niche, "Raw-Images")
                count = 0
                
                for file in os.listdir(folder_path):
                    if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')):
                        src = os.path.join(folder_path, file)
                        dst = os.path.join(dest_folder, file)
                        shutil.copy(src, dst)
                        count += 1
                
                messagebox.showinfo("Success", f"Imported {count} images!")
                self.log(f"✅ Imported {count} images from folder")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to import images:\n{e}")
        else:
            # Individual files
            file_paths = filedialog.askopenfilenames(
                title="Select Images",
                filetypes=[("Image Files", "*.png *.jpg *.jpeg *.gif *.webp"),
                          ("All Files", "*.*")]
            )
            
            if not file_paths:
                return
            
            try:
                dest_folder = os.path.join(self.current_niche, "Raw-Images")
                for file_path in file_paths:
                    shutil.copy(file_path, dest_folder)
                
                messagebox.showinfo("Success", f"Imported {len(file_paths)} images!")
                self.log(f"✅ Imported {len(file_paths)} images")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to import images:\n{e}")
    
    def import_sounds(self):
        """Import TikTok sounds list and download audio files."""
        if not self.current_niche:
            messagebox.showwarning("No Niche", "Please select a niche first.")
            return
        
        file_path = filedialog.askopenfilename(
            title="Select TikTok Sounds List",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        
        if not file_path:
            return
        
        try:
            dest = os.path.join(self.current_niche, "TikTok-Sounds.txt")
            shutil.copy(file_path, dest)
            
            # Count URLs
            with open(dest, 'r') as f:
                urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]
            
            if urls:
                # Ask if user wants to download audio files
                response = messagebox.askyesno("Download Audio", 
                                              f"Found {len(urls)} sound URLs.\n\n"
                                              f"Download audio files now?\n"
                                              f"(This may take a few minutes)")
                if response:
                    self.log(f"📥 Starting download of {len(urls)} audio files...")
                    self._download_sounds_thread(urls)
                else:
                    messagebox.showinfo("Success", f"Imported {len(urls)} TikTok sound URLs!\n"
                                                   f"You can download them later via Import → Download Sounds")
                    self.log(f"✅ Imported {len(urls)} sound URLs")
            else:
                messagebox.showinfo("Success", "Imported sounds list (no URLs found)")
                self.log(f"✅ Imported sounds list")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to import sounds:\n{e}")
    
    def _download_sounds_thread(self, urls):
        """Download sounds in background thread."""
        def download():
            try:
                import yt_dlp
                
                audio_folder = os.path.join(self.current_niche, "TikTok-Sounds")
                os.makedirs(audio_folder, exist_ok=True)
                
                success_count = 0
                failed_count = 0
                
                for idx, url in enumerate(urls, 1):
                    self.root.after(0, lambda i=idx, total=len(urls): 
                                   self.log(f"📥 Downloading audio {i}/{total}..."))
                    
                    try:
                        ydl_opts = {
                            'format': 'bestaudio/best',
                            'outtmpl': os.path.join(audio_folder, f'sound_{idx:03d}.%(ext)s'),
                            'postprocessors': [{
                                'key': 'FFmpegExtractAudio',
                                'preferredcodec': 'mp3',
                                'preferredquality': '192',
                            }],
                            'quiet': True,
                            'no_warnings': True,
                        }
                        
                        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                            ydl.download([url])
                        
                        success_count += 1
                        self.root.after(0, lambda i=idx: self.log(f"✅ Downloaded audio {i}"))
                    except Exception as e:
                        failed_count += 1
                        self.root.after(0, lambda i=idx, err=str(e): 
                                       self.log(f"⚠️  Failed to download audio {i}: {err}"))
                
                # Final update
                def final_update():
                    if success_count > 0:
                        messagebox.showinfo("Download Complete", 
                                          f"Successfully downloaded {success_count}/{len(urls)} audio files!\n"
                                          f"Failed: {failed_count}")
                        self.log(f"✅ Download complete: {success_count} successful, {failed_count} failed")
                    else:
                        messagebox.showerror("Download Failed", 
                                           "Failed to download any audio files.\n"
                                           "Make sure yt-dlp is installed and URLs are valid.")
                        self.log("❌ Audio download failed")
                
                self.root.after(0, final_update)
                
            except ImportError:
                def show_error():
                    messagebox.showerror("Missing Dependency", 
                                       "yt-dlp is not installed!\n\n"
                                       "Install it with:\n"
                                       "pip install yt-dlp")
                    self.log("❌ yt-dlp not installed")
                self.root.after(0, show_error)
            except Exception as e:
                def show_error():
                    messagebox.showerror("Error", f"Download failed:\n{e}")
                    self.log(f"❌ Download error: {e}")
                self.root.after(0, show_error)
        
        thread = threading.Thread(target=download)
        thread.daemon = True
        thread.start()
    
    def download_sounds_menu(self):
        """Download sounds from TikTok-Sounds.txt file."""
        if not self.current_niche:
            messagebox.showwarning("No Niche", "Please select a niche first.")
            return
        
        sounds_file = os.path.join(self.current_niche, "TikTok-Sounds.txt")
        if not os.path.exists(sounds_file):
            messagebox.showwarning("No Sounds List", 
                                  "No TikTok-Sounds.txt file found.\n\n"
                                  "Import a sounds list first (Import → Import Sounds List)")
            return
        
        try:
            with open(sounds_file, 'r') as f:
                urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]
            
            if not urls:
                messagebox.showwarning("No URLs", "No URLs found in TikTok-Sounds.txt")
                return
            
            response = messagebox.askyesno("Download Audio", 
                                          f"Found {len(urls)} sound URLs.\n\n"
                                          f"Download audio files now?\n"
                                          f"(This may take a few minutes)")
            if response:
                self.log(f"📥 Starting download of {len(urls)} audio files...")
                self._download_sounds_thread(urls)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to read sounds list:\n{e}")
    
    def show_about(self):
        """Show about dialog."""
        messagebox.showinfo("About", 
                           "Meme Video Generator v1.0\n\n"
                           "A professional tool for generating meme videos.\n\n"
                           "Features:\n"
                           "• Multi-niche support\n"
                           "• Automated video generation\n"
                           "• Customizable video settings\n"
                           "• Easy import tools\n\n"
                           "© 2026")

    def check_for_updates(self, show_up_to_date=True):
        """Check GitHub releases and notify if a newer version is available."""
        try:
            config = get_config()
            current_version = config.get('app.version', '0.0.0')
        except Exception:
            current_version = '0.0.0'

        api_url = f"https://api.github.com/repos/{self.repo_slug}/releases/latest"

        def fetch_latest():
            try:
                response = requests.get(api_url, timeout=6)
                response.raise_for_status()
                payload = response.json()
                tag = payload.get('tag_name') or payload.get('name') or ""
                latest_version = tag.lstrip('v') if isinstance(tag, str) else ""
                release_url = payload.get('html_url', f"https://github.com/{self.repo_slug}/releases")
                return latest_version, release_url
            except Exception as e:
                return None, str(e)

        latest_version, release_url = fetch_latest()

        if not latest_version:
            if show_up_to_date:
                messagebox.showwarning("Update Check", f"Could not check for updates.\n{release_url}")
            return

        try:
            if version.parse(latest_version) > version.parse(current_version):
                if messagebox.askyesno(
                    "Update Available",
                    f"A new version is available.\n\n"
                    f"Current: {current_version}\n"
                    f"Latest: {latest_version}\n\n"
                    f"Open the release page?"
                ):
                    webbrowser.open(release_url)
            elif show_up_to_date:
                messagebox.showinfo("Up to Date", f"You're on the latest version ({current_version}).")
        except Exception:
            if show_up_to_date:
                messagebox.showwarning("Update Check", "Could not compare versions.")


def main():
    """Main entry point for GUI."""
    root = tk.Tk()
    app = MemeGeneratorGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
