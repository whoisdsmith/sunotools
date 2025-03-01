# SunoGFT.py

**How to use the script:**

1. **Save the code:** Save the above code as a Python file, for example, `extract_playlist_links.py`.
2. **Run from the command line:**

    ```bash
    python sunoGFT.py <YOUR_SUNO_PLAYLIST_URL>
    ```

    Replace `<YOUR_SUNO_PLAYLIST_URL>` with the actual URL of the public SunoAI playlist you want to extract links from. For example:

    ```bash
    python sunoGFT.py https://suno.com/playlist/ccc8a381-0fe4-42cf-bf6a-893624ead57e
    ```

# SunoGPX.js

How to run the script:

1. **Install Node.js:** Make sure you have Node.js and npm (Node Package Manager) installed on your system.
2. **Save the script:** Save the code above as a `.js` file (e.g., `extract_suno_playlist.js`).
3. **Install dependencies:** Open a terminal or command prompt in the directory where you saved the script and run:

    ```bash
    npm install axios cheerio
    ```

4. **Run the script:**  Provide the Suno playlist URL as a command-line argument:

    ```bash
    node sunoGPX.js "https://suno.com/playlist/ccc8a381-0fe4-42cf-bf6a-893624ead57e"
    ```

    Replace `"https://suno.com/playlist/ccc8a381-0fe4-42cf-bf6a-893624ead57e"` with the actual URL of the public Suno playlist.

The script will print the extracted song URLs to the console.  If there's an error, it will print an error message.
