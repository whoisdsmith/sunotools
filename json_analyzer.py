import json
import jsonschema
from jsonschema import validate


def read_large_json(file_path, chunk_size=1024):
    with open(file_path, 'r') as file:
        buffer = ""
        while True:
            chunk = file.read(chunk_size)
            if not chunk:
                break
            buffer += chunk
            while True:
                try:
                    obj, idx = json.JSONDecoder().raw_decode(buffer)
                    yield obj
                    buffer = buffer[idx:].lstrip()
                except json.JSONDecodeError:
                    break


def validate_json(json_data, schema):
    try:
        validate(instance=json_data, schema=schema)
    except jsonschema.exceptions.ValidationError as err:
        return str(err)
    return None


def analyze_json(file_path, schema=None):
    errors = []
    for json_obj in read_large_json(file_path):
        if schema:
            error = validate_json(json_obj, schema)
            if error:
                errors.append(error)
    return errors


if __name__ == "__main__":
    file_path = r"C:\Users\whois\Documents\suno_ai_downloader\suno.json"  # Use raw string
    schema = {
        # Define your JSON schema here if you have one
    }
    errors = analyze_json(file_path, schema)
    if errors:
        print("Errors found in JSON file:")
        for error in errors:
            print(error)
    else:
        print("No errors found in JSON file.")