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

---

This script fulfills your request by extracting all specified song information from Suno.com URLs and formatting it into readable Markdown files. Adjust the selectors or data extraction logic if Suno’s website structure changes. Let me know if you need further customization!
