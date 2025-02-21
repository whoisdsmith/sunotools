import * as fs from 'fs/promises';
import { parse } from 'node-html-parser';
import fetch from 'node-fetch';
import * as cheerio from 'cheerio'; // Use named import for cheerio
import path from 'path';

// Function to save song details as a markdown file
async function saveSongDetailsAsMarkdown(title, artist, tags, lyrics, coverImageUrl) {
    const markdownContent = `
# ${title}

### Artist: ${artist}
### Tags: ${tags}
### Release Year: ${new Date().getFullYear()}  <!-- Assuming current year, adjust if needed -->

## Lyrics:
${lyrics}

![Cover Image](${coverImageUrl})

_Saved from Suno AI_
    `;

    const sanitizedTitle = title.replace(/[<>:"/\\|?*]+/g, '');
    const sanitizedArtist = artist.replace(/[<>:"/\\|?*]+/g, '');
    const markdownFilename = path.join('songs', `${sanitizedArtist} - ${sanitizedTitle}.md`);

    await fs.mkdir('songs', { recursive: true });
    await fs.writeFile(markdownFilename, markdownContent);
    console.log(`Saved markdown: ${markdownFilename}`);
}

// Function to process a Suno URL and extract metadata (without downloading the song)
async function processURL(url) {
    try {
        const uuid = url.match(/\b[0-9a-f]{8}\b-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-\b[0-9a-f]{12}\b/)[0];
        const sunoURL = `https://suno.com/song/${uuid}`;
        const result = await fetch(sunoURL);

        if (!result.ok) {
            console.error('Failed to fetch:', sunoURL);
            return;
        }

        const html = await result.text();
        const $ = cheerio.load(html);

        // Extract the title (update the selector to match the actual page structure)
        const title = $('h1').text().trim() || 'Unknown Title';

        // Extract the artist (update selector to match actual artist container)
        const artist = $('.artist-name').text().trim() || 'Unknown Artist';

        // Extract the tags (update the selector if needed)
        const tags = $('.tags').text().trim() || 'No Tags';

        // Extract the lyrics (update selector to match the actual lyrics container)
        const lyrics = $('.lyrics').text().trim() || 'No Lyrics';

        // Extract cover image URL (update the selector as needed)
        const coverImageUrl = $('img.cover').attr('src') || '';

        // Save the extracted details as a markdown file
        await saveSongDetailsAsMarkdown(title, artist, tags, lyrics, coverImageUrl);
    } catch (error) {
        console.error(`An error occurred while processing ${url}:`, error);
    }
}

// Main function to handle multiple URLs
async function main() {
    const urls = process.argv.slice(2);

    if (!urls.length) {
        console.error('Please provide at least one Suno URL.');
        process.exit(1);
    }

    for (const url of urls) {
        if (!url.startsWith('https://suno.com/song/')) {
            console.warn(`Skipping invalid URL: ${url}`);
            continue;
        }
        await processURL(url);
    }
}

main();