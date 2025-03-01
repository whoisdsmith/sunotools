# SunoTools

Here's a breakdown of the provided documentation and code snippets, organized into comprehensive summaries for each project and then a comparative analysis:

**Overall Project Summarization**

These projects all aim to provide programmatic access to Suno.ai, an AI music generation service. Since Suno.ai doesn't offer an official public API, these projects use various techniques, primarily browser automation (via Playwright) and, in some cases, reverse-engineering internal API endpoints, to achieve this. The projects differ in their programming languages, frameworks, feature sets, and approaches to authentication and CAPTCHA handling.

**Individual Project Summaries (Detailed)**

Each project summary contains:

* **Project Name:** A descriptive name based on the project's directory or main file.
* **Description:** A concise overview of the project's purpose and functionality.
* **Key Features:** A bulleted list of the project's main capabilities.
* **Technologies:** The core programming languages, libraries, and frameworks used.
* **Dependencies:**  A list of third-party packages that are needed by the program.
* **Authentication:** How the project handles authentication with Suno.ai.
* **CAPTCHA Handling:** How the project deals with Suno.ai's CAPTCHA challenges.
* **Deployment:** How the project can be deployed and run.
* **API Endpoints (if applicable):** A list of the API endpoints provided by the project, along with brief descriptions.
* **Code Examples (if applicable):** Snippets of code demonstrating how to use the API.
* **Strengths:** The project's advantages.
* **Weaknesses:** The project's limitations or drawbacks.
* **Overall Assessment:** A brief summary of the project's value and suitability for different use cases.

The following projects have been summarized in detail:

1. **API I (gcui-art/suno-api - Initial Version):**  A Next.js based project using Playwright and 2captcha.

2. **API II (SunoAPI/SunoAPI):** A Python/Streamlit project focused on UI.

3. **API III (gcui-art/suno-api - Updated):** A re-summarization of `gcui-art/suno-api` reflecting changes and a clearer focus.

4. **API IV (austin3306, FastAPI):** A Python/FastAPI project using direct API calls (not Playwright).

5. **APIs (Project Overview):** A directory summarizing other APIs, acting as a high-level overview of `gcui-art/suno-api`.

6. **bulkdl.md:** Javascript snippets for downloading songs and videos.

7. **discussion.md:**  Javascript and python code for download song audio and video, copied from a gist comment thread.

8. **gists.md:** Summaries and comparisons of two shell scripts, `api.sh` and `suno.sh`, showing different approaches to interacting with Suno (one uses GPT, the other is for downloading existing songs).

9. **Grok.md:** A javascript program, and a python program. The programs take a list of suno song URLs, downloads each page, extracts data, and generates Markdown output files.

10. **suno api.md:** A duplicate of `API III`.

11. **Suno Info.md:** An analysis of HTML snippets from the Suno website, looking for clues about how to extract playlist and song data.  *Not a runnable project*, but an analysis document.

12. **SunoGem.md:** An improved and complete javascript program for downloading song information from Suno and writing markdown files.

13. **SunoGPT.md:** Javascript code that reads a list of Suno.com song URLs, extracts metadata, and writes each result to a separate Markdown file.

14. **SunozaraAPI.md:**  Documentation for the Sunozara.com API, which is a *separate service* related to Suno.  It describes endpoints, authentication, error handling, and more.  This is *not* an unofficial Suno.ai API, but an API for a different platform.

15. **tuantinhte1234-suno-api4:** A duplicate (different name) of the final version of `gcui-art/suno-api`.

16. **sayanroy058-suno-api-new:** A duplicate of the final version of `gcui-art/suno-api`.

17. **redwan002117-suno-api:** A duplicate of the final version of `gcui-art/suno-api`.

18. **whoisdsmith-sunotools:** The project that contains the python program that takes suno URL as input, and generates markdown files as output.

19. **sunomegathread.md**: A summary of a Reddit megathread on Suno AI tips, tricks, and troubleshooting.

---

**1. Project: API I (gcui-art/suno-api - Initial Version)**

* **Description:** An API server, built with Next.js, providing endpoints for generating music, retrieving song/clip information, and extending audio via Suno.ai. It uses Playwright to interact with the Suno.ai website.
* **Key Features:**
  * Generate music (basic and custom modes).
  * Generate lyrics.
  * Get music information (by ID or all).
  * Get user quota information.
  * Extend audio length.
  * Generate stem tracks.
  * Get timestamps of each word in the lyrics.
  * OpenAI API compatibility (`/v1/chat/completions`).
  * Automatic account keep-alive.
  * CAPTCHA solving using 2Captcha.
  * One-click deployment to Vercel and Docker support.
* **Technologies:** Next.js, TypeScript, Playwright, 2Captcha, Axios, Tailwind CSS, Swagger/OpenAPI.
* **Dependencies:** `next`, `react`, `@types/react`, `playwright`, `@2captcha/captcha-solver`, `axios`, `next-swagger-doc`, `swagger-ui-react`, `pino`, `pino-pretty`, `proxy-from-env`.
* **Authentication:** Uses the user's Suno.ai cookie (`SUNO_COOKIE`) obtained from the browser.
* **CAPTCHA Handling:** Integrates with the 2Captcha service to automatically solve hCaptcha challenges.
* **Deployment:** Vercel (one-click deployment), Docker, or local execution.
* **API Endpoints:**
  * `/api/generate`: Generates music.
  * `/v1/chat/completions`: OpenAI-compatible music generation.
  * `/api/custom_generate`: Generates music with custom parameters.
  * `/api/generate_lyrics`: Generates lyrics.
  * `/api/get`: Retrieves music information.
  * `/api/get_limit`: Retrieves quota information.
  * `/api/extend_audio`: Extends audio length.
  * `/api/generate_stems`: Generates stem tracks.
  * `/api/get_aligned_lyrics`: Retrieves the timestamps for the words in the lyrics.
  * `/api/clip`: Retrieves clip information.
  * `/api/concat`: Generate the whole song.
* **Code Examples:** Provided for Python and JavaScript.
* **Strengths:**
  * Comprehensive feature set, closely mirroring Suno.ai functionality.
  * OpenAI compatibility for easy integration with existing tools.
  * Multiple deployment options.
  * Good documentation (Swagger/OpenAPI).
* **Weaknesses:**
  * Relies on Playwright and web scraping, making it potentially brittle to changes in Suno.ai's website.
  * Requires a paid 2Captcha account.
* **Overall Assessment:**  A robust and feature-rich API for interacting with Suno.ai. The OpenAI compatibility is a significant advantage.  The reliance on web scraping and a paid CAPTCHA service are potential drawbacks.

---

**2. Project: API II (SunoAPI/SunoAPI)**

* **Description:**  A Python-based client for Suno.ai, using Streamlit for a web-based user interface. It focuses on generating music, retrieving song information, and managing user accounts.
* **Key Features:**
  * Generate music and obtain song information.
  * Built-in token maintenance and keep-alive.
  * Support for multiple user accounts.
  * Music sharing square (displays publicly available songs).
  * Image analysis to generate songs (requires GPT-4o and S3 object storage).
  * Multilingual support.
* **Technologies:** Python, Streamlit, OpenAI (for image recognition), S3 object storage (for image uploads).
* **Dependencies:** `streamlit`, `requests`, `openai`
* **Authentication:** Uses Suno.ai session information and cookies.  Automatically maintains and keeps the program active.
* **CAPTCHA Handling:** Not explicitly addressed.  The focus is on UI and session management.
* **Deployment:** Docker, Docker Compose, Zeabur, Streamlit.
* **API Endpoints:** Not explicitly defined as REST endpoints. The project focuses on a Streamlit UI.
* **Code Examples:** Not provided in a readily usable API format.
* **Strengths:**
  * User-friendly web interface (Streamlit).
  * Multi-account support.
  * Built-in token management.
  * Image-to-song functionality.
* **Weaknesses:**
  * Less focused on providing a programmatic API (more of a user-facing application).
  * Requires OpenAI API key and S3 object storage for full functionality.
  * CAPTCHA handling is unclear.
* **Overall Assessment:**  A good option for users who want a visual interface to interact with Suno.ai.  Less suitable for developers who need a purely programmatic API.

---

**3. Project: API III (gcui-art/suno-api - Updated)**

* **Description:**  A refined version of the `gcui-art/suno-api` project (API I), offering a RESTful API for Suno.ai interaction, built with Next.js and Playwright.
* **Key Features:** (Same as API I, but with clearer emphasis)
  * Comprehensive Suno.ai functionality: generate music, extend audio, generate lyrics, get song/clip info, get user limits, generate stems.
  * OpenAI API compatibility.
  * Automatic account keep-alive.
  * CAPTCHA solving via 2Captcha.
  * Vercel, Docker, and local deployment.
* **Technologies:**  Same as API I (Next.js, TypeScript, Playwright, 2Captcha, etc.).
* **Dependencies:** Same as API I.
* **Authentication:** Uses Suno.ai cookie (`SUNO_COOKIE`).
* **CAPTCHA Handling:** Uses 2Captcha and Playwright with `rebrowser-patches`.
* **Deployment:** Vercel, Docker, Local.
* **API Endpoints:** Same as API I.
* **Code Examples:** Same as API I.
* **Strengths:** Same as API I, with improved clarity and a stronger focus on the API aspects.
* **Weaknesses:** Same as API I.
* **Overall Assessment:**  A well-structured and well-documented API for programmatically accessing Suno.ai.  The OpenAI compatibility, multiple deployment options, and detailed documentation make it a good choice for developers.

---

**4. Project: API IV (austin3306, FastAPI)**

* **Description:**  A Python-based API using FastAPI, focusing on generating music and lyrics and retrieving account information.  It uses *direct API calls* to Suno.ai (not Playwright).
* **Key Features:**
  * Generate music (with description mode).
  * Generate and retrieve lyrics.
  * Get user credits.
  * Get song feed.
  * Token maintenance and keep-alive.
  * CORS enabled.
* **Technologies:** Python, FastAPI, Uvicorn, Requests (implied).
* **Dependencies:** `fastapi`, `uvicorn`, `requests`.
* **Authentication:** Uses `SESSION_ID` and `COOKIE` environment variables, *and* fetches a JWT from `clerk.suno.com`.  This is a more robust authentication approach.
* **CAPTCHA Handling:** Not applicable, as it doesn't use browser automation.
* **Deployment:** Docker, Docker Compose.
* **API Endpoints:**
  * `/generate`: Generate music.
  * `/generate/description-mode`: Generate music using a description.
  * `/feed/{aid}`: Get song feed.
  * `/generate/lyrics/`: Generate lyrics.
  * `/lyrics/{lid}`: Get lyrics.
  * `/get_credits`: Get account credits.
* **Code Examples:** Not provided in the documentation.
* **Strengths:**
  * More robust authentication (JWT).
  * Doesn't rely on browser automation, potentially more stable.
  * FastAPI provides automatic API documentation.
  * Python-based, which might be preferred by some developers.
* **Weaknesses:**
  * Fewer features compared to the Playwright-based APIs (no audio extension, stem generation).
  * Relies on reverse-engineering internal Suno.ai APIs, which could break.
* **Overall Assessment:** A good option if you need a Python-based API and don't require the full range of features offered by the Playwright-based projects.  The direct API interaction is potentially more efficient but also more vulnerable to changes in Suno.ai's backend.

---

**5. Project: APIs (Project Overview)**

* **Description:**  This is *not* a separate project, but rather a high-level overview of the `gcui-art/suno-api` project (API I). It serves as a summary of the API's structure, functionality, and technologies.
* **Key Features, Technologies, Authentication, CAPTCHA, Deployment, API Endpoints:**  All refer to `gcui-art/suno-api` (API I).
* **Overall Assessment:** Useful as a quick introduction to `gcui-art/suno-api`, but doesn't provide any new functionality or code.

---

**6. Project: bulkdl.md**

* **Description:** Provides JavaScript snippets to be run in the browser's developer console to extract download links for audio and video files from the user's Suno library.
* **Key Features:**
  * Extracts audio (`audio_url`) and video (`video_url`) links.
  * Option to copy links to the clipboard or automatically save them to a `urls.txt` file.
* **Technologies:** JavaScript (browser-based).
* **Dependencies:** None (runs directly in the browser).
* **Authentication:** Relies on the user being logged into Suno.ai in their browser.
* **CAPTCHA Handling:** Not applicable.
* **Deployment:** Not applicable (run directly in the browser).
* **API Endpoints:** Not applicable.
* **Code Examples:**  The file itself contains the JavaScript code.
* **Strengths:**
  * Simple and easy to use.
  * No external dependencies.
* **Weaknesses:**
  * Requires manual interaction (copying and pasting code into the console).
  * Relies on the structure of the Suno.ai website, so it could break if the site changes.
  * Only downloads the currently *displayed* songs in the library (doesn't handle pagination automatically).
* **Overall Assessment:**  A quick and dirty solution for downloading songs if you don't mind manually scrolling through your library.

---

**7. Project: discussion.md**

* **Description:** Javascript code that copies direct URLs to all visible songs. Python code that takes those URLs, downloads the files, and renames them to their correct names.
* **Key Features:**
  * Extracts audio (`audio_url`) and video (`video_url`) links and formats them with the song title.
  * Downloads and renames songs.
* **Technologies:** JavaScript (browser-based) and Python.
* **Dependencies:** Requires Python and the `requests` library (`pip install requests`).
* **Authentication:** Relies on the user being logged into Suno.ai in their browser for the Javascript.
* **CAPTCHA Handling:** Not applicable.
* **Deployment:** Not applicable (run the Javascript in the browser, run the Python script locally).
* **API Endpoints:** Not applicable.
* **Code Examples:**  The file contains both the JavaScript and Python code snippets.
* **Strengths:**
  * Automates the download and renaming process.
  * Handles both audio and video files.
* **Weaknesses:**
  * Requires a two-step process (JavaScript to get URLs, Python to download).
  * Relies on the structure of the Suno.ai website for the Javascript.
  * Only downloads the currently *displayed* songs in the library (doesn't handle pagination automatically).
* **Overall Assessment:** A more automated solution than `bulkdl.md`, but still requires manual steps and is brittle to Suno website changes. The included Python script is helpful for handling downloads.

---

**8. Project: gists.md**

* **Description:**  Summaries and comparisons of two shell scripts, `api.sh` (sunosh) and `suno.sh` (suno_downloader).
* **`api.sh` (sunosh):**
  * **Description:** A comprehensive CLI tool for generating songs on Suno.ai. Uses OpenAI's GPT API for lyric generation and interacts directly with Suno's API.
  * **Key Features:**
    * GPT-powered lyric generation.
    * Lyric structure normalization (for Suno compatibility).
    * Direct Suno API interaction (authentication, generation, retrieval).
    * Token management.
    * Interactive workflow (prompts for lyrics, tags, title).
    * MP3 download.
  * **Technologies:** Shell scripting (bash), `curl`, `jq`, `wget`, `sed`, `grep`, `date`, OpenAI API.
  * **Dependencies:** `curl`, `jq`, `wget`, `sed`, `grep`, `date`, OpenAI API key.
  * **Authentication:** Requires a Suno `COOKIE` and `OPENAI_API_KEY`.
  * **CAPTCHA Handling:** Not explicitly addressed.  It relies on direct API interaction.
  * **Strengths:**
    * Complete song creation workflow (lyrics + generation).
    * GPT integration for high-quality lyrics.
    * Interactive and user-friendly CLI.
  * **Weaknesses:**
    * Requires OpenAI API key (paid service).
    * Relies on reverse-engineering Suno's internal API, which could break.
    * Shell scripting can be less portable and harder to maintain than other languages.
* **`suno.sh` (suno_downloader):**
  * **Description:** A simple shell script to download the MP3 and cover image of a *pre-existing* Suno.ai song, given its share URL.
  * **Key Features:**
    * Parses the Suno share URL to extract the song hash.
    * Downloads the MP3 and cover image using `wget`.
    * Extracts the album title from the Suno page.
  * **Technologies:** Shell scripting (bash), `wget`, `curl`, `awk`, `sed`.
  * **Dependencies:** `wget`, `curl`, `awk`, `sed`
  * **Authentication:** None (relies on publicly accessible download URLs).
  * **CAPTCHA Handling:** Not applicable.
  * **Strengths:**
    * Simple and focused on downloading existing songs.
    * No external API dependencies.
  * **Weaknesses:**
    * Doesn't generate songs; only downloads existing ones.
    * Relies on specific URL patterns and HTML structure, so it could break.
* **Overall Assessment:** `api.sh` is a powerful but complex tool for *creating* songs, while `suno.sh` is a simple utility for *downloading* existing songs.  They serve different purposes.

---

**9. Project: Grok.md**

* **Description:** Two programs: a JavaScript program (`parseSunoSongs.js`), and a Python program (`parse_suno_to_markdown.py`). Both programs take a list of Suno.com song URLs, fetch the HTML for each song, extract song and artist information (including lyrics), and save the information into individual Markdown files.
* **Key Features:**
  * Fetches song data from Suno.com URLs.
  * Extracts title, artist, lyrics, song ID, creation date, genre tags, cover image URL, and audio URL.
  * Outputs formatted Markdown files for each song.
  * Handles errors and invalid URLs.
  * Sanitizes filenames.
* **Technologies:**
  * **JavaScript:** Node.js, `node-fetch`, `node-html-parser`.
  * **Python:** `requests`, `BeautifulSoup4`, `argparse`, `re`.
* **Dependencies:**
  * **JavaScript:** `node-fetch`, `node-html-parser`.
  * **Python:** `requests`, `beautifulsoup4`.
* **Authentication:** Not required; the scripts access publicly available song pages.
* **CAPTCHA Handling:** Not applicable.
* **Deployment:** Run locally using Node.js or Python.
* **API Endpoints:** Not applicable; these are command-line scripts.
* **Code Examples:** The file contains the complete JavaScript and Python code.
* **Strengths:**
  * Comprehensive data extraction.
  * Clean Markdown output.
  * Handles errors and edge cases well.
  * No reliance on Playwright or 2Captcha.
  * Both JavaScript and Python versions provide flexibility.
* **Weaknesses:**
  * Relies on Suno.com's HTML structure, which could change.
  * Doesn't download the actual audio files (only extracts URLs).
* **Overall Assessment:** Excellent scripts for extracting song information from Suno.com and creating well-formatted Markdown reports. The choice between the JavaScript and Python versions depends on user preference.

---

**10. Project: suno api.md**

* This is just a duplicate of **API III**

---

**11. Project: Suno Info.md**

* **Description:** This is *not* a runnable project but an *analysis* of HTML snippets taken from the Suno.com website (using browser developer tools). It identifies the HTML elements that likely contain playlist and song information, describes their attributes, and infers their purpose.
* **Key Findings:**
  * Identifies HTML elements for playlist title, description, creator, song count, privacy settings, play/share buttons, etc.
  * Identifies HTML elements for song title, artist, version, genres, like/dislike buttons, share button, extend button, comments, etc.
  * Notes the extensive use of CSS classes (likely from Chakra UI).
  * Concludes that song playback and many interactive features are likely managed dynamically by JavaScript and backend APIs, *not* directly embedded in the initial HTML.
  * **Crucially, it confirms that direct links to audio files (.mp3) are *not* present in the static HTML.**
* **Technologies:** HTML, CSS (Chakra UI inferred), JavaScript (inferred).
* **Dependencies:** Not applicable.
* **Authentication:** Not applicable.
* **CAPTCHA Handling:** Not applicable.
* **Deployment:** Not applicable.
* **API Endpoints:** Not applicable.
* **Code Examples:** The document itself presents and analyzes the HTML snippets.
* **Strengths:**
  * Provides valuable insights into the structure of Suno.com's website.
  * Helps understand how information is presented and how dynamic content might be loaded.
* **Weaknesses:**
  * Not a runnable project; it's an analysis.
  * The findings are based on static HTML snapshots and could become outdated if Suno.com changes its website.
* **Overall Assessment:** Useful for anyone trying to reverse-engineer Suno.com's functionality or build tools to interact with it. The key takeaway is the absence of direct audio links in the static HTML.

---

**12. Project: SunoGem.md**

* **Description:** A JavaScript script (`parseSunoSongs.js`) that takes Suno.com song URLs as input, extracts song metadata and lyrics, and saves the information to Markdown files. This is an *improved and complete version* of the script from `Grok.md`, addressing some of the limitations and providing a more robust solution.
* **Key Features:**
  * Fetches HTML content of Suno.com song pages.
  * Extracts song data (title, artist, lyrics, song ID, creation date, tags, cover image URL, audio URL) from `<script>` tags.
  * Handles errors and edge cases (missing data, invalid JSON).
  * Outputs well-formatted Markdown files.
  * Sanitizes filenames.
* **Technologies:** Node.js, `node-fetch`, `node-html-parser`.
* **Dependencies:** `node-fetch`, `node-html-parser`.
* **Authentication:** Not required (accesses public song pages).
* **CAPTCHA Handling:** Not applicable.
* **Deployment:** Run locally with Node.js.
* **API Endpoints:** Not applicable (command-line script).
* **Code Examples:** The file contains the complete JavaScript code.
* **Strengths:**
  * Robust and reliable data extraction.
  * Improved error handling and JSON parsing.
  * Clean and well-formatted Markdown output.
  * No external API dependencies (beyond `node-fetch` and `node-html-parser`).
* **Weaknesses:**
  * Relies on Suno.com's HTML structure.
  * Doesn't download audio files (only extracts URLs).
* **Overall Assessment:** An excellent and well-crafted script for extracting song information from Suno.com and creating Markdown reports. It's a significant improvement over the earlier versions in `Grok.md`.

---

**13. Project: SunoGPT.md**

* **Description:**  A JavaScript script (`sunoParser.js`, very similar to `SunoGem.md`) that takes Suno.com song URLs, extracts metadata (title, artist, lyrics, song ID, creation date, genre tags, cover/audio URLs), and creates individual Markdown files for each song.
* **Key Features:**
  * Fetches HTML from Suno song URLs.
  * Extracts data from embedded JSON within `<script>` tags (`self.__next_f.push`).
  * Separately extracts lyrics from other script content.
  * Handles potential JSON parsing errors.
  * Creates Markdown files with formatted song information.
  * Sanitizes filenames.
  * Creates a `songs/` directory for output.
  * Processes URLs from command-line arguments or a text file.
* **Technologies:** Node.js, `node-fetch@2`, `node-html-parser`.
* **Dependencies:** `node-fetch@2`, `node-html-parser`
* **Authentication:** None required (fetches public song pages)
* **CAPTCHA Handling:** Not applicable.
* **Deployment:** Run locally with Node.js.
* **API Endpoints/Interface:** Command-line script (no web API).
* **Code Examples:** The file provides the complete JavaScript code.
* **Strengths:**
  * Robust JSON extraction logic (handles partial/broken JSON).
  * Clear Markdown output.
  * Flexible input (command-line arguments or file).
  * Handles common errors and invalid URLs.
* **Weaknesses:**
  * Relies on Suno's current HTML structure.
  * Does *not* download the audio files, only extracts URLs.
* **Overall Assessment:** A very well-written and reliable script for extracting song data from Suno and creating Markdown reports. It's a practical tool for archiving song metadata.

---

**14. Project: SunozaraAPI.md**

* **Description:** *Documentation* for the Sunozara.com API.  **This is NOT an unofficial Suno.ai API; it's the API for a different, related platform (Sunozara).**
* **Key Features (of the Sunozara API):**
  * User authentication (login, register).
  * Audio management (get, upload, update, delete).
  * Category and language management.
  * User profiles and favorites.
  * Articles, audiobooks, episodes.
  * Phone verification.
  * Locations, subscriptions, tags, products, coupons.
* **Technologies:**  The underlying technology is not specified, but it's a RESTful API.
* **Dependencies:** Not applicable (API documentation).
* **Authentication:** Bearer token authentication.
* **CAPTCHA Handling:** Not applicable.
* **Deployment:** Not applicable (API documentation).
* **API Endpoints:**  Numerous endpoints, documented in the file.
* **Code Examples:**  Includes a cURL example for login.
* **Strengths:**
  * Well-documented API.
  * Clear descriptions of endpoints, methods, request/response formats, and error codes.
* **Weaknesses:**
  * Not related to unofficial Suno.ai access.
* **Overall Assessment:**  Excellent documentation for the Sunozara.com API, but it's important to remember that this is *not* the same as Suno.ai.

---

**15, 16, 17. Projects: tuantinhte1234-suno-api4, sayanroy058-suno-api-new, redwan002117-suno-api**

* These are all duplicates (with different names/repository owners) of the final, refined version of `gcui-art/suno-api`.  They are functionally identical to **API III (gcui-art/suno-api - Updated)**.

---

**18. Project: whoisdsmith-sunotools**

* **Description:** Contains a Python script to extract and download information and files from suno.
* **Key Features:**
  * Parses suno song links.
  * Retrieves and displays all of the song's information.
  * Outputs song information in a formatted markdown file.
* **Technologies:** Python, requests, BeautifulSoup4, argparse, datetime
* **Dependencies:** `requests`, `beautifulsoup4`
* **Authentication:** Not required (accesses public song pages).
* **CAPTCHA Handling:** Not applicable.
* **Deployment:** Run locally with Python.
* **Overall Assessment:** A great tool for collecting and saving suno song information.

---
**19. Project: sunomegathread.md**

* **Description**: A summary of various tips and tricks for interacting with the suno.ai model. The document references several Reddit discussions.

---

**Comparative Analysis and Recommendations**

Here's a comparison of the projects and recommendations based on different use cases:

| Use Case                                     | Recommended Project(s)                                                                                                                                                                                                                                          | Justification                                                                                                                                                                                                                                                            |
| :------------------------------------------- | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Programmatic API access (comprehensive)** | **API III (gcui-art/suno-api - Updated)**, **tuantinhte1234-suno-api4**, **sayanroy058-suno-api-new**, **redwan002117-suno-api** (all are essentially the same)                                                                                                | These offer the most complete set of features, mirroring Suno.ai's website functionality.  They include OpenAI API compatibility, multiple deployment options, and robust CAPTCHA handling.                                                                             |
| **Programmatic API access (Python-based)**   | **API IV (austin3306, FastAPI)**                                                                                                                                                                                                                                  | If you prefer Python and don't need features like audio extension or stem generation, this is a good choice. It has strong authentication and doesn't rely on Playwright, making it potentially more stable.                                                               |
| **User-friendly web interface**             | **API II (SunoAPI/SunoAPI)**                                                                                                                                                                                                                                  | This is the best option if you want a visual interface rather than a programmatic API. It has multi-account support and a built-in token manager.                                                                                                                        |
| **Quickly downloading *displayed* songs**     | **bulkdl.md**                                                                                                                                                                                                                                                 | For simple, manual downloads of *visible* songs in your library, the JavaScript snippets are the quickest solution.  Requires manual scrolling.                                                                                                                              |
| **Automated download and renaming**         | **discussion.md**                                                                                                                                                                                                                                              | Offers a two-step process (JavaScript to extract URLs, Python to download and rename) that's more automated than `bulkdl.md`.  Still relies on the Suno.ai website structure.                                                                                                 |
| **Extracting song data to Markdown**        | **SunoGem.md**, **SunoGPT.md**, **Grok.md (Python Version)**                                                                                                                                                                                                  | These scripts provide a clean way to extract metadata and lyrics and create organized reports. `SunoGem.md` is the most robust and recommended JavaScript option.  `Grok.md` offers a good Python alternative.                                                               |
| **Comprehensive CLI song creation**        | **gists.md - api.sh (sunosh)**                                                                                                                                                                                                                                     | If you want a command-line tool that handles both lyric generation (via GPT) and Suno interaction, this is a powerful option.  Requires an OpenAI API key.                                                                                                                     |
| **Simple song downloader (existing songs)**   | **gists.md - suno.sh (suno_downloader)**                                                                                                                                                                                                                           | For downloading the MP3 and cover image of *existing* Suno songs (given their share URL), this shell script is a simple and efficient solution.                                                                                                                              |
| **Understanding Suno.com's HTML structure** | **Suno Info.md**                                                                                                                                                                                                                                                  | This isn't a tool, but an analysis of the HTML.  It's valuable for anyone trying to build their own tools or understand how Suno.com works under the hood.                                                                                                                 |
| **Accessing the Sunozara platform**          | **SunozaraAPI.md**                                                                                                                                                                                                                                                 | If you need to interact with the *Sunozara* platform (not Suno.ai directly), this documentation describes its official API.                                                                                                                                                |
| **Accessing all of a user's songs**          | **whoisdsmith-sunotools**, **Sunodl**, **extract_liked_songs.js (from Grok.md, requires Puppeteer and user cookies)**                                                                                                                                     | **whoisdsmith-sunotools** provides a well-made python script that does a good job. **Sunodl**: Best option for pulling down all songs from a user. **extract_liked_songs.js**: Can pull down all of a users likes, given that the user provides the cookies from their logged in session. |

**Key Considerations and Trade-offs:**

* **Playwright vs. Direct API Calls:** The most significant architectural difference is between projects that use Playwright (browser automation) and those that attempt to interact directly with Suno.ai's internal API (like API IV).
  * **Playwright (API I, API III, tuantinhte1234-suno-api4, sayanroy058-suno-api-new, redwan002117-suno-api):**
    * **Pros:** More closely mimics the user experience, can handle CAPTCHAs (with 2Captcha), and is less likely to be blocked.  More likely to adapt to changes in the *user-facing* parts of the Suno website.
    * **Cons:** Slower, more resource-intensive, more brittle to changes in the *website's structure* (HTML, CSS, JavaScript). Requires a browser and 2Captcha.
  * **Direct API Calls (API IV):**
    * **Pros:** Potentially faster and more efficient, doesn't require a browser or CAPTCHA solving.
    * **Cons:** Relies on reverse-engineering undocumented APIs, which are *much* more likely to change or be blocked.  Authentication is more complex (JWT).  May have fewer features.
* **CAPTCHA Handling:** Projects using Playwright *must* handle CAPTCHAs. They almost universally use 2Captcha, a paid service.  This adds a cost and dependency. Projects that don't use Playwright avoid this issue.
* **Authentication:** All unofficial Suno APIs rely on some form of cookie-based authentication.  The user needs to extract their Suno.ai cookie from their browser.  API IV uses a more sophisticated approach with JWTs.
* **Language and Framework:** The projects are split between Node.js/Next.js (API I, API III, and duplicates) and Python (API II, API IV, `Grok.md`, `discussion.md`, `whoisdsmith-sunotools`).  The choice depends on developer preference and existing infrastructure.
* **User Interface vs. API:** API II (SunoAPI/SunoAPI) prioritizes a user-friendly web interface (Streamlit), while the others focus on providing a programmatic API.
* **Completeness of Features:** The Playwright-based APIs (especially `gcui-art/suno-api` and its duplicates) offer the most complete set of features, mirroring almost everything available on the Suno.ai website.
* **OpenAI Compatibility:** Several of the projects offer an OpenAI-compatible API endpoint (`/v1/chat/completions`).  This is a major advantage for integration with existing AI tools and workflows.
* **Ease of Use:**  The JavaScript snippets (`bulkdl.md`, `discussion.md`) are the easiest to use for simple tasks (downloading) but are also the most limited and brittle.  The Next.js APIs are relatively easy to deploy (especially to Vercel).  The Python projects require more setup.

**Recommendations (Refined):**

1. **For most developers wanting a robust, feature-rich, and OpenAI-compatible API, `gcui-art/suno-api` (API III) or its duplicates (tuantinhte1234-suno-api4, sayanroy058-suno-api-new, redwan002117-suno-api) are the best choices.** They are well-documented, actively maintained, and offer the most comprehensive Suno.ai functionality.

2. **If you need a Python-based API and can accept fewer features (no audio extension or stems), API IV (FastAPI) is a good alternative.** It's potentially more stable due to direct API interaction (but also more at risk of being blocked).

3. **For users who prefer a web-based UI rather than a programmatic API, API II (SunoAPI/SunoAPI) is a good choice.**

4. **For quick and dirty downloads of *visible* songs in your library, the JavaScript snippets in `bulkdl.md` are the simplest option.**

5. **For more automated downloads, including renaming, use the combined JavaScript and Python approach in `discussion.md`.**

6. **For extracting song metadata and lyrics into well-formatted Markdown files, `SunoGem.md` or `SunoGPT.md` (JavaScript) and `Grok.md` (Python version) are excellent.**

7. **For generating lyrics with an LLM, use `api.sh`.**

8. **For downloading songs using a share link, use `suno.sh`.**

9. **For a complete, multi-featured, easy to use tool, use `whoisdsmith-sunotools`.**

10. **For pulling down all songs from an artist page or all songs from a playlist (using puppeteer), use `Sunodl`.**

11. **To get a comprehensive list of URLs from all of a user's liked songs, use the `extract_liked_songs.js` script from `Grok.md`, and combine the results with `parse_suno_to_markdown.py`, also from `Grok.md`.**

In conclusion, there's a rich ecosystem of tools for interacting with Suno.ai, each with its strengths and weaknesses. The best choice depends on your specific needs, technical skills, and preferred workflow. The `gcui-art/suno-api` project (and its duplicates) stands out for its comprehensiveness and developer-friendliness, while the other projects offer valuable alternatives and specialized functionality.
