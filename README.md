# RemarkableToEvernote

Python scripts that convert Remarkable notebooks and upload them to Evernote. Evernote notes can be enhanced with text recognition using Google Cloud Vision OCR and/or the addition of a PDF of the notebook.

## Getting Started

First, you need to retrieve an `access_token.txt` file using the Django server provided:

1. Run the Django server located in `python2/sample/django/manage.py`:

   ```sh
   cd python2/sample/django
   python2 manage.py runserver
   ```

   This requires a `config.py` file in the same directory with your Evernote API keys:

   ```python
   EN_CONSUMER_KEY = 'your_consumer_key'
   EN_CONSUMER_SECRET = 'your_consumer_secret'
   ```

2. Once the server is running, follow the prompts to get your `access_token.txt` file.

## Usage

To use the script, run the `main.py` with the desired options:

```sh
python3 main.py -h
```

### Command Line Arguments

```plaintext
usage: main.py [-h] [-p PATH] [-c] [-o] [-f] [-g] [-s START] [-e END]

Attach Remarkable notebook to Evernote note

options:
  -h, --help              show this help message and exit
  -p PATH, --path PATH    Specify the path to the directory containing .metadata files.
  -c, --copy              Specify whether to copy files from Remarkable to PC.
  -o, --ocr               Specify whether to perform OCR on the note.
  -f, --pdf               Specify whether to attach the PDF to the note.
  -g, --gcloud            Specify whether gcloud needs to be initialized.
  -s START, --start START Specify the start date of the notes to be converted (mm-dd-yy format).
  -e END, --end END       Specify the end date of the notes to be converted (mm-dd-yy format).
```

## Contributing

Contributions are welcome! Feel free to submit a pull request or open an issue.
