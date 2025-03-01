# Copy the entire content of suno_downloader.py here
from playwright.async_api import async_playwright
import os
import re
import json
import time
from datetime import datetime
from bs4 import BeautifulSoup
from mutagen.id3 import (
    ID3, USLT, APIC, TIT2, TPE1, TALB,
    TDRC, TCON, COMM, ID3NoHeaderError
)
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass
from pathlib import Path
import logging
from tqdm.asyncio import tqdm
import aiohttp
import aiofiles
import asyncio

# Configuration
CONFIG = {
    'max_concurrent_downloads': 5,
    'retry_attempts': 3,
    'retry_delay': 5,
    'rate_limit_delay': 1.0,
    'download_timeout': 300,
    'nav_timeout': 60000,
    'selector_timeout': 20000,
    'session_file': 'session.json',
    'progress_file': 'download_progress.json',
    'log_file': os.path.join('Logs', 'suno_downloader.log'),
    'suno_login_url': 'https://suno.ai/login',
    'suno_profile_url': 'https://suno.ai/profile'
}


@dataclass
class SongMetadata:
    """Class to hold song metadata"""
    title: str
    artist: str = "Suno.ai"
    album: str = ""
    genre: str = "AI Generated"
    year: str = ""
    lyrics: str = ""
    gpt_prompt: str = ""
    cover_url: str = ""
    mp3_url: str = ""
    download_path: str = ""


class SunoDownloader:
    def __init__(self, output_dir: str = "downloads", log_dir: Optional[str] = None):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Set up log directory
        if log_dir:
            CONFIG['log_file'] = os.path.join(log_dir, 'suno_downloader.log')
        log_path = Path(CONFIG['log_file'])
        log_path.parent.mkdir(parents=True, exist_ok=True)

        self.setup_logging()
        self.progress: Dict[str, dict] = self.load_progress()
        self.session_data: Dict = self.load_session()
        self.rate_limiter = asyncio.Semaphore(
            CONFIG['max_concurrent_downloads'])
        self.last_request_time = 0
        self.browser = None
        self.context = None

    def setup_logging(self):
        """Set up logging with both file and console handlers"""
        handlers = [
            logging.StreamHandler()  # Console handler always included
        ]

        try:
            # Add file handler if we can create/write to the log file
            file_handler = logging.FileHandler(CONFIG['log_file'])
            handlers.append(file_handler)
        except Exception as e:
            print(f"Warning: Could not set up file logging: {e}")

        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=handlers
        )
        self.logger = logging.getLogger(__name__)

    def load_progress(self) -> Dict:
        try:
            with open(CONFIG['progress_file'], 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def save_progress(self):
        with open(CONFIG['progress_file'], 'w') as f:
            json.dump(self.progress, f, indent=2)

    def load_session(self) -> Dict:
        try:
            with open(CONFIG['session_file'], 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    async def rate_limit(self):
        """Implement rate limiting"""
        current_time = time.time()
        elapsed = current_time - self.last_request_time
        if elapsed < CONFIG['rate_limit_delay']:
            await asyncio.sleep(CONFIG['rate_limit_delay'] - elapsed)
        self.last_request_time = time.time()

    async def extract_song_metadata(self, page, url: str) -> Optional[SongMetadata]:
        """Extract all metadata from the Suno song page"""
        try:
            await page.wait_for_selector("section.w-full > div:nth-child(1)",
                                         timeout=CONFIG['selector_timeout'])

            title = await page.title()
            lyrics = await page.text_content("section.w-full > div:nth-child(1)")

            # Extract MP3 URL
            mp3_url = await page.evaluate("""() => {
                const audioElement = document.querySelector('audio source');
                return audioElement ? audioElement.src : null;
            }""")

            # Extract cover image URL
            cover_url = await page.evaluate("""() => {
                const imgElement = document.querySelector('img[alt*="cover"]');
                return imgElement ? imgElement.src : null;
            }""")

            # Extract GPT prompt
            html_content = await page.content()
            gpt_prompt = self.extract_gpt_prompt(html_content)

            return SongMetadata(
                title=title.strip(),
                lyrics=lyrics.strip(),
                gpt_prompt=gpt_prompt,
                cover_url=cover_url,
                mp3_url=mp3_url
            )
        except Exception as e:
            self.logger.error(f"Error extracting metadata for {url}: {str(e)}")
            return None

    def extract_gpt_prompt(self, html: str) -> str:
        """Extract GPT prompt from HTML content"""
        soup = BeautifulSoup(html, "html.parser")
        for script in soup.find_all("script"):
            script_text = script.get_text()
            if "gpt_description_prompt" in script_text:
                match = re.search(
                    r'"gpt_description_prompt"\s*:\s*\\"?([^\\"]+)\\"?', script_text)
                if match:
                    return match.group(1).strip()
        return ""

    async def download_file_with_progress(self, session: aiohttp.ClientSession,
                                          url: str, filepath: Path) -> bool:
        """Download a file with progress bar"""
        try:
            async with session.get(url) as response:
                if response.status != 200:
                    raise aiohttp.ClientError(f"HTTP {response.status}")

                total_size = int(response.headers.get('content-length', 0))
                with tqdm(total=total_size, unit='iB', unit_scale=True) as pbar:
                    async with aiofiles.open(filepath, 'wb') as f:
                        async for chunk in response.content.iter_chunked(8192):
                            await f.write(chunk)
                            pbar.update(len(chunk))
                return True
        except Exception as e:
            self.logger.error(f"Error downloading {url}: {str(e)}")
            return False

    async def process_song(self, url: str, session: aiohttp.ClientSession):
        """Process a single song URL"""
        if url in self.progress and self.progress[url].get('completed'):
            self.logger.info(f"Skipping already downloaded song: {url}")
            return

        async with self.rate_limiter:
            await self.rate_limit()

            try:
                async with async_playwright() as p:
                    browser = await p.chromium.launch(headless=True)
                    page = await browser.new_page()
                    await page.goto(url, timeout=CONFIG['nav_timeout'])

                    metadata = await self.extract_song_metadata(page, url)
                    if not metadata:
                        raise Exception("Failed to extract metadata")

                    # Create song directory
                    song_dir = self.output_dir / \
                        self.sanitize_filename(metadata.title)
                    song_dir.mkdir(exist_ok=True)

                    # Download MP3
                    if metadata.mp3_url:
                        mp3_path = song_dir / \
                            f"{self.sanitize_filename(metadata.title)}.mp3"
                        if await self.download_file_with_progress(session, metadata.mp3_url, mp3_path):
                            await self.add_metadata_to_mp3(mp3_path, metadata)

                    # Download cover image
                    if metadata.cover_url:
                        cover_path = song_dir / "cover.jpg"
                        await self.download_file_with_progress(session, metadata.cover_url, cover_path)

                    # Save lyrics and prompt
                    if metadata.lyrics:
                        await self.save_text_file(song_dir / "lyrics.txt", metadata.lyrics)
                    if metadata.gpt_prompt:
                        await self.save_text_file(song_dir / "prompt.txt", metadata.gpt_prompt)

                    # Update progress
                    self.progress[url] = {
                        'completed': True,
                        'timestamp': datetime.now().isoformat(),
                        'title': metadata.title
                    }
                    self.save_progress()

                    await browser.close()

            except Exception as e:
                self.logger.error(f"Error processing {url}: {str(e)}")
                self.progress[url] = {
                    'completed': False,
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }
                self.save_progress()

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitize filename to be safe for all operating systems"""
        return re.sub(r'[<>:"/\\|?*]', '_', filename).rstrip('_')

    async def save_text_file(self, filepath: Path, content: str):
        """Save text content to file asynchronously"""
        async with aiofiles.open(filepath, 'w', encoding='utf-8') as f:
            await f.write(content)

    async def add_metadata_to_mp3(self, filepath: Path, metadata: SongMetadata):
        """Add metadata to MP3 file"""
        try:
            audio = ID3(filepath)
        except ID3NoHeaderError:
            audio = ID3()

        audio.add(TIT2(encoding=3, text=metadata.title))
        audio.add(TPE1(encoding=3, text=metadata.artist))
        audio.add(TALB(encoding=3, text=metadata.album))
        audio.add(TCON(encoding=3, text=metadata.genre))
        if metadata.year:
            audio.add(TDRC(encoding=3, text=metadata.year))
        if metadata.lyrics:
            audio.add(USLT(encoding=3, lang='eng',
                      desc='', text=metadata.lyrics))
        if metadata.gpt_prompt:
            audio.add(COMM(encoding=3, lang='eng',
                      desc='GPT Prompt', text=metadata.gpt_prompt))

        audio.save(filepath)

    async def download_songs(self, urls: List[str]):
        """Download multiple songs concurrently"""
        async with aiohttp.ClientSession() as session:
            tasks = [self.process_song(url, session) for url in urls]
            for task in tqdm(asyncio.as_completed(tasks), total=len(tasks)):
                await task

    async def login(self, email: str, password: str) -> bool:
        """Login to Suno.com account"""
        try:
            self.logger.info("Logging into Suno.com...")
            async with async_playwright() as p:
                self.browser = await p.chromium.launch(headless=True)
                self.context = await self.browser.new_context()

                # Try to load existing cookies
                if os.path.exists('cookies.json'):
                    with open('cookies.json', 'r') as f:
                        cookies = json.load(f)
                        await self.context.add_cookies(cookies)

                page = await self.context.new_page()
                await page.goto(CONFIG['suno_login_url'])

                # Check if we're already logged in
                if await self.is_logged_in(page):
                    self.logger.info("Already logged in!")
                    return True

                # Fill login form
                await page.fill('input[type="email"]', email)
                await page.fill('input[type="password"]', password)
                await page.click('button[type="submit"]')

                # Wait for navigation
                await page.wait_for_load_state('networkidle')

                # Check if login was successful
                if await self.is_logged_in(page):
                    self.logger.info("Login successful!")
                    # Save cookies for future use
                    cookies = await self.context.cookies()
                    with open('cookies.json', 'w') as f:
                        json.dump(cookies, f)
                    return True
                else:
                    self.logger.error("Login failed!")
                    return False

        except Exception as e:
            self.logger.error(f"Login error: {str(e)}")
            return False

    async def is_logged_in(self, page) -> bool:
        """Check if we're logged into Suno.com"""
        try:
            # Wait for either login form or profile indicator
            await page.wait_for_selector('input[type="email"], .profile-indicator',
                                         timeout=CONFIG['selector_timeout'])
            # If login form exists, we're not logged in
            login_form = await page.query_selector('input[type="email"]')
            return not bool(login_form)
        except Exception:
            return False

    async def scrape_song_urls(self) -> Set[str]:
        """Scrape all song URLs from the user's profile"""
        song_urls = set()
        try:
            self.logger.info("Scraping song URLs from profile...")
            page = await self.context.new_page()
            await page.goto(CONFIG['suno_profile_url'])

            # Wait for the songs to load
            await page.wait_for_selector('.song-list, .song-grid', timeout=CONFIG['selector_timeout'])

            # Scroll to load all songs
            last_height = await page.evaluate('document.body.scrollHeight')
            while True:
                await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
                await page.wait_for_timeout(2000)  # Wait for content to load
                new_height = await page.evaluate('document.body.scrollHeight')
                if new_height == last_height:
                    break
                last_height = new_height

            # Extract song URLs
            song_elements = await page.query_selector_all('a[href*="/song/"]')
            for element in song_elements:
                url = await element.get_attribute('href')
                if url:
                    full_url = f"https://suno.ai{url}" if url.startswith(
                        '/') else url
                    song_urls.add(full_url)

            self.logger.info(f"Found {len(song_urls)} songs!")
            return song_urls

        except Exception as e:
            self.logger.error(f"Error scraping song URLs: {str(e)}")
            return set()


if __name__ == "__main__":
    async def main():
        # Initialize downloader
        downloader = SunoDownloader()

        # Get login credentials
        email = input("Enter your Suno.com email: ")
        password = input("Enter your Suno.com password: ")

        # Login to Suno.com
        if not await downloader.login(email, password):
            print("Failed to login. Please check your credentials.")
            return

        # Scrape song URLs
        song_urls = await downloader.scrape_song_urls()
        if not song_urls:
            print("No songs found in your profile.")
            return

        print(f"Found {len(song_urls)} songs. Starting download...")

        # Start downloading
        await downloader.download_songs(list(song_urls))

    asyncio.run(main())
