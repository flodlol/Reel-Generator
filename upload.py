import os
import json
import random
import logging
from datetime import datetime, timedelta

from utils import bold, red
from upload_youtube import upload_video  # Import the upload function

# Configure logging
formatter = logging.Formatter(
    '%(asctime)s %(message)s',
    datefmt='[%H:%M:%S]'
)

# Set up logging to the console
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
console_handler.setLevel(logging.INFO)

# Set up logging to a file
file_handler = logging.FileHandler('upload.log')
file_handler.setFormatter(formatter)
file_handler.setLevel(logging.INFO)

# Get the logger and set the level
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(console_handler)
logger.addHandler(file_handler)

# Paths and constants
LOG_FILE_PATH = os.path.join(os.path.dirname(__file__), 'upload_log.json')
VIDEO_FOLDER = os.path.join(os.path.dirname(__file__), 'Meme-Generation', 'Meme-Final')

# Predefined upload times (in 24-hour format)
PREDEFINED_TIMES = [
    (0, 30),   # 00:30 AM
    (13, 30),  # 01:30 PM
    (21, 0)    # 9:00 PM
]

def load_log():
    """Load the upload log from a JSON file."""
    if os.path.isfile(LOG_FILE_PATH):
        with open(LOG_FILE_PATH, 'r') as file:
            return json.load(file)
    return {}

def save_log(log_data):
    """Save the upload log to a JSON file."""
    with open(LOG_FILE_PATH, 'w') as file:
        json.dump(log_data, file, indent=4)

def get_next_schedule_time(log_data):
    """Determine the next schedule time based on the log data."""
    now = datetime.now()
    
    # Retrieve last scheduled time from the log data, or default to now if not available
    last_schedule_time = datetime.fromisoformat(log_data.get('last_schedule_time', now.isoformat()))
    
    # Calculate the index for the current last scheduled time in the predefined list
    current_time_index = next((i for i, t in enumerate(PREDEFINED_TIMES)
                               if last_schedule_time.hour == t[0] and last_schedule_time.minute == t[1]), None)
    
    if current_time_index is None:
        # If last scheduled time was not found in predefined times, start with the first index
        next_time_index = 0
    else:
        # Calculate the next index, wrapping around if necessary
        next_time_index = (current_time_index + 1) % len(PREDEFINED_TIMES)
    
    # Choose the next predefined time
    next_time = PREDEFINED_TIMES[next_time_index]
    
    # Create the scheduled time based on the predefined time and add a random offset
    schedule_time = now.replace(hour=next_time[0], minute=next_time[1], second=0, microsecond=0) + timedelta(minutes=random.randint(-10, 10))
    
    # If the scheduled time is in the past, move it to the next day
    while schedule_time <= now:
        schedule_time += timedelta(days=1)
    
    # If the scheduled time is still before or equal to the last scheduled time, move it to the next day
    while schedule_time <= last_schedule_time:
        schedule_time += timedelta(days=1)
    
    # Log only the predefined time without the random offset
    rounded_time = now.replace(hour=next_time[0], minute=next_time[1], second=0, microsecond=0)
    
    return schedule_time, rounded_time

def get_next_video_number(log_data, video_numbers):
    """Determine the next video number based on the log data."""
    if log_data:
        last_video_number = log_data.get('last_video_number', -1)
        next_video_number = last_video_number + 1
        if next_video_number in video_numbers:
            return next_video_number
    return min(video_numbers) if video_numbers else None

def main():
    if not os.path.isdir(VIDEO_FOLDER):
        print(f"Video folder {VIDEO_FOLDER} does not exist.")
        return
    
    print("\n")
    num_videos = int(input("How many videos would you like to upload? (1-6): ").strip())
    if not (1 <= num_videos <= 6):
        print("Invalid number of videos. Must be between 1 and 6.")
        return
    
    upload_choice = input("Upload on YouTube? (yes/no): ").strip().lower()
    if upload_choice != 'yes':
        print("Okay, not uploading to YouTube.")
        print("\n")
        return

    log_data = load_log()
    upload_start_time = datetime.now()
    
    video_numbers = [int(f.split('_')[1]) for f in os.listdir(VIDEO_FOLDER) if f.endswith('.mp4')]
    if not video_numbers:
        print("No video files found in the folder.")
        return

    video_numbers.sort()
    
    uploaded_videos = []  # List to store the actual uploaded video filenames and schedule times

    for _ in range(num_videos):
        next_video_number = get_next_video_number(log_data, video_numbers)
        if not next_video_number:
            print("No valid video number found.")
            return
        
        video_file_name = os.path.join(VIDEO_FOLDER, f'meme_{next_video_number}_short.mp4')
        schedule_time, rounded_time = get_next_schedule_time(log_data)
        
        print("----------")
        # Log the schedule
        print(f"Scheduling {bold(f'meme_{next_video_number}_short.mp4')} @ {bold(f'{schedule_time}')}")
        
        if upload_video(video_file_name, schedule_time):
            log_data['last_video_number'] = next_video_number
            log_data['last_schedule_time'] = rounded_time.isoformat()  # Log the rounded time
            save_log(log_data)
            uploaded_videos.append((f'meme_{next_video_number}_short.mp4', schedule_time))
        else:
            logging.error(red(f"Failed to upload video {next_video_number}"))
    
    print("----------")
    upload_end_time = datetime.now()
    total_time = upload_end_time - upload_start_time
    
    print(f"Videos uploaded:")
    for video, schedule_time in uploaded_videos:
        print(f"\t{bold(video)} @ {bold(schedule_time.strftime('%Y-%m-%d %H:%M:%S'))}")
    print("\n")
    minutes, seconds = divmod(total_time.total_seconds(), 60)
    print(f"Total time taken: {bold(f'{int(minutes)} minutes and {int(seconds)} seconds')}")
    print("----------")

if __name__ == "__main__":
    main()
