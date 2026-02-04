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
from moviepy.editor import VideoFileClip, ImageClip, AudioFileClip, concatenate_videoclips
import moviepy.editor as mp
from moviepy.video.fx.all import fadein

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
        # Font is in Meme-Generation folder at project root
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        font_path = os.path.join(project_root, 'Meme-Generation', 'Proxima_Nova_Semibold.otf')
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
        font_path = os.path.join(project_root, 'Meme-Generation', 'Proxima_Nova_Semibold.otf')
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




def create_fade_5(image_path, video_duration=5, output_folder="meme_fade_folder", number=1):
    # Create the video clip with the fade effect
    image_clip = ImageClip(image_path, duration=video_duration).fx(fadein, duration=5)

    # Define the file path
    video_filename = f"meme_{number:04d}_f5.mp4"
    video_path = os.path.join(output_folder, video_filename)
    
    # Write the video file
    image_clip.write_videofile(video_path, codec='libx264', fps=24, audio=False, logger=None)

    # Ensure the return is always exactly 2 values
    return video_path, video_filename

def create_fade_10(image_path, video_duration=10, output_folder="meme_fade_folder", number=1):
    # Create the video clip with the fade effect
    image_clip = ImageClip(image_path, duration=video_duration).fx(fadein, duration=10)

    # Define the file path
    video_filename = f"meme_{number:04d}_f10.mp4"
    video_path = os.path.join(output_folder, video_filename)
    
    # Write the video file
    image_clip.write_videofile(video_path, codec='libx264', fps=24, audio=False, logger=None)

    # Ensure the return is always exactly 2 values
    return video_path, video_filename


def create_final_videos(number, audio_file):
    """Create both the long and short final videos for the given meme number."""
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    fade5_filename = f"meme_{number:04d}_f5.mp4"
    fade10_filename = f"meme_{number:04d}_f10.mp4"
    image_filename = f"meme_{number:04d}.jpg"
    
    fade5_path = os.path.join(meme_fade_folder, fade5_filename)
    fade10_path = os.path.join(meme_fade_folder, fade10_filename)
    meme_image_path = os.path.join(meme_images_folder, image_filename)

    if not os.path.isfile(fade5_path):
        logging.info(red(f"Fade video not found: {fade5_path}"))
        return [], []
    if not os.path.isfile(fade10_path):
        logging.info(red(f"Fade video not found: {fade10_path}"))
        return [], []
    if not os.path.isfile(meme_image_path):
        logging.info(red(f"Meme image not found: {meme_image_path}"))
        return [], []
    
    audio_clip = AudioFileClip(audio_file)
    fade5_clip = VideoFileClip(fade5_path)
    fade10_clip = VideoFileClip(fade10_path)

    short_final_filename = f"meme_{number:04d}_short.mp4"
    youtube_final_filename = f"meme_{number:04d}_youtube.mp4"
    long_final_filename = f"meme_{number:04d}_long.mp4"

    short_video_path = os.path.join(output_folder, short_final_filename)
    youtube_video_path = os.path.join(output_folder, youtube_final_filename)
    long_video_path = os.path.join(output_folder, long_final_filename)

    # Ensure the short video duration matches the audio clip's duration
    fade5_clip = fade5_clip.set_duration(audio_clip.duration).set_audio(audio_clip)

    # Save the short video with audio
    fade5_clip.write_videofile(
        short_video_path,
        codec='libx264',
        audio_codec='aac',
        fps=24,
        logger=None,
        threads=4,  # Enable multi-threading
        preset='veryfast',  # Speed up encoding with minimal quality loss
        ffmpeg_params=["-crf", "23"]  # Adjust CRF for a balance of speed and quality
    )


    
    # Create the youtube video by extending the last frame to 40 seconds
    youtube_duration = random.randint(40, 60)  # Random duration between 40 and 60 seconds
    meme_image_clip = ImageClip(meme_image_path).set_duration(youtube_duration - fade10_clip.duration)
    youtube_video = concatenate_videoclips([fade10_clip, meme_image_clip], method="compose")

    # Save the youtube video with audio
    youtube_video = youtube_video.set_duration(youtube_duration).set_audio(audio_clip)
    youtube_video.write_videofile(
        youtube_video_path,
        codec='libx264',
        audio_codec='aac',
        fps=24,
        logger=None,
        threads=4,  # Enable multi-threading
        preset='veryfast',  # Speed up encoding with minimal quality loss
        ffmpeg_params=["-crf", "23"]  # Adjust CRF for a balance of speed and quality
    )


    # Create the long video by extending the last frame to 64 seconds
    meme_image_clip = ImageClip(meme_image_path).set_duration(64 - fade5_clip.duration)
    long_video = concatenate_videoclips([fade5_clip, meme_image_clip], method="compose")

    # Ensure the long video has no audio
    long_video = long_video.without_audio()

    # Write the long video to file
    long_video.write_videofile(
        long_video_path, 
        codec='libx264', 
        fps=24, 
        logger=None, 
        threads=4,  
        preset='veryfast',
        ffmpeg_params=["-crf", "23"]
    )



    return short_final_filename, youtube_final_filename, long_final_filename



def process_single_meme(number, hashtags, video_number):
    """Process the creation of a single meme and its corresponding videos."""
    try:
        random_image_path = choose_random_image(raw_images_folder)
        if not random_image_path:
            logger.error("Failed to choose random image")
            return []

        random_quote, description = choose_random_quote(quotes_file)
        if not random_quote:
            logger.error("Failed to choose random quote")
            return []
        
        # Pass video_number when calling create_meme_with_text
        meme_short_path, meme_filename = create_meme_with_text(random_image_path, random_quote, meme_images_folder, number, video_number)
        logger.info(green(f"Meme image created: {meme_short_path}"))

        fade_short_path, fade_filename = create_fade_5(meme_filename, video_duration=5, output_folder=meme_fade_folder, number=number)
        logger.info(green(f"Fade-in (5 sec) video created: {fade_short_path}"))

        fade_short_path, fade_filename = create_fade_10(meme_filename, video_duration=10, output_folder=meme_fade_folder, number=number)
        logger.info(green(f"Fade-in (10 sec) video created: {fade_short_path}"))


        # Select a random audio file
        audio_files = [f for f in os.listdir(audio_folder) if f.endswith('.mp3')]
        if not audio_files:
            logger.error(red("No audio files found in the specified folder."))
            return []

        random_audio = os.path.join(audio_folder, random.choice(audio_files))
        audio_clip = AudioFileClip(random_audio)
        logger.info(f"Audio duration: {audio_clip.duration}")

        # Pass the random audio file to create_final_videos
        short_final_filename, youtube_final_filename, long_final_filename = create_final_videos(number, random_audio)

        logger.info(green(f"Final short video: {short_final_filename}"))
        logger.info(green(f"Final YouTube video: {youtube_final_filename}"))
        logger.info(green(f"Final long video: {long_final_filename}"))

        description_path = create_description_file(number, description, hashtags, output_folder)
        logger.info(green(f"Description file created: {shorten_path(description_path)}"))

        return [short_final_filename, youtube_final_filename, long_final_filename] if short_final_filename and youtube_final_filename and long_final_filename else []
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

    # Get the next available number
    start_number = get_next_filename(output_folder, "meme_", "_long.mp4")

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
    print(f"Total videos created: {cyan(bold(str(int(len(created_videos) / 2))))}")
    minutes, seconds = divmod(total_time.total_seconds(), 60)
    print(f"Total time taken: {cyan(bold(f'{int(minutes)} minutes and {int(seconds)} seconds'))}")


    

if __name__ == "__main__":
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        print("Please run this script through main.py")
