import json
import os


def create_markdown_from_suno_json(json_file):
    """Parses a Suno JSON file and creates a formatted Markdown file."""

    with open(json_file, "r") as f:
        data = json.load(f)

    markdown_file = os.path.splitext(json_file)[0] + ".md"

    with open(markdown_file, "w", encoding="utf-8") as f:
        for song in data:
            f.write(f"# Title: {song['title']}\n\n")
            f.write(f"Image URL: {song['image_url']}\n\n")

            f.write(f"**Created At:** {song['created_at']}\n")
            f.write(f"**Song ID:** {song['id']}\n")
            f.write(f"**Duration:** {song['duration']}\n\n")

            f.write(f"**Audio URL:** {song['audio_url']}\n")
            f.write(f"**Video URL:** {song['video_url']}\n\n")

            f.write(f"**Tags:** {song['tags']}\n\n")

            f.write(f"**Lyrics:**\n\n")
            f.write(f"```\n{format_lyrics(song['lyric'])}\n```\n\n")

            f.write(f"---\n\n")  # Separator between songs


def format_lyrics(lyrics):
    """Formats lyrics by adding extra newlines after section headers."""
    formatted_lyrics = ""
    for line in lyrics.splitlines():
        if line.startswith("["):  # Add an extra newline *before* section headers
            formatted_lyrics += "\n"
        formatted_lyrics += line + "\n"
    return formatted_lyrics


if __name__ == "__main__":
    json_filename = "suno.json"
    create_markdown_from_suno_json(json_filename)
    print(f"Markdown file '{json_filename}.md' created successfully.")
