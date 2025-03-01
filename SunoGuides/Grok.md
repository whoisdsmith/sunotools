# GrokSuno

To address your query, I've created a JavaScript script that parses a list of Suno.com song URLs and extracts detailed song and artist information, including the song title, artist name, lyrics, song ID, creation date, genre tags, cover image URL, and audio URL. The script then formats this information into nicely structured Markdown files, one for each song. Below is the complete solution, including explanations and instructions for use.

---

## Solution

### Overview

This script:

1. Accepts multiple Suno.com song URLs as command-line arguments.
2. Fetches the HTML content of each song page using `node-fetch`.
3. Extracts song metadata embedded in `<script>` tags using `node-html-parser`.
4. Parses the extracted JSON data to retrieve song details.
5. Extracts the song ID from the URL.
6. Formats the information into a Markdown file for each song, saved in a `songs` directory.

### Requirements

- **Node.js**: Ensure you have Node.js installed (version supporting ES modules, e.g., 14+).
- **Dependencies**: Install the required packages by running:

  ```bash
  npm install node-fetch node-html-parser
  ```

### Script Code

Create a file named `parseSunoSongs.js` and add the following code:

```javascript
import * as fs from 'fs/promises';
import fetch from 'node-fetch';
import { parse } from 'node-html-parser';

// Fetch HTML content from a URL
async function fetchPageContent(url) {
    const response = await fetch(url);
    if (!response.ok) {
        throw new Error(`Failed to fetch ${url}: ${response.statusText}`);
    }
    return await response.text();
}

// Extract all script tags from HTML
function extractScriptTags(html) {
    const root = parse(html);
    return root.querySelectorAll('script');
}

// Find script tags containing Suno data (self.__next_f.push)
function findDataScripts(scriptTags) {
    return scriptTags.filter(script => script.text.includes('self.__next_f.push'));
}

// Extract JSON data and lyrics from script tags
function extractDataFromScripts(dataScripts) {
    let concatenatedData = '';
    let lyricsData = '';

    for (const script of dataScripts) {
        const match = script.text.match(/self\.__next_f\.push\(\[\d+,"(.*)"\]\)/s);
        if (match && match[1]) {
            const unescapedString = JSON.parse(`"${match[1]}"`);
            if (unescapedString.trim().startsWith('{"clip":')) {
                concatenatedData += unescapedString;
            } else {
                lyricsData += unescapedString + '\n';
            }
        }
    }

    return { concatenatedData, lyricsData };
}

// Parse JSON data from concatenated script content
function extractJsonData(concatenatedData) {
    const jsonStartIndex = concatenatedData.indexOf('{"clip":');
    if (jsonStartIndex === -1) {
        throw new Error('JSON data not found in script content.');
    }

    const jsonString = concatenatedData.slice(jsonStartIndex);
    try {
        return JSON.parse(jsonString);
    } catch (error) {
        const positionMatch = error.message.match(/at position (\d+)/);
        if (positionMatch) {
            return JSON.parse(jsonString.slice(0, parseInt(positionMatch[1])));
        }
        throw new Error('Failed to parse JSON data.');
    }
}

// Extract song information from JSON data
function extractSongInformation(jsonData) {
    const clip = jsonData.clip;
    return {
        title: clip.title || 'Unknown Title',
        artist: clip.display_name || 'Unknown Artist',
        coverImageUrl: clip.image_large_url || clip.image_url || 'No Image URL',
        creationDate: clip.created_at || 'Unknown Date',
        audioUrl: clip.audio_url || 'No Audio URL',
        tags: Array.isArray(clip.metadata.tags) ? clip.metadata.tags.join(', ') : clip.metadata.tags || 'No Tags'
    };
}

// Sanitize filenames to remove invalid characters
function sanitizeFileName(name) {
    return name.replace(/[<>:"/\\|?*]/g, '-');
}

// Save song details to a Markdown file
async function saveSongDetailsAsMarkdown(details) {
    const { title, artist, tags, lyrics, coverImageUrl, creationDate, audioUrl, songId } = details;

    const markdownContent = `
# ${title}

**Song ID:** ${songId}

![Cover Image](${coverImageUrl})

**Artist:** ${artist}
**Tags:** ${tags}
**Release Date:** ${creationDate}
**Cover Image Download:** [Download Image](${coverImageUrl})
**Audio Download:** [Download Audio](${audioUrl})

## Lyrics:
${lyrics}
    `;

    const sanitizedArtist = sanitizeFileName(artist);
    const sanitizedTitle = sanitizeFileName(title);
    const markdownFilename = `songs/${sanitizedArtist} - ${sanitizedTitle} - ${songId}.md`;

    await fs.mkdir('songs', { recursive: true });
    await fs.writeFile(markdownFilename, markdownContent.trim());
    console.log(`Saved: ${markdownFilename}`);
}

// Process a single URL
async function processURL(url) {
    try {
        const html = await fetchPageContent(url);
        const scriptTags = extractScriptTags(html);
        const dataScripts = findDataScripts(scriptTags);
        const { concatenatedData, lyricsData } = extractDataFromScripts(dataScripts);
        const jsonData = extractJsonData(concatenatedData);
        const songDetails = extractSongInformation(jsonData);
        songDetails.lyrics = lyricsData.trim() || 'Lyrics not available';
        songDetails.songId = url.split('/').pop();

        await saveSongDetailsAsMarkdown(songDetails);
    } catch (error) {
        console.error(`Error processing ${url}:`, error.message);
    }
}

// Main execution: process all URLs from command-line arguments
async function main() {
    const urls = process.argv.slice(2);
    if (urls.length === 0) {
        console.error('Please provide at least one Suno song URL.');
        process.exit(1);
    }

    for (const url of urls) {
        if (!url.match(/https:\/\/suno\.com\/song\/[0-9a-f-]{36}/)) {
            console.warn(`Skipping invalid URL: ${url}`);
            continue;
        }
        await processURL(url);
    }
}

main().catch(error => console.error('Script failed:', error));
```

---

## How to Use

### Running the Script

1. Save the script as `parseSunoSongs.js`.
2. Open a terminal in the script's directory.
3. Install dependencies:

   ```bash
   npm install node-fetch node-html-parser
   ```

4. Run the script with one or more Suno song URLs:

   ```bash
   node parseSunoSongs.js https://suno.com/song/12bfb381-df41-4452-9846-399e5e70153d https://suno.com/song/c0e77570-5f30-4482-a981-bd169f75432e
   ```

### Output

- For each valid URL, the script creates a Markdown file in the `songs` directory.
- Filename format: `Artist - Title - SongID.md` (e.g., `The Casket Diaries - Neon Lights & Lullabies - 12bfb381-df41-4452-9846-399e5e70153d.md`).
- Example Markdown content:

  ```
  # Neon Lights & Lullabies

  **Song ID:** 12bfb381-df41-4452-9846-399e5e70153d

  ![Cover Image](https://cdn2.suno.ai/image_large_c0e77570-5f30-4482-a981-bd169f75432e.jpeg)

  **Artist:** The Casket Diaries
  **Tags:** midwest emo, electronic
  **Release Date:** 2024-12-07T04:15:00Z
  **Cover Image Download:** [Download Image](https://cdn2.suno.ai/image_large_c0e77570-5f30-4482-a981-bd169f75432e.jpeg)
  **Audio Download:** [Download Audio](https://cdn1.suno.ai/12bfb381-df41-4452-9846-399e5e70153d.mp3)

  ## Lyrics:
  [Intro]
  [Verse 1]
  Neon lights flicker in the night...
  ```

- If a URL fails (e.g., invalid or network error), the script logs an error and continues with the next URL.

---

## Explanation of Extracted Information

| **Information**       | **Source**                         | **Notes**                                                                 |
|-----------------------|------------------------------------|---------------------------------------------------------------------------|
| **Song Title**        | JSON: `clip.title`                | Falls back to "Unknown Title" if missing.                                |
| **Artist Name**       | JSON: `clip.display_name`         | Falls back to "Unknown Artist" if missing.                               |
| **Lyrics**            | Script tags (non-JSON content)    | Collected from script text; "Lyrics not available" if none found.        |
| **Song ID**           | URL (last segment)                | Extracted from the URL path (e.g., `12bfb381-df41-4452-9846-399e5e70153d`). |
| **Date**              | JSON: `clip.created_at`           | ISO format (e.g., `2024-12-07T04:15:00Z`); "Unknown Date" if missing.    |
| **Genre Tags**        | JSON: `clip.metadata.tags`        | Joined with commas if an array; "No Tags" if missing.                    |
| **Cover Image URL**   | JSON: `clip.image_large_url` or `clip.image_url` | Direct link; "No Image URL" if missing.                  |
| **Audio URL**         | JSON: `clip.audio_url`            | Direct link; "No Audio URL" if missing. May require authentication.      |

---

## Notes and Limitations

- **Dynamic Content**: The script relies on data embedded in `<script>` tags (`self.__next_f.push`). If Suno changes how data is loaded (e.g., fully API-based), the script may need adjustment.
- **Audio URL Access**: The `audio_url` from the JSON is included as the download link. However, downloading may require authentication or adherence to Suno’s terms, depending on your account status.
- **Lyrics**: Extracted from script tags; may include extra text if not cleanly separated from other data. An alternative approach using HTML parsing (e.g., `<p>` with class `whitespace-pre-wrap`) could be implemented for precision.
- **Error Handling**: The script skips invalid URLs and logs errors without stopping execution.

This script fulfills your request by extracting all specified song information from Suno.com URLs and formatting it into readable Markdown files. Adjust the selectors or data extraction logic if Suno’s website structure changes. Let me know if you need further customization!

---

Below is a Python script that combines the knowledge from the provided `whoisdsmith-sunotools/` project to parse a list of Suno.com song URLs, extract detailed song and artist information (including lyrics, song ID, artist name, song name, date, genre tags, cover image URL, and audio URL), and output the results into nicely formatted Markdown files. This script leverages techniques from files like `Grok.md`, `suno_downloader.py`, and `json2md.py`, using libraries such as `requests` for fetching pages, `BeautifulSoup` for HTML parsing, and custom logic to extract data from Suno's `<script>` tags.

The script accepts a text file with Suno song URLs (one per line), processes each URL, and saves the output as individual Markdown files in a `songs/` directory, named in the format `Artist - Song Name - SongID.md`.

---

### Script: `parse_suno_to_markdown.py`

```python
import os
import re
import json
import requests
from bs4 import BeautifulSoup
import argparse
from datetime import datetime

# Default headers to mimic a browser request
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def fetch_page_content(url):
    """Fetch HTML content from a Suno URL."""
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None

def extract_script_data(html):
    """Extract data from self.__next_f.push script tags."""
    if not html:
        return None, None
    soup = BeautifulSoup(html, 'html.parser')
    script_tags = soup.find_all('script')
    concatenated_data = ''
    lyrics_data = ''

    for script in script_tags:
        if 'self.__next_f.push' in script.text:
            match = re.search(r'self\.__next_f\.push\(\[\d+,"(.*)"\]\)', script.text, re.DOTALL)
            if match and match[1]:
                unescaped = json.loads(f'"{match[1]}"')
                if unescaped.strip().startswith('{"clip":'):
                    concatenated_data += unescaped
                else:
                    lyrics_data += unescaped + '\n'

    return concatenated_data, lyrics_data.strip()

def parse_json_data(concatenated_data):
    """Parse JSON data from concatenated script content."""
    if not concatenated_data:
        return None
    json_start = concatenated_data.index('{"clip":')
    json_str = concatenated_data[json_start:]

    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        position = re.search(r'at position (\d+)', str(e))
        if position:
            valid_json = json_str[:int(position.group(1))]
            return json.loads(valid_json)
        print(f"Failed to parse JSON: {e}")
        return None

def extract_song_info(json_data, lyrics_data, url):
    """Extract song and artist information from JSON and lyrics data."""
    if not json_data or 'clip' not in json_data:
        return None

    clip = json_data['clip']
    song_id = url.split('/')[-1]
    title = clip.get('title', 'Unknown Title')
    artist = clip.get('display_name', 'Unknown Artist')
    creation_date = clip.get('created_at', 'Unknown Date')
    tags = clip.get('metadata', {}).get('tags', 'No Tags')
    if isinstance(tags, list):
        tags = ', '.join(tags)
    cover_image_url = clip.get('image_large_url', clip.get('image_url', 'No Image URL'))
    audio_url = clip.get('audio_url', 'No Audio URL')
    lyrics = lyrics_data if lyrics_data else 'Lyrics not available'

    return {
        'song_id': song_id,
        'title': title,
        'artist': artist,
        'creation_date': creation_date,
        'tags': tags,
        'cover_image_url': cover_image_url,
        'audio_url': audio_url,
        'lyrics': lyrics
    }

def sanitize_filename(name):
    """Sanitize filenames by removing invalid characters."""
    return re.sub(r'[<>:"/\\|?*]', '-', name)

def save_to_markdown(song_info):
    """Save song information to a formatted Markdown file."""
    if not song_info:
        return

    output_dir = 'songs'
    os.makedirs(output_dir, exist_ok=True)

    sanitized_artist = sanitize_filename(song_info['artist'])
    sanitized_title = sanitize_filename(song_info['title'])
    filename = f"{output_dir}/{sanitized_artist} - {sanitized_title} - {song_info['song_id']}.md"

    # Format creation date
    try:
        date_obj = datetime.fromisoformat(song_info['creation_date'].replace('Z', '+00:00'))
        formatted_date = date_obj.strftime('%B %d, %Y at %I:%M %p UTC')
    except ValueError:
        formatted_date = song_info['creation_date']

    markdown_content = f"""# {song_info['title']}

**Song ID:** {song_info['song_id']}

![Cover Image]({song_info['cover_image_url']})

**Artist:** {song_info['artist']}
**Genre Tags:** {song_info['tags']}
**Release Date:** {formatted_date}
**Cover Image URL:** [{song_info['cover_image_url']}]({song_info['cover_image_url']})
**Audio URL:** [{song_info['audio_url']}]({song_info['audio_url']})

## Lyrics

```

{song_info['lyrics']}

```
"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(markdown_content.strip())
        print(f"Saved: {filename}")
    except IOError as e:
        print(f"Error saving {filename}: {e}")

def process_url(url):
    """Process a single Suno song URL and extract information."""
    print(f"Processing: {url}")
    html = fetch_page_content(url)
    if not html:
        return

    concatenated_data, lyrics_data = extract_script_data(html)
    if not concatenated_data:
        print(f"No valid script data found for {url}")
        return

    json_data = parse_json_data(concatenated_data)
    if not json_data:
        print(f"Could not parse JSON data for {url}")
        return

    song_info = extract_song_info(json_data, lyrics_data, url)
    if song_info:
        save_to_markdown(song_info)
    else:
        print(f"Failed to extract song info for {url}")

def main():
    parser = argparse.ArgumentParser(description="Parse Suno.com song URLs and save info as Markdown.")
    parser.add_argument('--input', '-i', type=str, required=True,
                        help="Path to a text file containing Suno song URLs (one per line)")

    args = parser.parse_args()

    # Read URLs from the input file
    try:
        with open(args.input, 'r', encoding='utf-8') as f:
            urls = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"Input file {args.input} not found.")
        return
    except IOError as e:
        print(f"Error reading {args.input}: {e}")
        return

    if not urls:
        print("No URLs found in the input file.")
        return

    print(f"Found {len(urls)} URLs to process.")
    for url in urls:
        if not re.match(r'https://suno\.com/song/[0-9a-f-]{36}', url):
            print(f"Skipping invalid URL: {url}")
            continue
        process_url(url)

if __name__ == "__main__":
    main()
```

---

### How to Use the Script

1. **Prerequisites:**
   - Install required Python packages:

     ```bash
     pip install requests beautifulsoup4
     ```

   - Ensure Python 3.6+ is installed.

2. **Prepare Input File:**
   - Create a text file (e.g., `suno_urls.txt`) with Suno song URLs, one per line. Example:

     ```
     https://suno.com/song/12bfb381-df41-4452-9846-399e5e70153d
     https://suno.com/song/c0e77570-5f30-4482-a981-bd169f75432e
     ```

3. **Run the Script:**
   - Execute the script with the input file as an argument:

     ```bash
     python parse_suno_to_markdown.py --input suno_urls.txt
     ```

   - The script will process each URL and save the output in the `songs/` directory.

4. **Output:**
   - For each valid URL, a Markdown file is created in `songs/` with the format `Artist - Song Name - SongID.md`.
   - Example output file (`songs/The Casket Diaries - Neon Lights & Lullabies - 12bfb381-df41-4452-9846-399e5e70153d.md`):

     ```markdown
     # Neon Lights & Lullabies

     **Song ID:** 12bfb381-df41-4452-9846-399e5e70153d

     ![Cover Image](https://cdn2.suno.ai/image_large_c0e77570-5f30-4482-a981-bd169f75432e.jpeg)

     **Artist:** The Casket Diaries
     **Genre Tags:** midwest emo, electronic
     **Release Date:** December 7, 2024 at 04:15 AM UTC
     **Cover Image URL:** [https://cdn2.suno.ai/image_large_c0e77570-5f30-4482-a981-bd169f75432e.jpeg](https://cdn2.suno.ai/image_large_c0e77570-5f30-4482-a981-bd169f75432e.jpeg)
     **Audio URL:** [https://cdn1.suno.ai/12bfb381-df41-4452-9846-399e5e70153d.mp3](https://cdn1.suno.ai/12bfb381-df41-4452-9846-399e5e70153d.mp3)

     ## Lyrics

     ```

     [Intro]
     [Verse 1]
     Neon lights flicker in the night...

     ```
     ```

---

### Features and Implementation Details

1. **Input Handling:**
   - Accepts a text file with URLs via the `--input` argument, ensuring flexibility for batch processing.

2. **Data Extraction:**
   - Uses `requests` to fetch HTML and `BeautifulSoup` to parse `<script>` tags containing `self.__next_f.push` data (inspired by `Grok.md`).
   - Separates JSON data (song metadata) and lyrics from script content, handling edge cases like malformed JSON.

3. **Song Information:**
   - Extracts:
     - **Song ID:** From the URL.
     - **Title:** `clip.title`.
     - **Artist:** `clip.display_name`.
     - **Creation Date:** `clip.created_at`, formatted as a readable string.
     - **Genre Tags:** `clip.metadata.tags`, joined into a comma-separated string.
     - **Cover Image URL:** `clip.image_large_url` or `clip.image_url`.
     - **Audio URL:** `clip.audio_url`.
     - **Lyrics:** From non-JSON script content or defaults to "Lyrics not available".

4. **Output Formatting:**
   - Creates a `songs/` directory and saves each song’s data in a Markdown file.
   - Sanitizes filenames to remove invalid characters (e.g., `<`, `>`, `:`).
   - Formats the Markdown with a header, metadata table, embedded cover image, and lyrics in a code block.

5. **Error Handling:**
   - Validates URLs with a regex pattern.
   - Handles network errors, JSON parsing failures, and file I/O issues with informative messages.

---

### Notes and Limitations

- **Dependencies:** Requires only `requests` and `beautifulsoup4`, keeping it lightweight compared to alternatives using `playwright` or `puppeteer`.
- **Suno Structure Dependency:** Relies on Suno’s current `<script>` tag structure (`self.__next_f.push`). Changes to the site may break extraction.
- **No Downloads:** This script extracts metadata and URLs but does not download files (can be extended with `requests` if needed).
- **Lyrics Accuracy:** Lyrics extraction may include extra text if not cleanly separated in the script tags.

This script fulfills your request by providing a robust, standalone solution to parse Suno song URLs and format the output into Markdown files, leveraging the collective knowledge from your provided project files. Let me know if you’d like to extend it (e.g., to download files or add more features)!

---

To extract all 1318 liked song URLs from `https://suno.com/playlist/liked` while logged into Suno.com, where the page dynamically loads only 20-40 songs at a time, we'll need a script that can scroll through the playlist and capture all song URLs. Since the page uses lazy loading, a manual approach or static HTML scraping won't suffice—you'll need a tool that can interact with the page dynamically, such as Puppeteer (JavaScript) or Playwright (Python), to simulate scrolling and extract the links as they load.

Based on the knowledge from your provided `whoisdsmith-sunotools/` project, particularly the `SunoURLS/sunoGPX.js` script, which uses Puppeteer to scroll and extract song URLs from a Suno playlist, I’ll adapt that approach here. The script will:

- Navigate to `https://suno.com/playlist/liked`.
- Scroll until all 1318 songs are loaded (or no new content appears).
- Extract unique song URLs.
- Save them to a file.

Since you’re logged in, you’ll need to run this script in a browser context where your session cookies are available, but for automation, we’ll use Puppeteer with a pre-authenticated session (you’ll need to provide cookies manually). Here’s the script:

---

### Script: `extract_liked_songs.js`

```javascript
const puppeteer = require('puppeteer');
const fs = require('fs/promises');

async function extractLikedSongs(playlistUrl, cookieString, outputFile = 'liked_songs.txt') {
    // Launch browser with options to maximize and ensure visibility
    const browser = await puppeteer.launch({
        headless: false, // Set to false so you can see the browser; change to "new" for headless
        args: ['--start-maximized']
    });
    const page = await browser.newPage();

    // Set cookies to maintain logged-in state
    const cookies = cookieString.split('; ').map(cookie => {
        const [name, value] = cookie.split('=');
        return { name, value, domain: 'suno.com', path: '/' };
    });
    await page.setCookie(...cookies);

    try {
        // Navigate to the liked songs playlist
        console.log(`Navigating to ${playlistUrl}...`);
        await page.goto(playlistUrl, { waitUntil: 'networkidle2' });

        // Estimate total songs (optional, for validation)
        let totalSongs = 1318; // Hardcoded based on your input; adjust if needed
        console.log(`Target number of songs: ${totalSongs}`);

        // Scroll to load all songs
        let previousHeight;
        let attempts = 0;
        const maxAttempts = 50; // Increased to ensure all 1318 songs load
        const scrollDelay = 1500; // Delay after each scroll in milliseconds

        while (attempts < maxAttempts) {
            previousHeight = await page.evaluate('document.body.scrollHeight');
            await page.evaluate('window.scrollTo(0, document.body.scrollHeight)');
            await new Promise(resolve => setTimeout(resolve, scrollDelay));

            const newHeight = await page.evaluate('document.body.scrollHeight');
            if (newHeight === previousHeight) {
                attempts++;
            } else {
                attempts = 0; // Reset if new content loaded
            }

            // Check current number of songs loaded
            const loadedSongs = await page.$$eval('a[href^="/song/"]', links => links.length);
            console.log(`Songs loaded: ${loadedSongs}/${totalSongs}`);
            if (loadedSongs >= totalSongs) break; // Exit if all songs are loaded
        }

        // Extract all song URLs
        await page.waitForSelector('a[href^="/song/"]', { timeout: 30000 });
        const songLinks = await page.$$eval('a[href^="/song/"]', links =>
            links
                .map(a => a.getAttribute('href'))
                .filter(href => !href.includes('?show_comments=true'))
                .map(href => `https://suno.com${href}`)
        );

        // Remove duplicates
        const uniqueSongLinks = [...new Set(songLinks)];
        console.log(`Extracted ${uniqueSongLinks.length} unique song URLs.`);

        if (uniqueSongLinks.length < totalSongs) {
            console.warn(`Expected ${totalSongs} songs, but only found ${uniqueSongLinks.length}. Some may not have loaded.`);
        }

        // Save to file
        const outputString = uniqueSongLinks.join('\n');
        await fs.writeFile(outputFile, outputString, 'utf8');
        console.log(`Saved ${uniqueSongLinks.length} URLs to ${outputFile}`);

        return uniqueSongLinks;

    } catch (error) {
        console.error('Error fetching or processing playlist:', error);
        return [];
    } finally {
        await browser.close();
    }
}

async function main() {
    const playlistUrl = 'https://suno.com/playlist/liked';

    // Replace this with your actual cookie string from the browser
    // Example: '__client=abc123; session=xyz789; ...'
    const cookieString = 'YOUR_COOKIE_STRING_HERE'; // See instructions below to get this

    if (!cookieString || cookieString === 'YOUR_COOKIE_STRING_HERE') {
        console.error('Please provide your Suno.com cookie string in the script (see instructions).');
        return;
    }

    const songUrls = await extractLikedSongs(playlistUrl, cookieString);

    if (songUrls.length === 0) {
        console.log('No song URLs extracted. Check your cookies or URL.');
    }
}

main();
```

---

### How to Use the Script

#### Prerequisites

1. **Install Node.js and npm:**
   - Download and install from [nodejs.org](https://nodejs.org/).
2. **Install Puppeteer:**
   - Run in your terminal:

     ```bash
     npm install puppeteer
     ```

3. **Save the Script:**
   - Save the code as `extract_liked_songs.js`.

#### Getting Your Cookie String

Since `https://suno.com/playlist/liked` requires authentication:

1. Log into Suno.com in your browser (e.g., Chrome).
2. Open Developer Tools (`F12` or right-click > Inspect).
3. Go to the **Network** tab.
4. Refresh the page (`F5`) while on `https://suno.com/playlist/liked`.
5. Find a request (e.g., `liked` or `client?_clerk_js_version`).
6. Right-click the request > Copy > Copy as cURL.
7. Paste the cURL command into a text editor.
8. Extract the `Cookie:` header value (e.g., `__client=abc123; session=xyz789; ...`).
9. Replace `'YOUR_COOKIE_STRING_HERE'` in the script with this value.

#### Running the Script

1. **Execute the Script:**

   ```bash
   node extract_liked_songs.js
   ```

   - The browser will open visibly (headless set to `false`) so you can monitor progress. Change to `headless: "new"` for background execution once tested.
2. **Output:**
   - The script saves all extracted URLs to `liked_songs.txt`, one per line.
   - It logs progress (e.g., "Songs loaded: 40/1318") and warns if fewer than 1318 songs are found.

---

### Features and Details

- **Dynamic Scrolling:** Scrolls until all songs load or a maximum of 50 attempts is reached, with a 1.5-second delay per scroll to allow content to load.
- **Cookie Authentication:** Uses your provided cookies to access the authenticated `liked` playlist.
- **URL Extraction:** Targets `<a href^="/song/">` links, filtering out comment links, and ensures uniqueness.
- **Progress Tracking:** Logs the number of songs loaded versus the target (1318).
- **Output:** Saves URLs in a plain text file, easily reusable with other tools from your project (e.g., `parse_suno_to_markdown.py`).

---

### Notes and Limitations

- **Cookie Validity:** The script relies on valid cookies. If your session expires, you’ll need to update the cookie string.
- **Load Limits:** Suno may cap the number of songs loaded per page view. If 1318 isn’t reached, manual intervention or API access (not available here) might be needed.
- **Performance:** Loading 1318 songs may take several minutes due to scrolling and network delays. Adjust `scrollDelay` or `maxAttempts` if needed.
- **Headless Mode:** Set to `false` for visibility during testing; switch to `"new"` for automation.

---

### Example Output (`liked_songs.txt`)

```
https://suno.com/song/12bfb381-df41-4452-9846-399e5e70153d
https://suno.com/song/c0e77570-5f30-4482-a981-bd169f75432e
```

You can then use this file with your previous script (`parse_suno_to_markdown.py`) to process the URLs into Markdown files:

```bash
python parse_suno_to_markdown.py --input liked_songs.txt
```

---

