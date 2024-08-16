import os
import time
import logging
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from utils import bold, green, red, cyan

# Paths and constants
PROFILE_PATH = "/Users/flod/Library/Application Support/Firefox/Profiles/7d6h1zfq.MeowChiefShow"
YOUTUBE_UPLOAD_URL = 'https://www.youtube.com/upload'
VIDEO_FOLDER = os.path.join(os.path.dirname(__file__), 'Meme-Generation', 'Meme-Final')

def upload_video(video_file_name, schedule_time):
    """Upload a video to YouTube and log the process."""
    print(f"Starting uploading to {red(bold('YouTube'))}")
    logging.info(green(f"Starting the upload process for file: {video_file_name}"))
    
    if not os.path.isfile(video_file_name):
        logging.error(red(f"Video file {video_file_name} not found."))
        return False
    
    # Setup Firefox options for Heroku
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.profile = PROFILE_PATH  # Use the correct profile path for Heroku

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
