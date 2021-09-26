import tweepy
import logging
import os
LOG_ID = 866985685470019604
TWITTER_CHANNEL = 866987655770013696
PREFIX = "!"
RED = 0xE0495F
YELLOW = 0xFCE9AF
GREEN = 0xB1D587
MAIN = 0x83B942
PERMS = 8
MOD_ROLE = 866970453456846888, 866985346116616202
MUTED = 867022751255887873
BLUE = 0x1DA1F2

logger = logging.getLogger()

def create_api():
    consumer_key = os.getenv("CONSUMER_KEY")
    consumer_secret = os.getenv("CONSUMER_SECRET")
    access_token = os.getenv("ACCESS_TOKEN")
    access_token_secret = os.getenv("ACCESS_TOKEN_SECRET")

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth, wait_on_rate_limit=True,
        wait_on_rate_limit_notify=True)
    try:
        api.verify_credentials()
    except Exception as e:
        logger.error("Error creating API", exc_info=True)
        raise e
    logger.info("API created")
    return api