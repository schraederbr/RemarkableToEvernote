from evernote.api.client import EvernoteClient
from evernote.api.client import NoteStore

from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.shortcuts import redirect
# rename config.py.template to config.py and paste your credentials. 
from config import EN_CONSUMER_KEY, EN_CONSUMER_SECRET

def read_request_token_from_file(file_path='request_token.txt'):
    with open(file_path, 'r') as f:
        oauth_token = f.readline().strip()
        oauth_token_secret = f.readline().strip()

    return oauth_token, oauth_token_secret

# Seems like this only get 128 notes.
def getAllNotes(authToken, noteStore, maxCount=None):
	noteFilter = NoteStore.NoteFilter()
	noteFilter.words = "*"
	sharedNotes = []
	offset = 0
	if not maxCount:
		maxCount = 500
	while len(sharedNotes) < maxCount:
		try:
			noteList = noteStore.findNotes(authToken, noteFilter, offset, 50)
			sharedNotes += noteList.notes
		except (EDAMNotFoundException, EDAMSystemException, EDAMUserException), e:
			print "Error getting shared notes:"
			print type(e), e
			return None

		if len(sharedNotes) % 50 != 0:
			## We've retrieved all of the notes 
			break
		else:
			offset += 50
	return sharedNotes[:maxCount]


def get_evernote_client(token=None):
    if token:
        return EvernoteClient(token=token, sandbox=False)
    else:
        return EvernoteClient(
            consumer_key=EN_CONSUMER_KEY,
            consumer_secret=EN_CONSUMER_SECRET,
            sandbox=False
        )


def index(request):
    return render_to_response('oauth/index.html')


def auth(request):
    client = get_evernote_client()
    callbackUrl = 'http://%s%s' % (
        request.get_host(), reverse('evernote_callback'))
    request_token = client.get_request_token(callbackUrl)
    with open('request_token.txt', 'w') as f:
        f.write(request_token['oauth_token'] + '\n')
        f.write(request_token['oauth_token_secret'] + '\n')
    # Save the request token information for later
    request.session['oauth_token'] = request_token['oauth_token']
    request.session['oauth_token_secret'] = request_token['oauth_token_secret']

    # Redirect the user to the Evernote authorization URL
    return redirect(client.get_authorize_url(request_token))


def callback(request):
    try:
        # Read the saved request token and secret from the file
        saved_oauth_token, saved_oauth_token_secret = read_request_token_from_file()
        
        # Make sure session tokens and saved tokens match
        assert saved_oauth_token == request.session['oauth_token']
        assert saved_oauth_token_secret == request.session['oauth_token_secret']
        
        client = get_evernote_client()
        access_token = client.get_access_token(
            saved_oauth_token,
            saved_oauth_token_secret,
            request.GET.get('oauth_verifier', '')
        )
    except (KeyError, AssertionError):
        return redirect('/')

    # At this point, you should save the `access_token` securely for future API calls
    # Replace `request.session` with your secure token storage mechanism
    request.session['access_token'] = access_token

    # Initialize the Evernote client with the access token
    client = get_evernote_client(access_token)

    note_store = client.get_note_store()
    notebooks = note_store.listNotebooks()
    notes = getAllNotes(access_token, note_store)
    import pdb; pdb.set_trace()

    return render_to_response('oauth/callback.html', {'notebooks': notebooks})

def reset(request):
    return redirect('/')
