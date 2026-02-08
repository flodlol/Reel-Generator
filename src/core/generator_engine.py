import os
import sys
import re
import time
import random
import warnings
import textwrap
import logging
import json

from datetime import datetime, timedelta

from PIL import Image, ImageDraw, ImageFont
# MoviePy 2.x imports
from moviepy import VideoFileClip, ImageClip, AudioFileClip, concatenate_videoclips
from moviepy.video.fx.FadeIn import FadeIn

from utils import bold, red, green, cyan, shorten_path


# Suppress specific warnings from MoviePy or general warnings
warnings.filterwarnings("ignore", category=UserWarning, module="moviepy")


# Configure logging
formatter = logging.Formatter(
    '%(asctime)s %(message)s',
    datefmt='[%H:%M:%S]'
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(message)s',
    datefmt='[%H:%M:%S]'
)
logger = logging.getLogger()

# Remove any existing handlers
for handler in logger.handlers[:]:
    logger.removeHandler(handler)

# Set up logging to the console
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter('%(asctime)s %(message)s', datefmt='[%H:%M:%S]'))
logger.addHandler(console_handler)

# Set up logging to a file
file_handler = logging.FileHandler('generator.log')
file_handler.setFormatter(logging.Formatter('%(asctime)s %(message)s', datefmt='[%H:%M:%S]'))
logger.addHandler(file_handler)

logging.getLogger('moviepy').setLevel(logging.ERROR)


BASE_PATH = None


def choose_random_image(folder):
    """Choose a random image from the specified folder."""
    images = [f for f in os.listdir(folder) if f.lower().endswith(('jpg', 'jpeg', 'png'))]
    if not images:
        logger.error(red("No images found in the folder"))
    return os.path.join(folder, random.choice(images))

def choose_random_quote(file):
    """Choose a random quote and its description from the specified file."""
    with open(file, 'r') as f:
        content = f.read()
    quote_blocks = [block.strip() for block in content.split('\n\n') if block.strip()]
    quote_block = random.choice(quote_blocks)
    lines = quote_block.split('\n')
    quote = lines[0]
    description = lines[1].strip('- ') if len(lines) > 1 else ""
    return quote, description

def get_next_filename(folder, prefix, extension):
    """Find the next available filename in the specified folder."""
    files = os.listdir(folder)
    matching_files = [f for f in files if f.startswith(prefix) and f.endswith(extension)]
    if not matching_files:
        return 1
    numbers = [int(re.search(r'\d+', f).group()) for f in matching_files]
    return max(numbers) + 1

def create_description_file(number, description, hashtags, output_folder):
    """Create a JSON file with the meme description and hashtags."""
    description_folder = os.path.join(os.path.dirname(output_folder), 'Meme-Description')
    if not os.path.exists(description_folder):
        os.makedirs(description_folder)
    
    description_filename = f"meme_{number:04d}.json"
    description_path = os.path.join(description_folder, description_filename)
    
    # Combine description and hashtags
    combined_description = f"{description} {hashtags}"
    
    data = {
        "description": combined_description
    }
    
    with open(description_path, 'w') as f:
        json.dump(data, f, indent=1)
    
    return description_path


def get_text_dimensions(text_string, font):
    ascent, descent = font.getmetrics()
    text_width = font.getmask(text_string).getbbox()[2]
    text_height = font.getmask(text_string).getbbox()[3] + descent
    return (text_width, text_height)

def create_meme_with_text(image_path, text, output_folder, number, video_number):
    """Create a meme image with text and video number, save it to the output folder."""
    background_width = 1080
    background_height = 1920

    # Create black background
    black_background = Image.new('RGB', (background_width, background_height), color='black')
    
    # Open the input image
    with Image.open(image_path) as original_img:
        img = original_img.copy()
        img.thumbnail((background_width, background_height - 300))  # Leave space for text and video number
    
    # Set up font for the quote text
    font_size = 60
    try:
        # Custom font stored in assets/fonts at project root
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        font_path = os.path.join(project_root, 'assets', 'fonts', 'Proxima_Nova_Semibold.otf')
        font = ImageFont.truetype(font_path, font_size)
    except IOError as e:
        logger.warning(red(f"Custom font not found: {e}. Trying system fonts."))
        # Try system fonts as fallback (Pillow 10+ doesn't have load_default)
        try:
            # Try Arial on macOS/Windows or DejaVu on Linux
            system_fonts = [
                "/System/Library/Fonts/Helvetica.ttc",
                "/System/Library/Fonts/Supplemental/Arial.ttf",
                "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                "C:\\Windows\\Fonts\\Arial.ttf"
            ]
            font = None
            for font_path in system_fonts:
                if os.path.exists(font_path):
                    font = ImageFont.truetype(font_path, font_size)
                    logger.info(f"Using system font: {font_path}")
                    break
            if not font:
                raise IOError("No suitable font found")
        except Exception as e2:
            logger.error(red(f"Failed to load any font: {e2}"))
            raise

    # Calculate maximum text width
    max_text_width = img.width - 60

    # Wrap text
    wrapped_lines = []
    current_line = []
    words = text.split()
    for word in words:
        current_line.append(word)
        line = ' '.join(current_line)
        width, _ = get_text_dimensions(line, font)
        if width > max_text_width:
            if len(current_line) == 1:
                wrapped_lines.append(line)
                current_line = []
            else:
                wrapped_lines.append(' '.join(current_line[:-1]))
                current_line = [word]
    if current_line:
        wrapped_lines.append(' '.join(current_line))

    # Calculate text box dimensions
    line_heights = [get_text_dimensions(line, font)[1] for line in wrapped_lines]
    total_text_height = sum(line_heights) + (len(wrapped_lines) - 1) * 10  # 10px line spacing
    box_padding = 30
    box_height = total_text_height + 2 * box_padding
    text_box_width = img.width

    # Create text box
    text_box = Image.new('RGB', (text_box_width, box_height), color='white')
    draw = ImageDraw.Draw(text_box)

    # Draw quote text on the text box
    y_position = box_padding
    for line in wrapped_lines:
        text_width, text_height = get_text_dimensions(line, font)
        text_x = (text_box_width - text_width) // 2
        draw.text((text_x, y_position), line, font=font, fill='black')
        y_position += text_height + 10

    # Calculate positions
    total_height = box_height + img.height
    vertical_center = (background_height - total_height) // 2
    text_box_position = ((background_width - text_box_width) // 2, vertical_center)
    meme_position = ((background_width - img.width) // 2, text_box_position[1] + box_height)

    # Paste text box and image onto background
    black_background.paste(text_box, text_box_position)
    black_background.paste(img, meme_position)

    # Set up font for the video number (half the size of the quote text)
    part_font_size = font_size // 2
    try:
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        font_path = os.path.join(project_root, 'assets', 'fonts', 'Proxima_Nova_Semibold.otf')
        part_font = ImageFont.truetype(font_path, part_font_size)
    except IOError:
        # Use same fallback logic as main font
        system_fonts = [
            "/System/Library/Fonts/Helvetica.ttc",
            "/System/Library/Fonts/Supplemental/Arial.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "C:\\Windows\\Fonts\\Arial.ttf"
        ]
        part_font = None
        for font_path in system_fonts:
            if os.path.exists(font_path):
                part_font = ImageFont.truetype(font_path, part_font_size)
                break
        if not part_font:
            raise IOError("No suitable font found for part number")

    # Add the video number ("part") below the meme image with the smaller font
    video_number_text = f"part {video_number}"
    video_number_width, video_number_height = get_text_dimensions(video_number_text, part_font)
    
    # Calculate the position to center the part text below the meme
    part_text_x_position = (background_width - video_number_width) // 2
    video_number_y_position = meme_position[1] + img.height + 20

    # Draw the part text on the black background in white
    draw = ImageDraw.Draw(black_background)
    draw.text((part_text_x_position, video_number_y_position), video_number_text, font=part_font, fill='white')

    # Save the meme
    meme_filename = os.path.join(output_folder, f"meme_{number:04d}.jpg")
    black_background.save(meme_filename, quality=95)

    short_path = shorten_path(meme_filename)
    return short_path, meme_filename




def process_single_meme(number, hashtags, video_number):
    """Process the creation of a single meme video - lightweight and fast."""
    try:
        # Select random image and quote
        random_image_path = choose_random_image(raw_images_folder)
        if not random_image_path:
            logger.error("Failed to choose random image")
            return []

        random_quote, description = choose_random_quote(quotes_file)
        if not random_quote:
            logger.error("Failed to choose random quote")
            return []
        
        # Select random audio file
        audio_files = [f for f in os.listdir(audio_folder) if f.endswith('.mp3')]
        if not audio_files:
            logger.error(red("No audio files found in the specified folder."))
            return []

        random_audio = os.path.join(audio_folder, random.choice(audio_files))
        audio_clip = AudioFileClip(random_audio)
        video_duration = audio_clip.duration
        logger.info(f"Audio duration: {video_duration}s")
        
        # Create meme image
        meme_short_path, meme_filename = create_meme_with_text(random_image_path, random_quote, meme_images_folder, number, video_number)
        logger.info(green(f"Meme image: {meme_short_path}"))

        # Create single video with fade-in effect (duration = audio length)
        fade_duration = min(3, video_duration / 2)  # Fade for 3 sec or half the audio duration
        image_clip = ImageClip(meme_filename, duration=video_duration).with_effects([FadeIn(fade_duration)])
        
        # Add audio
        final_clip = image_clip.with_audio(audio_clip)
        
        # Save single output video
        output_filename = f"meme_{number:04d}.mp4"
        output_path = os.path.join(output_folder, output_filename)
        
        final_clip.write_videofile(
            output_path,
            codec='libx264',
            audio_codec='aac',
            fps=24,
            logger=None,
            threads=4,
            preset='ultrafast',  # Fastest encoding
            ffmpeg_params=["-crf", "28"]  # Lower quality for speed
        )
        
        logger.info(green(f"Video created: {output_filename}"))

        # Create description file
        description_path = create_description_file(number, description, hashtags, output_folder)
        logger.info(green(f"Description: {shorten_path(description_path)}"))
        
        # Clean up
        audio_clip.close()
        final_clip.close()

        return [output_filename]
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        logger.error(red(f"Error processing meme: {e}"))
        logger.error(error_details)
        # Re-raise the exception so the GUI can see it
        raise



def main(*args, auto_count=None):
    """
    Main function to generate meme videos.
    
    Args:
        *args: Path to niche folder
        auto_count: Number of videos to generate (if None, will prompt for input)
    """
    global BASE_PATH

    # Check if BASE_PATH is provided as an argument
    if args and isinstance(args[0], str):
        BASE_PATH = args[0]
    elif len(sys.argv) > 1:
        BASE_PATH = sys.argv[1]
    else:
        print("Please provide the niche path as an argument.")
        return

    # Now define the paths that depend on BASE_PATH
    global raw_images_folder, quotes_file, meme_images_folder, meme_fade_folder, audio_folder, output_folder
    raw_images_folder = os.path.join(BASE_PATH, 'Raw-Images')
    quotes_file = os.path.join(BASE_PATH, 'Quotes.txt')
    meme_images_folder = os.path.join(BASE_PATH, 'Meme-Images')
    meme_fade_folder = os.path.join(BASE_PATH, 'Meme-Fade')
    audio_folder = os.path.join(BASE_PATH, 'TikTok-Sounds')
    output_folder = os.path.join(BASE_PATH, 'Meme-Final')
    credentials_path = os.path.join(BASE_PATH, 'Credentials.json')

    with open(credentials_path, 'r') as f:
        credentials = json.load(f)
    hashtags = credentials.get('hashtags', '')

    # Create the Meme-Images folder if it doesn't exist
    if not os.path.exists(meme_images_folder):
        os.makedirs(meme_images_folder)

    # Read the video number from the upload_log.json
    log_file_path = os.path.join(BASE_PATH, 'upload_log.json')
    with open(log_file_path, 'r+') as log_file:
        log_data = json.load(log_file)
        video_number = log_data.get('video_number', 1)

    # Get number of videos to generate
    if auto_count is not None:
        num_videos = auto_count
    else:
        print("How many videos would you like to generate?")
        num_videos = int(input("> ").strip())
        print("\n")

    start_time = datetime.now()
    created_videos = []

    # Get the next available number based on existing outputs
    start_number = get_next_filename(output_folder, "meme_", ".mp4")

    for i in range(num_videos):
        current_number = start_number + i
        logger.info(bold(f"Processing video {i + 1}/{num_videos}"))
        
        # Process the meme with the current video number
        created_videos += process_single_meme(current_number, hashtags, video_number)
        
        # Increment the video number and update the log
        video_number += 1
        log_data['video_number'] = video_number
        with open(log_file_path, 'w') as log_file:
            json.dump(log_data, log_file, indent=2)

    # Print summary
    print("----------")
    print("\n")
    end_time = datetime.now()
    total_time = end_time - start_time

    print("Videos created:")
    for video in created_videos:
        print(f"\t{bold(cyan(video))}")
    print("\n")
    print(f"Total videos created: {cyan(bold(str(len(created_videos))))}")
    minutes, seconds = divmod(total_time.total_seconds(), 60)
    print(f"Total time taken: {cyan(bold(f'{int(minutes)} minutes and {int(seconds)} seconds'))}")


    

if __name__ == "__main__":
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        print("Please run this script through main.py")
