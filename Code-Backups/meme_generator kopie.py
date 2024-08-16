import os
import random
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
        quotes = f.readlines()
    if not quotes:
        raise ValueError("No quotes found in the file")
    return random.choice(quotes).strip()

# Function to create a meme
def create_meme(image_path, text, output_folder):
    # Load image
    img = Image.open(image_path)
    draw = ImageDraw.Draw(img)

    # Load a font
    try:
        font = ImageFont.truetype("arial.ttf", 40)  # You can adjust the font and size
    except IOError:
        font = ImageFont.load_default()

    # Calculate text size and position using textbbox
    bbox = draw.textbbox((0, 0), text, font)  # Get bounding box of the text
    textwidth = bbox[2] - bbox[0]  # Width of the bounding box
    textheight = bbox[3] - bbox[1]  # Height of the bounding box
    width, height = img.size
    x = (width - textwidth) / 2
    y = height - textheight - 10  # Padding from the bottom

    # Add text to the image
    draw.text((x, y), text, font=font, fill="white")

    # Save the meme image
    meme_filename = os.path.join(output_folder, "meme_{}.jpg".format(random.randint(1, 10000)))
    img.save(meme_filename)

    return meme_filename

# Main function to generate a meme
def generate_meme():
    image_path = choose_random_image(cat_images_folder)
    quote = choose_random_quote(quotes_file)
    meme_path = create_meme(image_path, quote, meme_images_folder)
    print("Meme created and saved at: {}".format(meme_path))

# Run the meme generator
if __name__ == "__main__":
    generate_meme()
