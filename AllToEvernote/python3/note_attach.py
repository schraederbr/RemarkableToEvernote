import time
import sys
import os
import cgi
from evernote.api.client import EvernoteClient
from evernote.api.client import NoteStore
from evernote.edam.type.ttypes import Note, Resource, ResourceAttributes, Data
import hashlib
from evernote.edam.type.ttypes import Note, Resource, Data
# from evernote.edam.limits.constants import RESOURCE_SIZE_MAX_FREE
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.shortcuts import redirect
from datetime import datetime
from config import EN_CONSUMER_KEY, EN_CONSUMER_SECRET
from bs4 import BeautifulSoup
import argparse
access_token = None

def get_evernote_client(token=None):
    if token:
        return EvernoteClient(token=token, sandbox=False)
    else:
        return EvernoteClient(
            consumer_key=EN_CONSUMER_KEY,
            consumer_secret=EN_CONSUMER_SECRET,
            sandbox=False
        )


def get_notes_with_title(authToken, noteStore, title , maxCount=None):
	noteFilter = NoteStore.NoteFilter()
	noteFilter.words = "intitle:" + title
	notes = []
	offset = 0
	if not maxCount:
		maxCount = 500
	while len(notes) < maxCount:
		try:
			noteList = noteStore.findNotes(authToken, noteFilter, offset, 50)
			notes += noteList.notes
		except Exception as e:
			print("Error getting shared notes:")
			print(type(e), e)
			return None

		if len(notes) % 50 != 0:
			## We've retrieved all of the notes 
			break
		else:
			offset += 50
	return notes[:maxCount]




def attach_pdf_to_existing_note(note_store, note_guid, pdf_path=None, ocr=None):
    # Fetch the existing note
    note = note_store.getNote(note_guid, True, False, False, False)
    if(pdf_path):
        # Read the PDF file
        with open(pdf_path, 'rb') as pdf_file:
            pdf_data = pdf_file.read()

        # Create a new resource for the PDF
        data = Data(body=pdf_data)
        resource_attributes = ResourceAttributes()
        resource_attributes.fileName = note.title + '_rm.pdf'
        resource_attributes.attachment = True
        resource = Resource(data=data, mime='application/pdf', attributes=resource_attributes)

        # Generate the hash of the PDF data
        hash_hex = hashlib.md5(pdf_data).hexdigest()

        # If the note already has resources, append the new resource. Otherwise, create a new list.
        if note.resources:
            note.resources.append(resource)
        else:
            note.resources = [resource]
    # Append a reference to the new resource in the note's content
    

    note.content = note.content.replace('</en-note>', '')  # Remove the closing tag
    note.content += "<div><b><h1>Remarkable Content:</h1></b></div>"
    if ocr:
        with open(ocr, 'r') as f:
            ocr_text = f.read()

        note.content += "<div><b>OCR Content:</b></div>"

        # Split the OCR text into pages
        pages = ocr_text.split("PAGE_END")

        # Iterate over each page and add it to the note content
        for page in pages:
            if page.strip():  # Check if the page has content other than whitespace
                escaped_page = cgi.escape(page)  # Use cgi.escape to deal with special characters
                note.content += "<div><pre>{}</pre></div>".format(escaped_page)

        if not pdf_path:
            note.content += '</en-note>'

    if pdf_path:
        note.content += '<en-media type="application/pdf" hash="{}"/></en-note>'.format(hash_hex)

    note_store.updateNote(note)
	


def main():
    global access_token

    parser = argparse.ArgumentParser(description="Attach pdf to Evernote note")
    parser.add_argument(
        "-t", "--token",
        default=None, 
        help="Specify the path to the directory containing .metadata files."
    )
    parser.add_argument(
        "-d", "--date",
        default=None,  
        help="Specify the date of the note to be converted."
    )
    parser.add_argument(
        "-o", "--ocr",
        default=None,
        help="Specify name of converted OCR txt file."
    )
    parser.add_argument(
        "-f", "--pdf",
        default=None,
        help="Specify the PDF file to attach."
    )


    args = parser.parse_args()
    client = get_evernote_client()
    if(args.token):
        access_token = args.token
    else:
        with open ('access_token.txt', 'r') as f:
            access_token = f.readline().strip()
    
    # Initialize the Evernote client with the access token
    client = get_evernote_client(access_token)
    note_store = client.get_note_store()
    # makeNote(note_store, 'test', 'test', [], None)
    # Get the current date and time
    now = datetime.now()
    formatted_date = now.strftime("%m-%d-%y")
    if(args.date):
        formatted_date = args.date

    
    notes = get_notes_with_title(access_token, note_store, formatted_date)
    # If note doesn't exist, create it
    if(notes == None or len(notes) == 0):
        print("Note doesn't exist. Creating it now")
        note = Note()
        note.title = formatted_date
        note.content = '<!DOCTYPE en-note SYSTEM "http://xml.evernote.com/pub/enml2.dtd"><en-note></en-note>'
        note = note_store.createNote(note)
    else:
        note = notes[0]

    
    print("Attaching to note titled: " + note.title)

    attach_pdf_to_existing_note(note_store, note.guid, args.pdf, args.ocr)

    print('Successfully attached to note')
    
    

if __name__ == "__main__":
    main()