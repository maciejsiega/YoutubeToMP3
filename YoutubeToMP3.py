"""
Version 1.1
"""

import os
import tkinter as tk
from tkinter import filedialog
from pytube import YouTube
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_audio
import ssl
import eyed3
import logging
import threading
import queue
import time
import re

# Disable SSL certificate verification
ssl._create_default_https_context = ssl._create_unverified_context

# Define download directory
DOWNLOAD_DIRECTORY = os.path.join(os.path.expanduser("~"), "Desktop", "MP3 Downloaded")

# Check if download directory exists; create if it doesn't
os.makedirs(DOWNLOAD_DIRECTORY, exist_ok=True)

def add_metadata(file_path, author, title):
    """Add artist and title metadata to an MP3 file."""
    audiofile = eyed3.load(file_path)
    audiofile.tag.title = title
    audiofile.tag.artist = author
    audiofile.tag.save()

def extract_audio(video_file, audio_file, author, title):
    """Extract audio from video file."""
    try:
        ffmpeg_extract_audio(video_file, audio_file)
        os.remove(video_file)
        add_metadata(audio_file, author, title)
    except Exception as e:
        logging.error(f"Error extracting audio: {e}")

def load_links_and_download():
    """Handle loading links from a file and start downloading."""
    file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
    if file_path:
        with open(file_path, "r") as file:
            urls = file.readlines()
            total_urls = 0
            total_files = len(urls)
            for idx, url in enumerate(urls, start=1):
                url = url.strip()
                if url:
                    if is_valid_youtube_url(url):
                        total_urls+=1
                        download_queue.put(url)
                    else:
                        logging.error(f"Invalid URL format: {url}")
                        update_status(f"Invalid URL format: {url}")
                        time.sleep(4)
        update_status(f"Downloading {total_urls} of {total_files} files...")
        time.sleep(4)
        download_audio()

def download_audio():
    """Download audio from YouTube URL."""
    while not download_queue.empty():
        url = download_queue.get()
        try:
            update_status("Downloading next audio file")
            yt = YouTube(url)
            stream = yt.streams.filter(only_audio=True).first()
            if stream:
                filename = f"{yt.author}-{yt.title}"
                filename = remove_special_characters(filename)
                audio_file = os.path.join(DOWNLOAD_DIRECTORY, f"{filename}.mp3")
                temp_video_file = os.path.join(DOWNLOAD_DIRECTORY, 'temp_video')

                stream.download(output_path=DOWNLOAD_DIRECTORY, filename='temp_video')

                if os.path.exists(temp_video_file):
                    update_status(f"Extracting audio from {filename}...")
                    extraction_thread = threading.Thread(target=extract_audio, args=(temp_video_file, audio_file, str(yt.author), str(yt.title)))
                    extraction_thread.start()
                    extraction_thread.join()  
                    update_status(f"Downloaded {filename}")
                    if os.path.exists(temp_video_file):  # Check if the file still exists before removing
                        os.remove(temp_video_file)  # Remove temporary video file
                    time.sleep(5)  # 5 seconds delay between downloads
                else:
                    logging.error(f"No temporary file found for url: {url}")
                    update_status(f"No temporary file found for url: {url}")
            else:
                logging.error(f"No audio stream found for URL: {url}")
                update_status(f"No audio stream found for URL: {url}")
        except Exception as e:
            logging.error(f"Error downloading from URL: {url}. Error: {e}")
            update_status(f"Error downloading from URL: {url}. Error: {e}")
        finally:
            download_queue.task_done()
            time.sleep(2)

def remove_special_characters(text):
    """Remove special characters from text."""
    allowed_characters = " -[]()&"
    return ''.join(char for char in text if char.isalnum() or char in allowed_characters)

def update_status(message:str):
    """Update status_label with text."""
    status_label.config(text=message)
    root.update()

def close_app():
    """Close the application."""
    root.destroy()
    logging.shutdown()

def download_single_audio():
    """Manually download audio from YouTube URL."""
    url = url_entry.get()
    if url:
        if is_valid_youtube_url(url):
            download_queue.put(url)
            download_audio()
        else:
            logging.error(f"Invalid URL format: {url}")
            update_status(f"Invalid URL format: {url}")
    else:
        update_status("URL is empty")

def is_valid_youtube_url(url:str):
    """Check if the URL is a valid format youtube link."""
    pattern = r"(https?://)?(www\.)?(youtube\.com|youtu\.be)/.+"
    return bool(re.match(pattern, url))

# Create the main Tkinter window
root = tk.Tk()
root.title("YouTube Video to MP3 Converter")
root.minsize(370, 235)
root.maxsize(370, 235)
root.geometry("+100+100")  # Set the initial position of the window
root['padx'] = 5  # Horizontal padding
root['pady'] = 5  # Vertical padding

# Create and pack widgets
url_label = tk.Label(root, text="Enter YouTube URL:")
url_label.pack(pady=5)

url_entry = tk.Entry(root, width=50)
url_entry.pack(pady=5)

single_download_button = tk.Button(root, text="Download single audio", command=download_single_audio)
single_download_button.pack(pady=5)

load_button = tk.Button(root, text="Load links from the file and download", command=load_links_and_download)
load_button.pack(pady=5)

status_label = tk.Label(root, text="Ready", fg="yellowgreen", anchor="w", justify="left")
status_label.pack(pady=5)

close_button = tk.Button(root, text="Close", command=close_app)
close_button.pack(pady=2)

# Configure logging
logging.basicConfig(
    filename=os.path.join(DOWNLOAD_DIRECTORY, '0logs.log'),
    level=logging.ERROR,
    format='%(asctime)s [%(levelname)s]: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Create a queue for managing downloads
download_queue = queue.Queue()

# Start the Tkinter main loop
if __name__ == "__main__":
    root.mainloop()
