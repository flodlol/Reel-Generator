import os
import time
import logging
import json
import traceback

from datetime import datetime
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException


from utils import bold, green, red, cyan, purple, pink
from utils import shorten_path_from_project_meme
from utils import clear_text


# Extracts the month and day from a string date in format "MM/DD/YYYY".
def extract_month_day(string_date):
    try:
        # Split the string date into components using "/" as delimiter
        month, day, year = string_date.split("/")

        # Convert month string to full month name (optional)
        month_names = {
            "01": "January",
            "02": "February",
            "03": "March",
            "04": "April",
            "05": "May",
            "06": "June",
            "07": "July",
            "08": "August",
            "09": "September",
            "10": "October",
            "11": "November",
            "12": "December",
        }
        month = month_names.get(month, month)  # Use original month string if not found in dictionary

        return month, day
    except ValueError:
        # Handle invalid date format
        logging.error(red("Invalid date format. Please use MM/DD/YYYY."))
        return None, None


# Function to find and click on the specified day number
def find_and_click_day(driver, day_number):
    # Convert day_number to string to ensure comparison works
    day_str = str(day_number)

    # Wait for the calendar days to be present using the correct selector
    days_of_the_month = driver.find_elements(By.CSS_SELECTOR, "span.day")

    # Find the index of the day with text "1"
    start_index = None
    for index, day in enumerate(days_of_the_month):
        if day.text == "1":
            start_index = index
            break

    # If "1" is found, traverse the calendar starting from the next day
    if start_index is not None:
        for day in days_of_the_month[start_index:]:
            if day.text == day_str:
                day.click()
                logging.info(f"Clicked on day {bold(day_number)}")
                break
    else:
        logging.error(red("The calendar does not contain day 1"))

# Parses a time string in the format "HH:MM" and returns a tuple of (hour, minute).
# Args:time_string: The time string to parse (e.g., "8:00", "16:55").
# Returns: A tuple of (hour, minute) integers, or None if the format is invalid.
# Raises: ValueError: If the time string is in an invalid format.
def parse_time_string(time_string):
    try:
        # Split the string by colon (':') to separate hours and minutes
        hour, minute = time_string.split(":")

        # Convert hour and minute strings to integers
        hour = int(hour)
        minute = int(minute)

        # Validate the parsed values (0-23 for hour, 0-59 for minute)
        if 0 <= hour <= 23 and 0 <= minute <= 59:
            return hour, minute
        else:
            raise ValueError(
                "Invalid time format. Hour must be between 0 and 23, minute between 0 and 59."
            )
    except ValueError as e:
        logging.error(red(f"Error parsing time string: {e}"))
        return None

def select_time_from_dropdown(driver, time_scrollbar_element, time_string):
    actions = ActionChains(driver)
    actions.move_to_element(time_scrollbar_element).perform()

    # Convert the time_string to string if it's not already
    time_string = str(time_string)

    # Scroll up loop
    initial_scroll_position = int(
        driver.execute_script(
            "return arguments[0].scrollTop", time_scrollbar_element
        )
    )

    for i in range(initial_scroll_position, 0, -100):
        driver.execute_script(
            "arguments[0].scrollTop -= 100", time_scrollbar_element
        )
        try:
            options = time_scrollbar_element.find_elements(
                By.CSS_SELECTOR, "div.tiktok-timepicker-option-item"
            )
            if options:
                wait = WebDriverWait(driver, 0)  # Set a timeout of 1 second
                wait.until(EC.element_to_be_clickable(options[int(time_string)]))
                options[int(time_string)].click()
                break
        except:
            continue

    scroll_height = driver.execute_script(
        "return arguments[0].scrollHeight", time_scrollbar_element
    )

    # Scroll down loop
    for i in range(0, scroll_height, 100):
        driver.execute_script(
            "arguments[0].scrollTop += 100", time_scrollbar_element
        )
        try:
            options = time_scrollbar_element.find_elements(
                By.CSS_SELECTOR, "div.tiktok-timepicker-option-item"
            )
            if options:
                wait = WebDriverWait(driver, 0)  # Set a timeout of 1 second
                wait.until(EC.element_to_be_clickable(options[int(time_string)]))
                options[int(time_string)].click()
                break
        except:
            continue


def get_description_from_json(video_file_name, base_path):
    """Read the description from the corresponding JSON file."""
    video_number = video_file_name.split('_')[1].split('.')[0]
    json_file_name = f"meme_{video_number}.json"
    json_file_path = os.path.join(base_path, 'Meme-Description', json_file_name)
    
    try:
        with open(json_file_path, 'r') as json_file:
            data = json.load(json_file)
            return data.get('description', '')
    except FileNotFoundError:
        logging.error(red(f"Description file not found: {json_file_path}"))
        return ''
    except json.JSONDecodeError:
        logging.error(red(f"Error decoding JSON file: {json_file_path}"))
        return ''
    

def _set_description(driver, description: str) -> None:
    """Sets the description of the video"""
    
    if not description:
        logging.info("No description provided.")
        return

    # Remove any characters outside the BMP range (emojis, etc) & Fix accents
    description = description.encode("utf-8", "ignore").decode("utf-8")

    saved_description = description  # save the description in case it fails

    try:
        # Wait for the description field to be present
        logging.info("Waiting for description field")
        desc = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, "//div[@contenteditable='true']")
            )
        )
        logging.info("Description field found")

        logging.info("Clicking on description field")
        desc.click()

        time.sleep(1)

        # Clear existing text
        video_filename = os.path.basename(description)

        logging.info("Clearing the existing file name in description.")
        for _ in range(len(video_filename)):
            desc.send_keys(Keys.BACKSPACE)
        
        time.sleep(1)

        time.sleep(1)

        # Split the description into words for processing
        words = description.split(" ")

        for word in words:
            if word.startswith("#"):
                # Handle hashtags
                logging.info(f"Adding hashtag: {word}")
                desc.send_keys(word)
                desc.send_keys(" " + Keys.BACKSPACE)

                WebDriverWait(driver, 30).until(
                    EC.presence_of_element_located(
                        (By.XPATH, "//div[contains(@class, 'mention-list-popover')]")
                    )
                )
                desc.send_keys(Keys.ENTER)

            elif word.startswith("@"):
                # Handle mentions
                logging.info(green(f"Adding mention: {word}"))
                desc.send_keys(word)
                desc.send_keys(" ")
                time.sleep(1)
                desc.send_keys(Keys.BACKSPACE)

                WebDriverWait(driver, 30).until(
                    EC.presence_of_element_located(
                        (By.XPATH, "//span[contains(@class, 'user-id')]")
                    )
                )

                found = False
                waiting_interval = 0.5
                timeout = 5
                start_time = time.time()

                while not found and (time.time() - start_time < timeout):
                    user_id_elements = driver.find_elements(
                        By.XPATH, "//span[contains(@class, 'user-id')]"
                    )
                    time.sleep(1)

                    for i, user_id_element in enumerate(user_id_elements):
                        if user_id_element.is_enabled:
                            username = user_id_element.text.split(" ")[0]
                            if username.lower() == word[1:].lower():
                                found = True
                                logging.info("Matching User found : Clicking User")
                                for _ in range(i):
                                    desc.send_keys(Keys.DOWN)
                                desc.send_keys(Keys.ENTER)
                                break

                    if not found:
                        logging.info(f"No match. Waiting for {waiting_interval} seconds...")
                        time.sleep(waiting_interval)

            else:
                # Add regular words
                desc.send_keys(word + " ")

        logging.info("Description set successfully.")

    except Exception as exception:
        logging.error(red(f"Failed to set description. Error type: {type(exception).__name__}"))
        logging.error(red(f"Error message: {str(exception)}"))
        logging.error(red(f"Error traceback: {traceback.format_exc()}"))
        logging.error(red(f"Failed to set description: {exception}"))
        clear_text(desc)  # Clear the text field before retrying
        desc.send_keys(saved_description)
        logging.info("Fallback: description added without formatting.")


def upload_video_to_tiktok(video_file_name_long, schedule_time, credentials):
    """Upload a video to TikTok and log the process."""
    print(f"Starting uploading to {purple(bold('TikTok'))}")
    logging.info(green(f"Starting the upload process for file: {bold(shorten_path_from_project_meme(video_file_name_long))}"))

    if not os.path.isfile(video_file_name_long):
        logging.error(red(f"Video file {video_file_name_long} not found."))
        return False

    # Setup Firefox options
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.profile = credentials.get('profile_path')  # Use the profile path from credentials

    if not options.profile:
        logging.error(red("Profile path not found in credentials."))
        return False

    # Initialize the Firefox WebDriver with the profile
    driver = webdriver.Firefox(options=options)

    try:
        # Open TikTok upload page
        logging.info(green("Opening TikTok upload page."))
        driver.get('https://www.tiktok.com/creator-center/upload?lang=en')

        # Wait for the upload input field to be present
        logging.info(green("Waiting for the upload input field to be present."))
        upload_input = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, "//input[@type='file']"))
        )

        # Upload the video file
        logging.info(f"Uploading video file: {bold(shorten_path_from_project_meme(video_file_name_long))}")
        upload_input.send_keys(video_file_name_long)
        
        # Remove split window if it appears
        try:
            WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[./div[text()='Not now']]"))
            ).click()
            logging.info(green("Removed split window."))
        except TimeoutException:
            logging.info(green("Split window not found. Continuing..."))

        # Get the description from the JSON file
        base_path = os.path.dirname(os.path.dirname(video_file_name_long))
        description = get_description_from_json(os.path.basename(video_file_name_long), base_path)

        # Set the description
        try:
            logging.info(green("Setting video description."))
            _set_description(driver, description)
        except Exception as e:
            logging.error(red(f"Error in setting description: {str(e)}"))
            logging.error(red(f"Traceback: {traceback.format_exc()}"))
        time.sleep(10)


        # Clicks on "schedule" checkbox
        logging.info(green("Opening schedule menu"))
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '[value="schedule"]'))
        ).click()

        # Locate all elements with the class "tiktok-timepicker-disable-scrollbar"
        logging.info(green("Opening the timepicker menu"))
        time_scrollbar_elements = driver.find_elements(
            By.CSS_SELECTOR, "div.tiktok-timepicker-disable-scrollbar"
        )

        # Stores the date and time drop down list locators
        time_and_date_lists = driver.find_elements(
            By.CSS_SELECTOR, "input.TUXTextInputCore-input"
        )

        # Stores the hour and minute from Script Time
        hour = schedule_time.strftime("%H")
        minute = int(schedule_time.strftime("%M")) // 5
        minute = str(minute).zfill(2)  # Ensure it’s two digits

        if hour is not None and minute is not None:
            logging.info(f"Changing the time to {bold(f'{hour}:{minute}')}")
        else:
            logging.info(red("Invalid time string format."))

        # Clicks on "time" dropdown list
        logging.info(green("Clicking the 'time' dropdown list"))
        time_and_date_lists[0].click()

        # Selects the hour from the dropdown list
        logging.info(green("Selecting the hour from the dropdown list"))
        select_time_from_dropdown(driver, time_scrollbar_elements[0], hour)

        # Clicks on "time" dropdown list
        logging.info(green("Clicking the 'time' dropdown list"))
        time_and_date_lists[0].click()

        # Selects the minute from the dropdown list
        logging.info(green("Selecting the minute from the dropdown list"))
        select_time_from_dropdown(driver, time_scrollbar_elements[1], minute)

        # Clicks on "date" dropdown list
        logging.info(green("Clicking the 'date' dropdown list"))
        time_and_date_lists[1].click()

        formatted_date = schedule_time.strftime("%m/%d/%Y")
        logging.info(pink(formatted_date))

        # Get the month and the day from date String
        month, day = extract_month_day(formatted_date)

        while True:
            # Wait for the month header element to be present
            month_header_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.month-header-wrapper"))
            )

            # Get the text of the month header element
            logging.info(green("Selecting the month"))
            month_text = month_header_element.text
            logging.info(f"Month header text: {bold(month_text)}")

            # Check if the month text is correct
            if month in month_text:
                logging.info("Month found!")
                break

            # Wait for the arrow elements to be present
            arrow_elements = driver.find_elements("span.arrow")
            # Click the second arrow (right arrow)
            arrow_elements[1].click()

        # Clicks on the day on pop up calendar
        logging.info(green("Selecting the day on pop up calendar"))
        find_and_click_day(driver, day)
        time.sleep(2)

        # Clicks on "schedule" button
        logging.info(green("Clicking on the 'schedule' button"))
        WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button.TUXButton--primary"))
        ).click()

        logging.debug(green("Video posted successfully"))
        return True

    except Exception as e:
        logging.error(red(f"An error occurred during the upload process: {e}"))
        logging.error(red(f"Traceback: {traceback.format_exc()}"))
        return False

    finally:
        # Close the browser
        logging.info("Closing the browser.")
        driver.quit()




class FailedToUpload(Exception):
    """A video failed to upload"""

    def __init__(self, message=None):
        super().__init__(message or self.__doc__)