# RemarkableToEvernote
Python scripts that take Remarkable notebooks and uploads them to Evernote. 

Evernote notes can be appended with Google Cloud Vision OCR and/or a pdf of the notebook

python3 main.py -h
usage: main.py [-h] [-p PATH] [-c] [-o] [-f] [-g] [-s START] [-e END]

Attach Remarkable notebook to Evernote note

options:
  -h, --help              show this help message and exit
  -p PATH, --path PATH    Specify the path to the directory containing .metadata files.
  -c, --copy              Specify whether to copy files from Remarkable to PC.
  -o, --ocr               Specify whether to perform OCR on the note.
  -f, --pdf               Specify whether to attach the PDF to the note.
  -g, --gcloud            Specify whether gcloud needs to be initiliazed.
  -s START, --start START Specify the start date of the notes to be converted. (mm-dd-yy format)
  -e END, --end END       Specify the end date of the notes to be converted.  (mm-dd-yy format)
