import json
import os

# Raw string to handle backslashes
file_path = r"C:\Users\User\Documents\Github\suno_ai_downloader\allsongs.json"
output_file = "MPS.md"


def create_markdown_file(data, output_file):
    """
    Extracts song data from the JSON and writes it to a formatted markdown file.
    """

    try:
        playlist_clips = data.get("playlist_clips", [])

        # Explicit encoding for non-ASCII characters
        with open(output_file, "w", encoding="utf-8") as md_file:
            for clip_data in playlist_clips:
                clip = clip_data.get("clip", {})
                title = clip.get("title", "Untitled")
                created_at = clip.get("created_at", "Unknown Date")
                lyrics = clip.get("metadata", {}).get(
                    "lyrics", "No lyrics available")

                md_file.write(f"## {title}\n\n")
                md_file.write(f"**Date Created:** {created_at}\n\n")
                md_file.write("**Lyrics**\n\n")
                md_file.write(f"{lyrics}\n\n")
                md_file.write("---\n\n")

        print(f"Successfully extracted data and wrote to {output_file}")

    except Exception as e:
        print(f"An error occurred: {e}")


# Load the JSON data from the file
try:
    # Explicit encoding for non-ASCII characters
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
except FileNotFoundError:
    print(f"Error: The file '{file_path}' was not found.")
    exit()
except json.JSONDecodeError:
    print(f"Error: The file '{file_path}' contains invalid JSON.")
    exit()

# Create the markdown file
create_markdown_file(data, output_file)
