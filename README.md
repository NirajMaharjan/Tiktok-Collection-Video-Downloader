# Setup
- git clone https://github.com/yourusername/tiktok-downloader.git
- cd tiktok-downloader


# Get urls of collections
A browser-based script to extract TikTok video/photo URLs from a page. This script automatically scrolls through a TikTok page (like your favorites or a user's profile) and collects all video/photo URLs.

### How to Use get_urls.js:
1. Copy the contents of get_urls.js or get_urls.min.js
2. Open the TikTok page you want to extract URLs from (e.g., your favorites page, a user's profile)
3. Open your browser's developer console (usually F12 or right-click -> Inspect -> Console)
4. Paste the script and press Enter
The script will:
* Automatically scroll through the page
* Collect all video/photo URLs
* Download a text file named after the page title (e.g., "Favorites.txt")

# Download the videos
1. Create Your URL List
    Create a text file urls.txt with TikTok URLs:<br/>
        https://www.tiktok.com/@username/video/1234567890
        https://vm.tiktok.com/abcdefg
        https://www.tiktok.com/@another_user/video/9876543210
4️⃣ Run the Downloader
- python download_all.py urls.txt
5️⃣ Get Your Files
📁 downloads/videos/     ← Your downloaded videos
📁 audio/               ← Converted audio files (WAV)
📄 tiktok_downloader.log ← Detailed logs