from datetime import datetime
import os
import json
import argparse
from typing import Dict
from pdf2image import convert_from_path
from rmrl import render
from datetime import datetime, timedelta
from google.cloud import vision

def pdf_to_png(pdf_path, output_path, filename):
    # Convert the PDF to images
    images = convert_from_path(pdf_path)

    for i, image in enumerate(images):
        # Save each image as a PNG file
        image.save(output_path + '/' + filename + '_' + str(i) + '_.png', 'PNG')




def get_note_names_and_ids(directory: str) -> Dict[str, str]:
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

def get_todays_note(path, date=None):
    if(not date):
        now = datetime.now()
        date = now.strftime("%m-%d-%y")
    # Read metadata from the specified directory
    metadata_dict = get_note_names_and_ids(path)
    # Return full path of note
    return (date, f"{path}/{metadata_dict[date]}.content")
    
def parse_gcloud_json(file):
    with open(file, 'r') as f:
        data = json.load(f)
        
    # Extracting text from json response
    if('responses' not in data):
        return ''
    if('fullTextAnnotation' not in data['responses'][0]):
        return ''
    return data['responses'][0]['fullTextAnnotation']['text']

    # with open(file, 'w') as f:
    #     f.write(text)

def gcloud_ocr(infile, outfile):
    client = vision.ImageAnnotatorClient()

    with open(infile, 'rb') as image_file:
        content = image_file.read()

    image = vision.Image(content=content)

    response = client.text_detection(
        image=image,
        image_context={"language_hints": ["en"]},  # Set language hint to English ("en")
    )

    texts = response.text_annotations
    if(len(texts) == 0):
        return ''
    output = texts[0].description
    with open(outfile, 'w') as f:
        f.write(output)
    return output

def single_day(args, date):
    note_tuple = get_todays_note(args.path, date)
    note_path = note_tuple[1]
    note_date = note_tuple[0]
    if not os.path.exists(note_date):
        os.makedirs(note_date)
    if not os.path.exists(note_date + '/PNGs'):
        os.makedirs(note_date + '/PNGs')

    print("Converting {} to PDF...".format(note_path))
    # This should be handled directly by python, not this system call
    
    output = render(note_path)
    with open(note_date + '/' + note_date + '.pdf', 'wb') as f:
        f.write(output.read())

    if(args.ocr):
        
        if(args.gcloud):
            print('Setting up google cloud vision')
            os.system('gcloud init')
        print("Converting {} to PNGs...".format(note_date + '.pdf'))
        pdf_to_png(note_date + '/' + note_date + '.pdf', note_date + '/PNGs', note_date)

        print("Running gcloud OCR on " + note_date + " PNGs...")
        
        count = 1
        text = ''
        for filename in os.listdir(note_date + '/PNGs'):
                print(filename)
                text += gcloud_ocr(note_date + '/PNGs/' + filename, note_date + '/' + filename + '.txt')  + '\n' + 'PAGE_' + str(count) + '\n' + 'PAGE_END' + '\n'
                count += 1    
        with open(note_date + '/' + note_date + '.txt', 'w') as f2:
            f2.write(text)
    print("Attaching content to Evernote note...")
    if(args.ocr):
        if(args.pdf):
            os.system('python2 note_attach.py -d ' + note_date + ' -o ' + note_date + '/' + note_date + '.txt -f ' + note_date + '/' + note_date + '.pdf')
        else:
            os.system('python2 note_attach.py -d ' + note_date + ' -o ' + note_date + '/' + note_date + '.txt')
    else:
        if(args.pdf):
            os.system('python2 note_attach.py -d ' + note_date + ' -f ' + note_date + '/' + note_date + '.pdf')
        else:
            print("No PDF or OCR content to attach to Evernote note. Exiting...")

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Attach Remarkable note to Evernote note")
    parser.add_argument(
        "-p", "--path",
        default='xochitl',  # Default to the current working directory
        help="Specify the path to the directory containing .metadata files."
    )
    parser.add_argument(
        "-c", "--copy",
        action='store_true',
        help="Specify whether to copy files from Remarkable to PC."
    )
    parser.add_argument(
        "-o", "--ocr",
        action='store_true',
        help="Specify whether to perform OCR on the note."
    )
    parser.add_argument(
        "-f", "--pdf",
        action='store_true',
        help="Specify whether to attach the PDF to the note."
    )
    parser.add_argument(
        "-g", "--gcloud",
        action='store_true',
        help="Specify whether gcloud needs to be initiliazed."
    )
    parser.add_argument(
        "-s", "--start",
        default=None,
        help="Specify the start date of the notes to be converted."
    )
    parser.add_argument(
        "-e", "--end",
        default=None,
        help="Specify the end date of the notes to be converted."
    )
    

    # Parse command-line arguments
    args = parser.parse_args()
    if(args.copy):
        os.system('scp -r root@10.11.99.1:/home/root/.local/share/remarkable/xochitl/ .')


    if(not args.end):
        if(not args.start):
            single_day(args, None)
        else:
            single_day(args, args.start)
    else:
        start_datetime = datetime.strptime(args.start, "%m-%d-%y")
        end_datetime = datetime.strptime(args.end, "%m-%d-%y")

        # Iterate through each day
        current_date = start_datetime
        while current_date <= end_datetime:
            print(current_date.strftime("%m-%d-%y"))
            single_day(args, current_date.strftime("%m-%d-%y"))
            current_date += timedelta(days=1)

if __name__ == "__main__":
    main()