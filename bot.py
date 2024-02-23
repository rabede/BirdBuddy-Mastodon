import asyncio
import datetime
import requests
import os
from mastodon import Mastodon
from birdbuddy.client import BirdBuddy
from dotenv import load_dotenv

# Load environment variables or replace these with your actual credentials
load_dotenv()
ACCESS_TOKEN = os.getenv('MASTODON_ACCESS_TOKEN')
URL = os.getenv('MASTODON_API_BASE_URL')
EMAIL = os.getenv('BB_NAME')
PASS = os.getenv('BB_PASS')

# Initialize Mastodon client
mastodon = Mastodon(
    access_token=ACCESS_TOKEN,
    api_base_url=URL
)

# Initialize BirdBuddy client
bb = BirdBuddy(EMAIL, PASS)
bb.language_code = "de"

# Utility function to upload images to Mastodon and return media IDs
def upload_images_to_mastodon(image_urls):
    media_ids = []
    for url in image_urls:
        response = requests.get(url)
        media = mastodon.media_post(response.content, "image/png")
        media_ids.append(media['id'])
    return media_ids

# Example function to post a bird sighting on Mastodon
async def post_bird_sighting():
    getPostcards = await bb.new_postcards()

    # return if no new postcards are detected
    if len(getPostcards) == 0:
        print("No new postcards found.")
        return
    # after postcard sighting is confirmed use finishPostcard
    getSightings = await bb.sighting_from_postcard(getPostcards[0])
    getReport = getSightings.report
    # get report status and set type

    imageUrls = [item['contentUrl'] for item in getSightings.medias]
    videoUrls = [item['contentUrl'] for item in getSightings.video_media]

    # Determine if there is a video url and select appropriate emoji for embed
    if len(videoUrls) > 0:
        videoEmoji = 'Yes'
        hasVideo = True
    else:
        videoEmoji = 'No'
        hasVideo = False

    appendToDescription = f"\n🖼️ Images captured: {len(imageUrls)} \n📹 Video captured: {videoEmoji}"

    split_string = str(getReport).split("'")
    recognized_phrase = split_string[3]
    if recognized_phrase == "mystery" or recognized_phrase == "best_guess":
        birdIcon = ""
        descriptionText = f"🐦 Total visits: ??{appendToDescription}"
        embedTitle = "Unidentifiable bird spotted!"
        embedColor = 0xb5b5b6
    else:

        birdName = getReport['sightings'][0]['species']['name']
        birdIcon = getReport['sightings'][0]['species']['iconUrl']
        try:
            birdVisitCount = getReport['sightings'][0]['count']
            descriptionText = f"🐦 Total visits: {str(birdVisitCount)}{appendToDescription}"
            embedTitle = f"{birdName} spotted!"
            embedColor = 0x4dff4d
        except:
            birdVisitCount = 1
            descriptionText = f"This is your first time being visited by a {birdName}!\n\n🐦 Total Visits: 1{appendToDescription}"
            embedTitle = f"{birdName} unlocked!"
            embedColor = 0xf1c232    

    # Upload images and get their media IDs
    media_ids = upload_images_to_mastodon(imageUrls)
    
    # Construct the status text
    status_text = f"#BirdBuddy reports {embedTitle} on {datetime.datetime.now().strftime('%d.%m.%Y %H:%M')}"
    
    # Post status with media on Mastodon
    mastodon.status_post(status_text, media_ids=media_ids)

# Async event loop to call post_bird_sighting periodically
async def periodic_bird_sighting_posting(interval_seconds=3600):  
    while True:
        await post_bird_sighting()
        await asyncio.sleep(interval_seconds)  # Wait for the specified interval before posting again

# Run the event loop
asyncio.run(periodic_bird_sighting_posting(60))  