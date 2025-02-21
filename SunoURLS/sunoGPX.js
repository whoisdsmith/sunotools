import puppeteer from 'puppeteer';
import * as fs from 'fs/promises';

async function extractPlaylistSongs(playlistUrl) {
    const browser = await puppeteer.launch({ headless: "new" });
    const page = await browser.newPage();

    try {
        await page.goto(playlistUrl, { waitUntil: 'networkidle2' });

        // Extract total number of songs
        const totalSongsText = await page.$eval('div.line-clamp-1.text-ellipsis.overflow-hidden.w-fit', el => el.textContent);
        const totalSongsMatch = totalSongsText.match(/(\d+)\s+songs/);
        let totalSongs = 0;
        if (totalSongsMatch) {
            totalSongs = parseInt(totalSongsMatch[1], 10);
        } else {
            console.warn("Could not find total song count. Continuing anyway.");
        }

        // Robust Scrolling with Delay (using Promise-based delay)
        let previousHeight;
        let attempts = 0;
        const maxAttempts = 20; // Limit scroll attempts
        const scrollDelay = 1500; // milliseconds to wait AFTER scrolling

        while (attempts < maxAttempts) {
            previousHeight = await page.evaluate('document.body.scrollHeight');
            await page.evaluate('window.scrollTo(0, document.body.scrollHeight)');
            await new Promise(resolve => setTimeout(resolve, scrollDelay)); // Correct delay

            try {
                await page.waitForFunction(`document.body.scrollHeight > ${previousHeight}`, { timeout: 10000 });
                attempts = 0;
            } catch (e) {
                attempts++;
            }
        }
        console.log("Finished Scrolling");

        // Extract song URLs, filtering out those with "?show_comments=true"
        await page.waitForSelector('a[href^="/song/"]');
        const songLinks = await page.$$eval('a[href^="/song/"]', links =>
            links.map(a => a.getAttribute('href'))
                .filter(href => !href.includes('?show_comments=true'))
                .map(href => `https://suno.com${href}`)
        );

        const uniqueSongLinks = [...new Set(songLinks)]; // Remove Duplicates
        if (uniqueSongLinks.length !== totalSongs) {
            console.warn(`Extracted ${uniqueSongLinks.length} song URLs, but expected ${totalSongs}. There may be missing songs.`);
        }

        await browser.close();
        return uniqueSongLinks;

    } catch (error) {
        console.error("Error fetching or processing playlist:", error, error.stack);
        await browser.close();
        return [];
    }
}

async function main() {
    const playlistUrl = process.argv[2];

    if (!playlistUrl) {
        console.error("Please provide a Suno playlist URL as a command-line argument.");
        return;
    }
    if (!playlistUrl.includes("suno.com/playlist/")) {
        console.error("Invalid playlist URL.  Must be a suno.com/playlist/ URL");
        return;
    }

    const songUrls = await extractPlaylistSongs(playlistUrl);

    if (songUrls.length > 0) {
        const outputString = songUrls.join(' ');
        try {
            await fs.writeFile('url.txt', outputString);
            console.log("Song URLs written to url.txt");
        } catch (err) {
            console.error("Error writing to file:", err);
        }
    } else {
        console.log("No song URLs found in the playlist.");
    }
}

main();