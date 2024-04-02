#!/usr/bin/python3
import asyncio
import requests
import os
import logging
from mastodon import Mastodon
from birdbuddy.client import BirdBuddy
from dotenv import load_dotenv
from FlickrUpload import FlickrUpload
from LocalSave import LocalSave

# Load environment variables or replace these with your actual credentials
load_dotenv()
EMAIL = os.getenv('BB_NAME')
PASS = os.getenv('BB_PASS')

ACCESS_TOKEN = os.getenv('MASTODON_ACCESS_TOKEN')
URL = os.getenv('MASTODON_API_BASE_URL')
VISIBILITY = os.getenv('MASTODON_VISIBILITY')
MAX_FILES = int(os.getenv('MASTODON_MAX_FILES'))

SLEEP = int(os.getenv('SECONDS_TO_SLEEP'))
FILENAME = os.getenv('LOGFILE')

FLICKR = os.getenv('FLICKR_KEY')

LOCL = os.getenv('LOCAL_DEST')

logging.basicConfig(level=logging.DEBUG, filename=FILENAME, format='%(asctime)s - %(levelname)s - %(name)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

last_postcard_id = []

mastodon = Mastodon(
    access_token=ACCESS_TOKEN,
    api_base_url=URL
)
logging.info(f'{URL} initialized')

bb = BirdBuddy(EMAIL, PASS)
bb.language_code = "de"

if FLICKR:
    uploader = FlickrUpload(source='./') 

if LOCL:
    local = LocalSave(source='./', dest=LOCL)    

# Utility function to upload images to Mastodon and return media IDs
def upload_images_to_mastodon(image_urls, birdName):
    description = f'{birdName} im Futterhäuschen'
    media_ids = []
    for url in image_urls:
        response = requests.get(url)
        media = mastodon.media_post(response.content, "image/png", description=description)
        media_ids.append(media['id'])
    logging.debug(f'{media_ids} uploaded')    
    return media_ids

def post_status(imageUrls, status_text, birdName):
    # Upload images and get their media IDs
    media_ids = upload_images_to_mastodon(imageUrls, birdName)
    # Post status with media on Mastodon
    mastodon.status_post(status_text, media_ids=media_ids,  visibility=VISIBILITY)


# check for bird sightings
async def check_bird_sighting():
    global last_postcard_id
    logging.debug(f'Last Postcard ID: {last_postcard_id}')

    try:
        postcards = await bb.new_postcards()
        if len(postcards) == 0:
            logging.debug('No new postcards')
            return
    except Exception as e:
        logging.debug(e)
        return
    
    for postcard in postcards:
        id = postcard['id']
        if id  in last_postcard_id:
            logging.debug('No new postcards')
            return
        
        last_postcard_id.append(id)
        logging.debug(f'Last Postcard ID: {last_postcard_id}')

        imageUrls = []
        videoUrls = []

        sightingTimestamp = postcard.created_at
        sightingTime = sightingTimestamp.strftime('%d.%m.%Y %H:%M')

        try:
            sighting = await bb.sighting_from_postcard(postcard)
            report = sighting.report
        except Exception as e:
            logging.debug(e)
            return

        try: 
            birdName = report['sightings'][0]['species']['name']
            birdIcon = report['sightings'][0]['species']['iconUrl']
        except KeyError as e:
            birdName = 'unbekannt'# report['sightings'][0]['_typename']

        for imageCount, image in enumerate(sighting.medias, start=1):
            createtAt = image.created_at
            imgName = createtAt.strftime('%Y%m%d_%H%M%S')  + '_'  + birdName  + str(imageCount)
            imageUrl = image.content_url
            if imageCount <= MAX_FILES:
                imageUrls.append(imageUrl)          

            # Send an HTTP GET request to the image URL
            response = requests.get(imageUrl)

            # Check if the request was successful
            if response.status_code == 200:
                with open(f'{imgName}.jpg', 'wb') as file:
                    # Write the content of the response (the image) to the file
                    file.write(response.content)
            else:
                print(f"Failed to retrieve image. Status code: {response.status_code}")
            
        for videoCount, video in enumerate(sighting.video_media, start=1):       
            createtAt = video.created_at
            videoName = createtAt.strftime('%Y%m%d_%H%M%S')  + '_'  + birdName  + str(videoCount)
            videoUrl =  video['contentUrl']
            videoUrls.append(videoUrl)
            # Determine if there is a video url and select appropriate emoji for embed
            if len(videoUrls) > 0:
                videoEmoji = f'{videoUrls[0]}'
                response = requests.get(videoUrl)
                if response.status_code == 200:
                    with open(f'{videoName}.mp4', 'wb') as file:
                        file.write(response.content)
                else:
                    print(f"Failed to retrieve image. Status code: {response.status_code}")
            else:
                videoEmoji = 'No'

        description = f"\n🖼️Bilder: {imageCount} \n📹 Video: {videoEmoji}"

        split_string = str(report).split("'")
        recognized_phrase = split_string[3]
        if recognized_phrase == "mystery" or recognized_phrase == "best_guess":

            descriptionText = f"🐦 Besuche bisher: ??{description}"
            embedTitle = "Art nicht erkannt!"
        else:

            try:
                birdVisitCount = report['sightings'][0]['count']
                descriptionText = f"🐦 Besuche bisher: {str(birdVisitCount)}{description}"
                embedTitle = f"hatte Besuch von {birdName}"
            except:
                birdVisitCount = 1
                descriptionText = f"Erster Besuch von  {birdName}!\n\n🐦  1{description}"
                embedTitle = f"{birdName} erstmals gesichtet!"

        # Construct the status text
        status_text = f"#BirdBuddy {embedTitle}  {sightingTime} \n{descriptionText}\n#BirdsOfMastodon #Leverkusen #{birdName}"
        logging.info(status_text)

        post_status(imageUrls, status_text, birdName)
        if FLICKR:
            uploader.upload()

        if LOCL:
            local.move()            


# Async event loop to call check_bird_sighting periodically
async def main(interval_seconds):  
    while True:
        await check_bird_sighting()
        logging.debug(f'Wait {interval_seconds} seconds before trying again')
        await asyncio.sleep(interval_seconds) 

asyncio.run(main(SLEEP))  
