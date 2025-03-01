# SunoGPT

---

## Overview

1. **Reads a list of Suno.com song URLs** from a local text file or command-line arguments.
2. **Fetches each page’s HTML** using `node-fetch`.
3. **Parses hidden JSON data** (often embedded in `<script>` tags) to locate the desired metadata.
4. **Extracts**:
   - Song ID (from the URL)
   - Song title
   - Artist name
   - Lyrics
   - Creation date
   - Genre tags
   - Cover image URL
   - Audio URL
5. **Writes a Markdown file** with all these details in a neat, readable format. Each file goes into a `songs/` directory.

You can tweak the script if Suno changes how they embed data, but it should work as of the approach demonstrated in your references citeturn0file0.

---

## Requirements

1. **Node.js** (version 14 or higher)
2. **Dependencies**:

   ```bash
   npm install node-fetch@2 node-html-parser
   ```

   > Note: If you’re on Node 18+, you can use the built-in `fetch`, but the code below uses `node-fetch@2` to ensure broader compatibility.

---

## The Script

Create a file named `sunoParser.js` (or any name you prefer) and copy the following code:

```js
/**
 * sunoParser.js
 *
 * Parses a list of Suno.com song URLs, extracts metadata, and writes each result
 * to a separate Markdown file in the "songs" directory.
 *
 * Inspired by/Adapted from the Suno scripts in your provided references.
 */

import * as fs from 'fs/promises';
import fetch from 'node-fetch';
import { parse } from 'node-html-parser';

// Utility: sanitize filenames to avoid invalid characters on most OS
function sanitizeFileName(name) {
  return name.replace(/[<>:"/\\|?*]/g, '-');
}

/**
 * Fetch the raw HTML for a given Suno.com song URL.
 */
async function fetchPageContent(url) {
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`Failed to fetch ${url}: ${response.statusText}`);
  }
  return response.text();
}

/**
 * Extract relevant script tags that contain the JSON data for the song.
 *
 * On Suno, the data can appear in lines like:
 *    self.__next_f.push([1,"{\"clip\": ... }"])
 */
function extractSongDataScripts(html) {
  const root = parse(html);
  return root.querySelectorAll('script')
    .filter(script => script.text.includes('self.__next_f.push'));
}

/**
 * Parse the script text to extract JSON data (metadata) and lyrics separately.
 *
 * Some script tags contain JSON for the clip metadata,
 * others might contain text that ends up being the lyrics.
 */
function extractDataAndLyrics(scriptTags) {
  let rawJsonStrings = '';
  let lyrics = '';

  for (const script of scriptTags) {
    // Example match: self.__next_f.push([1,"{\"clip\": ... }"])
    const match = script.text.match(/self\.__next_f\.push\(\[\d+,"(.*)"\]\)/s);
    if (match && match[1]) {
      // The data is JSON-escaped, so we decode it by wrapping in quotes for JSON.parse
      const decoded = JSON.parse(`"${match[1]}"`);

      // Heuristic: If the string starts with {"clip":...} then it’s the JSON chunk
      if (decoded.trim().startsWith('{"clip":')) {
        rawJsonStrings += decoded;
      } else {
        // Otherwise, it’s likely part of the lyrics or other text
        lyrics += `${decoded}\n`;
      }
    }
  }

  return { rawJsonStrings, lyrics };
}

/**
 * From the concatenated JSON strings, locate the actual JSON object that starts
 * with `{"clip": ... }`.
 */
function parseClipData(rawJson) {
  const startIndex = rawJson.indexOf('{"clip":');
  if (startIndex === -1) {
    throw new Error('No valid clip JSON found in the combined script data.');
  }

  const jsonString = rawJson.slice(startIndex);
  let parsed;
  try {
    parsed = JSON.parse(jsonString);
  } catch (err) {
    // If there's a partial parse error, try to salvage by cutting at the indicated position
    const positionMatch = err.message.match(/at position (\d+)/);
    if (positionMatch) {
      const cutPos = parseInt(positionMatch[1], 10);
      parsed = JSON.parse(jsonString.slice(0, cutPos));
    } else {
      throw new Error(`JSON parse failed: ${err.message}`);
    }
  }
  return parsed;
}

/**
 * Extract the relevant metadata fields (title, artist, cover image, audio URL, tags, creation date)
 * from the parsed JSON data.
 */
function extractSongMetadata(clipData) {
  const clip = clipData.clip ?? {};
  return {
    title: clip.title || 'Unknown Title',
    artist: clip.display_name || 'Unknown Artist',
    coverImage: clip.image_large_url || clip.image_url || '',
    audioUrl: clip.audio_url || '',
    date: clip.created_at || 'Unknown Date',
    tags: Array.isArray(clip.metadata?.tags)
      ? clip.metadata.tags.join(', ')
      : (clip.metadata?.tags ?? 'No Tags'),
  };
}

/**
 * Write a Markdown file containing all the extracted data.
 */
async function writeMarkdown({
  songId,
  title,
  artist,
  date,
  tags,
  coverImage,
  audioUrl,
  lyrics,
}) {
  // Our markdown structure
  const mdContent = `
# ${title}

**Song ID:** ${songId}

**Artist:** ${artist}
**Date:** ${date}
**Tags:** ${tags}

![Cover Image](${coverImage})

**Cover Image Download**: [Link](${coverImage})
**Audio Download**: [Link](${audioUrl})

## Lyrics
${lyrics || 'Lyrics not available'}
  `;

  // Create a directory named "songs" if it doesn’t exist
  await fs.mkdir('songs', { recursive: true });

  const safeArtist = sanitizeFileName(artist);
  const safeTitle = sanitizeFileName(title);
  const fileName = `songs/${safeArtist} - ${safeTitle} - ${songId}.md`;

  await fs.writeFile(fileName, mdContent.trim());
  console.log(`Created: ${fileName}`);
}

/**
 * Process a single Suno.com song URL:
 * - Fetch HTML
 * - Extract JSON + lyrics
 * - Parse the clip data
 * - Collect fields, then write to .md
 */
async function processSunoSong(url) {
  try {
    // The Song ID is typically the last path segment (UUID-like)
    const songId = url.split('/').pop();

    // 1) Fetch page HTML
    const html = await fetchPageContent(url);

    // 2) Extract scripts that contain JSON data
    const scriptTags = extractSongDataScripts(html);

    // 3) Parse out JSON chunk(s) and lyrics text
    const { rawJsonStrings, lyrics } = extractDataAndLyrics(scriptTags);

    // 4) Parse the JSON chunk to get the clip data
    const clipJson = parseClipData(rawJsonStrings);

    // 5) Extract final metadata from the JSON
    const { title, artist, date, tags, coverImage, audioUrl } = extractSongMetadata(clipJson);

    // 6) Write everything into a Markdown file
    await writeMarkdown({
      songId,
      title,
      artist,
      date,
      tags,
      coverImage,
      audioUrl,
      lyrics: lyrics.trim(),
    });
  } catch (err) {
    console.error(`Error processing ${url}:\n`, err);
  }
}

/**
 * Main routine:
 *
 * 1) Reads URLs from the command line, or from a local "suno_urls.txt" file if desired.
 * 2) Loops over each URL, calling processSunoSong(url).
 */
async function main() {
  const urls = process.argv.slice(2);

  if (urls.length === 0) {
    console.log('Usage: node sunoParser.js <songURL1> <songURL2> ...');
    console.log('Or provide a text file of URLs and read them in, e.g.:');
    console.log('  cat suno_urls.txt | xargs node sunoParser.js');
    process.exit(1);
  }

  for (const url of urls) {
    // Basic check: must start with "https://suno.com/song/"
    if (!/^https:\/\/suno\.com\/song\//.test(url)) {
      console.warn(`Skipping invalid Suno song URL: ${url}`);
      continue;
    }
    await processSunoSong(url);
  }
}

main();
```

---

## How to Use

1. **Create or copy the script** above as `sunoParser.js`.
2. **Install dependencies** in the same folder:

   ```bash
   npm install node-fetch@2 node-html-parser
   ```

3. **Prepare your list of song URLs**. You can:
   - Pass them directly as command-line arguments:

     ```bash
     node sunoParser.js https://suno.com/song/12bfb381-df41-4452-9846-399e5e70153d https://suno.com/song/c0e77570-5f30-4482-a981-bd169f75432e
     ```

   - Or store them in a text file (e.g., `suno_urls.txt`) and pipe them in:

     ```bash
     cat suno_urls.txt | xargs node sunoParser.js
     ```

4. **Check the output** inside a newly created `songs/` folder. Each song gets its own Markdown file with the format:

   ```
   Artist - Title - SongID.md
   ```

---

## Example Markdown Output

A sample `.md` file might look like this (shortened for illustration):

```
# Neon Lights & Lullabies

**Song ID:** 12bfb381-df41-4452-9846-399e5e70153d

**Artist:** The Casket Diaries
**Date:** 2024-12-07T04:15:00Z
**Tags:** midwest emo, electronic, shoegaze

![Cover Image](https://cdn2.suno.ai/image_large_12bfb381-df41-4452-9846-399e5e70153d.jpeg)

**Cover Image Download**: [Link](https://cdn2.suno.ai/image_large_12bfb381-df41-4452-9846-399e5e70153d.jpeg)
**Audio Download**: [Link](https://cdn1.suno.ai/12bfb381-df41-4452-9846-399e5e70153d.mp3)

## Lyrics
[Intro]
Distant city lights...
[End]
```

---

## Important Notes

1. **Dynamic Site Structure**: If Suno changes how they embed data (for instance, removing `self.__next_f.push` references), the script logic to retrieve JSON/lyrics will need to be updated.
2. **Audio Download Access**: Some audio URLs may require account authentication or subscription. In many cases, you can still capture the direct `audio_url` field.
3. **Lyrics Extraction**: Lyrics might appear in separate lines or fragments; this script merges any non-JSON lines into a single block. Adjust as needed for more precise lyric parsing.
4. **File System**: Markdown files are saved in a folder named `songs`. You can rename or reorganize as desired.
5. **Error Handling**: The script logs errors but continues processing each URL in sequence rather than terminating after a single failure.

**That’s it!** You now have a script that, given any number of Suno.com song URLs, fetches each page, extracts the relevant metadata, and writes out a neatly structured Markdown file for your archives. Feel free to modify the layout, add headings, or tweak field names to suit your preference.

---
