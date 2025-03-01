# Download all Suno (app.suno.ai) songs displayed on a page

> ## Excerpt
>
> Download all Suno (app.suno.ai) songs displayed on a page - suno-download-all-songs.js

---

Download all Suno (app.suno.ai) songs displayed on a page

**[gadelkareem](https://gist.github.com/gadelkareem)** commented [Sep 12, 2024](https://gist.github.com/FGRibreau/420b5da7289969e5746298356a49423c?permalink_comment_id=5187296#gistcomment-5187296) •

edited

Modified it a bit to download the video and rename the file:

```js
//  open your javascript console and paste this
copy([...$('[role="grid"]')[Object.keys($('[role="grid"]')).filter(x => x.startsWith('__reactProps'))[0]].children[0].props.values[0][1].collection]
  .filter(x => x.value.audio_url || x.value.video_url)
  .map(x => {
    const title = x.value.title.trim() || x.value.id ;
    const audio = x.value.audio_url ? `${title}.mp3|${x.value.audio_url}` : '';
    const video = x.value.video_url ? `${title}.mp4|${x.value.video_url}` : '';
    return [audio, video].filter(Boolean).join("\n");
  })
  .join("\n")
)
// now you have a list of mp3 urls directly in your clipboard that you can pass to wget or a url downloader
```

Script to download and rename

```python
# Usage: python suno-downloader.py <path-to-js-output-file>
import requests
import os
import sys

def download_file(url, filename):
    response = requests.get(url, stream=True)
    response.raise_for_status()
    with open(filename, 'wb') as file:
        for chunk in response.iter_content(chunk_size=8192):
            file.write(chunk)

def main():
    js_file = sys.argv[1]
    with open(js_file, 'r') as file:
        js_output = file.read()


    # Split the input string into individual file entries
    file_entries = js_output.split("\n")

    # Create a directory to store the downloaded files
    if not os.path.exists('downloads'):
        os.makedirs('downloads')

    names = ()
    # Process each file entry
    for entry in file_entries:
        try:
            i = 0
            print(f"Processing: {entry}")
            filename, url = entry.split('|')
            print(f"Downloading: {filename}")
            org_name =  os.path.splitext(filename)[0]
            ext = os.path.splitext(filename)[1]
            # make sure the file name is unique
            while filename in names:
                i += 1
                name = org_name + "_" + str(i)
                filename = name + ext

            names = names + (filename,)




            download_file(url, os.path.join('downloads', filename))
            print(f"Successfully downloaded: {filename}")
        except Exception as e:
            print(f"Failed to download {entry}. Error: {str(e)}")

    print("Download process completed.")

if __name__ == "__main__":
    main()
```

[![@SurfingTurtles](https://avatars.githubusercontent.com/u/177594493?s=80&v=4)](https://gist.github.com/SurfingTurtles)

###

**[SurfingTurtles](https://gist.github.com/SurfingTurtles)** commented [Sep 16, 2024](https://gist.github.com/FGRibreau/420b5da7289969e5746298356a49423c?permalink_comment_id=5193970#gistcomment-5193970) •

edited

[@gadelkareem](https://github.com/gadelkareem) Hi! I've figured out how to do the console part and get the filename/url combo list in my clipboard, but how do I then use the .py code to finish the task? I'm using IDLE on Mac to place the .py but am not sure how the clipboard text connects to the .py part.

[![@gadelkareem](https://avatars.githubusercontent.com/u/1441127?s=80&v=4)](https://gist.github.com/gadelkareem)

###

**[gadelkareem](https://gist.github.com/gadelkareem)** commented [Sep 17, 2024](https://gist.github.com/FGRibreau/420b5da7289969e5746298356a49423c?permalink_comment_id=5195096#gistcomment-5195096)

[@SurfingTurtles](https://github.com/SurfingTurtles) Put the coppied text inside a txt file then run the python `python3 suno-downloader.py output.txt`

[![@Godjiro](https://avatars.githubusercontent.com/u/124950048?s=80&v=4)](https://gist.github.com/Godjiro)

###

**[Godjiro](https://gist.github.com/Godjiro)** commented [Oct 12, 2024](https://gist.github.com/FGRibreau/420b5da7289969e5746298356a49423c?permalink_comment_id=5232247#gistcomment-5232247)

> [@SurfingTurtles](https://github.com/SurfingTurtles) Put the coppied text inside a txt file then run the python `python3 suno-downloader.py output.txt`

Can not figure, what name the txt file should be? I created file output.txt - i got answer \[Errno 2\] No such file or directory
Where to get "suno-downloader"? or smth?

[![@gadelkareem](https://avatars.githubusercontent.com/u/1441127?s=80&v=4)](https://gist.github.com/gadelkareem)

###

**[gadelkareem](https://gist.github.com/gadelkareem)** commented [Oct 14, 2024](https://gist.github.com/FGRibreau/420b5da7289969e5746298356a49423c?permalink_comment_id=5233880#gistcomment-5233880)

rename the text file you created to suno-downloader.py and make sure to install python

[![@jagamypriera](https://avatars.githubusercontent.com/u/4131801?s=80&v=4)](https://gist.github.com/jagamypriera)

###

**[jagamypriera](https://gist.github.com/jagamypriera)** commented [Nov 12, 2024](https://gist.github.com/FGRibreau/420b5da7289969e5746298356a49423c?permalink_comment_id=5279207#gistcomment-5279207) •

edited

Here is a script to download and rename files in Bash.

- Save this script as `download.sh`, then run `chmod +x download.sh`.
- Put the list of MP3 and MP4 URLs ([that you get from @gadelkareem javascript](https://gist.github.com/FGRibreau/420b5da7289969e5746298356a49423c?permalink_comment_id=5187296#gistcomment-5187296:~:text=//%20%20open%20your%20javascript%20console%20and%20paste%20this%0Acopy,can%20pass%20to%20wget%20or%20a%20url%20downloader)) inside `input.txt`
- Then run `./download.sh`

```shell
#!/bin/bash

# Read the file line by line
while IFS="|" read -r filename url; do
    # Use curl to download the file
    curl -o "$filename" "$url"

    # Wait for 1 second
    sleep 1
done < input.txt

```

[![@M1XZG](https://avatars.githubusercontent.com/u/22931360?s=80&v=4)](https://gist.github.com/M1XZG)

###

**[M1XZG](https://gist.github.com/M1XZG)** commented [Feb 11, 2025](https://gist.github.com/FGRibreau/420b5da7289969e5746298356a49423c?permalink_comment_id=5433934#gistcomment-5433934) •

edited

I'd like to offer an updated js snippet to the work done by [@gadelkareem](https://github.com/gadelkareem) , this one will handle the renaming of multiple song names. Don't we all just love how SUNO always spends double our credits making 2 songs fo every prompt.

I found the original code above was a bit problematic because it would try to name the songs the same which doesn't work well when bulk downloading.

This code will give multiple songs of the same name a number such as `songname_2`, `songname_3` etc. The first song name is untouched.

Example:

```
Virtual Rainfall.mp3|https://cdn1.suno.ai/b75f73f7-e535-4e40-982b-b59342ac1291.mp3
Virtual Rainfall.mp4|https://cdn1.suno.ai/b75f73f7-e535-4e40-982b-b59342ac1291.mp4
Virtual Rainfall_2.mp3|https://cdn1.suno.ai/923ea8f2-bcfa-4c19-b75e-1218618fde52.mp3
Virtual Rainfall_2.mp4|https://cdn1.suno.ai/923ea8f2-bcfa-4c19-b75e-1218618fde52.mp4
```

```
// open your javascript console and paste this
copy([...$('[role="grid"]')[Object.keys($('[role="grid"]')).filter(x =&gt; x.startsWith('__reactProps'))[0]].children[0].props.values[0][1].collection]
  .filter(x =&gt; x.value.audio_url || x.value.video_url)
  .reduce((acc, x) =&gt; {
    const title = x.value.title.trim() || x.value.id;
    acc.titles[title] = (acc.titles[title] || 0) + 1;
    const uniqueTitle = acc.titles[title] &gt; 1 ? `${title}_${acc.titles[title]}` : title;
    const audio = x.value.audio_url ? `${uniqueTitle}.mp3|${x.value.audio_url}` : '';
    const video = x.value.video_url ? `${uniqueTitle}.mp4|${x.value.video_url}` : '';
    acc.urls.push([audio, video].filter(Boolean).join("\n"));
    return acc;
  }, { urls: [], titles: {} }).urls.join("\n")
)
// now you have a list of mp3 urls directly in your clipboard that you can pass to wget or a url downloader
```

I hope this helps.

[![@M1XZG](https://avatars.githubusercontent.com/u/22931360?s=80&v=4)](https://gist.github.com/M1XZG)

###

**[M1XZG](https://gist.github.com/M1XZG)** commented [Feb 11, 2025](https://gist.github.com/FGRibreau/420b5da7289969e5746298356a49423c?permalink_comment_id=5433944#gistcomment-5433944)

If you want a slightly improved download script that [@jagamypriera](https://github.com/jagamypriera) created, this one will let you specify any input file you like but it also handles duplicate filenames by appending a number to the song name.

example:

```
Stardust Reverberation.mp3
Stardust Reverberation.mp4
Stardust Reverberation_2.mp3
Stardust Reverberation_2.mp4
```

```
#!/bin/bash

# Check if the input file is provided
if [ -z "$1" ]; then
    echo "Usage: $0 &lt;input_file&gt;"
    exit 1
fi

input_file="$1"

# Read the file line by line
while IFS="|" read -r filename url; do
    # Check if the file already exists
    if [[ -e "$filename" ]]; then
        base="${filename%.*}"
        ext="${filename##*.}"
        counter=2
        while [[ -e "${base}_${counter}.${ext}" ]]; do
            ((counter++))
        done
        filename="${base}_${counter}.${ext}"
    fi

    # Print the song name being downloaded
    echo "Downloading $filename"

    # Use curl to download the file
    curl -o "$filename" "$url"

    # Wait for 1 second
    sleep 1
done &lt; "$input_file"
```

I hope this helps someone.
