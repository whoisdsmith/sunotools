"""
Extractor module for Suno.com

Extracts lyrics and song data from HTML pages.
"""

import re
import json
import logging
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

def extract_lyrics(html_content):
    """
    Extract lyrics from a song page HTML.
    
    Args:
        html_content (str): HTML content of the song page
        
    Returns:
        str: Lyrics text or None if not found
    """
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Try common selectors for lyrics
        lyrics_selectors = [
            '.lyrics-container',
            '.song-lyrics',
            '.lyrics-content',
            '.lyric-body',
            '#lyrics',
            '[data-lyrics]',
            '.lyrics'
        ]
        
        for selector in lyrics_selectors:
            lyrics_elem = soup.select_one(selector)
            if lyrics_elem:
                return lyrics_elem.get_text(strip=True)
        
        # Try to find lyrics in script tags
        scripts = soup.find_all('script')
        for script in scripts:
            if not script.string:
                continue
                
            # Look for lyrics in various formats
            lyrics_patterns = [
                r'"lyrics"\s*:\s*"([^"]+)"',
                r'"lyrics":"([^"]+)"',
                r'"text"\s*:\s*"([^"]+)"',
                r'"lyrics":\s*`([^`]+)`'
            ]
            
            for pattern in lyrics_patterns:
                match = re.search(pattern, script.string, re.DOTALL)
                if match:
                    # Clean up escaped characters
                    lyrics = match.group(1)
                    lyrics = lyrics.replace('\\n', '\n').replace('\\r', '').replace('\\t', '')
                    lyrics = lyrics.replace('\\"', '"').replace('\\\\', '\\')
                    return lyrics
        
        # Try to look for structured data
        json_ld = soup.find('script', {'type': 'application/ld+json'})
        if json_ld and json_ld.string:
            try:
                ld_data = json.loads(json_ld.string)
                if isinstance(ld_data, dict) and 'lyrics' in ld_data:
                    return ld_data['lyrics']
            except json.JSONDecodeError:
                pass
        
        # Look for a div with ID containing 'lyric'
        lyric_divs = soup.find_all('div', id=lambda x: x and 'lyric' in x.lower())
        if lyric_divs:
            return lyric_divs[0].get_text(strip=True)
        
        # Last resort: look for paragraphs within main content
        main_content = soup.find('main') or soup.find('article') or soup
        paragraphs = main_content.find_all('p', limit=20)  # Limit to avoid getting too much unrelated text
        
        # If we find paragraphs with decent amount of text, they might be lyrics
        potential_lyrics = []
        for p in paragraphs:
            text = p.get_text(strip=True)
            if len(text) > 20:  # Threshold for a meaningful line of lyrics
                potential_lyrics.append(text)
        
        if potential_lyrics:
            return "\n\n".join(potential_lyrics)
        
    except Exception as e:
        logger.error(f"Error extracting lyrics: {e}")
    
    return None

def extract_song_data(html_content):
    """
    Extract song data from a song page HTML.
    
    Args:
        html_content (str): HTML content of the song page
        
    Returns:
        dict: Song data or None if not found
    """
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # First, try to find song data in script tags
        scripts = soup.find_all('script')
        
        for script in scripts:
            if not script.string:
                continue
                
            # Look for song data in common patterns
            song_data_patterns = [
                r'window\.__SONG__\s*=\s*({.*?});',
                r'window\.__INITIAL_STATE__\s*=\s*({.*?});',
                r'"song"\s*:\s*({.*?})[\,\}]',
                r'song\s*:\s*({.*?})[\,\}]'
            ]
            
            for pattern in song_data_patterns:
                matches = re.search(pattern, script.string, re.DOTALL)
                if matches:
                    try:
                        song_data = json.loads(matches.group(1))
                        
                        # If we found song data, clean it up and return
                        if isinstance(song_data, dict):
                            # If 'song' is nested within the data, extract it
                            if 'song' in song_data and isinstance(song_data['song'], dict):
                                return song_data['song']
                            return song_data
                    except json.JSONDecodeError:
                        continue
        
        # If we couldn't find song data in scripts, try to extract it from the page
        song_data = {}
        
        # Extract title
        title_elem = soup.find('h1') or soup.find('title')
        if title_elem:
            title = title_elem.text.strip()
            # Remove website name if present
            title = re.sub(r'\s*\|\s*Suno.*$', '', title)
            song_data['title'] = title
        
        # Extract metadata
        meta_description = soup.find('meta', {'name': 'description'})
        if meta_description:
            song_data['description'] = meta_description.get('content')
        
        meta_keywords = soup.find('meta', {'name': 'keywords'})
        if meta_keywords:
            song_data['keywords'] = meta_keywords.get('content')
        
        # Extract song ID
        song_id_elem = soup.find('meta', {'property': 'al:ios:url'})
        if song_id_elem:
            url = song_id_elem.get('content', '')
            song_id_match = re.search(r'song/([^/]+)', url)
            if song_id_match:
                song_data['id'] = song_id_match.group(1)
        
        # Extract image URL
        og_image = soup.find('meta', {'property': 'og:image'})
        if og_image:
            song_data['artwork_url'] = og_image.get('content')
        
        # Extract audio URL
        audio_elem = soup.find('audio')
        if audio_elem and audio_elem.get('src'):
            song_data['audio_url'] = audio_elem.get('src')
        
        # Extract creation date
        date_elem = soup.find('time') or soup.find(class_=lambda c: c and 'date' in c)
        if date_elem:
            if date_elem.get('datetime'):
                song_data['created_at'] = date_elem.get('datetime')
            else:
                song_data['created_at'] = date_elem.text.strip()
        
        # Extract lyrics
        lyrics = extract_lyrics(html_content)
        if lyrics:
            song_data['lyrics'] = lyrics
        
        # Extract author/artist
        author_elem = soup.find(class_=lambda c: c and ('author' in c or 'artist' in c))
        if author_elem:
            song_data['artist'] = author_elem.text.strip()
        
        # If we have at least some basic data, return it
        if song_data.get('title') or song_data.get('id'):
            return song_data
        
    except Exception as e:
        logger.error(f"Error extracting song data: {e}")
    
    return None
