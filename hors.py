import json

# Path to the HAR file
har_file_path = r"C:\Users\User\Documents\Github\suno_ai_downloader\hors.json"
output_file_path = r"C:\Users\User\Documents\Github\suno_ai_downloader\headers.json"

try:
    # Read the HAR file
    with open(har_file_path, 'r', encoding='utf-8') as file:
        har_data = json.load(file)

    # Initialize a list to store filtered headers
    filtered_headers = []

    # Iterate through each entry in the HAR file
    for entry in har_data['log']['entries']:
        url = entry['request']['url']

        # Check if the URL matches the pattern for the specific API endpoint
        if 'https://studio-api.prod.suno.com/api/feed/v2?is_liked=true&page=' in url:
            # Extract the page number from the URL
            try:
                page_num = int(url.split('page=')[1])
                # Check if the page number is between 1 and 65
                if 1 <= page_num <= 65:
                    # Extract request and response headers
                    headers = {
                        'page': page_num,
                        'request_url': url,
                        'request_headers': entry['request']['headers'],
                        'response_headers': entry['response']['headers'] if 'headers' in entry['response'] else []
                    }
                    filtered_headers.append(headers)
            except (IndexError, ValueError) as e:
                print(f"Error parsing URL {url}: {e}")
                continue

    # Sort the filtered headers by page number for consistency
    filtered_headers.sort(key=lambda x: x['page'])

    # Write the filtered headers to a new JSON file
    with open(output_file_path, 'w', encoding='utf-8') as output_file:
        json.dump(filtered_headers, output_file, indent=2, ensure_ascii=False)

    print(
        f"Successfully exported headers for pages 1-65 to {output_file_path}")

except FileNotFoundError:
    print(f"Error: The file {har_file_path} was not found.")
except json.JSONDecodeError:
    print(f"Error: The file {har_file_path} is not a valid JSON file.")
except Exception as e:
    print(f"An error occurred: {e}")
