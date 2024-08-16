from moviepy.editor import VideoFileClip, ImageClip, AudioFileClip, concatenate_videoclips
import random
import os
import re
import time

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
        print(f"Fade video not found: {fade_video_path}")
        return [], []  # Return empty lists if files are missing
    if not os.path.isfile(meme_image_path):
        print(f"Meme image not found: {meme_image_path}")
        return [], []  # Return empty lists if files are missing
    
    # Select a random audio file
    audio_files = [f for f in os.listdir(audio_folder) if f.endswith('.mp3')]
    if not audio_files:
        raise FileNotFoundError("No audio files found in the specified folder.")
    
    random_audio = os.path.join(audio_folder, random.choice(audio_files))
    print(f"Loading audio file: {random_audio}")

    try:
        # Load the fade video and trim it to 5 seconds
        fade_video_clip = VideoFileClip(fade_video_path).subclip(0, 5)
        
        # Load the image and set it to be static for 59 seconds
        meme_image_clip = ImageClip(meme_image_path).set_duration(59).set_fps(1)
        
        # Load the audio file
        audio_clip = AudioFileClip(random_audio)
    except Exception as e:
        raise RuntimeError(f"Error loading clips: {e}")

    # Long video (1 minute 4 seconds)
    final_clip_long = concatenate_videoclips([fade_video_clip, meme_image_clip])
    final_clip_long = final_clip_long.set_audio(audio_clip)
    output_file_name_long = f"meme_{number}_long.mp4"
    output_path_long = os.path.join(output_folder, output_file_name_long)
    
    try:
        final_clip_long.write_videofile(output_path_long, codec='libx264', audio_codec='aac', fps=24)
        print(f"Long final video created successfully: {output_path_long}")
    except Exception as e:
        raise RuntimeError(f"Error creating long final video: {e}")

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
        print(f"Short final video created successfully: {output_path_short}")
        return [output_path_long, output_path_short]  # Return the list of created video paths
    except Exception as e:
        raise RuntimeError(f"Error creating short final video: {e}")

def process_all_videos():
    fade_folder = 'Meme-Fade'
    output_folder = 'Meme-Final'

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Get all fade videos sorted by number
    fade_files = get_all_files(fade_folder, 'meme_', '.mp4')

    if not fade_files:
        raise FileNotFoundError("No fade videos found in the specified folder.")

    existing_videos = [f for f in os.listdir(output_folder) if f.startswith('meme_') and f.endswith('.mp4')]
    existing_numbers = {get_file_number(f) for f in existing_videos}

    # Track the start time
    start_time = time.time()

    created_videos = []
    # Process videos from lowest to highest number
    for fade_video in fade_files:
        number = get_file_number(os.path.basename(fade_video))
        if number in existing_numbers:
            print(f"Videos for meme_{number} already exist. Skipping.")
            continue
        print(f"Processing meme_{number}")
        video_paths = create_final_videos(number)
        if video_paths:
            created_videos.extend(video_paths)

    # Track the end time
    end_time = time.time()
    total_time = end_time - start_time

    # Print summary
    print("\n" + "-"*50)
    print("Summary of created videos:")
    for video in created_videos:
        print(f"  - {video}")
    print(f"Total videos created: {len(created_videos)}")
    print(f"Total time taken: {total_time:.2f} seconds")
    print("-"*50)

if __name__ == "__main__":
    process_all_videos()
