import os
import re
import flickrapi
import webbrowser
from dotenv import load_dotenv

class FlickrUpload:
    def __init__(self, source='.'):
        load_dotenv()  # Load environment variables from .env file
        self.api_key = os.getenv('FLICKR_KEY')
        self.api_secret = os.getenv('FLICKR_SECRET')
        self.source = source
        self.flickr = flickrapi.FlickrAPI(self.api_key, self.api_secret, format='rest')
        self.authenticate()

    def authenticate(self):
        # Authenticate - this will open a web browser window for the user to authenticate
        if not self.flickr.token_valid(perms='write'):
            # Get a request token
            self.flickr.get_request_token(oauth_callback='oob')

            # Open the authorization URL in the web browser
            authorize_url = self.flickr.auth_url(perms='write')
            webbrowser.open_new_tab(authorize_url)

            # Prompt user for the verifier code from the browser
            verifier = str(input('Verifier code: '))

            # Trade the request token for an access token
            self.flickr.get_access_token(verifier)

    def upload(self):
        # Define the directory path where the jpg files are located
        files = [file for file in os.listdir(self.source) if file.endswith('.jpg') or file.endswith('.mp4')]
        for file in files:
            title = re.search(r'^\d{8}_\d{6}_(.*?)\d*\.(jpg|mp4)$', file).group(1)
            photo_path = os.path.join(self.source, file)
            tags = f'{title} BirdBuddy birds Vögel'
            description = f'{title} frisst am BirdBuddy'
            
            try: 
                response = self.flickr.upload(filename=photo_path, title=title, tags=tags, description=description)
            except Exception as e:
                response = f'{photo_path}\n{e}'
            print(response)