import requests
from bs4 import BeautifulSoup
import pandas as pd
import logging
import argparse
from urllib.parse import urljoin
import time

# Set up logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


def scrape_data(url, session):
    logging.info(f"Scraping URL: {url}")
    try:
        response = session.get(url, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        logging.error(f"Error fetching {url}: {e}")
        return None

    soup = BeautifulSoup(response.content, 'html.parser')

    # Define the selectors
    selectors = {
        "Title": "div.animate-marquee > a.whitespace-nowrap.mr-24",
        "Tags": ".md\\:mt-4 .font-sans.break-all.text-sm.text-primary.mr-1",
        "Metadata": "span.text-secondary.text-sm.font-sans",
        "Lyrics": "textarea[readonly]",
        "Cover": "img.absolute.inset-0.w-full.h-full.object-cover",
        "Link": "div.animate-marquee > a.whitespace-nowrap.mr-24"
    }

    data = {}

    # Extract Title
    title_element = soup.select_one(selectors['Title'])
    data['Title'] = title_element.get_text(
        strip=True) if title_element else None

    # Extract Tags
    tag_elements = soup.select(selectors['Tags'])
    data['Tags'] = ', '.join([tag.get_text(strip=True)
                             for tag in tag_elements]) if tag_elements else None

    # Extract Metadata
    metadata_elements = soup.select(selectors['Metadata'])
    data['Metadata'] = ', '.join([meta.get_text(
        strip=True) for meta in metadata_elements]) if metadata_elements else None

    # Extract Lyrics
    lyrics_element = soup.select_one(selectors['Lyrics'])
    data['Lyrics'] = lyrics_element.get_text(
        strip=True) if lyrics_element else None

    # Extract Cover image URL
    cover_element = soup.select_one(selectors['Cover'])
    if cover_element and cover_element.has_attr('src'):
        data['Cover'] = urljoin(url, cover_element['src'])
    else:
        data['Cover'] = None

    # Extract Link
    link_element = soup.select_one(selectors['Link'])
    if link_element and link_element.has_attr('href'):
        data['Link'] = urljoin(url, link_element['href'])
    else:
        data['Link'] = None

    return data


def main(input_file, output_file):
    # Read URLs from the input file
    with open(input_file, 'r') as file:
        urls = [line.strip() for line in file if line.strip()]

    if not urls:
        logging.error("No URLs found in the input file.")
        return

    # Initialize a session
    session = requests.Session()
    session.headers.update({'User-Agent': 'Mozilla/5.0 (compatible; Bot/1.0)'})

    # Scrape data from all URLs
    scraped_data = []
    for url in urls:
        data = scrape_data(url, session)
        if data:
            scraped_data.append(data)
        time.sleep(1)  # Polite crawling by adding a delay between requests

    # Create a DataFrame and save to CSV
    df = pd.DataFrame(scraped_data)
    df.to_csv(output_file, index=False)

    logging.info(f"Data scraped and saved to {output_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Scrape data from URLs and save to CSV.")
    parser.add_argument('--input', required=True,
                        help="Input file containing URLs")
    parser.add_argument(
        '--output', default='scraped_data.csv', help="Output CSV file")

    args = parser.parse_args()

    main(args.input, args.output)
