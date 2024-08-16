import os
import random
import textwrap
from PIL import Image, ImageDraw, ImageFont

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
        font = ImageFont.truetype("arial.ttf", font_size)
    except IOError:
        print("Custom font not found. Using default font.")
        font = ImageFont.load_default()
        font_size = 20  # Default font size is much smaller, you might need to adjust this

    # Create a drawing context for the black background
    draw = ImageDraw.Draw(black_background)

    # Set white box width and height
    text_box_width = img.width  # White box width matches meme image width
    max_text_width = text_box_width - 60  # Allow some padding
    # Wrap text to fit within the white box width
    wrapped_text = textwrap.fill(text, width=(text_box_width // font_size * 2))  # Adjust width for wrapping
    
    # Create a drawing context for the white box
    text_box = Image.new('RGB', (text_box_width, 1), color='white')  # Start with height of 1 to calculate text height
    draw = ImageDraw.Draw(text_box)
    
    # Get the text bounding box
    text_bbox = draw.textbbox((0, 0), wrapped_text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    
    # Update the height of the white box
    box_padding = 30  # Padding around the text
    box_height = (text_height + 2 * box_padding)
    text_box = Image.new('RGB', (text_box_width, box_height), color='white')
    draw = ImageDraw.Draw(text_box)
    
    # Center the text within the white box
    text_x = (text_box_width - text_width) // 2
    text_y = (box_height - text_height) // 2
    draw.text((text_x, text_y), wrapped_text, font=font, fill='black')

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

    # Save the final image
    meme_filename = os.path.join(output_folder, "meme_{}.jpg".format(random.randint(1, 10000)))
    black_background.save(meme_filename)

    return meme_filename

# Main function to generate a meme
def generate_meme():
    image_path = choose_random_image(cat_images_folder)
    quote = choose_random_quote(quotes_file)
    meme_path = create_meme_with_text(image_path, quote, meme_images_folder)
    print("Meme created and saved at: {}".format(meme_path))

# Run the meme generator
if __name__ == "__main__":
    generate_meme()
