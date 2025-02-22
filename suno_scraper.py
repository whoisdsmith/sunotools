import asyncio
import aiohttp
import logging
import re
from pathlib import Path
from typing import Optional, Dict, List
from bs4 import BeautifulSoup
from tqdm.asyncio import tqdm_asyncio

# Configure logging to output both to console and to a log file
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("suno_scraper.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)


async def extract_song_data(song_url: str, session: aiohttp.ClientSession) -> Optional[Dict[str, str]]:
    """
    Asynchronously extracts song data from a Suno song URL based on HTML analysis.

    Args:
        song_url (str): The URL of the Suno song page.
        session (aiohttp.ClientSession): The active aiohttp session.

    Returns:
        dict: A dictionary containing extracted song data, or None if extraction fails.
    """
    try:
        async with session.get(song_url) as response:
            response.raise_for_status()  # Raises exception for bad status codes
            content = await response.read()
            soup = BeautifulSoup(content, 'html.parser')
            song_data: Dict[str, str] = {}

            # 1. Cover Image URL
            cover_container = soup.find('div', class_='relative w-[200px]')
            if cover_container:
                img_tag = cover_container.find('img')
                if img_tag:
                    song_data['cover_image_url'] = img_tag.get('src')

            # 2. Song Title
            title_input = soup.find('input', type='text', value=True)
            if title_input:
                song_data['title'] = title_input.get('value')

            # 3. Artist Name and Profile Link
            artist_container = soup.find(
                'div', class_='flex flex-row items-center gap-2 font-sans font-medium text-sm text-primary')
            artist_link = artist_container.find(
                'a', href=re.compile(r'^/@')) if artist_container else None
            if artist_link:
                song_data['artist_name'] = artist_link.get_text(strip=True)
                href = artist_link.get('href')
                if href:
                    song_data['artist_profile_url'] = "https://suno.com" + href

                # 4. Artist Avatar Image URL
                avatar_container = artist_link.find_previous(
                    'div', class_='relative flex-shrink')
                if avatar_container:
                    avatar_img = avatar_container.find('img')
                    if avatar_img:
                        song_data['artist_avatar_url'] = avatar_img.get('src')

            # 5. Song Tags/Genres
            genres_container = soup.find(
                'div', class_='font-sans break-all gap-2 text-sm text-lightGray')
            if genres_container:
                genre_links = genres_container.find_all(
                    'a', class_='hover:underline text-primary')
                song_data['genres'] = [link.get_text(
                    strip=True) for link in genre_links]

            # 6. Song Creation Date/Time
            date_time_elem = soup.find(
                'span', class_='text-secondary text-sm', title=True)
            if date_time_elem:
                song_data['creation_date_time'] = date_time_elem.get('title')

            # 7. Song Version
            version_elem = soup.find('span', string=re.compile(
                r'^v\d+$'), class_='text-xs font-medium font-sans')
            if version_elem:
                song_data['version'] = version_elem.get_text(strip=True)

            # 8. Lyrics
            lyrics_elem = soup.find('p', class_='whitespace-pre-wrap')
            if lyrics_elem:
                song_data['lyrics'] = lyrics_elem.get_text(strip=True)

            logging.info(f"Successfully extracted data for: {song_url}")
            return song_data

    except Exception as e:
        logging.error(f"Error processing URL: {song_url} - {e}")
        return None


def format_song_markdown(song_data: Dict[str, str], song_url: str) -> str:
    """
    Formats song data into markdown.

    Args:
        song_data (dict): Dictionary of song data.
        song_url (str): The original Suno song URL.

    Returns:
        str: Markdown formatted string for the song.
    """
    if not song_data:
        return ""

    markdown_output = (
        f"## {song_data.get('title', 'Unknown Title')}\n\n"
        f"**Artist:** {song_data.get('artist_name', 'Unknown Artist')} "
        f"([Profile]({song_data.get('artist_profile_url', '#')}))\n\n"
        f"**Suno Song URL:** [{song_url}]({song_url})\n\n"
    )

    if 'cover_image_url' in song_data:
        markdown_output += f"![Cover Image]({song_data['cover_image_url']})\n\n"

    if 'genres' in song_data:
        markdown_output += "**Genres:**\n"
        for genre in song_data['genres']:
            markdown_output += f"- {genre}\n"
        markdown_output += "\n"

    if 'creation_date_time' in song_data:
        markdown_output += f"**Creation Date & Time:** {song_data['creation_date_time']}\n\n"

    if 'version' in song_data:
        markdown_output += f"**Version:** {song_data['version']}\n\n"

    if 'lyrics' in song_data:
        markdown_output += "**Lyrics:**\n```\n"
        markdown_output += song_data['lyrics'] + "\n```\n\n"

    markdown_output += "---\n"  # Separator between songs
    return markdown_output


def load_song_urls(file_path: Path) -> List[str]:
    """
    Loads and splits song URLs from a file.

    Args:
        file_path (Path): Path to the file containing URLs.

    Returns:
        List[str]: List of song URLs.
    """
    try:
        content = file_path.read_text(encoding='utf-8').strip()
        # Assuming URLs are on a single line separated by spaces
        return [url for url in content.split() if url]
    except Exception as e:
        logging.error(f"Error reading URL file: {e}")
        return []


async def main():
    # Define the file path using pathlib for cross-platform compatibility
    url_file_path = Path(
        r"C:\Users\User\Documents\Github\suno_ai_downloader\unique_songs.txt")

    if not url_file_path.exists():
        logging.error(f"Error: URL file not found at {url_file_path}")
        return

    song_urls = load_song_urls(url_file_path)
    if not song_urls:
        logging.info("No song URLs found in the file.")
        return

    all_songs_markdown = ""

    # Create tasks and a mapping from each task to its URL
    tasks_list = []
    task_mapping = {}
    async with aiohttp.ClientSession() as session:
        for url in song_urls:
            if url:
                task = asyncio.create_task(extract_song_data(url, session))
                tasks_list.append(task)
                task_mapping[task] = url

        # Process tasks as they complete with a progress bar
        for future in tqdm_asyncio.as_completed(tasks_list, total=len(tasks_list), desc="Processing songs"):
            song_data = await future
            original_url = task_mapping.get(future, "Unknown URL")
            if song_data:
                all_songs_markdown += format_song_markdown(
                    song_data, original_url)
            else:
                logging.warning(
                    f"Skipping URL due to extraction failure: {original_url}")

    output_file_path = Path("suno_song_data.md")
    try:
        output_file_path.write_text(all_songs_markdown, encoding="utf-8")
        logging.info(f"Song data extracted and saved to {output_file_path}")
    except Exception as e:
        logging.error(f"Error writing markdown file: {e}")

if __name__ == "__main__":
    asyncio.run(main())
