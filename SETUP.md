# Meme Video Generator - Setup Guide

## Prerequisites

Before you start, make sure you have:

1. **Python 3.9+** with tkinter support
   - On macOS: `brew install python-tk@3.12`
   - On Ubuntu/Debian: `sudo apt install python3-tk`
   - On Windows: Tkinter comes with Python installer

2. **Firefox Browser** - For automated uploads

3. **FFmpeg** - For video processing
   - On macOS: `brew install ffmpeg`
   - On Ubuntu/Debian: `sudo apt install ffmpeg`
   - On Windows: Download from ffmpeg.org

## First Time Setup

### 1. Install Dependencies

Make sure you have Python 3.9+ and Firefox installed, then:

```bash
# The virtual environment already exists in Project-Env/
# Install any missing packages:
./Project-Env/bin/python -m pip install -r requirements.txt
```

### 2. Configure Your Niches

Each niche needs its own configuration. Here's how to set up:

#### Create a New Niche

1. Navigate to `data/niches/` folder
2. Create a folder with `!` prefix (e.g., `!MyNiche`)
3. Inside, create these folders:
   - `Raw-Images/` - Put your source images here
   - `Meme-Images/` - Generated meme images (auto-created)
   - `Meme-Fade/` - Fade effect videos (auto-created)
   - `Meme-Final/` - Final videos (auto-created)
   - `Meme-Description/` - Video descriptions (auto-created)
   - `TikTok-Sounds/` - TikTok audio files (optional)

#### Setup Credentials

Create `Credentials.json` in your niche folder:

```json
{
  "profile_path": "/path/to/your/firefox/profile",
  "time_set": "Set 1"
}
```

**Finding Your Firefox Profile Path:**

**On macOS:**
```bash
ls ~/Library/Application\ Support/Firefox/Profiles/
```

**On Linux:**
```bash
ls ~/.mozilla/firefox/
```

**On Windows:**
```
dir %APPDATA%\Mozilla\Firefox\Profiles\
```

#### Create Quotes File

Create `Quotes.txt` in your niche folder:

```
This is my first funny quote
- A description or context for the meme

Another hilarious quote
- More context here
```

**Format:** Each quote is separated by a blank line. First line is the quote, second line (with `-`) is the description.

#### Initialize Upload Log

Create `upload_log.json` in your niche folder:

```json
{
  "last_video_number_youtube": 0,
  "last_schedule_time_youtube": "N/A",
  "last_video_number_tiktok": 0,
  "last_schedule_time_tiktok": "N/A"
}
```

### 3. Setup Firefox Profiles

#### For YouTube

1. Open Firefox Profile Manager:
   ```bash
   /Applications/Firefox.app/Contents/MacOS/firefox -ProfileManager
   # On Linux: firefox -ProfileManager
   # On Windows: firefox.exe -ProfileManager
   ```

2. Create a new profile named "youtube-memes"
3. Launch Firefox with this profile
4. Go to youtube.com and log in to your channel
5. Keep logged in (don't log out)
6. Note the profile path and add it to your `Credentials.json`

#### For TikTok

1. Create another profile named "tiktok-memes"
2. Log in to TikTok
3. Add the profile path to `Credentials.json`

### 4. Test Your Setup

1. Launch the app: `./launch.sh`
2. Select your niche from the dropdown
3. Try generating 1 test meme
4. Check that it appears in `Meme-Final/`

## Example Niche Structure

```
data/niches/
└── !Cat/
    ├── Credentials.json          # Your Firefox profile path
    ├── Quotes.txt                # Your quotes
    ├── upload_log.json           # Upload tracking
    ├── TikTok-Sounds.txt         # Optional: Sound list
    ├── Raw-Images/               # Add your images here
    │   ├── cat1.jpg
    │   ├── cat2.jpg
    │   └── cat3.jpg
    ├── Meme-Images/              # Auto-generated
    ├── Meme-Fade/                # Auto-generated
    ├── Meme-Final/               # Auto-generated
    └── Meme-Description/         # Auto-generated
```

## Configuration Files

### config/config.yaml

Main application settings. You can customize:
- Video duration and quality
- Upload schedules
- Time sets for posting
- Browser settings

### Niche Credentials.json

```json
{
  "profile_path": "/Users/yourname/Library/Application Support/Firefox/Profiles/xxxxx.youtube-memes",
  "time_set": "Set 1",
  "youtube_channel": "Your Channel Name",
  "tiktok_username": "yourusername"
}
```

## Troubleshooting

### "No niches found"
- Create a folder in `data/niches/` starting with `!`
- Example: `!Cat`, `!Dog`, `!Funny`

### "Credentials file not found"
- Create `Credentials.json` in your niche folder
- Use the template above

### "No images found"
- Add `.jpg`, `.jpeg`, or `.png` files to `Raw-Images/`

### Firefox profile errors
- Use absolute paths (full path, not `~/`)
- Make sure Firefox is closed when the app uses the profile
- Test the profile path by copying it and checking it exists

### Permission errors
- Make sure all folders are writable
- On Linux/Mac: `chmod -R 755 data/niches/`

## Running the App

```bash
# Simple launch
./launch.sh

# Or run directly
./Project-Env/bin/python run_app.py
```

## Tips for Multiple Users

- Each user should have their own Firefox profiles
- Don't share `Credentials.json` files (they're git-ignored)
- Keep quotes and images in separate folders per niche
- Use different niches for different accounts

## Need Help?

Check the logs in the `logs/` folder for detailed error messages.
