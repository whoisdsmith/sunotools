# Gists

These two shell scripts provide different ways to interact with Suno AI's song generation service.  Here's a summary of each and their differences:

**`api.sh` (sunosh):  A Comprehensive CLI with GPT Integration**

* **Purpose:** This script is a full-fledged command-line interface (CLI) named "sunosh" designed for generating songs on Suno AI. It leverages OpenAI's GPT models for lyric generation and integrates directly with Suno's API.  It automates the entire process from lyric creation to song generation and retrieval.
* **Key Features:**
  * **GPT Integration:** Uses OpenAI's API (specifically `gpt-3.5-turbo`) to generate lyrics based on user-provided instructions. The script crafts a prompt for the GPT model, sends the request, and processes the response.
  * **Lyric Structure Handling:**  The script normalizes song structure metatags (e.g., "Refrain", "Couplet") into standard Suno AI tags like `[chorus]`, `[verse]`, `[bridge]`, etc. This ensures the generated lyrics are in a format Suno understands.
  * **Suno API Interaction:**  It directly calls Suno's APIs for:
    * Authentication (retrieving and refreshing session tokens using a user-provided cookie).
    * Song generation (`/api/generate/v2/`).
    * Retrieving song information (`/api/feed/`).
  * **Token Management:** Handles Suno AI authentication by fetching and refreshing session tokens.  Requires a user-provided `COOKIE` from the Suno website (obtained via browser developer tools).
  * **Interactive Workflow:** Guides the user through a series of prompts:
    * Specifying instructions for lyric generation.
    * Validating and regenerating lyrics.
    * Entering song tags (genres).
    * Choosing a song title.
  * **Song Retrieval:** After generation, the script waits for the song to become available ("listenable") and optionally "downloadable". It retrieves the audio URL and can download the MP3 file using `wget`.
  * **Error Handling:** Includes checks for missing information (lyrics instructions, tags, title), invalid song structure, and API errors (e.g., 401 Unauthorized).
  * **Configuration:** Requires user to provide their Suno `COOKIE` and `OPENAI_API_KEY` in the script.
  * **Dependencies:** `curl`, `jq`, `wget`, `sed`, `grep`, `date`.
* **How it works:** The script breaks down the song generation process into distinct steps:
    1. **Lyrics:**  The user provides instructions for the lyrics (e.g., "write a song about bread in French").  The script uses these instructions to query the OpenAI API, generating the song lyrics. It then checks that the song lyrics have the correct song structure, prompts the user to accept or regenerate the lyrics.
    2. **Tags and Title:** The user is prompted for song tags/genres and a title.
    3. **Generation:** The script combines the lyrics, tags, and title, and sends a request to the Suno AI API to generate the song.  The API returns unique IDs for the generated song clips.
    4. **Retrieval:** The script polls the Suno AI API, waiting for the generated song to become available.  It can then stream (listenable) or download (downloadable) the song.

**`suno.sh` (suno_downloader):  Simple Song Downloader**

* **Purpose:** This script is a much simpler tool designed to download the MP3 and cover image of a *pre-existing* song on Suno AI, given its URL.  It doesn't generate songs itself.
* **Key Features:**
  * **URL Parsing:** Extracts the song's unique hash from the Suno "Share" URL provided by the user.
  * **MP3 Download:** Constructs the MP3 download URL based on the extracted hash and uses `wget` to download the file.  It cleverly changes `suno.com` to `cdn1.suno.ai` and removes `/song/` from the URL to get the direct MP3 link.
  * **Image Download:** Constructs the cover image download URL based on the hash and uses `wget` to download the JPEG.
  * **Album Title Extraction:** Fetches the HTML of the Suno song page and extracts the album title from the `<meta property="og:title">` tag. It uses `sed` to clean up the title.
  * **Error Handling:** Includes basic error checks for URL parsing and title retrieval.
  * **Dependencies:** `wget`, `curl`, `awk`, `sed`.
* **How it works:**
    1. The user provides the Suno "Share" URL.
    2. The script extracts the song hash from the URL.
    3. It constructs the direct MP3 download link and downloads the file.
    4. It constructs the cover image link and downloads the file.
    5. It retrieves the song's title from the Suno page and uses it to name the downloaded files.

**Key Differences Summarized**

| Feature               | `api.sh` (sunosh)                                                                         | `suno.sh` (suno_downloader)                                                   |
| --------------------- | ----------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------ |
| **Primary Function**  | Generates and retrieves songs                                                             | Downloads existing songs                                                        |
| **Lyric Generation**   | Yes, using OpenAI's GPT API                                                                 | No                                                                             |
| **Suno API Interaction** | Direct API calls for generation, authentication, and retrieval                           | Indirectly, by constructing download URLs based on the share link               |
| **User Input**       | Interactive prompts for lyrics, tags, and title                                            | Single URL input                                                               |
| **Authentication**   | Requires Suno `COOKIE` and `OPENAI_API_KEY`                                                      | None (relies on publicly accessible download URLs)                               |
| **Complexity**          | More complex, full-featured CLI                                                            | Simpler, focused on downloading                                                   |
| **Dependencies** | `curl`, `jq`, `wget`, `sed`, `grep`, `date`                                                        | `wget`, `curl`, `awk`, `sed`                                                         |
| **File Naming** | Uses user chosen title. If multiple songs, uses title and an incrementing id | Extracts the album/song title from the Suno web page to name the files. |

In essence, `api.sh` is a comprehensive tool for *creating* and managing Suno AI songs, while `suno.sh` is a simple utility for *downloading* existing songs. `api.sh` handles the entire song creation workflow, while `suno.sh` assumes the song has already been created on the Suno website.
