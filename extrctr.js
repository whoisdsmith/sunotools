import * as cheerio from 'cheerio';
import axios from 'axios';

async function extractSunoData(url) {
    try {
        const response = await axios.get(url);
        const html = response.data;
        const $ = cheerio.load(html);
        let sunoData = null;


        // Extract SUNO_DATA
        $('script').each((i, script) => {
            const scriptContent = $(script).html();
            if (scriptContent && scriptContent.includes('window.__SUNO_DATA__')) {
                const regex = /window\.__SUNO_DATA__\s*=\s*({.*?});/s;
                const match = regex.exec(scriptContent);
                if (match && match[1]) {
                    try {
                        sunoData = JSON.parse(match[1]);

                        // Stop iterating once data is found
                        return false; // This is how you break out of a cheerio each loop


                    } catch (e) {
                        console.error("Error parsing SUNO_DATA:", e);
                        return false; // Stop in case of parse error
                    }
                }
            }
        });



        if (sunoData) {
            return { jsonData: sunoData }; // Return only the relevant data
        } else {
            return { error: "Could not find window.__SUNO_DATA__" }; // Specific error
        }

    } catch (error) {
        console.error("Error fetching or processing URL:", error);
        return { error: error.message }; // Detailed error message
    }
}

async function main() {
    const sunoUrl = process.argv[2];

    if (!sunoUrl) {
        console.error("Please provide a Suno URL as a command-line argument.");
        return;
    }

    const extractedData = await extractSunoData(sunoUrl);
    console.log(JSON.stringify(extractedData, null, 2)); // Pretty-print JSON

}


main();