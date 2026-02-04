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
from datetime import datetime
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.niche_manager import NicheManager
from src.utils import get_config, init_config, setup_logger


class MemeGeneratorGUI:
    """Main GUI application for Meme Video Generator."""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Meme Video Generator v1.0")
        self.root.geometry("900x700")
        self.root.resizable(True, True)
        
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
        
        # Default video settings
        self.video_settings = {
            'font': 'Arial',
            'font_size': 72,
            'font_color': '#FFFFFF',
            'fade_duration': 0.5,
            'fade_in_start': True,
            'fade_out_end': True,
            'sound_fade': 0.3,
            'text_position': 'center',
            'bg_color': '#000000'
        }
        
        # Setup UI
        self.setup_ui()
        self.load_niches()
    
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
        help_menu.add_command(label="About", command=self.show_about)
        
        # Header
        header_frame = ttk.Frame(self.root, padding="10")
        header_frame.pack(fill=tk.X)
        
        title = ttk.Label(header_frame, text="🎬 Meme Video Generator", 
                         font=("Arial", 20, "bold"))
        title.pack()
        
        subtitle = ttk.Label(header_frame, text="Generate and Upload Meme Videos", 
                           font=("Arial", 10))
        subtitle.pack()
        
        # Separator
        ttk.Separator(self.root, orient='horizontal').pack(fill=tk.X, pady=10)
        
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
        self.niche_dropdown.pack(fill=tk.X, pady=(0, 10))
        self.niche_dropdown.bind('<<ComboboxSelected>>', self.on_niche_selected)
        
        # Niche info
        info_frame = ttk.LabelFrame(left_panel, text="Niche Info", padding="10")
        info_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        self.info_text = scrolledtext.ScrolledText(info_frame, height=15, width=30, 
                                                   wrap=tk.WORD, state='disabled')
        self.info_text.pack(fill=tk.BOTH, expand=True)
        
        # Right panel - Actions
        right_panel = ttk.Frame(main_frame)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # Action buttons
        actions_frame = ttk.LabelFrame(right_panel, text="Actions", padding="10")
        actions_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Generate section
        gen_frame = ttk.Frame(actions_frame)
        gen_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(gen_frame, text="Generate Videos:").pack(side=tk.LEFT)
        self.gen_count = tk.IntVar(value=1)
        count_spin = ttk.Spinbox(gen_frame, from_=1, to=20, textvariable=self.gen_count, 
                                width=10)
        count_spin.pack(side=tk.LEFT, padx=10)
        
        self.gen_btn = ttk.Button(gen_frame, text="🎨 Generate Videos", 
                                 command=self.generate_memes, width=20)
        self.gen_btn.pack(side=tk.LEFT)
        
        # Customize button
        customize_frame = ttk.Frame(actions_frame)
        customize_frame.pack(fill=tk.X, pady=5)
        
        self.customize_btn = ttk.Button(customize_frame, text="⚙️ Video Settings", 
                                       command=self.show_video_settings, width=20)
        self.customize_btn.pack(side=tk.LEFT, padx=5)
        
        self.folder_btn = ttk.Button(customize_frame, text="📁 Open Output Folder", 
                                    command=self.open_output_folder, width=20)
        self.folder_btn.pack(side=tk.LEFT, padx=5)
        
        # Log output
        log_frame = ttk.LabelFrame(right_panel, text="Activity Log", padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, wrap=tk.WORD)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Output preview
        preview_frame = ttk.LabelFrame(right_panel, text="Output Folder Preview", padding="10")
        preview_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        self.preview_text = scrolledtext.ScrolledText(preview_frame, height=8, wrap=tk.WORD, state='disabled')
        self.preview_text.pack(fill=tk.BOTH, expand=True)
        
        # Status bar
        status_frame = ttk.Frame(self.root)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.status_var = tk.StringVar(value="Ready")
        status_label = ttk.Label(status_frame, textvariable=self.status_var, 
                                relief=tk.SUNKEN, anchor=tk.W)
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
        
        self.preview_text.config(state='normal')
        self.preview_text.delete(1.0, tk.END)
        
        try:
            output_folder = os.path.join(self.current_niche, "Meme-Final")
            if not os.path.exists(output_folder):
                self.preview_text.insert(1.0, "No videos generated yet.\n\nClick 'Generate Videos' to create your first video!")
                self.preview_text.config(state='disabled')
                return
            
            files = [f for f in os.listdir(output_folder) if f.endswith('.mp4')]
            files.sort(reverse=True)  # Most recent first
            
            if not files:
                self.preview_text.insert(1.0, "No videos in output folder.")
            else:
                info = f"📁 Output: Meme-Final/\n"
                info += f"📊 Total Videos: {len(files)}\n\n"
                info += "Recent Videos:\n"
                info += "-" * 40 + "\n"
                
                for i, file in enumerate(files[:8]):  # Show last 8
                    file_path = os.path.join(output_folder, file)
                    size_mb = os.path.getsize(file_path) / (1024 * 1024)
                    mod_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                    info += f"{i+1}. {file}\n"
                    info += f"   {size_mb:.1f} MB | {mod_time.strftime('%H:%M %d/%m')}\n"
                
                if len(files) > 8:
                    info += f"\n... +{len(files) - 8} more"
                
                self.preview_text.insert(1.0, info)
        except Exception as e:
            self.preview_text.insert(1.0, f"Error loading preview:\n{e}")
        finally:
            self.preview_text.config(state='disabled')
    
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
        dialog.geometry("1100x700")
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
        
        ttk.Label(font_frame, text="Font Family:").grid(row=0, column=0, sticky=tk.W, pady=5)
        font_var = tk.StringVar(value=self.video_settings['font'])
        font_combo = ttk.Combobox(font_frame, textvariable=font_var, width=25,
                                   values=['Arial', 'Impact', 'Comic Sans MS', 'Times New Roman', 'Courier New', 'Helvetica'])
        font_combo.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        
        ttk.Label(font_frame, text="Font Size:").grid(row=1, column=0, sticky=tk.W, pady=5)
        size_var = tk.IntVar(value=self.video_settings['font_size'])
        ttk.Spinbox(font_frame, from_=20, to=200, textvariable=size_var, width=10).grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(font_frame, text="Font Color:").grid(row=2, column=0, sticky=tk.W, pady=5)
        color_var = tk.StringVar(value=self.video_settings['font_color'])
        color_entry = ttk.Entry(font_frame, textvariable=color_var, width=12)
        color_entry.grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        
        def choose_color():
            color = colorchooser.askcolor(color=color_var.get())[1]
            if color:
                color_var.set(color)
        
        ttk.Button(font_frame, text="Choose", command=choose_color).grid(row=2, column=2, padx=5)
        
        ttk.Label(font_frame, text="Text Position:").grid(row=3, column=0, sticky=tk.W, pady=5)
        pos_var = tk.StringVar(value=self.video_settings.get('text_position', 'above'))
        ttk.Combobox(font_frame, textvariable=pos_var, width=15,
                    values=['above', 'center', 'below'], state='readonly').grid(row=3, column=1, sticky=tk.W, padx=5, pady=5)
        
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
        # Scaled to 405x720 to fit in dialog
        preview_canvas = tk.Canvas(preview_panel, width=405, height=720, bg='black', highlightthickness=1, highlightbackground='#555')
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
            
            # Portrait canvas: 405x720 (9:16 ratio, scaled from 1080x1920)
            canvas_width = 405
            canvas_height = 720
            
            if sample_image_pil:
                try:
                    from PIL import Image, ImageTk, ImageDraw, ImageFont
                    
                    # Create black background (matching generator)
                    bg = Image.new('RGB', (canvas_width, canvas_height), 'black')
                    
                    # Resize image to fit (matching generator: leave ~112px for text/spacing)
                    img = sample_image_pil.copy()
                    img.thumbnail((canvas_width, canvas_height - 112), Image.Resampling.LANCZOS)
                    
                    # Create WHITE text box with BLACK text (matching generator exactly)
                    text = "Sample Meme Text"
                    font_size = max(22, int(size_var.get() * 0.375))  # Scale for preview
                    
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
                    
                    box_padding = 11  # Scaled from 30px
                    box_height = text_height + 2 * box_padding
                    text_box_width = img.width
                    
                    # Create white text box
                    text_box = Image.new('RGB', (text_box_width, box_height), 'white')
                    text_draw = ImageDraw.Draw(text_box)
                    
                    # Draw black text centered on white box
                    text_x = (text_box_width - text_width) // 2
                    text_y = box_padding
                    text_draw.text((text_x, text_y), text, font=font, fill='black')
                    
                    # Calculate positions (matching generator: center vertically)
                    position = pos_var.get()
                    total_content_height = box_height + img.height
                    
                    if position == 'above':
                        # Text box above image, centered vertically
                        vertical_center = (canvas_height - total_content_height) // 2
                        text_box_y = vertical_center
                        img_y = text_box_y + box_height
                    elif position == 'below':
                        # Image above text box, centered vertically
                        vertical_center = (canvas_height - total_content_height) // 2
                        img_y = vertical_center
                        text_box_y = img_y + img.height
                    else:  # center
                        # Text box above image (default generator behavior)
                        vertical_center = (canvas_height - total_content_height) // 2
                        text_box_y = vertical_center
                        img_y = text_box_y + box_height
                    
                    # Paste text box and image onto black background
                    text_box_x = (canvas_width - text_box_width) // 2
                    img_x = (canvas_width - img.width) // 2
                    
                    bg.paste(text_box, (text_box_x, text_box_y))
                    bg.paste(img, (img_x, img_y))
                    
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
        
        # Initial preview
        self.root.after(100, update_preview)
        
        # Save button at bottom
        button_frame = ttk.Frame(dialog)
        button_frame.pack(fill=tk.X, padx=15, pady=(10, 15))
        
        def save_settings():
            self.video_settings = {
                'font': font_var.get(),
                'font_size': size_var.get(),
                'font_color': color_var.get(),
                'fade_duration': fade_dur_var.get(),
                'fade_in_start': fade_in_var.get(),
                'fade_out_end': fade_out_var.get(),
                'sound_fade': sound_fade_var.get(),
                'text_position': pos_var.get(),
                'bg_color': bg_color_var.get()
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


def main():
    """Main entry point for GUI."""
    root = tk.Tk()
    app = MemeGeneratorGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
