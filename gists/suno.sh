# * Usage:
#   cd [path where the script file is stored]
#   sudo chmod 777 suno_downloader.sh
#   ./suno_downloader.sh
#
# * Description: After creating an audio file on Suno.com, click "Copy Share link" to copy the URL.
#   Then paste it when prompted by this script to download both the MP3 file and the cover image file.
#
# * Requirements: wget
#
# * Log:
#   2025. 1. 11 : Downloading mp3 / jpeg files

#!/bin/bash

echo -n "Enter URL: "
read link

# Extract the hash value from the URL
hash=$(echo "$link" | awk -F'/song/' '{print $2}')

if [ -z "$hash" ]; then
    echo "Error: Unable to extract hash value from URL."
    exit 1
fi

echo "Extracted hash: $hash"

# Fetch the album title from the SUNO page
page_url="https://suno.com/song/$hash"
echo "Fetching album information from $page_url"

# Retrieve the HTML
html=$(curl -s "$page_url")

# Extract the content of 'og:title' using sed
og_title=$(echo "$html" | sed -n 's/.*<meta property="og:title" content="\([^"]*\)".*/\1/p')

if [ -z "$og_title" ]; then
    echo "Error: Unable to retrieve og:title content."
    album_title="unknown_album"
else
    # Extract just the album title from the og:title (removing "by...")
    album_title=$(echo "$og_title" | sed -E 's/^(.*) by .*$/\1/')
fi

echo "Album Title: $album_title"

# Construct the MP3 download path
mp3_download=$(echo "$link.mp3" | sed -e 's/suno.com/cdn1\.suno\.ai/g' -e 's/\/song\//\//g')
echo "Downloading MP3 from $mp3_download"
wget -q $mp3_download -O "${album_title}.mp3"

# Construct the image download path
img_download="https://cdn2.suno.ai/image_large_$hash.jpeg"
echo "Downloading image from $img_download"
wget -q $img_download -O "${album_title}.jpeg"

echo "Download complete: ${album_title}.mp3 and ${album_title}.jpeg"