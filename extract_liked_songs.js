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
    const cookieString = '_gcl_au=1.1.749036338.1739734221; _ga=GA1.1.1991273834.1739734221; afUserId=e830426f-57da-49b3-add5-5a74fb7dd7dd-p; _fbp=fb.1.1739734221431.128381570279739444; AF_SYNC=1739734221578; ajs_anonymous_id=83ec963b-8e55-450a-bad5-d78165cdd5cf; _tt_enable_cookie=1; _ttp=rynhFlbNeTPj7Y0p8jzR3zFGtK9.tt.1; __client_uat=1739734291; __refresh_U9tcbTPE=GhGeM8vBQNfIN3QmfjFs; __client_uat_U9tcbTPE=1739734291; _u=noXc7R1%2BlnrHIqG6fv21kLqY40fDyEGh%2FFa6cY8T%2FlaJe3lvYsDKYhAErvIsnZL7p9yLwu88ROesPPNVPsA5mbQvFQW%2BmYrfJXnU2DOIcxk1XwX%2BA0eF8pxf7C8kXgi1TiqwQAwaZiTnq1mLltCH71utlA9kqcWgnT9cwEPFdWrZFPiuhWGr5zwolKxeSnOMu1k36FQBTszrqhM%2B%2FzywpztslyhS3gM%2FEFqLXO7Xo%2F%2FjINIuBIfd%2BXssEHBDKvVCjtRv%2Bv7LJBFOQ6ELUfrgiqEXnqAIo273hciFekQ5jc7TfkNbLoxXcmOZvDGCbn7BXkV2%2FFjDMBNlojnXaJyNJLlnsWHBAHIDs5ss%2BwhctPxV8yTUBraA5phH0Rh3fCRBquYciQstPz6SDfMcevDJX%2F2zYwWp0kv2333E8gHRHvYDsA7jVq5RnoIn69Ap%2BOb1aAZzN8oZCBybyAV274aNdkft62IZyqnx9TNot5VTFVCH0gSK3vb%2BPfPHhydrhdZJ%2Bm4wEpJFAyGJQuAMCZb6ZnUJ4St9rpL3%2BKG3CnXnD1E7dup8Db4ohv%2BztorTN1Wzf%2Fc%2FKaUkKL7ATqkg3kDP8X3fYNgCGAG2d5l5hGJMyDWmMIg8l4tHKpAWfV%2B%2F2g%3D%3D.w4jAeY2rou7eCOs7SiNa5Jv%2F5khGzNOLZxLY2geH9N8%3D; _ga_7B0KEDD7XP=GS1.1.1740191826.3.1.1740191854.0.0.0; __session_U9tcbTPE=eyJhbGciOiJSUzI1NiIsImNhdCI6ImNsX0I3ZDRQRDExMUFBQSIsImtpZCI6Imluc18yT1o2eU1EZzhscWRKRWloMXJvemY4T3ptZG4iLCJ0eXAiOiJKV1QifQ.eyJhdWQiOiJzdW5vLWFwaSIsImF6cCI6Imh0dHBzOi8vc3Vuby5jb20iLCJleHAiOjE3NDAxOTI2NDUsImZ2YSI6Wzc2MzgsLTFdLCJodHRwczovL3N1bm8uYWkvY2xhaW1zL2NsZXJrX2lkIjoidXNlcl8ybFNsaEVSWHJIdUtReVEyVGtQcmNSbFJ6SkMiLCJodHRwczovL3N1bm8uYWkvY2xhaW1zL2VtYWlsIjoidGhlY2Fza2V0ZGlhcmllc0BnbWFpbC5jb20iLCJodHRwczovL3N1bm8uYWkvY2xhaW1zL3Bob25lIjpudWxsLCJpYXQiOjE3NDAxOTI1ODUsImlzcyI6Imh0dHBzOi8vY2xlcmsuc3Vuby5jb20iLCJqdGkiOiI3ZDgwNjg0N2U1MTdjNTRmZGE0MSIsIm5iZiI6MTc0MDE5MjU3NSwic2lkIjoic2Vzc18ydDhXZ05jbUljOXNVUWQwN2doQUFtUVZlUDAiLCJzdWIiOiJ1c2VyXzJsU2xoRVJYckh1S1F5UTJUa1ByY1JsUnpKQyJ9.U3i5nx8fyrKrZXYtQ9gbDVXubZRQf664UG4zl22dSyRYtaol7uB0wk_K57KlG8iUv0jaUhOwkW85Wc6eIVQfnwH1YsK1WBzWrl1kJuLWKJYKdC6PfPurI22xMYZkNVMfZVPYo36cIpj8STCwi_d2LSk1bes5QPkRuwzScrzHTbl7ec_qmEYXpsUBkFNsMfGfnC2BiUXNhR6o8SnGmex8ScamSTtfKjEhpX9_SUL_XlgShylA5ENrW-n_A_W1nxGnUyTHK_r_MtfXcLrVqhT13f6Zsazlm4rX-PAFkjpYawhHPOncPJ4K9ZmLSJlbelSyyeRoMdQwH70UnKJS4t5UKw; __session=eyJhbGciOiJSUzI1NiIsImNhdCI6ImNsX0I3ZDRQRDExMUFBQSIsImtpZCI6Imluc18yT1o2eU1EZzhscWRKRWloMXJvemY4T3ptZG4iLCJ0eXAiOiJKV1QifQ.eyJhdWQiOiJzdW5vLWFwaSIsImF6cCI6Imh0dHBzOi8vc3Vuby5jb20iLCJleHAiOjE3NDAxOTI2NDUsImZ2YSI6Wzc2MzgsLTFdLCJodHRwczovL3N1bm8uYWkvY2xhaW1zL2NsZXJrX2lkIjoidXNlcl8ybFNsaEVSWHJIdUtReVEyVGtQcmNSbFJ6SkMiLCJodHRwczovL3N1bm8uYWkvY2xhaW1zL2VtYWlsIjoidGhlY2Fza2V0ZGlhcmllc0BnbWFpbC5jb20iLCJodHRwczovL3N1bm8uYWkvY2xhaW1zL3Bob25lIjpudWxsLCJpYXQiOjE3NDAxOTI1ODUsImlzcyI6Imh0dHBzOi8vY2xlcmsuc3Vuby5jb20iLCJqdGkiOiI3ZDgwNjg0N2U1MTdjNTRmZGE0MSIsIm5iZiI6MTc0MDE5MjU3NSwic2lkIjoic2Vzc18ydDhXZ05jbUljOXNVUWQwN2doQUFtUVZlUDAiLCJzdWIiOiJ1c2VyXzJsU2xoRVJYckh1S1F5UTJUa1ByY1JsUnpKQyJ9.U3i5nx8fyrKrZXYtQ9gbDVXubZRQf664UG4zl22dSyRYtaol7uB0wk_K57KlG8iUv0jaUhOwkW85Wc6eIVQfnwH1YsK1WBzWrl1kJuLWKJYKdC6PfPurI22xMYZkNVMfZVPYo36cIpj8STCwi_d2LSk1bes5QPkRuwzScrzHTbl7ec_qmEYXpsUBkFNsMfGfnC2BiUXNhR6o8SnGmex8ScamSTtfKjEhpX9_SUL_XlgShylA5ENrW-n_A_W1nxGnUyTHK_r_MtfXcLrVqhT13f6Zsazlm4rX-PAFkjpYawhHPOncPJ4K9ZmLSJlbelSyyeRoMdQwH70UnKJS4t5UKw; _dd_s=rum=0&expire=1740193522343 // See instructions below to get this'

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