
# BirdBuddy Mastodon Companion

This is a simple copy of [DenchyRS's Birdini](https://github.com/DenchyRS/Birdini), where I replaced the Discord stuff with Mastodon.

As Birdini, this script depends on [jhansche's pybirdbuddy](https://github.com/jhansche/pybirdbuddy)

# Setup Guide

1. Clone the repository

    `git clone https://github.com/rabede/BirdBuddy2Mastodon.git`

2. CD into new directory, create and activate your python environment

    `cd BirdBuddy2Mastodon`

    `python -m venv .envMasto`

    `source .envMasto/bin/activate`

3. Install dependencies

    `python -m pip install -r requirements.txt`

4. Rename `.env template.txt` to `.env` and insert your credentials (Make sure to add `.env` to `.gitignore` before any pushing!)   

5. Run and test locallally

    `python birdbuddy2mastodon.py`

6. Install as daemon on your RasperryPi or other    

    use birdbuddy2mastodon.service as a template, replace USER with your preferences and pathes if necessary

# Environment Variables

`BB_NAME`

This is the email used to log into your BirdBuddy account. Note that this has to be an email/password login and can not be an integration like login with Google. A good work around for this issue (if your primary account is using such type of login). Is to create a new account using an email and then inviting them to be a guest at your feeder.

`BB_PASS`

This is the password used to log into your BirdBuddy account.

`MASTODON_ACCESS_TOKEN`

Access token for your Mastodon App 

`MASTODON_API_BASE_URL`

URL of your Mastodon Instance e.g. 'https://mastodon.social' 

`MASTODON_VISIBILITY`

Set the visibility of your post  ('direct', 'private', 'unlisted', 'public')

`MASTODON_MAX_FILES`

Maximum number of files Mastodon accepts appended to a post (currently 4)

`SECONDS_TO_SLEEP` 

Number of seconds between checks for new postcards

`LOGFILE`

Name of logfile (leave empty for console log)
