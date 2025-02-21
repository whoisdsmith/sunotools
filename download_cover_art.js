import * as fs from 'fs/promises';
import { parse } from 'node-html-parser';
import path from 'path';

const BASE_PATH = 'C:\\Users\\User\\Documents\\Github\\suno_ai_downloader\\cover_art';

async function main() {
  const filePath = 'C://Users//User//Documents//Github//suno_ai_downloader//unique_songs.txt'; // Path to your URL list

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
        await fetchAndSaveCoverArt(formattedUrl); //  Call the function to fetch and save
      } catch (err) {
        console.error(`Error processing ${formattedUrl}:`, err);
      }
    }
  } catch (err) {
    console.error('Error reading file:', err);
  }
}

async function fetchAndSaveCoverArt(url) {
  const result = await fetch(url);
  if (!result.ok) {
    console.error('Failed to fetch:', url);
    return;
  }
  const html = await result.text();
  const root = parse(html);

  let pushedData = '';

  // Loop over all script tags, same logic as your original script
  for (const script of root.querySelectorAll('script')) {
    if (!script.text.startsWith('self.__next_f.push([')) {
      continue;
    }

    const data = script.text.match(
      /\s*self\.__next_f.push\(\[\s*1,\s*"(?<wanted>.*)",?\s*\]\);?/m,
    );
    if (data && data[1]) {
      const better = JSON.parse(`"${data[1]}"`);
      pushedData += better;
    }
  }

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
    if(!json || !json.clip) {
        console.error('Failed to parse clip data:', url);
        return;
    }

  await doImage(json.clip); // Call doImage with the clip data
}


async function doImage(data) {
  const artBuffer = await fetch(data.image_large_url).then((res) =>
    res.arrayBuffer(),
  );

  // Get the song title
  const songTitle = data.title;

  // Create the song directory
  const songDirPath = path.join(BASE_PATH, songTitle);
  await fs.mkdir(songDirPath, { recursive: true });

  // Define the base filename (only the song title)
  let baseFilename = songTitle;
  let filename = path.join(songDirPath, `${baseFilename}.jpg`);

  // Check if file exists, and use Roman numerals for duplicates
  filename = await getUniqueFilenameRoman(filename, songDirPath, baseFilename);

  // Save the image file
  await fs.writeFile(filename, Buffer.from(artBuffer));
  console.log('Wrote cover art:', filename);
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
  const decimalValues = Object.keys(romanMap).map(Number).sort((a, b) => b - a);

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