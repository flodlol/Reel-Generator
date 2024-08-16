from moviepy.editor import ImageClip
from moviepy.video.fx.all import fadein
import os
import re

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
    image_basename = os.path.basename(image_path).split('.')[0]  # Get the base name without extension
    video_filename = f"{image_basename}_f.mp4"  # Add '_f' before the extension
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
                print(f"Creating video for {meme_image}...")
                video_path = create_fade_in_video(image_path, video_duration=5, output_folder=output_video_folder)
                print(f"Video created and saved at: {video_path}")

# Run the processing
if __name__ == "__main__":
    process_all_meme_images()
