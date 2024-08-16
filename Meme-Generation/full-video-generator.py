import os
import re
import time
import random
import textwrap
import logging
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import VideoFileClip, ImageClip, AudioFileClip, concatenate_videoclips
from moviepy.video.fx.all import fadein


# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    datefmt='%H:%M:%S'  # This sets the time format to HH:MM:SS
)



# MEME GENERATOR

# Paths to the folders and files
cat_images_folder = 'Cat-Images'
quotes_file = 'Quotes.txt'
meme_images_folder = 'Meme-Images'

# Create the Meme-Images folder if it doesn't exist
if not os.path.exists(meme_images_folder):
    os.makedirs(meme_images_folder)

# Function to choose a random image from the Cat-Images folder
def choose_random_image(folder):
    images = [f for f in os.listdir(folder) if f.lower().endswith(('jpg', 'jpeg', 'png'))]
    if not images:
        raise ValueError("No images found in the folder")
    return os.path.join(folder, random.choice(images))

# Function to choose a random quote from the Quotes.txt file
def choose_random_quote(file):
    with open(file, 'r') as f:
        # Read the entire file content
        content = f.read()
    
    # Split the content into quotes using double newlines as the separator
    quotes = [quote.strip() for quote in content.split('\n\n') if quote.strip()]
    
    if not quotes:
        raise ValueError("No quotes found in the file")
    
    return random.choice(quotes)

# Function to find the next available filename in the output folder
def get_next_filename(folder):
    # List all files in the folder
    files = os.listdir(folder)
    # Filter for filenames that match 'meme_X.jpg'
    meme_files = [f for f in files if f.startswith('meme_') and f.endswith('.jpg')]
    # Extract the numbers and find the highest one
    numbers = [int(f.split('_')[1].split('.')[0]) for f in meme_files]
    next_number = max(numbers, default=0) + 1
    return os.path.join(folder, f"meme_{next_number}.jpg")

# Function to create a meme on a black background with text in a white box
def create_meme_with_text(image_path, text, output_folder):
    # Dimensions for the black background
    background_width = 1080
    background_height = 1920

    # Create a black background image
    black_background = Image.new('RGB', (background_width, background_height), color='black')

    # Load the meme image
    img = Image.open(image_path)

    # Load a font with a fixed size
    font_size = 60
    try:
        font = ImageFont.truetype("Proxima_Nova_Semibold.otf", font_size)
    except IOError:
        print("Custom font not found. Using default font.")
        font = ImageFont.load_default()
        font_size = 20  # Default font size is much smaller, you might need to adjust this

    # Create a drawing context for the black background
    draw = ImageDraw.Draw(black_background)

    # Set white box width and calculate text width
    text_box_width = img.width  # White box width matches meme image width
    max_text_width = text_box_width - 60  # Allow some padding
    
    # Wrap text to fit within the white box width
    wrapped_lines = textwrap.wrap(text, width=(text_box_width // font_size * 2))  # Adjust width for wrapping
    
    # Create a drawing context for the white box
    text_box = Image.new('RGB', (text_box_width, 1), color='white')  # Start with height of 1 to calculate text height
    draw = ImageDraw.Draw(text_box)
    
    # Calculate height of the text box
    total_text_height = 0
    for line in wrapped_lines:
        text_bbox = draw.textbbox((0, 0), line, font=font)
        text_height = text_bbox[3] - text_bbox[1]
        total_text_height += text_height + 10  # Add some space between lines
    
    box_padding = 30  # Padding around the text
    box_height = (total_text_height + 2 * box_padding)  # White box height is based on text height and padding
    text_box = Image.new('RGB', (text_box_width, box_height), color='white')
    draw = ImageDraw.Draw(text_box)

    # Draw each line of text centered
    y_position = box_padding
    for line in wrapped_lines:
        text_bbox = draw.textbbox((0, 0), line, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_x = (text_box_width - text_width) // 2
        draw.text((text_x, y_position), line, font=font, fill='black')
        line_height = text_bbox[3] - text_bbox[1]
        y_position += line_height + 10  # Add space between lines

    # Resize the meme image to fit within the black background
    meme_max_width = background_width
    meme_max_height = background_height - box_height
    img.thumbnail((meme_max_width, meme_max_height))  # Resize with padding
    meme_width, meme_height = img.size

    # Calculate positions to center the white box and image
    total_height = box_height + meme_height
    if total_height > background_height:
        raise ValueError("Image too large to fit within the background.")

    vertical_center = (background_height - total_height) // 2
    text_box_position = ((background_width - text_box_width) // 2, vertical_center)
    meme_position = (text_box_position[0], text_box_position[1] + box_height)

    # Paste the white box and the meme image onto the black background
    black_background.paste(text_box, text_box_position)
    black_background.paste(img, meme_position)

    # Get the next available filename
    meme_filename = get_next_filename(output_folder)
    # Save the final image
    black_background.save(meme_filename)

    return meme_filename

# Main function to generate memes
def generate_memes(count):
    for _ in range(count):
        image_path = choose_random_image(cat_images_folder)
        quote = choose_random_quote(quotes_file)
        meme_path = create_meme_with_text(image_path, quote, meme_images_folder)
        logging.info("Meme created and saved at: {}".format(meme_path))
        print("\n")

# Prompt the user for the number of memes to generate
def main():
    try:
        print("\n" + "-"*50 + "\n")
        num_memes = int(input("How many memes would you like to generate? "))
        if num_memes < 1:
            raise ValueError("The number of memes must be at least 1.")
    except ValueError as e:
        print(f"Invalid input: {e}")
        return
    
    print("\n")
    generate_memes(num_memes)

# Run the main function
if __name__ == "__main__":
    main()



# FADE GENERATOR

# Paths to the folders and files
meme_images_folder = 'Meme-Images'
output_video_folder = 'Meme-Fade'

# Create the Meme-Fade folder if it doesn't exist
if not os.path.exists(output_video_folder):
    os.makedirs(output_video_folder)

def create_fade_in_video(image_path, video_duration=5, output_folder='Meme-Fade'):
    """Create a video with a fade-in effect for the given image."""
    # Load the image as a video clip
    image_clip = ImageClip(image_path, duration=video_duration)

    # Apply fade-in effect to the image clip
    image_clip = fadein(image_clip, duration=video_duration)

    # Create the output path with '_f' suffix
    image_basename = os.path.basename(image_path).split('.')[0]
    video_filename = f"{image_basename}_f.mp4"
    video_path = os.path.join(output_folder, video_filename)

    # Write the video to a file
    image_clip.write_videofile(video_path, codec='libx264', fps=24)

    return video_path

def get_latest_meme_number(output_folder):
    """Get the highest number from existing fade-in videos."""
    highest_number = 0
    for filename in os.listdir(output_folder):
        match = re.match(r'meme_(\d+)_f\.mp4', filename)
        if match:
            number = int(match.group(1))
            if number > highest_number:
                highest_number = number
    return highest_number

def process_all_meme_images():
    """Process all meme images to create fade-in videos."""
    # Get the latest meme number from existing fade videos
    latest_number = get_latest_meme_number(output_video_folder)

    # Get all meme images
    meme_images = [f for f in os.listdir(meme_images_folder) if f.startswith('meme_') and f.endswith('.jpg')]

    # Process each meme image
    for meme_image in meme_images:
        meme_image_name = meme_image.split('.')[0]  # Base name without extension
        match = re.match(r'meme_(\d+)', meme_image_name)
        if match:
            number = int(match.group(1))
            if number > latest_number:
                image_path = os.path.join(meme_images_folder, meme_image)
                video_path = create_fade_in_video(image_path, video_duration=5, output_folder=output_video_folder)
                logging.info(f"Fade created and saved at: {video_path}")

# Run the processing
if __name__ == "__main__":
    process_all_meme_images()



# FINAL VIDEO GENERATOR

def get_file_number(filename):
    """Extract the number from a filename."""
    match = re.search(r'\d+', filename)
    return int(match.group()) if match else None

def get_latest_file(folder, prefix, extension):
    """Get the latest file with the specified prefix and extension."""
    files = [f for f in os.listdir(folder) if f.startswith(prefix) and f.endswith(extension)]
    if not files:
        return None
    files.sort(key=lambda x: get_file_number(x), reverse=True)
    return os.path.join(folder, files[0])

def get_all_files(folder, prefix, extension):
    """Get all files with the specified prefix and extension, sorted by number."""
    files = [f for f in os.listdir(folder) if f.startswith(prefix) and f.endswith(extension)]
    if not files:
        return []
    files.sort(key=lambda x: get_file_number(x))
    return [os.path.join(folder, f) for f in files]

def create_final_videos(number):
    fade_folder = 'Meme-Fade'
    image_folder = 'Meme-Images'
    audio_folder = 'TikTok-Sounds'
    output_folder = 'Meme-Final'
    
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Define filenames
    fade_filename = f"meme_{number}_f.mp4"
    image_filename = f"meme_{number}.jpg"
    
    fade_video_path = os.path.join(fade_folder, fade_filename)
    meme_image_path = os.path.join(image_folder, image_filename)

    if not os.path.isfile(fade_video_path):
        logging.info(f"Fade video not found: {fade_video_path}")
        return [], []  # Return empty lists if files are missing
    if not os.path.isfile(meme_image_path):
        logging.info(f"Meme image not found: {meme_image_path}")
        return [], []  # Return empty lists if files are missing
    
    # Select a random audio file
    audio_files = [f for f in os.listdir(audio_folder) if f.endswith('.mp3')]
    if not audio_files:
        logging.error("No audio files found in the specified folder.")
    
    random_audio = os.path.join(audio_folder, random.choice(audio_files))
    logging.info(f"Loading audio file: {random_audio}")

    try:
        # Load the fade video and trim it to 5 seconds
        fade_video_clip = VideoFileClip(fade_video_path).subclip(0, 5)
        
        # Load the image and set it to be static for 59 seconds
        meme_image_clip = ImageClip(meme_image_path).set_duration(59).set_fps(1)
        
        # Load the audio file
        audio_clip = AudioFileClip(random_audio)
    except Exception as e:
        logging.error(f"Error loading clips: {e}")

    # Long video (1 minute 4 seconds)
    final_clip_long = concatenate_videoclips([fade_video_clip, meme_image_clip])
    final_clip_long = final_clip_long.set_audio(audio_clip)
    output_file_name_long = f"meme_{number}_long.mp4"
    output_path_long = os.path.join(output_folder, output_file_name_long)
    
    try:
        final_clip_long.write_videofile(output_path_long, codec='libx264', audio_codec='aac', fps=24)
        logging.info(f"Long final video created successfully: {output_path_long}")
    except Exception as e:
        logging.error(f"Error creating long final video: {e}")

    # Short video
    audio_duration = audio_clip.duration

    # Determine the duration of the static frame for the short version
    if audio_duration > 30:
        # Randomly select a total duration between 15 and 25 seconds
        total_duration = random.uniform(15, 25)
        meme_image_duration = total_duration - 5  # Image duration is total - 5 seconds fade
    else:
        meme_image_duration = max(0, audio_duration - 5)  # Image duration is audio duration - 5 seconds fade
    
    meme_image_clip_short = ImageClip(meme_image_path).set_duration(meme_image_duration).set_fps(1)
    final_clip_short = concatenate_videoclips([fade_video_clip, meme_image_clip_short])
    final_clip_short = final_clip_short.set_audio(audio_clip)
    output_file_name_short = f"meme_{number}_short.mp4"
    output_path_short = os.path.join(output_folder, output_file_name_short)

    try:
        final_clip_short.write_videofile(output_path_short, codec='libx264', audio_codec='aac', fps=24)
        logging.info(f"Short final video created successfully: {output_path_short}")
        return [output_path_long, output_path_short]  # Return the list of created video paths
    except Exception as e:
        logging.error(f"Error creating short final video: {e}")

def process_all_videos():
    fade_folder = 'Meme-Fade'
    output_folder = 'Meme-Final'

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Get all fade videos sorted by number
    fade_files = get_all_files(fade_folder, 'meme_', '.mp4')

    if not fade_files:
        logging.error("No fade videos found in the specified folder.")

    existing_videos = [f for f in os.listdir(output_folder) if f.startswith('meme_') and f.endswith('.mp4')]
    existing_numbers = {get_file_number(f) for f in existing_videos}

    # Track the start time
    start_time = time.time()

    created_videos = []
    # Process videos from lowest to highest number
    for fade_video in fade_files:
        number = get_file_number(os.path.basename(fade_video))
        if number in existing_numbers:
            # logging.info(f"Videos for meme_{str(number).zfill(4)} already exist. Skipping.")
            continue
        logging.info(f"Processing meme_{number}")
        video_paths = create_final_videos(number)
        if video_paths:
            created_videos.extend(video_paths)

    # Track the end time
    end_time = time.time()
    total_time = end_time - start_time

    # Print summary
    print("\n" + "-"*50 + "\n")
    print("Videos created:")
    for video in created_videos:
        print(f"\t{video}")
    print("\n")
    print(f"Total videos created: {int(len(created_videos)/2)}")
    print(f"Total time taken: {total_time:.2f} seconds")
    print("\n" + "-"*50 + "\n")

if __name__ == "__main__":
    process_all_videos()
