import requests
from bs4 import BeautifulSoup
import argparse

def extract_song_links_from_playlist(playlist_url):
    """
    Extracts song links from a public SunoAI playlist URL.

    Args:
        playlist_url (str): The URL of the public SunoAI playlist.

    Returns:
        list: A list of song URLs extracted from the playlist, or None if an error occurs.
    """
    try:
        response = requests.get(playlist_url)
        response.raise_for_status()  # Raise an exception for HTTP errors

        soup = BeautifulSoup(response.content, 'html.parser')

        song_links = []
        # Inspecting SunoAI playlist page, song links are typically in 'a' tags
        # that have href attributes starting with '/song/' and are within a specific section.
        # Let's try a general approach to find all such links first.
        for link_tag in soup.find_all('a', href=True):
            href = link_tag['href']
            if href.startswith('/song/'):
                full_song_link = f"https://suno.com{href}"
                song_links.append(full_song_link)

        # Remove duplicate links if any and return the unique song links
        return list(set(song_links))

    except requests.exceptions.RequestException as e:
        print(f"Error fetching playlist URL: {e}")
        return None
    except Exception as e:
        print(f"Error parsing playlist page: {e}")
        return None

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract song links from a public SunoAI playlist.")
    parser.add_argument("playlist_url", help="The public SunoAI playlist URL")

    args = parser.parse_args()
    playlist_url = args.playlist_url

    if not playlist_url.startswith("https://suno.com/playlist/"):
        print("Error: Please provide a valid SunoAI playlist URL that starts with 'https://suno.com/playlist/'")
    else:
        song_links = extract_song_links_from_playlist(playlist_url)

        if song_links:
            print("\nExtracted Song Links from the Playlist:")
            for link in song_links:
                print(link)
        else:
            print("No song links found or an error occurred.")