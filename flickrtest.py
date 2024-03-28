import os
import re
import flickrapi
import webbrowser
import shutil

api_key = u'a2e8e61171f51d869ec178df9bc13865'
api_secret = u'7961f3d068c6c3b8'
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

jpg_files = [file for file in os.listdir(source) if file.endswith('.jpg')]
for jpg_file in jpg_files:
    title = re.search(r'^\d{8}_\d{6}_(.*?)\d*\.jpg$', jpg_file).group(1)
    photo_path = os.path.join(source, jpg_file)
    destfile = os.path.join(destination, jpg_file)
    tags = f'{title} BirdBuddy birds Vögel'
    description = f'{title} frisst am BirdBuddy'
    
    response = flickr.upload(filename=photo_path, title=title, tags=tags, description=description)
    print(response)
    shutil.move(photo_path, destfile)
