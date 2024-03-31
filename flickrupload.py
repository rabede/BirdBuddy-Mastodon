import os
import re
import flickrapi
import webbrowser
import shutil
from dotenv import load_dotenv

load_dotenv()
KEY = os.getenv('FLICKR_KEY')
SECRET = os.getenv('FLICKR_SECRET')
api_key = KEY
api_secret = SECRET
source = '.'
destination = '../media/'

# Initialize the FlickrAPI instance
flickr = flickrapi.FlickrAPI(api_key, api_secret, format='rest')

# Authenticate - this will open a web browser window for the user to authenticate
if not flickr.token_valid(perms='write'):
    # Get a request token
    flickr.get_request_token(oauth_callback='oob')

    # Open the authorization URL in the web browser
    authorize_url = flickr.auth_url(perms='write')
    webbrowser.open_new_tab(authorize_url)

    # Prompt user for the verifier code from the browser
    verifier = str(input('Verifier code: '))
    
    # Trade the request token for an access token
    flickr.get_access_token(verifier)

# Define the directory path where the jpg files are located
files = [file for file in os.listdir(source) if file.endswith('.jpg') or file.endswith('.mp4')]
for file in files:
    title = re.search(r'^\d{8}_\d{6}_(.*?)\d*\.(jpg|mp4)$', file).group(1)
    photo_path = os.path.join(source, file)
    destfile = os.path.join(destination, file)
    tags = f'{title} BirdBuddy birds Vögel'
    description = f'{title} frisst am BirdBuddy'
    
    try: 
        response = flickr.upload(filename=photo_path, title=title, tags=tags, description=description)
    except Exception as e:
        response = f'{photo_path}/n{e}'
    print(response)
    shutil.move(photo_path, destfile)
