import * as fs from 'fs/promises';
import MP3Tag from 'mp3tag.js';
import { parse } from 'node-html-parser';
import path from 'path';

const BASE_PATH = 'C:\\Users\\User\\Documents\\Github\\suno_ai_downloader\\tracks';

async function main() {
  const filePath = 'C://Users//User//Documents//Github//suno_ai_downloader//unique_songs.txt';

  try {
    const fileContent = await fs.readFile(filePath, 'utf-8');
    const urls = fileContent.split(/\s+/).filter(line => line.trim() !== '');

    for (const url of urls) {
      const uuid = url.match(
        /\b[0-9a-f]{8}\b-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-\b[0-9a-f]{12}\b/,
      );

      if (!uuid) {
        console.error('Invalid UUID:', url);
        continue;
      }

      console.log('Processing UUID:', uuid[0]);
      const formattedUrl = `https://suno.com/song/${uuid[0]}`;

      try {
        // Pass the UUID (song ID) along with the URL
        await fetchSongData(formattedUrl, uuid[0]);
      } catch (err) {
        console.error(`Error processing ${formattedUrl}:`, err);
      }
    }
  } catch (err) {
    console.error('Error reading file:', err);
  }
}

// Note: Added a second parameter "songId" to receive the song UUID
async function fetchSongData(url, songId) {
  const result = await fetch(url);
  if (!result.ok) {
    console.error('Failed to fetch:', url);
    return;
  }
  const html = await result.text();
  const root = parse(html);

  let pushedData = '';

  // Loop over all script tags to find the one with the pushed data
  for (const script of root.querySelectorAll('script')) {
    // Check if script tag contains desired data
    if (!script.text.startsWith('self.__next_f.push([')) {
      continue;
    }

    // Extract the data from the script tag using regex
    const data = script.text.match(
      /\s*self\.__next_f.push\(\[\s*1,\s*"(?<wanted>.*)",?\s*\]\);?/m,
    );
    if (data && data[1]) {
      const better = JSON.parse(`"${data[1]}"`);
      pushedData += better;
    }
  }

  // Extract JSON data starting from '{"clip":'
  const start = pushedData.indexOf('{"clip":');
  if (start === -1) {
    console.error('Failed to find clip data in', url);
    return;
  }

  const clip = pushedData.slice(start);
  let json = null;
  let endCut = 0;

  try {
    json = JSON.parse(clip);
  } catch (e) {
    const position = e.message.match(/position (\d+)/);
    if (position) {
      endCut = parseInt(position[1]);
    } else {
      console.error('Failed to parse json:', e);
      return;
    }

    try {
      json = JSON.parse(clip.slice(0, endCut));
    } catch (e) {
      console.error('Failed to parse json again:', e);
      return;
    }
  }

  // Pass the songId down to doSong
  await doSong(json.clip, songId);
}

// Updated doSong function to accept the songId parameter
async function doSong(data, songId) {
  const mp3Buffer = await fetch(data.audio_url).then((res) =>
    res.arrayBuffer(),
  );
  const artBuffer = await fetch(data.image_large_url).then((res) =>
    res.arrayBuffer(),
  );

  const songTitle = data.title;
  const songDirPath = path.join(BASE_PATH, songTitle);
  await fs.mkdir(songDirPath, { recursive: true });

  // Define the base filename (only the song title)
  let baseFilename = songTitle;
  let filename = path.join(songDirPath, `${baseFilename}.mp3`);

  // Check if file exists, and use Roman numerals for duplicates
  filename = await getUniqueFilenameRoman(filename, songDirPath, baseFilename);

  // Apply metadata to MP3 using MP3Tag.js
  const tag = new MP3Tag(Buffer.from(mp3Buffer));
  tag.read();
  tag.tags.title = songTitle;          // Use only song title
  tag.tags.artist = data.display_name;
  tag.tags.album = songTitle;          // Set album tag
  tag.tags.genre = data.metadata.tags;
  // Here we incorporate the song ID into the comment tag for later duplicate filtering.
  tag.tags.comment = `Suno AI (Song ID: ${songId})`;
  tag.tags.year = new Date(data.created_at).getFullYear().toString();
  tag.tags.v2.APIC = [
    {
      format: 'image/jpeg',
      type: 0,
      description: 'Suno AI',
      data: Buffer.from(artBuffer),
    },
  ];

  // Alternatively, if you prefer to store the song ID in a custom tag (e.g., TXXX),
  // you could uncomment the following block (provided MP3Tag.js supports it):
  /*
  tag.tags.v2.TXXX = [
    {
      description: 'Song ID',
      data: songId,
    },
  ];
  */

  // Save the MP3 file
  await fs.writeFile(
    filename,
    Buffer.from(
      tag.save({
        strict: true, // Strict mode, validates all inputs against the standards.
        id3v2: { padding: 4096 },
      }),
    ),
  );

  if (tag.error) {
    console.error('MP3Tag error:', tag.error);
  } else {
    console.log('Wrote:', filename);
  }
}

// Function to get a unique filename using Roman numerals
async function getUniqueFilenameRoman(filepath, dir, baseFilename) {
  let ext = path.extname(filepath);
  let filename = path.basename(filepath, ext);
  let counter = 0; // Start at 0, first instance will be without Roman Numeral
  let newFilename = path.join(dir, `${baseFilename}${ext}`);

  while (await fileExists(newFilename)) {
    counter++;
    const roman = toRoman(counter);
    newFilename = path.join(dir, `${baseFilename} ${roman}${ext}`);
  }

  return newFilename;
}

// Helper function to convert numbers to Roman numerals
function toRoman(num) {
  const romanMap = {
    1: 'I',
    4: 'IV',
    5: 'V',
    9: 'IX',
    10: 'X',
    40: 'XL',
    50: 'L',
    90: 'XC',
    100: 'C',
    400: 'CD',
    500: 'D',
    900: 'CM',
    1000: 'M',
  };

  let result = '';
  const decimalValues = Object.keys(romanMap)
    .map(Number)
    .sort((a, b) => b - a);

  for (const decimal of decimalValues) {
    while (num >= decimal) {
      result += romanMap[decimal];
      num -= decimal;
    }
  }

  return result;
}

// Helper function to check if a file exists
async function fileExists(filepath) {
  try {
    await fs.access(filepath);
    return true;
  } catch (err) {
    return false;
  }
}

main();
