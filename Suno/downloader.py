"""
Downloader module for Suno.com

Handles downloading of songs, cover images, lyrics, and metadata.
"""

import os
import re
import json
import time
import logging
import requests
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urljoin, quote

from extractor import extract_lyrics, extract_song_data

logger = logging.getLogger(__name__)

class SunoDownloader:
    """Handles downloading content from Suno.com accounts."""
    
    BASE_URL = "https://suno.com"
    API_URL = "https://suno.com/api"
    
    def __init__(self, session, user_info, base_dir, audio_dir, images_dir, 
                 lyrics_dir, metadata_dir, request_delay=1.0, verbose=False):
        """
        Initialize the downloader.
        
        Args:
            session (requests.Session): Authenticated session
            user_info (dict): Information about the logged-in user
            base_dir (Path): Base directory for downloads
            audio_dir (Path): Directory for audio files
            images_dir (Path): Directory for cover images
            lyrics_dir (Path): Directory for lyrics
            metadata_dir (Path): Directory for metadata
            request_delay (float): Delay between requests
            verbose (bool): Enable verbose logging
        """
        self.session = session
        self.user_info = user_info
        self.base_dir = base_dir
        self.audio_dir = audio_dir
        self.images_dir = images_dir
        self.lyrics_dir = lyrics_dir
        self.metadata_dir = metadata_dir
        self.request_delay = request_delay
        
        # Set up logging level based on verbose flag
        log_level = logging.DEBUG if verbose else logging.INFO
        logger.setLevel(log_level)
    
    def get_user_songs(self, username):
        """
        Get list of songs for a user.
        
        Args:
            username (str): Username to download songs from (e.g. @thecasketdiaries)
            
        Returns:
            list: List of song objects
        """
        username = username.strip('@')
        songs = []
        page = 1
        per_page = 50  # Typical pagination size, may need adjustment
        
        logger.info(f"Fetching songs for user @{username}")
        
        # Try multiple API endpoints since we don't know the exact structure
        api_endpoints = [
            f"{self.API_URL}/users/{username}/songs",
            f"{self.API_URL}/profile/{username}/songs",
            f"{self.API_URL}/creators/{username}/songs",
            f"{self.BASE_URL}/api/users/{username}/songs",
        ]
        
        # Also try to scrape the profile page directly
        profile_url = f"{self.BASE_URL}/@{username}"
        
        # First, try API endpoints
        for endpoint in api_endpoints:
            try:
                logger.debug(f"Trying API endpoint: {endpoint}")
                has_more = True
                page = 1
                endpoint_songs = []
                
                while has_more:
                    url = f"{endpoint}?page={page}&per_page={per_page}"
                    logger.debug(f"Fetching page {page} from {url}")
                    
                    response = self.session.get(url)
                    if response.status_code != 200:
                        logger.debug(f"API response failed with status {response.status_code}")
                        break
                    
                    try:
                        data = response.json()
                        
                        # Handle different response formats
                        page_songs = None
                        if isinstance(data, list):
                            page_songs = data
                        elif isinstance(data, dict):
                            if 'songs' in data:
                                page_songs = data['songs']
                            elif 'results' in data:
                                page_songs = data['results']
                            elif 'data' in data:
                                page_songs = data['data']
                        
                        if page_songs:
                            endpoint_songs.extend(page_songs)
                            has_more = len(page_songs) >= per_page
                            
                            # Log progress
                            logger.info(f"Found {len(endpoint_songs)} songs so far")
                            
                            # Increment page for next request
                            page += 1
                            time.sleep(self.request_delay)
                        else:
                            has_more = False
                    except json.JSONDecodeError:
                        logger.debug("Failed to parse JSON response")
                        has_more = False
                
                if endpoint_songs:
                    logger.info(f"Successfully retrieved {len(endpoint_songs)} songs from API")
                    songs = endpoint_songs
                    break
                    
            except Exception as e:
                logger.warning(f"Error fetching songs from {endpoint}: {e}")
        
        # If API endpoints didn't work, try scraping the profile page
        if not songs:
            logger.info("API endpoints failed, attempting to scrape profile page")
            try:
                profile_response = self.session.get(profile_url)
                if profile_response.status_code == 200:
                    songs = self._extract_songs_from_profile_page(profile_response.text)
                    logger.info(f"Extracted {len(songs)} songs from profile page")
            except Exception as e:
                logger.warning(f"Error scraping profile page: {e}")
        
        # If we still don't have songs, try one more approach - paginated fetching from HTML pages
        if not songs:
            logger.info("Attempting to scrape songs from paginated profile pages")
            songs = self._scrape_songs_from_paginated_profile(username)
            
        return songs
    
    def _extract_songs_from_profile_page(self, page_content):
        """
        Extract songs from profile page HTML.
        
        Args:
            page_content (str): HTML content of the profile page
            
        Returns:
            list: List of song objects
        """
        songs = []
        soup = BeautifulSoup(page_content, 'html.parser')
        
        # Look for songs in script tags (common pattern)
        scripts = soup.find_all('script')
        for script in scripts:
            if not script.string:
                continue
                
            # Try different patterns to find song data
            song_patterns = [
                r'window\.__INITIAL_STATE__\s*=\s*({.*?});',
                r'window\.__PRELOADED_STATE__\s*=\s*({.*?});',
                r'window\.__SONGS__\s*=\s*(\[.*?\]);',
                r'"songs"\s*:\s*(\[.*?\])',
                r'"results"\s*:\s*(\[.*?\])'
            ]
            
            for pattern in song_patterns:
                matches = re.search(pattern, script.string, re.DOTALL)
                if matches:
                    try:
                        data = json.loads(matches.group(1))
                        
                        # Extract songs from the data based on structure
                        extracted_songs = None
                        if isinstance(data, list):
                            extracted_songs = data
                        elif isinstance(data, dict):
                            if 'songs' in data:
                                extracted_songs = data['songs']
                            elif 'profile' in data and 'songs' in data['profile']:
                                extracted_songs = data['profile']['songs']
                            elif 'results' in data:
                                extracted_songs = data['results']
                            elif 'data' in data and 'songs' in data['data']:
                                extracted_songs = data['data']['songs']
                        
                        if extracted_songs and len(extracted_songs) > 0:
                            logger.debug(f"Found {len(extracted_songs)} songs in script tag")
                            return extracted_songs
                    except json.JSONDecodeError:
                        continue
        
        # If script tags don't have the data, look for song cards in the HTML
        song_cards = soup.find_all('div', {'class': re.compile(r'song-card|track-item|music-item')})
        
        for card in song_cards:
            try:
                song = {}
                
                # Try to extract song ID
                id_attr = card.get('data-song-id') or card.get('id') or card.get('data-id')
                if id_attr:
                    song['id'] = id_attr
                
                # Try to extract song title
                title_elem = card.find('h3') or card.find('div', {'class': 'title'})
                if title_elem:
                    song['title'] = title_elem.text.strip()
                
                # Try to extract artwork/cover URL
                img_elem = card.find('img')
                if img_elem:
                    song['artwork_url'] = img_elem.get('src') or img_elem.get('data-src')
                
                # If we have at least an ID and title, add the song
                if 'id' in song and 'title' in song:
                    songs.append(song)
            except Exception as e:
                logger.debug(f"Error extracting song from card: {e}")
        
        return songs
    
    def _scrape_songs_from_paginated_profile(self, username):
        """
        Scrape songs from paginated profile pages.
        
        Args:
            username (str): Username without @ symbol
            
        Returns:
            list: List of song objects
        """
        songs = []
        page = 1
        has_more = True
        
        while has_more:
            url = f"{self.BASE_URL}/@{username}?page={page}"
            logger.debug(f"Scraping songs from profile page {page}: {url}")
            
            try:
                response = self.session.get(url)
                if response.status_code != 200:
                    break
                
                page_songs = self._extract_songs_from_profile_page(response.text)
                
                if page_songs:
                    songs.extend(page_songs)
                    logger.info(f"Found {len(page_songs)} songs on page {page}")
                    
                    # If we got fewer songs than expected, assume we've reached the end
                    if len(page_songs) < 10:  # Assuming 10+ songs per page
                        has_more = False
                else:
                    has_more = False
                
                # Increment page for next request
                page += 1
                time.sleep(self.request_delay)
                
            except Exception as e:
                logger.warning(f"Error scraping profile page {page}: {e}")
                has_more = False
        
        return songs
    
    def download_audio(self, song):
        """
        Download the audio file for a song.
        
        Args:
            song (dict): Song object with metadata
            
        Returns:
            bool: True if successful, False otherwise
        """
        song_id = song.get('id')
        if not song_id:
            logger.error("Song ID is missing, cannot download audio")
            return False
        
        title = song.get('title', f"song-{song_id}")
        safe_title = self._safe_filename(title)
        
        logger.info(f"Downloading audio for '{title}' (ID: {song_id})")
        
        # Create filename
        filename = f"{safe_title}-{song_id}.mp3"
        filepath = self.audio_dir / filename
        
        # Skip if file already exists
        if filepath.exists():
            logger.info(f"Audio file already exists: {filepath}")
            return True
        
        # First, try to get the audio URL from the song object
        audio_url = song.get('audio_url') or song.get('mp3_url') or song.get('stream_url')
        
        # If URL is not in the song object, try to get it from the song page
        if not audio_url:
            audio_url = self._get_audio_url_from_song_page(song_id)
        
        # If we still don't have a URL, try the API directly
        if not audio_url:
            audio_url = self._get_audio_url_from_api(song_id)
        
        # If we have a URL, download the file
        if audio_url:
            try:
                # Ensure URL is absolute
                if not audio_url.startswith('http'):
                    audio_url = urljoin(self.BASE_URL, audio_url)
                
                logger.debug(f"Downloading audio from: {audio_url}")
                
                # Download with streaming to handle large files
                response = self.session.get(audio_url, stream=True)
                response.raise_for_status()
                
                with open(filepath, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                logger.info(f"Audio saved to: {filepath}")
                return True
                
            except Exception as e:
                logger.error(f"Error downloading audio for song {song_id}: {e}")
                return False
        else:
            logger.error(f"Could not find audio URL for song {song_id}")
            return False
    
    def _get_audio_url_from_song_page(self, song_id):
        """
        Extract audio URL from the song page.
        
        Args:
            song_id (str): ID of the song
            
        Returns:
            str: Audio URL or None if not found
        """
        song_url = f"{self.BASE_URL}/song/{song_id}"
        
        try:
            logger.debug(f"Fetching song page: {song_url}")
            response = self.session.get(song_url)
            
            if response.status_code != 200:
                logger.debug(f"Failed to get song page, status: {response.status_code}")
                return None
            
            # Look for audio URL in the page
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Try to find audio element
            audio_elem = soup.find('audio')
            if audio_elem and audio_elem.get('src'):
                return audio_elem.get('src')
            
            # Look for data in script tags
            scripts = soup.find_all('script')
            
            for script in scripts:
                if not script.string:
                    continue
                
                # Look for patterns that might contain the audio URL
                patterns = [
                    r'"audio_url"\s*:\s*"(https?://[^"]+)"',
                    r'"mp3_url"\s*:\s*"(https?://[^"]+)"',
                    r'"stream_url"\s*:\s*"(https?://[^"]+)"',
                    r'"url"\s*:\s*"(https?://[^"]+\.mp3[^"]*)"',
                ]
                
                for pattern in patterns:
                    match = re.search(pattern, script.string)
                    if match:
                        return match.group(1)
            
            # Extract song data using our utility function
            song_data = extract_song_data(response.text)
            if song_data and 'audio_url' in song_data:
                return song_data['audio_url']
            
        except Exception as e:
            logger.error(f"Error extracting audio URL from song page: {e}")
        
        return None
    
    def _get_audio_url_from_api(self, song_id):
        """
        Try to get audio URL from API endpoints.
        
        Args:
            song_id (str): ID of the song
            
        Returns:
            str: Audio URL or None if not found
        """
        # Try different possible API endpoints
        api_endpoints = [
            f"{self.API_URL}/songs/{song_id}",
            f"{self.API_URL}/song/{song_id}",
            f"{self.BASE_URL}/api/songs/{song_id}"
        ]
        
        for endpoint in api_endpoints:
            try:
                logger.debug(f"Trying API endpoint: {endpoint}")
                response = self.session.get(endpoint)
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        
                        # Look for audio URL in response
                        if isinstance(data, dict):
                            for key in ['audio_url', 'mp3_url', 'stream_url', 'url']:
                                if key in data and data[key]:
                                    return data[key]
                                    
                            # Check nested data structure
                            if 'song' in data and isinstance(data['song'], dict):
                                for key in ['audio_url', 'mp3_url', 'stream_url', 'url']:
                                    if key in data['song'] and data['song'][key]:
                                        return data['song'][key]
                    except json.JSONDecodeError:
                        continue
            except Exception as e:
                logger.debug(f"Error with API endpoint {endpoint}: {e}")
        
        return None
    
    def download_image(self, song):
        """
        Download the cover image for a song.
        
        Args:
            song (dict): Song object with metadata
            
        Returns:
            bool: True if successful, False otherwise
        """
        song_id = song.get('id')
        if not song_id:
            logger.error("Song ID is missing, cannot download image")
            return False
        
        title = song.get('title', f"song-{song_id}")
        safe_title = self._safe_filename(title)
        
        logger.info(f"Downloading cover image for '{title}' (ID: {song_id})")
        
        # Create filename
        filename = f"{safe_title}-{song_id}.jpg"
        filepath = self.images_dir / filename
        
        # Skip if file already exists
        if filepath.exists():
            logger.info(f"Image file already exists: {filepath}")
            return True
        
        # First, try to get the image URL from the song object
        image_url = None
        for key in ['artwork_url', 'cover_url', 'image_url', 'cover_image', 'thumbnail']:
            if key in song and song[key]:
                image_url = song[key]
                break
        
        # If URL is not in the song object, try to get it from the song page
        if not image_url:
            image_url = self._get_image_url_from_song_page(song_id)
        
        # If we have a URL, download the file
        if image_url:
            try:
                # Ensure URL is absolute
                if not image_url.startswith('http'):
                    image_url = urljoin(self.BASE_URL, image_url)
                
                logger.debug(f"Downloading image from: {image_url}")
                
                response = self.session.get(image_url)
                response.raise_for_status()
                
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                
                logger.info(f"Image saved to: {filepath}")
                return True
                
            except Exception as e:
                logger.error(f"Error downloading image for song {song_id}: {e}")
                return False
        else:
            logger.error(f"Could not find image URL for song {song_id}")
            return False
    
    def _get_image_url_from_song_page(self, song_id):
        """
        Extract image URL from the song page.
        
        Args:
            song_id (str): ID of the song
            
        Returns:
            str: Image URL or None if not found
        """
        song_url = f"{self.BASE_URL}/song/{song_id}"
        
        try:
            # Check if we recently fetched this page to avoid redundant requests
            logger.debug(f"Fetching song page: {song_url}")
            response = self.session.get(song_url)
            
            if response.status_code != 200:
                logger.debug(f"Failed to get song page, status: {response.status_code}")
                return None
            
            # Look for image URL in the page
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Try common patterns for cover images
            img_selectors = [
                'img.cover-image',
                'img.song-cover',
                'img.artwork',
                '.song-artwork img',
                '.cover-art img'
            ]
            
            for selector in img_selectors:
                img = soup.select_one(selector)
                if img and (img.get('src') or img.get('data-src')):
                    return img.get('src') or img.get('data-src')
            
            # Look for meta tags with image
            meta_img = soup.find('meta', {'property': 'og:image'})
            if meta_img and meta_img.get('content'):
                return meta_img.get('content')
            
            # Extract song data using our utility function
            song_data = extract_song_data(response.text)
            if song_data:
                for key in ['artwork_url', 'cover_url', 'image_url', 'cover_image', 'thumbnail']:
                    if key in song_data and song_data[key]:
                        return song_data[key]
            
        except Exception as e:
            logger.error(f"Error extracting image URL from song page: {e}")
        
        return None
    
    def download_lyrics(self, song):
        """
        Download the lyrics for a song.
        
        Args:
            song (dict): Song object with metadata
            
        Returns:
            bool: True if successful, False otherwise
        """
        song_id = song.get('id')
        if not song_id:
            logger.error("Song ID is missing, cannot download lyrics")
            return False
        
        title = song.get('title', f"song-{song_id}")
        safe_title = self._safe_filename(title)
        
        logger.info(f"Downloading lyrics for '{title}' (ID: {song_id})")
        
        # Create filename
        filename = f"{safe_title}-{song_id}.txt"
        filepath = self.lyrics_dir / filename
        
        # Skip if file already exists
        if filepath.exists():
            logger.info(f"Lyrics file already exists: {filepath}")
            return True
        
        # First, check if lyrics are in the song object
        lyrics = song.get('lyrics') or song.get('text')
        
        # If not, try to get them from the song page
        if not lyrics:
            lyrics = self._get_lyrics_from_song_page(song_id)
        
        # If we have lyrics, save them to file
        if lyrics:
            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    # Add song title as header
                    f.write(f"{title}\n")
                    f.write("=" * len(title) + "\n\n")
                    f.write(lyrics)
                
                logger.info(f"Lyrics saved to: {filepath}")
                return True
                
            except Exception as e:
                logger.error(f"Error saving lyrics for song {song_id}: {e}")
                return False
        else:
            logger.warning(f"Could not find lyrics for song {song_id}")
            # Create an empty lyrics file so we don't try again
            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(f"{title}\n")
                    f.write("=" * len(title) + "\n\n")
                    f.write("[No lyrics found]")
                
                logger.info(f"Empty lyrics placeholder saved to: {filepath}")
                return True
            except Exception as e:
                logger.error(f"Error saving empty lyrics file: {e}")
                return False
    
    def _get_lyrics_from_song_page(self, song_id):
        """
        Extract lyrics from the song page.
        
        Args:
            song_id (str): ID of the song
            
        Returns:
            str: Lyrics text or None if not found
        """
        song_url = f"{self.BASE_URL}/song/{song_id}"
        
        try:
            logger.debug(f"Fetching song page for lyrics: {song_url}")
            response = self.session.get(song_url)
            
            if response.status_code != 200:
                logger.debug(f"Failed to get song page, status: {response.status_code}")
                return None
            
            # Use our utility function to extract lyrics
            lyrics = extract_lyrics(response.text)
            
            if lyrics:
                return lyrics
            
            # If our utility function doesn't find lyrics, try common patterns
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Try common selectors for lyrics
            lyrics_selectors = [
                '.lyrics',
                '.song-lyrics',
                '.lyric-content',
                '#lyrics',
                '[data-lyrics]'
            ]
            
            for selector in lyrics_selectors:
                lyrics_elem = soup.select_one(selector)
                if lyrics_elem:
                    return lyrics_elem.get_text(strip=True)
            
        except Exception as e:
            logger.error(f"Error extracting lyrics from song page: {e}")
        
        return None
    
    def save_metadata(self, song):
        """
        Save song metadata to a JSON file.
        
        Args:
            song (dict): Song object with metadata
            
        Returns:
            bool: True if successful, False otherwise
        """
        song_id = song.get('id')
        if not song_id:
            logger.error("Song ID is missing, cannot save metadata")
            return False
        
        title = song.get('title', f"song-{song_id}")
        safe_title = self._safe_filename(title)
        
        logger.info(f"Saving metadata for '{title}' (ID: {song_id})")
        
        # Create filename
        filename = f"{safe_title}-{song_id}.json"
        filepath = self.metadata_dir / filename
        
        # Skip if file already exists
        if filepath.exists():
            logger.info(f"Metadata file already exists: {filepath}")
            return True
        
        # Enrich metadata if it's missing key information
        if 'title' not in song or not song.get('details'):
            enriched_song = self._enrich_song_metadata(song)
            if enriched_song:
                song = {**song, **enriched_song}
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(song, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Metadata saved to: {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving metadata for song {song_id}: {e}")
            return False
    
    def _enrich_song_metadata(self, song):
        """
        Enrich song metadata with additional details from the song page.
        
        Args:
            song (dict): Basic song object
            
        Returns:
            dict: Enriched song object or None if failed
        """
        song_id = song.get('id')
        if not song_id:
            return None
        
        song_url = f"{self.BASE_URL}/song/{song_id}"
        
        try:
            logger.debug(f"Fetching song page for metadata: {song_url}")
            response = self.session.get(song_url)
            
            if response.status_code != 200:
                logger.debug(f"Failed to get song page, status: {response.status_code}")
                return None
            
            # Extract song data using our utility function
            return extract_song_data(response.text)
            
        except Exception as e:
            logger.error(f"Error enriching metadata: {e}")
            return None
    
    def _safe_filename(self, filename):
        """
        Create a safe filename from the given string.
        
        Args:
            filename (str): Original filename
            
        Returns:
            str: Safe filename
        """
        # Remove invalid characters
        safe = re.sub(r'[\\/*?:"<>|]', "", filename)
        # Replace spaces and multiple dashes
        safe = re.sub(r'\s+', "-", safe)
        safe = re.sub(r'-+', "-", safe)
        # Limit length
        if len(safe) > 100:
            safe = safe[:97] + "..."
        return safe
