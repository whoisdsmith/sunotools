import * as fs from 'fs/promises';
import fetch from 'node-fetch';
import { parse } from 'node-html-parser';
// Removed 'path' import since it's not used

async function fetchPageContent(url) {
    const response = await fetch(url);
    if (!response.ok) {
        throw new Error(`Failed to fetch page: ${response.statusText}`);
    }
    const html = await response.text();
    return html;
}

function extractScriptTags(html) {
    const root = parse(html);
    const scriptTags = root.querySelectorAll('script');
    return scriptTags;
}

function findDataScripts(scriptTags) {
    return scriptTags.filter(script => script.text.includes('self.__next_f.push'));
}

function extractDataFromScripts(dataScripts) {
    let concatenatedData = '';
    let lyricsData = '';

    for (const script of dataScripts) {
        const match = script.text.match(/self\.__next_f\.push\(\[\d+,"(.*)"\]\)/s);
        if (match && match[1]) {
            // Unescape the string
            const unescapedString = JSON.parse(`"${match[1]}"`);
            // Check if the string contains JSON data
            if (unescapedString.trim().startsWith('{"clip":')) {
                concatenatedData += unescapedString;
            } else {
                // Collect lyrics or other text content
                lyricsData += unescapedString + '\n';
            }
        }
    }

    return { concatenatedData, lyricsData };
}

function extractJsonData(concatenatedData) {
    const jsonStartIndex = concatenatedData.indexOf('{"clip":');
    if (jsonStartIndex === -1) {
        throw new Error('JSON data not found in concatenated string.');
    }

    const jsonString = concatenatedData.slice(jsonStartIndex);

    let jsonData;
    try {
        jsonData = JSON.parse(jsonString);
    } catch (error) {
        const positionMatch = error.message.match(/at position (\d+)/);
        if (positionMatch) {
            const validJsonSubstring = jsonString.slice(0, parseInt(positionMatch[1]));
            jsonData = JSON.parse(validJsonSubstring);
        } else {
            throw new Error('Failed to parse JSON data.');
        }
    }

    return jsonData;
}

function extractSongInformation(jsonData) {
    const clip = jsonData.clip;

    const title = clip.title || 'Unknown Title';
    const artist = clip.display_name || 'Unknown Artist';
    const coverImageUrl = clip.image_large_url || clip.image_url || 'No Image URL';
    const creationDate = clip.created_at || 'Unknown Date';
    const audioUrl = clip.audio_url || 'No Audio URL';
    const tags = clip.metadata.tags || 'No Tags';

    return {
        title,
        artist,
        coverImageUrl,
        creationDate,
        audioUrl,
        tags,
    };
}

function sanitizeFileName(name) {
    return name.replace(/[<>:"/\\|?*]/g, '-');
}

async function saveSongDetailsAsMarkdown(details) {
    const {
        title,
        artist,
        tags,
        lyrics,
        coverImageUrl,
        creationDate,
        audioUrl,
    } = details;

    const markdownContent = `
# ${title}

![Cover Image](${coverImageUrl})

**Artist:** ${artist}  
**Tags:** ${tags}  
**Release Date:** ${creationDate}  
**Listen:** [MP3 Link](${audioUrl})

## Lyrics:
${lyrics}
`;

    const sanitizedArtist = sanitizeFileName(artist);
    const sanitizedTitle = sanitizeFileName(title);
    const markdownFilename = `songs/${sanitizedArtist} - ${sanitizedTitle}.md`;

    await fs.writeFile(markdownFilename, markdownContent);
    console.log(`Saved markdown: ${markdownFilename}`);
}

// Only one definition of processURL
async function processURL(url) {
    try {
        const html = await fetchPageContent(url);
        const scriptTags = extractScriptTags(html);
        const dataScripts = findDataScripts(scriptTags);
        const { concatenatedData, lyricsData } = extractDataFromScripts(dataScripts);
        const jsonData = extractJsonData(concatenatedData);
        const songDetails = extractSongInformation(jsonData);
        songDetails.lyrics = lyricsData.trim() || 'Lyrics not available';

        // Save the song details as markdown
        await saveSongDetailsAsMarkdown(songDetails);
    } catch (error) {
        console.error(`An unexpected error occurred while processing ${url}:`, error);
    }
}

// Get the URL from the command line arguments
const args = process.argv.slice(2);
if (args.length === 0) {
    console.error('Please provide a Suno URL as an argument');
    process.exit(1);
}

const songUrl = args[0];
processURL(songUrl);
