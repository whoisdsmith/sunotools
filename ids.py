import re


def extract_ids(input_file, output_file):
    id_pattern = re.compile(r'"id":\s*"([^"]+)"')
    ids = []

    with open(input_file, 'r') as infile:
        for line in infile:
            match = id_pattern.search(line)
            if match:
                ids.append(match.group(1))

    with open(output_file, 'w') as outfile:
        for id in ids:
            outfile.write(id + '\n')


if __name__ == "__main__":
    input_file = "SunoAI2.txt"
    output_file = "extracted_ids.txt"
    extract_ids(input_file, output_file)
    print(f"IDs have been extracted to {output_file}")
