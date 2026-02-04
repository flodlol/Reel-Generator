
<div align="center">
  <img src="public/logo/128.png" alt=“Study-Track Logo" width="128">
  <h1>Meme Video Generator</h1>
  <p>Automated meme video generator with customizable settings.
</p>



---

<div align=“left">


## Quick Start

1. **Install Requirements**
   ```bash
   brew install python-tk@3.12 ffmpeg
   ```

2. **Launch the App**
   ```bash
   ./launch.sh
   ```

3. **Create Your First Niche**
   - Click **File → New Niche**
   - Enter your niche name (e.g., "Dog", "Cat", "Tech")
   - Click Create

4. **Import Your Content**
   - **Import → Import Quotes** - Add your meme quotes
   - **Import → Import Images** - Add your meme images
   - **Import → Import Sounds List** - Add TikTok sound URLs

5. **Customize Your Videos**
   - Click **Customize → Video Settings**
   - Adjust font, colors, fade effects, and more
   - Preview your settings in real-time
   - Save your preferences

6. **Generate Videos**
   - Select your niche from the dropdown
   - Choose how many videos to generate
   - Click "Generate Videos"
   - Monitor progress in the activity log
   - Preview generated videos in the output folder preview

## Features

✅ **GUI Application** - No console commands needed
✅ **Built-in Niche Creator** - Create niches directly in the app
✅ **Easy Import Tools** - Import quotes, images, and sounds with file browser
✅ **Video Customization** - Full control over:
   - Font family, size, and color
   - Fade transitions (in/out)
   - Sound fade effects
   - Text positioning
   - Background colors
   - Real-time preview
✅ **Output Preview** - See generated videos in the app
✅ **Multi-niche Support** - Manage multiple content niches
✅ **Automated Generation** - Generate multiple videos with one click

## Menu Options

**File Menu:**
- New Niche - Create a new content niche
- Open Output Folder - Open generated videos folder
- Exit - Close the application

**Import Menu:**
- Import Quotes - Load quotes from a text file
- Import Images - Load images (folder or individual files)
- Import Sounds List - Load TikTok sound URLs

**Customize Menu:**
- Video Settings - Customize fonts, colors, fades, and effects

## Project Structure

```
Project-Memes/
├── launch.sh              # Start the app
├── requirements.txt       # Python dependencies
├── src/                   # Source code
│   ├── app.py            # GUI application
│   ├── core/             # Core engines
│   └── utils/            # Utilities
├── config/               # Templates
└── Meme-Generation/      # Your niches (created in app)
```

## Requirements

- Python 3.9+ with tkinter
- FFmpeg for video processing
- API credentials optional (for future upload features)

## Documentation

See [SETUP.md](SETUP.md) for detailed setup instructions.
