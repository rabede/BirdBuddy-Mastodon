#!/usr/bin/python3
import asyncio
import datetime
import requests
import os
import logging
from mastodon import Mastodon
from birdbuddy.client import BirdBuddy
from dotenv import load_dotenv

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

logging.basicConfig(level=logging.DEBUG, filename=FILENAME, format='%(asctime)s - %(levelname)s - %(name)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

last_postcard_id = ''


# Initialize Mastodon client
mastodon = Mastodon(
    access_token=ACCESS_TOKEN,
    api_base_url=URL
)
logging.info(f'{URL} initialized')

# Initialize BirdBuddy client
bb = BirdBuddy(EMAIL, PASS)
bb.language_code = "de"

# Utility function to upload images to Mastodon and return media IDs
def upload_images_to_mastodon(image_urls, birdName):
    description = f'{birdName} im Futteräuschen'
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
    logging.info('Checking new sightings')
    try:
        postcards = await bb.new_postcards()
        # return if no new postcards are detected
        if len(postcards) == 0 or postcards[0]['id'] == last_postcard_id:
            logging.debug('No new postcards')
            return
    except Exception as e:
        logging.debug(e)
        return
    
    last_postcard_id = postcards[0]['id'] 
    logging.debug(postcards)

    # after postcard sighting is confirmed use finishPostcard
    try:
        sighting = await bb.sighting_from_postcard(postcards[0])
    except Exception as e:
        logging.debug(e)
        return
    
    report = sighting.report
    logging.debug(sighting)
    logging.debug(report)
    
    imageUrls = [item['contentUrl'] for item in sighting.medias]
    imageCount = len(imageUrls)
    logging.debug(imageUrls)
    # Make sure, Mastodons file limit won't be exceeded
    if imageCount > MAX_FILES:
        imageUrls = imageUrls[:MAX_FILES]

    videoUrls = [item['contentUrl'] for item in sighting.video_media]
    logging.debug(videoUrls)
    # Determine if there is a video url and select appropriate emoji for embed
    if len(videoUrls) > 0:
        videoEmoji = f'{videoUrls[0]}'
        hasVideo = True 
    else:
        videoEmoji = 'No'
        hasVideo = False

    description = f"\n🖼️ Images captured: {imageCount} \n📹 Video captured: {videoEmoji}"

    split_string = str(report).split("'")
    recognized_phrase = split_string[3]
    if recognized_phrase == "mystery" or recognized_phrase == "best_guess":
        birdIcon = ""
        descriptionText = f"🐦 Total visits: ??{description}"
        embedTitle = "Unidentifiable bird spotted!"
        embedColor = 0xb5b5b6
    else:

        birdName = report['sightings'][0]['species']['name']
        birdIcon = report['sightings'][0]['species']['iconUrl']
        try:
            birdVisitCount = report['sightings'][0]['count']
            descriptionText = f"🐦 Total visits: {str(birdVisitCount)}{description}"
            embedTitle = f"spotted a {birdName}"
            embedColor = 0x4dff4d
        except:
            birdVisitCount = 1
            descriptionText = f"This is my first time being visited by a {birdName}!\n\n🐦 Total Visits: 1{description}"
            embedTitle = f"{birdName} unlocked!"
            embedColor = 0xf1c232    

    # Construct the status text
    status_text = f"#BirdBuddy {embedTitle} on {datetime.datetime.now().strftime('%d.%m.%Y %H:%M')} \n{descriptionText}"
    logging.info(status_text)

    post_status(imageUrls, status_text, birdName)


# Async event loop to call check_bird_sighting periodically
async def main(interval_seconds):  
    while True:
        await check_bird_sighting()
        logging.debug(f'Wait {interval_seconds} seconds before trying again')
        await asyncio.sleep(interval_seconds) 

# Run the event loop
asyncio.run(main(SLEEP))  
