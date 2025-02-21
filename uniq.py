def process_urls(input_file, output_file):
    with open(input_file, 'r') as infile:
        content = infile.read()

    # Split the content by commas to get individual URLs
    urls = content.split(',')

    # Remove duplicates by converting the list to a set, then back to a list
    unique_urls = list(set(urls))

    # Remove any empty strings that may result from trailing commas
    unique_urls = [url for url in unique_urls if url]

    # Join the unique URLs with a space
    result = ' '.join(unique_urls)

    # Write the result to the output file
    with open(output_file, 'w') as outfile:
        outfile.write(result)


if __name__ == "__main__":
    input_file = 'songs.txt'
    output_file = 'unique_songs.txt'
    process_urls(input_file, output_file)
    print(f"Unique URLs have been written to {output_file}")
