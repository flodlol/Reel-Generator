import json
import os
import random
import time
import logging
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from utils import bold, cyan, green, red

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
PROFILE_PATH = "/Users/flod/Library/Application Support/Firefox/Profiles/7d6h1zfq.MeowChiefShow"
YOUTUBE_UPLOAD_URL = 'https://www.youtube.com/upload'
LOG_FILE_PATH = os.path.join(os.path.dirname(__file__), 'upload_log.json')
VIDEO_FOLDER = os.path.join(os.path.dirname(__file__), 'Meme-Generation', 'Meme-Final')
MIN_INTERVAL = 230  # Minimum minutes between uploads
MAX_INTERVAL = 250  # Maximum minutes between uploads

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

def get_next_video_number(log_data, video_numbers):
    """Determine the next video number based on the log data."""
    if log_data:
        last_video_number = log_data.get('last_video_number', -1)
        next_video_number = last_video_number + 1
        if next_video_number in video_numbers:
            return next_video_number
    return min(video_numbers) if video_numbers else None

def get_next_schedule_time(log_data):
    """Determine the next schedule time based on the log data."""
    if log_data:
        last_schedule_time = datetime.fromisoformat(log_data.get('last_schedule_time'))
        next_schedule_time = last_schedule_time + timedelta(minutes=random.randint(MIN_INTERVAL, MAX_INTERVAL))
    else:
        next_schedule_time = datetime.now() + timedelta(minutes=random.randint(MIN_INTERVAL, MAX_INTERVAL))
    
    # Ensure the time is correctly adjusted to the next day if it overflows the current day
    if next_schedule_time.day != last_schedule_time.day:
        next_schedule_time = next_schedule_time.replace(day=last_schedule_time.day + 1)
    
    return next_schedule_time

def upload_video_youtube(video_file_name, schedule_time):
    """Upload a video to YouTube and log the process."""
    logging.info(green(f"Starting the upload process for file: {video_file_name}"))
    
    if not os.path.isfile(video_file_name):
        logging.error(red(f"Video file {video_file_name} not found."))
        return False
    
    # Setup Firefox options
    options = Options()
    options.profile = PROFILE_PATH

    # Initialize the Firefox WebDriver with the profile
    driver = webdriver.Firefox(options=options)
    
    try:
        # Open YouTube upload page
        logging.info(green("Opening YouTube upload page."))
        driver.get(YOUTUBE_UPLOAD_URL)
        
        # Wait for the upload input field to be present
        logging.info(green("Waiting for the upload input field to be present."))
        upload_input = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, "//input[@type='file']"))
        )
        
        # Get the absolute path of the video file
        video_file_path = os.path.abspath(video_file_name)
        
        # Upload the video file
        logging.info(f"Uploading video file: {video_file_path}")
        upload_input.send_keys(video_file_path)
        
        # Wait for the upload to start
        logging.info(green("Waiting for video upload to start."))
        WebDriverWait(driver, 120).until(
            EC.presence_of_element_located((By.XPATH, "//ytcp-video-upload-progress"))
        )
        
        # Wait for the video upload to complete
        logging.info(green("Waiting for video upload to complete."))
        WebDriverWait(driver, 300).until(
            EC.invisibility_of_element_located((By.XPATH, "//ytcp-video-upload-progress"))
        )
        logging.info(green("Video upload completed."))
        
        # Set 'No, it's not made for kids'
        logging.info(green("Selecting 'No, it's not made for kids' option."))
        WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.XPATH, "//tp-yt-paper-radio-button[@name='VIDEO_MADE_FOR_KIDS_NOT_MFK']"))
        ).click()
        
        # Click 'Next' button (3 times)
        for i in range(3):
            logging.info(green(f"Clicking 'Next' button ({i + 1}/3)."))
            WebDriverWait(driver, 30).until(
                EC.element_to_be_clickable((By.XPATH, "//ytcp-button[@id='next-button']"))
            ).click()
        

        # Set the schedule time using the provided method
        logging.info(green("Opening the schedule menu."))
        WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.XPATH, "//ytcp-icon-button[@id='second-container-expand-button']"))
        ).click()


        # Open date_picker
        logging.info(green("Clicking on the date field."))
        date_field = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.XPATH, "//ytcp-text-dropdown-trigger[@id='datepicker-trigger']"))
        )
        date_field.click()

        date_input = driver.find_element(By.CSS_SELECTOR, "input.tp-yt-paper-input")
        date_input.clear()
        logging.info(f"Changing the date to {bold(schedule_time.strftime('%b %d, %Y'))}")
        # Transform date into required format: Mar 19, 2021
        date_input.send_keys(schedule_time.strftime("%b %d, %Y"))
        date_input.send_keys(Keys.RETURN)
        logging.info(f"Successfully changed the date")

     
        # Click on the time field
        logging.info(green("Clicking on the time field."))
        time_field = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.XPATH, "//ytcp-form-input-container[@id='time-of-day-container']"))
        )
        time_field.click()

        time_input = driver.find_element(By.CSS_SELECTOR, "input.tp-yt-paper-input")
        time_input.clear()
        logging.info(f"Changing the time to {bold(schedule_time.strftime('%H:%M'))}")
        time_input.send_keys(schedule_time.strftime('%H:%M'))
        time_input.send_keys(Keys.RETURN)
        logging.info(f"Successfully changed the time")


        # Wait for 2 seconds before clicking 'Schedule'
        logging.info(green("Waiting for 2 seconds before clicking 'Schedule' button."))
        time.sleep(2)
        
        # Click 'Schedule' button
        logging.info(green("Clicking 'Schedule' button to finalize the upload."))
        WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.XPATH, "//ytcp-button[@id='done-button']"))
        ).click()
        
        # Wait 3 seconds to ensure the schedule operation completes
        logging.info(green("Waiting for 3 seconds before closing the browser."))
        time.sleep(3)
        
        logging.info(green("Upload process completed successfully."))
        return True
        
    except Exception as e:
        logging.error(red(f"An error occurred during the upload process: {e}"))
        return False
    
    finally:
        # Close the browser
        logging.info("Closing the browser.")
        driver.quit()

def main():
    # Check if VIDEO_FOLDER exists
    if not os.path.isdir(VIDEO_FOLDER):
        print(f"Video folder {VIDEO_FOLDER} does not exist.")
        return
    
    print("\n")
    num_videos = int(input(cyan("How many videos would you like to upload? (1-6): ").strip()))
    if not (1 <= num_videos <= 6):
        print("Invalid number of videos. Must be between 1 and 6.")
        return
    
    upload_choice = input(cyan("Upload on YouTube? (yes/no): ").strip().lower())
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
    
    uploaded_videos = []  # List to store the actual uploaded video filenames

    for _ in range(num_videos):
        next_video_number = get_next_video_number(log_data, video_numbers)
        if not next_video_number:
            print("No valid video number found.")
            return
        
        video_file_name = os.path.join(VIDEO_FOLDER, f'meme_{next_video_number}_short.mp4')
        schedule_time = get_next_schedule_time(log_data)
        
        print("----------")
        # Log the schedule
        print(f"Starting uploading to {red(bold('YouTube'))}")
        print(f"Scheduling {bold(f"meme_{next_video_number}_short.mp4")} @ {bold(f"{schedule_time}")}")
        
        if upload_video_youtube(video_file_name, schedule_time):
            log_data['last_video_number'] = next_video_number
            log_data['last_schedule_time'] = schedule_time.isoformat()
            save_log(log_data)
            uploaded_videos.append(f'meme_{next_video_number}_short.mp4')
        else:
            logging.error(red(f"Failed to upload video {next_video_number}"))
    
    print("----------")
    upload_end_time = datetime.now()
    total_time = upload_end_time - upload_start_time
    
    print(f"Videos uploaded:")
    for video in uploaded_videos:
        print(f"\t{bold(video)}")
    print("\n")
    print(f"Total time taken: {bold(f"{total_time}")}")
    print("----------")

if __name__ == "__main__":
    main()
