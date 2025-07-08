#!/usr/bin/env python3
"""
TikTok Video Downloader and Audio Converter
Downloads TikTok videos from URLs in a text file and converts them to WAV audio files.
"""

import os
import sys
import subprocess
import logging
from pathlib import Path
from urllib.parse import urlparse
import re
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('tiktok_downloader.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class TikTokDownloader:
    def __init__(self, urls_file, output_dir="downloads", audio_dir="audios"):
        self.urls_file = urls_file
        self.output_dir = Path(output_dir)
        self.audio_dir = Path(audio_dir)
        self.video_dir = self.output_dir / "videos"
        
        # Create directories
        self.video_dir.mkdir(parents=True, exist_ok=True)
        self.audio_dir.mkdir(parents=True, exist_ok=True)
        
        # Check dependencies
        self.check_dependencies()
    
    def check_dependencies(self):
        """Check if required tools are installed"""
        try:
            subprocess.run(["yt-dlp", "--version"], 
                         capture_output=True, check=True)
            logger.info("yt-dlp is available")
        except (subprocess.CalledProcessError, FileNotFoundError):
            logger.error("yt-dlp is not installed. Install with: pip install yt-dlp")
            sys.exit(1)
        
        try:
            subprocess.run(["ffmpeg", "-version"], 
                         capture_output=True, check=True)
            logger.info("ffmpeg is available")
        except (subprocess.CalledProcessError, FileNotFoundError):
            logger.error("ffmpeg is not installed. Please install ffmpeg")
            sys.exit(1)
    
    def read_urls(self):
        """Read URLs from the text file"""
        try:
            with open(self.urls_file, 'r', encoding='utf-8') as f:
                urls = [line.strip() for line in f if line.strip()]
            
            # Filter valid TikTok URLs
            tiktok_urls = []
            for url in urls:
                if self.is_valid_tiktok_url(url):
                    tiktok_urls.append(url)
                else:
                    logger.warning(f"Invalid TikTok URL: {url}")
            
            logger.info(f"Found {len(tiktok_urls)} valid TikTok URLs")
            return tiktok_urls
        
        except FileNotFoundError:
            logger.error(f"URLs file not found: {self.urls_file}")
            sys.exit(1)
        except Exception as e:
            logger.error(f"Error reading URLs file: {e}")
            sys.exit(1)
    
    def is_valid_tiktok_url(self, url):
        """Check if URL is a valid TikTok URL"""
        tiktok_patterns = [
            r'https?://(?:www\.)?tiktok\.com/@[\w\.-]+/video/\d+',
            r'https?://(?:vm|vt)\.tiktok\.com/[\w\d]+',
            r'https?://(?:www\.)?tiktok\.com/t/[\w\d]+',
        ]
        
        for pattern in tiktok_patterns:
            if re.match(pattern, url):
                return True
        return False
    
    def download_video(self, url, index):
        """Download a single TikTok video"""
        try:
            # Custom filename template
            filename_template = f"tiktok_{index:03d}_%(id)s.%(ext)s"
            output_path = self.video_dir / filename_template
            
            # yt-dlp command
            cmd = [
                "yt-dlp",
                "--no-warnings",
                
                "--write-info-json",
                "--write-description",
                "--write-thumbnail",
                "-f", "best/worst",  # Limit to 720p for faster downloads
                "-o", str(output_path),
                url
            ]
            
            logger.info(f"Downloading video {index}: {url}")
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"Successfully downloaded video {index}")
                
                # Find the actual downloaded video file
                video_files = list(self.video_dir.glob(f"tiktok_{index:03d}_*.mp4"))
                if video_files:
                    return video_files[0]
                else:
                    # Try other extensions
                    video_files = list(self.video_dir.glob(f"tiktok_{index:03d}_*"))
                    video_files = [f for f in video_files if f.suffix in ['.mp4', '.mov', '.avi', '.mkv']]
                    if video_files:
                        return video_files[0]
                
                logger.warning(f"Downloaded video {index} but couldn't find the file")
                time.sleep(2)
                return None
            else:
                logger.error(f"Failed to download video {index}: {result.stderr}")
                return None
                
        except Exception as e:
            logger.error(f"Error downloading video {index}: {e}")
            return None
    
    def convert_to_audio(self, video_file, index):
        """Convert video to WAV audio"""
        try:
            audio_filename = f"tiktok_{index:03d}_audio.wav"
            audio_path = self.audio_dir / audio_filename
            
            cmd = [
                "ffmpeg",
                "-i", str(video_file),
                "-vn",  # No video
                "-acodec", "pcm_s16le",  # WAV format
                "-ar", "44100",  # Sample rate
                "-ac", "2",  # Stereo
                "-y",  # Overwrite output file
                str(audio_path)
            ]
            
            logger.info(f"Converting video {index} to audio")
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"Successfully converted video {index} to audio")
                return audio_path
            else:
                logger.error(f"Failed to convert video {index} to audio: {result.stderr}")
                return None
                
        except Exception as e:
            logger.error(f"Error converting video {index} to audio: {e}")
            return None
    
    def process_all(self):
        """Process all URLs: download videos and convert to audio"""
        urls = self.read_urls()
        
        if not urls:
            logger.error("No valid URLs found")
            return
        
        successful_downloads = 0
        successful_conversions = 0
        
        for index, url in enumerate(urls, 1):
            logger.info(f"Processing {index}/{len(urls)}: {url}")
            
            # Download video
            video_file = self.download_video(url, index)
            
            if video_file:
                successful_downloads += 1
                
                # Convert to audio
                audio_file = self.convert_to_audio(video_file, index)
                
                if audio_file:
                    successful_conversions += 1
                    logger.info(f"Audio saved: {audio_file}")
            
            logger.info(f"Completed {index}/{len(urls)}")
            print("-" * 50)
        
        # Summary
        logger.info(f"\nSUMMARY:")
        logger.info(f"Total URLs: {len(urls)}")
        logger.info(f"Successful downloads: {successful_downloads}")
        logger.info(f"Successful audio conversions: {successful_conversions}")
        logger.info(f"Videos saved in: {self.video_dir}")
        logger.info(f"Audio files saved in: {self.audio_dir}")

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Download TikTok videos and convert to audio")
    parser.add_argument("urls_file", help="Text file containing TikTok URLs (one per line)")
    parser.add_argument("--output-dir", default="downloads", help="Directory for video downloads")
    parser.add_argument("--audio-dir", default="audio", help="Directory for audio files")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.urls_file):
        print(f"Error: URLs file '{args.urls_file}' not found")
        sys.exit(1)
    
    downloader = TikTokDownloader(
        urls_file=args.urls_file,
        output_dir=args.output_dir,
        audio_dir=args.audio_dir
    )
    
    try:
        downloader.process_all()
    except KeyboardInterrupt:
        logger.info("Process interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()