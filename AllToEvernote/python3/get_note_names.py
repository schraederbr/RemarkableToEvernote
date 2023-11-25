from datetime import datetime
import os
import json
import argparse
from typing import Dict

def read_metadata_from_directory(directory: str) -> Dict[str, str]:
    metadata_dict = {}
    for filename in os.listdir(directory):
        if filename.endswith('.metadata'):
            file_path = os.path.join(directory, filename)
            try:
                with open(file_path, 'r') as file:
                    data = json.load(file)
                    visible_name = data.get('visibleName', 'Unknown')
                    metadata_dict[visible_name] = filename.split('.')[0]
            except json.JSONDecodeError:
                print(f"Error reading {filename}: not a valid JSON file.")
    return metadata_dict

def get_todays_note(path):
    now = datetime.now()
    formatted_date = now.strftime("%m-%d-%y")
    # Read metadata from the specified directory
    metadata_dict = read_metadata_from_directory(path)

    # Print the result
    # for filename, visible_name in metadata_dict.items():
    #     print(f"{filename}: {visible_name}")
    print(metadata_dict[formatted_date])
    

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Read .metadata files and extract visibleNames.")
    parser.add_argument(
        "-p", "--path",
        default=os.getcwd(),  # Default to the current working directory
        help="Specify the path to the directory containing .metadata files."
    )

    # Parse command-line arguments
    args = parser.parse_args()
    get_todays_note(args.path)
    

if __name__ == "__main__":
    main()