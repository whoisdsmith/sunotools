import requests
from bs4 import BeautifulSoup
import re
import os


def extract_song_data(song_url):
    """
    Extracts song data from a Suno song URL based on HTML analysis.

    Args:
        song_url (str): The URL of the Suno song page.

    Returns:
        dict: A dictionary containing extracted song data, or None if extraction fails.
    """
    try:
        response = requests.get(song_url)
        response.raise_for_status()  # Raise an exception for bad status codes
        soup = BeautifulSoup(response.content, 'html.parser')

        song_data = {}

        # 1. Cover Image URL
        cover_image_element = soup.find('div', class_='relative w-[200px]')
        if cover_image_element:
            img_tag = cover_image_element.find('img')
            if img_tag:
                song_data['cover_image_url'] = img_tag.get('src')

        # 2. Song Title
        title_input_element = soup.find('input', type='text', value=True)
        if title_input_element:
            song_data['title'] = title_input_element.get('value')

        # 3. Artist Name and Profile Link
        artist_link_element = soup.find('div', class_='flex flex-row items-center gap-2 font-sans font-medium text-sm text-primary').find(
            'a', href=re.compile(r'^/@')) if soup.find('div', class_='flex flex-row items-center gap-2 font-sans font-medium text-sm text-primary') else None
        if artist_link_element:
            song_data['artist_name'] = artist_link_element.text.strip()
            song_data['artist_profile_url'] = "https://suno.com" + \
                artist_link_element.get('href')

        # 4. Artist Avatar Image URL
        if artist_link_element:  # Reuse artist_link_element context to find avatar nearby
            artist_avatar_img_element = artist_link_element.find_previous('div', class_='relative flex-shrink').find(
                'img') if artist_link_element.find_previous('div', class_='relative flex-shrink') else None
            if artist_avatar_img_element:
                song_data['artist_avatar_url'] = artist_avatar_img_element.get(
                    'src')

        # 5. Song Tags/Genres
        genres_container = soup.find(
            'div', class_='font-sans break-all gap-2 text-sm text-lightGray')
        if genres_container:
            genre_links = genres_container.find_all(
                'a', class_='hover:underline text-primary')
            song_data['genres'] = [link.text.strip() for link in genre_links]

        # 6. Song Creation Date/Time
        date_time_element = soup.find(
            'span', class_='text-secondary text-sm', title=True)
        if date_time_element:
            song_data['creation_date_time'] = date_time_element.get('title')

        # 7. Song Version
        version_element = soup.find('span', string=re.compile(
            r'^v\d+$'), class_='text-xs font-medium font-sans')
        if version_element:
            song_data['version'] = version_element.text.strip()

        # 8. Lyrics
        lyrics_p_element = soup.find('p', class_='whitespace-pre-wrap')
        if lyrics_p_element:
            song_data['lyrics'] = lyrics_p_element.text.strip()

        return song_data

    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL: {song_url} - {e}")
        return None
    except AttributeError as e:
        print(
            f"Error parsing HTML for URL: {song_url} - {e} (HTML structure might have changed)")
        return None


def format_song_markdown(song_data, song_url):
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

    markdown_output = f"""
## {song_data.get('title', 'Unknown Title')}

**Artist:** {song_data.get('artist_name', 'Unknown Artist')} ([Profile]({song_data.get('artist_profile_url', '#')}))

**Suno Song URL:** [{song_url}]({song_url})

"""

    if 'cover_image_url' in song_data:
        markdown_output += f"""
![Cover Image]({song_data['cover_image_url']})

"""

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
        markdown_output += "**Lyrics:**\n"
        markdown_output += "```\n"
        markdown_output += song_data['lyrics']
        markdown_output += "\n```\n\n"

    markdown_output += "---\n"  # Separator between songs
    return markdown_output


if __name__ == "__main__":
    # Raw string for Windows path
    url_file_path = r"C:\Users\User\Documents\Github\suno_ai_downloader\unique_songs.txt"

    song_urls = []
    try:
        with open(url_file_path, "r") as file:
            urls_line = file.readline()
            song_urls = urls_line.strip().split(" ")  # Split by space and strip whitespace
    except FileNotFoundError:
        print(f"Error: URL file not found at {url_file_path}")
        exit()
    except Exception as e:
        print(f"Error reading URL file: {e}")
        exit()

    if not song_urls:
        print("No song URLs found in the file.")
        exit()

    all_songs_markdown = ""

    for url in song_urls:
        if url.strip():  # Check for empty URLs in case of extra spaces
            # strip url to remove any leading/trailing whitespaces
            song_data = extract_song_data(url.strip())
            if song_data:
                all_songs_markdown += format_song_markdown(
                    song_data, url.strip())

    # Save to markdown file
    output_file_path = "suno_song_data.md"
    with open(output_file_path, "w", encoding="utf-8") as md_file:
        md_file.write(all_songs_markdown)

    print(f"Song data extracted and saved to {output_file_path}")
