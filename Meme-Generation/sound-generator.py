import os
import yt_dlp as ytdlp

# Define paths
mp3_folder = 'TikTok-Sounds'
urls_file = 'TikTok-Sounds.txt'
downloaded_file = 'downloaded_urls.txt'

# Create the output folder if it doesn't exist
os.makedirs(mp3_folder, exist_ok=True)

# Load already downloaded URLs
def load_downloaded_urls():
    if os.path.exists(downloaded_file):
        with open(downloaded_file, 'r') as file:
            return set(line.strip() for line in file)
    return set()

# Save a URL as downloaded
def save_downloaded_url(url):
    with open(downloaded_file, 'a') as file:
        file.write(url + '\n')

# Generate a unique filename for each new MP3
def get_next_mp3_filename():
    existing_files = [f for f in os.listdir(mp3_folder) if f.startswith('audio_') and f.endswith('.mp3')]
    if existing_files:
        existing_numbers = [int(f.split('_')[1].split('.')[0]) for f in existing_files]
        next_number = max(existing_numbers) + 1
    else:
        next_number = 1
    return os.path.join(mp3_folder, f'audio_{next_number}.mp3')

# Download TikTok video directly as MP3
def download_tiktok_as_mp3(url):
    mp3_filename = get_next_mp3_filename()
    ydl_opts = {
        'format': 'bestaudio/best',  # Download best audio
        'outtmpl': mp3_filename,
        'noplaylist': True,
        'quiet': True  # Suppress output from yt_dlp
    }
    with ytdlp.YoutubeDL(ydl_opts) as ydl:
        try:
            ydl.download([url])
            return mp3_filename
        except Exception:
            return None

# Process URLs from file with sequential numbering
def process_urls_from_file():
    downloaded_urls = load_downloaded_urls()
    
    with open(urls_file, 'r') as file:
        urls = file.readlines()
    
    urls = [url.strip() for url in urls if url.strip()]
    total_urls = len(urls)
    new_mp3_files = 0

    for url in urls:
        if url in downloaded_urls:
            continue
        
        mp3_path = download_tiktok_as_mp3(url)
        
        if mp3_path:
            save_downloaded_url(url)
            new_mp3_files += 1

    # Count total MP3 files in the output folder
    total_mp3_files = len([f for f in os.listdir(mp3_folder) if f.startswith('audio_') and f.endswith('.mp3')])

    # Print summary
    print("\n" + "-"*50)
    print(f"New MP3s added: {new_mp3_files}")
    print(f"Total MP3s in folder: {total_mp3_files}")
    print("\n" + "-"*50)

# Main function
def main():
    try:
        process_urls_from_file()
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
