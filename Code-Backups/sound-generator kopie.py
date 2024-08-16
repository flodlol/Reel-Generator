import os
import yt_dlp as ytdlp

# Define paths
mp3_folder = 'TikTok-Sounds'
urls_file = 'TikTok-Sounds.txt'

# Create the output folder if it doesn't exist
os.makedirs(mp3_folder, exist_ok=True)

# Download TikTok video directly as MP3
def download_tiktok_as_mp3(url, number):
    ydl_opts = {
        'format': 'bestaudio/best',  # Download best audio
        'outtmpl': os.path.join(mp3_folder, f'audio-video_{number}.mp3'),
        'noplaylist': True,
        'quiet': True  # Suppress output from yt_dlp
    }
    with ytdlp.YoutubeDL(ydl_opts) as ydl:
        try:
            ydl.download([url])
            return os.path.join(mp3_folder, f'audio-video_{number}.mp3')
        except Exception as e:
            return None

# Process URLs from file with sequential numbering
def process_urls_from_file():
    with open(urls_file, 'r') as file:
        urls = file.readlines()
    
    urls = [url.strip() for url in urls if url.strip()]
    total_urls = len(urls)
    successful_downloads = 0
    failed_downloads = 0
    
    for i, url in enumerate(urls, start=1):
        mp3_path = download_tiktok_as_mp3(url, i)
        if mp3_path:
            successful_downloads += 1
        else:
            failed_downloads += 1
    
    print(f"Total URLs processed: {total_urls}")
    # print(f"Successful downloads: {successful_downloads}")
    # print(f"Failed downloads: {failed_downloads}")

# Main function
def main():
    try:
        process_urls_from_file()
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
