# Suno Song Downloader

An efficient and automated tool to download songs from Suno.com, including cover images, lyrics, and metadata in MP3 format.

## Features

- **Concurrent Downloads**: Uses asyncio for efficient parallel downloading
- **Progress Tracking**: Maintains download progress and can resume interrupted downloads
- **Metadata Management**: Embeds lyrics, cover art, and GPT prompts into MP3 files
- **Rate Limiting**: Prevents server overload and blocking
- **Error Handling**: Robust retry mechanism for failed downloads
- **Organized Output**: Creates a structured directory for each song

## Requirements

- Python 3.8 or higher
- pip (Python package installer)

## Installation

1. Clone this repository:

   ```bash
   git clone https://github.com/yourusername/suno-downloader.git
   cd suno-downloader
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Install Playwright browsers:

   ```bash
   playwright install chromium
   ```

## Usage

1. Create a file named `url.txt` containing Suno song URLs (one per line)

2. Run the downloader:

   ```bash
   python suno_downloader.py
   ```

3. The script will:
   - Create a `downloads` directory for the songs
   - Download MP3s, cover images, and metadata
   - Show progress with a progress bar
   - Save download progress in case of interruption

## Output Structure

```plaintext
downloads/
├── song_name_1/
│   ├── song_name_1.mp3 (with embedded metadata)
│   ├── cover.jpg
│   ├── lyrics.txt
│   └── prompt.txt
├── song_name_2/
...
```

## Configuration

You can modify the following settings in the script:

- `max_concurrent_downloads`: Number of parallel downloads (default: 5)
- `retry_attempts`: Number of retry attempts for failed downloads (default: 3)
- `rate_limit_delay`: Delay between requests in seconds (default: 1.0)
- `download_timeout`: Download timeout in seconds (default: 300)

## Progress Tracking

The script maintains two JSON files:

- `download_progress.json`: Tracks download progress
- `session.json`: Stores session information

These files allow the script to resume interrupted downloads.

## Logging

Logs are stored in the `Logs` directory:

- `suno_downloader.log`: Contains detailed operation logs

## Error Handling

The script implements several error handling mechanisms:

- Automatic retries for failed downloads
- Rate limiting to prevent server blocks
- Progress saving for resuming interrupted downloads

## Contributing

Feel free to submit issues and enhancement requests!

## License

This project is licensed under the MIT License - see the LICENSE file for details.
