import os
import requests
import logging
from pytube import YouTube
from yt_dlp import YoutubeDL
import cv2
import numpy as np
from urllib.parse import urlparse

# Setup logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Exception classes for better error handling
class DownloadError(Exception):
    """Custom exception for download-related errors."""
    pass

class WatermarkRemovalError(Exception):
    """Custom exception for watermark removal errors."""
    pass

class FileNotFoundError(Exception):
    """Custom exception for file-not-found errors."""
    pass

# Utility functions
def validate_url(url, trusted_domains=None):
    """Validates if the URL is from a trusted source."""
    if trusted_domains is None:
        trusted_domains = ['youtube.com', 'tiktok.com', 'facebook.com', 'instagram.com', 'twitter.com', 'spotify.com', 'soundcloud.com', 'amazonmusic.com', 'deezer.com']

    parsed_url = urlparse(url)
    if parsed_url.netloc.lower() not in trusted_domains:
        raise ValueError(f"URL is from an untrusted source: {parsed_url.netloc}")
    return True

def detect_content_type(url):
    """Detects content type (video, audio, image, etc.) based on URL."""
    content_types = {
        "video": ["youtube", "tiktok", "facebook", "instagram", "twitter"],
        "audio": ["spotify", "soundcloud", "amazonmusic", "deezer"],
        "image": [".jpg", ".png", ".gif", ".jpeg", ".bmp", ".webp"],
        "pdf": [".pdf"],
        "text": [".txt"],
        "zip": [".zip"],
        "rar": [".rar"],
        "7z": [".7z"]
    }

    for category, identifiers in content_types.items():
        for identifier in identifiers:
            if identifier in url.lower() or url.lower().endswith(identifier):
                return category
    return "unknown"

# Downloader class to handle download and watermark removal
class Downloader:
    def __init__(self, url, trusted_domains=None):
        self.url = url
        validate_url(url, trusted_domains)  # Validate URL during initialization

    def download_video(self, save_path="video.mp4", format_str='bestvideo[height<=1080]+bestaudio/best'):
        """Downloads video content from the URL."""
        try:
            ydl_opts = {
                'format': format_str,
                'outtmpl': save_path,
                'noplaylist': True
            }
            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([self.url])
            logging.info(f"Video downloaded successfully to {save_path}")
            return save_path
        except Exception as e:
            logging.error(f"Error downloading video: {e}")
            raise DownloadError(f"Failed to download video: {str(e)}")

    def remove_watermark_inpaint(self, input_path, output_path, watermark_positions=None, inpaint_radius=7):
        """Removes watermark from the video using inpainting."""
        if watermark_positions is None:
            watermark_positions = [(10, 10, 100, 50), (200, 50, 150, 80)]  # Default watermark positions
        try:
            cap = cv2.VideoCapture(input_path)
            if not cap.isOpened():
                raise FileNotFoundError(f"Unable to open video file: {input_path}")

            frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(output_path, fourcc, fps, (frame_width, frame_height))

            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break

                mask = np.zeros(frame.shape[:2], dtype="uint8")
                for pos in watermark_positions:
                    mask[pos[1]:pos[1]+pos[3], pos[0]:pos[0]+pos[2]] = 255  # Adjust mask for watermark region

                inpainted_frame = cv2.inpaint(frame, mask, inpaint_radius, cv2.INPAINT_TELEA)
                out.write(inpainted_frame)

            cap.release()
            out.release()
            logging.info(f"Watermark removed and saved: {output_path}")
            return True
        except Exception as e:
            logging.error(f"Error removing watermark: {e}")
            raise WatermarkRemovalError(f"Failed to remove watermark: {str(e)}")

    def download_file(self, content_type, save_path="downloaded_file"):
        """Downloads other content types like audio, image, etc."""
        try:
            response = requests.get(self.url)
            if response.status_code == 200:
                with open(save_path, 'wb') as file:
                    file.write(response.content)
                logging.info(f"Downloaded {content_type} to {save_path}")
            else:
                logging.error(f"Failed to download file: {response.status_code}")
        except Exception as e:
            logging.error(f"Error downloading file: {e}")
            raise DownloadError(f"Failed to download {content_type}: {str(e)}")

# Main function for orchestrating tasks
def main():
    """Main function to manage the downloader process."""
    os.system('cls' if os.name == 'nt' else 'clear')
    print("Hello! Welcome to the ultimate downloader.")

    try:
        url = input("Enter the URL to download: ")
        downloader = Downloader(url)
    except ValueError as e:
        print(f"Invalid URL: {e}")
        return

    content_type = detect_content_type(url)
    try:
        if content_type == "video":
            print("Detected as video. Downloading...")
            downloaded_path = downloader.download_video()

            print("Checking and removing watermark if any...")
            output_path = "watermark_removed_video.mp4"
            watermark_positions = [(10, 10, 100, 50), (200, 50, 150, 80)]
            if downloader.remove_watermark_inpaint(downloaded_path, output_path, watermark_positions):
                print(f"Watermark removed successfully. Saved at {output_path}")
            else:
                print("No watermark detected or removal failed.")

        elif content_type == "audio":
            print("Detected as audio. Downloading audio...")
            downloader.download_file("audio", "audio.mp3")
        elif content_type in ["image", "pdf", "text", "zip", "rar", "7z"]:
            print(f"Detected as {content_type}. Downloading...")
            downloader.download_file(content_type, f"downloaded.{content_type}")
        else:
            print("Content type could not be detected. Unsupported URL.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
