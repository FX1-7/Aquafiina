import discord
from discord.ext import tasks, commands
import tweepy
from dotenv import load_dotenv
from os import getenv
import logging
from config import BLUE, TWITTER_CHANNEL
import datetime as dt

# Setup logging
logger = logging.getLogger()

# Load .env variables
load_dotenv()

#  OAuth setting
auth = tweepy.AppAuthHandler(getenv("CONSUMER_KEY"), getenv("CONSUMER_SECRET"))
api = tweepy.API(auth, wait_on_rate_limit=True,
                 wait_on_rate_limit_notify=True)
userID = "AquafiinaVT"

# Declaration and Initilization

LatestTweets = []
html_escape_table = {
        "&": "&amp;",
        '"': "&quot;",
        "'": "&apos;",
        ">": "&gt;",
        "<": "&lt;",
        "→": "&rarr;",
        "↑": "&uarr;",
        "←": "&larr;",
        "↓": "&darr;",
        "↔": "&harr;",
        "£": "&pound;",
        "ö": "&ouml;",
        }


class Twitter(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.twitter.start()
        print(self.bot)

    @tasks.loop(seconds=960)
    async def twitter(self):
        await self.bot.wait_until_ready()
        tweets = api.user_timeline(screen_name=userID, count=200, include_rts=False, tweet_mode="extended",
                                   exclude_replies=True)
        for info in tweets[:10]:
            TweetID = info.id
            ScreenName = info.user
            TweetText = info.full_text
            for k, v in html_escape_table.items():
                if v in TweetText:
                    TweetText = TweetText.replace(v, k)
            PfpLink = ScreenName.profile_image_url_https
            channel = self.bot.get_channel(TWITTER_CHANNEL)
            if TweetID in LatestTweets:
                print("Skipped an ID!")
                return
            else:
                LatestTweets.append(TweetID)
                print("Added Tweet ID to list")
                em = discord.Embed(description=f"{TweetText}", colour=BLUE)
                em.set_author(name=f"{ScreenName.name}", url=f"https://twitter.com/{userID}/status/{TweetID}", icon_url=PfpLink)
                em.set_footer(icon_url="https://abs.twimg.com/icons/apple-touch-icon-192x192.png")
                em.timestamp = dt.datetime.utcnow()
                await channel.send(embed=em)



def setup(bot):
    bot.add_cog(Twitter(bot))
