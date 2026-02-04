import os
import sys
import json
import random
import logging
from datetime import datetime, timedelta

from utils import bold, red, green, cyan, purple, pink, light_grey, dark_grey
from utils import shorten_path_from_project_meme

from upload_youtube import upload_video_to_youtube
from upload_tiktok import upload_video_to_tiktok

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
file_handler = logging.FileHandler('upload.log')
file_handler.setFormatter(logging.Formatter('%(asctime)s %(message)s', datefmt='[%H:%M:%S]'))
logger.addHandler(file_handler)

BASE_PATH = None

# Predefined upload times (in 24-hour format)
TIME_SETS = {
    "Set 1": [
        (0, 30),   # 00:30 AM
        (13, 30),  # 01:30 PM
        (21, 0)    # 9:00 PM
    ],
    "Set 2": [
        (13, 0),   # 1:00 PM
        (16, 0),   # 4:00 PM
        (19, 0)    # 7:00 PM
    ],
    "Set 3": [
        (16, 0),   # 4:00 PM
        (20, 0)    # 6:00 PM
    ]
}

def load_credentials(credentials_path):
    """Load the credentials from Credentials.json."""
    with open(credentials_path, 'r') as f:
        credentials = json.load(f)
    return credentials

def load_upload_log(upload_log_path):
    """Load the upload log from upload_log.json."""
    if os.path.exists(upload_log_path):
        with open(upload_log_path, 'r') as log_file:
            return json.load(log_file)
    else:
        return {}

def save_log(upload_log, upload_log_path):
    """Save the updated upload log to upload_log.json."""
    with open(upload_log_path, 'w') as log_file:
        json.dump(upload_log, log_file, indent=4)
    print(f'Upload log updated at {upload_log_path}')

def get_next_video_number(last_video_number, video_numbers):
    """Determine the next video number based on the last uploaded video number."""
    next_video_number = last_video_number + 1

    while next_video_number not in video_numbers:
        next_video_number += 1
        if next_video_number > max(video_numbers):
            return None

    return next_video_number

def get_next_schedule_time(upload_log, platform, current_time_set):
    """Determine the next schedule time based on the credentials for the specific platform."""
    now = datetime.now()
    min_time_difference = timedelta(hours=2)  # Minimum 2 hours between uploads

    # Get the most recent upload time for the platform
    last_schedule_time_key = f'last_schedule_time_{platform}'
    last_schedule_time_str = upload_log.get(last_schedule_time_key)
    
    if last_schedule_time_str:
        last_schedule_time = datetime.fromisoformat(last_schedule_time_str)
    else:
        last_schedule_time = now - timedelta(days=1)

    # Find the next available time slot
    for days_ahead in range(7):  # Look up to a week ahead
        for time_slot in current_time_set:
            potential_time = now.replace(hour=time_slot[0], minute=time_slot[1], second=0, microsecond=0) + timedelta(days=days_ahead)
            if potential_time > now and potential_time - last_schedule_time >= min_time_difference:
                # Add a random offset
                schedule_time = potential_time + timedelta(minutes=random.randint(-10, 10))
                return schedule_time, potential_time

    # If no suitable time found within a week, return None
    return None, None

def main(*args):
    global BASE_PATH

    # Check if BASE_PATH is provided as an argument
    if args and isinstance(args[0], str):
        BASE_PATH = args[0]
    elif len(sys.argv) > 1:
        BASE_PATH = sys.argv[1]
    else:
        print("Please provide the niche path as an argument.")
        return

    # Define the paths
    global VIDEO_FOLDER, CREDENTIALS_PATH
    VIDEO_FOLDER = os.path.join(BASE_PATH, 'Meme-Final')
    CREDENTIALS_PATH = os.path.join(BASE_PATH, 'Credentials.json')
    UPLOAD_LOG_PATH = os.path.join(BASE_PATH, 'upload_log.json')

    if not os.path.isfile(CREDENTIALS_PATH):
        print(red(f"Credentials file not found: {CREDENTIALS_PATH}"))
        return
    
    if not os.path.isfile(UPLOAD_LOG_PATH):
        print(red(f"Upload log file not found: {UPLOAD_LOG_PATH}"))
        return

    credentials = load_credentials(CREDENTIALS_PATH)
    upload_log = load_upload_log(UPLOAD_LOG_PATH)

    if not os.path.isdir(VIDEO_FOLDER):
        print(red(f"Video folder {VIDEO_FOLDER} does not exist."))
        return

    # Prompt user to choose a time set
    print("\n")
    print("Available time sets:")
    for i, (set_name, times) in enumerate(TIME_SETS.items(), 1):
        print(f"{i}. {', '.join([f'{h:02d}:{m:02d}' for h, m in times])}")
    print("\n")

    while True:
        try:
            print(dark_grey("Choose a time set (enter the number)"))
            set_choice = int(input("> ").strip())
            if 1 <= set_choice <= len(TIME_SETS):
                current_time_set = list(TIME_SETS.values())[set_choice - 1]
                break
            else:
                print(red("Invalid choice. Please enter a valid number."))
        except ValueError:
            print(red("Invalid input. Please enter a number."))

    print("\n")
    print(bold("How many videos would you like to upload? (1-6)"))
    num_videos = int(input("> ").strip())
    if not (1 <= num_videos <= 6):
        print(red("Invalid number of videos. Must be between 1 and 6."))
        return

    print("\n")
    upload_choice_youtube = input(f"Upload on {bold(red('YouTube'))}? (yes/no): ").strip().lower()
    upload_choice_youtube = 'yes' if upload_choice_youtube == 'x' else 'no' if not upload_choice_youtube else upload_choice_youtube

    upload_choice_tiktok = input(f"Upload on {bold(purple('TikTok'))}? (yes/no): ").strip().lower()
    upload_choice_tiktok = 'yes' if upload_choice_tiktok == 'x' else 'no' if not upload_choice_tiktok else upload_choice_tiktok

    if upload_choice_youtube != 'yes' and upload_choice_tiktok != 'yes':
        print("Okay, not uploading to any platform.")
        print("\n")
        return

    # Get the last made video number
    meme_final_path = os.path.join(BASE_PATH, 'Meme-Final')
    meme_files = [f for f in os.listdir(meme_final_path) if f.startswith('meme_') and f.endswith('_long.mp4')]
    last_made_video = max(meme_files, key=lambda x: int(x.split('_')[1]), default="meme_0000_long.mp4")
    last_made_video_number = last_made_video.split('_')[1]

    def format_datetime(dt_string):
        if dt_string == 'N/A':
            return 'N/A'
        dt = datetime.fromisoformat(dt_string)
        return f"{dt.strftime('%H:%M')} ({dt.strftime('%d %b %Y')})"

    try:    
        youtube_video_number = f"meme_{upload_log['last_video_number_youtube']:04d}"
        youtube_time = format_datetime(upload_log['last_schedule_time_youtube'])
        tiktok_video_number = f"meme_{upload_log['last_video_number_tiktok']:04d}"
        tiktok_time = format_datetime(upload_log['last_schedule_time_tiktok'])
    except (FileNotFoundError, json.JSONDecodeError, KeyError):
        youtube_video_number = 'meme_0000'
        youtube_time = 'N/A'
        tiktok_video_number = 'meme_0000'
        tiktok_time = 'N/A'

    last_video_number_youtube = upload_log['last_video_number_youtube']
    last_video_number_tiktok = upload_log['last_video_number_tiktok']

    print('\n')
    print(dark_grey(f"* Last made video number: {bold(light_grey(f'meme_{last_made_video_number}'))}"))
    print(dark_grey(f"* Last video uploaded to YouTube: {bold(light_grey(youtube_video_number))} — {bold(light_grey(youtube_time))}"))
    print(dark_grey(f"* Last video uploaded to TikTok: {bold(light_grey(tiktok_video_number))} — {bold(light_grey(tiktok_time))}"))
    print('\n')
    
    upload_start_time = datetime.now()

    video_numbers = [int(f.split('_')[1]) for f in os.listdir(VIDEO_FOLDER) if f.endswith('.mp4')]
    if not video_numbers:
        print(red("No video files found in the folder."))
        return

    video_numbers = list(set(video_numbers))  # Remove duplicates
    video_numbers.sort()

    uploaded_videos = []

    for _ in range(num_videos):
        if upload_choice_youtube == 'yes':
            next_video_number_youtube = get_next_video_number(last_video_number_youtube, video_numbers)
            if next_video_number_youtube is None:
                print(red("No more videos available for YouTube upload."))
                break
            video_file_name_short = os.path.join(VIDEO_FOLDER, f'meme_{next_video_number_youtube:04d}_youtube.mp4')
            
            schedule_time, rounded_time = get_next_schedule_time(upload_log, 'youtube', current_time_set)
            if schedule_time is None:
                print(red("Unable to find a suitable upload time for YouTube. Skipping."))
                continue

            print("\n")
            print("----------")
            print(f"Scheduling {bold(f'meme_{next_video_number_youtube:04d}_short.mp4')} @ {bold(f'{schedule_time}')}")
            if upload_video_to_youtube(video_file_name_short, schedule_time, credentials):
                upload_log['last_video_number_youtube'] = next_video_number_youtube
                upload_log['last_schedule_time_youtube'] = rounded_time.isoformat()
                save_log(upload_log, UPLOAD_LOG_PATH)  # Save after YouTube upload
                uploaded_videos.append((f'meme_{next_video_number_youtube:04d}_youtube.mp4', schedule_time, 'YouTube'))
                last_video_number_youtube = next_video_number_youtube
            else:
                logger.error(red(f"Failed to upload video {next_video_number_youtube} to YouTube"))

        if upload_choice_tiktok == 'yes':
            next_video_number_tiktok = get_next_video_number(last_video_number_tiktok, video_numbers)
            if next_video_number_tiktok is None:
                print(red("No more videos available for TikTok upload."))
                break
            video_file_name_long = os.path.join(VIDEO_FOLDER, f'meme_{next_video_number_tiktok:04d}_long.mp4')
            
            schedule_time, rounded_time = get_next_schedule_time(upload_log, 'tiktok', current_time_set)
            if schedule_time is None:
                print(red("Unable to find a suitable upload time for TikTok. Skipping."))
                continue

            print(f"Scheduling {bold(f'meme_{next_video_number_tiktok:04d}_long.mp4')} @ {bold(f'{schedule_time}')}")
            if upload_video_to_tiktok(video_file_name_long, schedule_time, credentials):
                upload_log['last_video_number_tiktok'] = next_video_number_tiktok
                upload_log['last_schedule_time_tiktok'] = rounded_time.isoformat()
                save_log(upload_log, UPLOAD_LOG_PATH)  # Save after TikTok upload
                uploaded_videos.append((f'meme_{next_video_number_tiktok:04d}_long.mp4', schedule_time, 'TikTok'))
                last_video_number_tiktok = next_video_number_tiktok
            else:
                logger.error(red(f"Failed to upload video {next_video_number_tiktok} to TikTok"))

    print("----------")
    print("\n")
    upload_end_time = datetime.now()
    total_time = upload_end_time - upload_start_time

    print(f"Videos uploaded:")
    for video, schedule_time, platform in uploaded_videos:
        if platform == "YouTube":
            platform = (red(platform))
        elif platform == "TikTok":
            platform = (purple(platform))
        else:
            platform = platform

        print(f"\t{bold(cyan(video))} on {bold(platform)} @ {bold(schedule_time.strftime('%Y-%m-%d %H:%M'))}")
    print("\n")
    minutes, seconds = divmod(total_time.total_seconds(), 60)
    print(f"Total time taken: {cyan(bold(f'{int(minutes)} minutes and {int(seconds)} seconds'))}")


if __name__ == "__main__":
    main()

