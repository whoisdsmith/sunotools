# Scripts

Here's a summary of each Suno AI project script you provided, outlining their purpose, functionality, and key features:

**1. `backUpPlaylist.js`**

* **Purpose:** Backs up song metadata, music, and art files from a specified Suno playlist.
* **Functionality:**
  * Loads the JSZip library for creating ZIP archives.
  * Fetches the bearer token from cookies for authentication.
  * Retrieves all clips from the specified playlist, handling pagination.
  * Downloads music (MP3) and art (JPEG) files based on user-defined filters.
  * Skips public or private clips based on filter settings.
  * Creates a JSON file containing the metadata of all clips.
  * Compiles all files into a ZIP archive named `suno_backup.zip` and triggers a download.
* **Key Features:**
  * Playlist ID input.
  * Filters for including/excluding public and private clips.
  * Options to download music and art files.
  * Error handling for failed file downloads.
  * Delay to prevent API overloading.
  * Creates Metadata file

**2. `blockAllTrenders.js`**

* **Purpose:** Blocks all users currently featured on the Suno trending page.
* **Functionality:**
  * Fetches the bearer token.
  * Retrieves the list of trending songs from the "Global" trending section.
  * Iterates through each trending song and extracts the creator's information.
  * Sends a "creator\_not\_interested" feedback request for each creator, effectively blocking them.
  * Includes a delay to prevent API overloading.
* **Key Features:**
  * Automated blocking of all trending users.
  * Uses the "creator\_not\_interested" feedback type.
  * Error handling.

**3. `blockBadActors.js`**

* **Purpose:** Blocks a predefined list of Suno users considered "bad actors."
* **Functionality:**
  * Contains a hardcoded array `badActors` with user display names and song IDs.
  * Uses local storage (`diskrot:banCounter`) to track progress and resume after session expiration.
  * Iterates through the `badActors` list, fetching the song ID from the provided URL.
  * Sends a "creator\_not\_interested" feedback request to block each user.
  * Handles potential token expiration (401) or rate-limiting (429) errors.
  * Includes a delay.
* **Key Features:**
  * Persistent blocking progress using local storage.
  * Predefined list of users to block.
  * Robust error handling for session expiration.
  * "creator\_not\_interested" feedback type.

**4. `emptyTrash.js`**

* **Purpose:** Permanently deletes all songs from the user's Suno trash, excluding persona clips.
* **Functionality:**
  * Fetches the bearer token.
  * Retrieves trashed clips in batches (default size: 20).
  * Filters clips to exclude persona clips (those with `persona_id` or `persona` in metadata).
  * Sends a bulk delete request for the filtered clip IDs.
  * Handles pagination to process all trashed items.
  * Includes a delay.
* **Key Features:**
  * Batch processing for efficient deletion.
  * Persona clip exclusion.
  * Error handling and token refresh suggestion.

**5. `filterByUploads.js`**

* **Purpose:** Retrieves and displays a list of all uploaded clips by the user.
* **Functionality:**
  * Fetches the bearer token.
  * Calculates the total number of project pages.
  * Retrieves all clips from the user's default project, handling pagination.
  * Filters the clips to include only those with `metadata.type` equal to "upload".
  * Prints the filtered uploads to the console.
* **Key Features:**
  * Filters clips based on upload status.
  * Pagination handling.
  * Delay for API requests.

**6. `follwerExport.js`**

* **Purpose:** Exports a list of the user's followers with additional statistics.
* **Functionality:**
  * Loads JSZip.
  * Fetches the bearer token.
  * Retrieves follower data, handling pagination.
  * For each follower, fetches additional creator info (likes, clips).
  * Calculates ratios: likes/followers, clips/followers, clips/likes.
  * Creates a JSON file (`followers.json`) containing follower data and statistics.
  * Compiles the JSON into a ZIP archive (`suno_follower.zip`) and triggers download.
* **Key Features:**
  * Detailed follower statistics.
  * Pagination handling.
  * Data export as a ZIP file.
  * Delay for API requests.

**7. `haters.js`**

* **Purpose:** Identifies and displays users who have unfollowed or unliked the user's clips.
* **Functionality:**
  * Fetches the bearer token.
  * Retrieves the user's notifications.
  * Filters notifications to find those with types containing "unfollow" or "clip\_unlike".
  * Prints the filtered "haters" notifications to the console.
* **Key Features:**
  * Identifies negative interactions.
  * Clear console output.

**8. `restoreFromTrash.js`**

* **Purpose:** Restores a specific song from the trash, given its ID.
* **Functionality:**
  * Fetches the bearer token.
  * Sends a request to untrash the clip with the provided `songID`.
* **Key Features:**
  * Simple restoration of a single clip.

**9. `sunoBackup.js`**

* **Purpose:** Backs up the user's song metadata, with optional music and art files.  *Very similar to* `backUpPlaylist.js`, *but backs up the user's entire library, not just a playlist.*
* **Functionality:**
  * Loads JSZip.
  * Fetches the bearer token.
  * Calculates the total number of project pages.
  * Retrieves all clips from the user's default project, handling pagination.
  * Downloads music (MP3) and art (JPEG) files based on user-defined filters.
  * Skips public or private clips based on filter settings.
  * Creates a JSON file containing the metadata of all clips.
  * Compiles all files into a ZIP archive (`suno_backup.zip`) and triggers a download.
* **Key Features:**
  * Filters for including/excluding public and private clips.
  * Options to download music and art files.
  * Error handling for failed downloads.
  * Delay to prevent API overloading.
  * Comprehensive backup of the user's entire library.
  * Creates Metadata file

**10. `sunoSupport.js`**

* **Purpose:** Retrieves and displays the user's account information, including session details, creator stats, and billing info.
* **Functionality:**
  * Fetches the bearer token.
  * Retrieves session data (user ID, username, email, subscription status).
  * Fetches creator info (statistics like likes and clip counts).
  * Fetches billing info (subscription type, credits, renewal date, etc.).
  * Combines the data into an `accountInfo` object and prints it to the console.
* **Key Features:**
  * Comprehensive account information retrieval.
  * Error handling for failed API requests.
  * Masks sensitive parts of email.

**11. `trashSearch.js`**

* **Purpose:** Provides a user interface to search for songs within the user's trash.
* **Functionality:**
  * Fetches the bearer token.
  * Calculates the total number of items in the trash.
  * Creates a fixed search bar at the top of the page with:
    * A text input field for the search term.
    * A "Search" button.
    * A "Show/Hide Results" toggle button.
    * A progress indicator.
    * A results container (initially hidden).
  * When the search button is clicked:
    * Retrieves all trashed clips.
    * Filters clips based on the search term in the title.
    * Displays search results with links to the songs on Suno.
    * Updates the progress indicator.
* **Key Features:**
  * User-friendly search interface.
  * Dynamic search results.
  * Progress indicator.
  * Links to view trashed songs directly.
  * Results are displayed directly on the page.

In summary, these scripts provide a powerful toolkit for managing and interacting with a Suno AI account, covering backups, user blocking, trash management, follower analysis, and account information retrieval. They are all well-structured, handle common error scenarios, and use delays to avoid overloading the Suno API.  The use of local storage in `blockBadActors.js` is a particularly good practice for long-running operations. The `trashSearch.js` script is excellent for providing a user interface directly within the Suno web page.
