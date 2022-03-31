import discord
from discord.ext import tasks, commands
import tweepy
from dotenv import load_dotenv
from os import getenv
import logging
from config import BLUE, TWITTER_CHANNEL
import datetime as dt
import aiosqlite

# Setup logging
logger = logging.getLogger()

# Load .env variables
load_dotenv()

#  OAuth setting
auth = tweepy.OAuth2AppHandler(getenv("CONSUMER_KEY"), getenv("CONSUMER_SECRET"))
api = tweepy.API(auth, wait_on_rate_limit=True)
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
            try:
                TweetID = info.id
                ScreenName = info.user
                CreatedTime = info.created_at
                TweetText = info.full_text
                Media = info.extended_entities
                Pic = Media["media"][0]["media_url_https"]
            except:
                Pic = discord.Embed.Empty
                pass
            for k, v in html_escape_table.items():
                if v in TweetText:
                    TweetText = TweetText.replace(v, k)
            PfpLink = ScreenName.profile_image_url_https
            channel = self.bot.get_channel(TWITTER_CHANNEL)
            async with aiosqlite.connect("data.db") as db:
                LatestTweets = await db.execute("SELECT TweetID FROM Tweets WHERE TweetID=?", (TweetID,))
                LatestTweets = await LatestTweets.fetchall()
                print(LatestTweets)
            if LatestTweets:
                print("Skipped an ID!")
                continue
            else:
                async with aiosqlite.connect("data.db") as db:
                    data = (TweetID,)
                    await db.execute("INSERT INTO Tweets(TweetID) VALUES (?)", data)
                    await db.commit()
                print("Added Tweet ID to list")
                em = discord.Embed(description=f"{TweetText}", colour=BLUE)
                em.set_author(name=f"{ScreenName.name}", url=f"https://twitter.com/{userID}/status/{TweetID}",
                              icon_url=PfpLink)
                em.set_footer(text="‎",
                              icon_url="https://abs.twimg.com/icons/apple-touch-icon-192x192.png")
                em.set_image(url=Pic)
                em.timestamp = dt.datetime.utcnow()
                await channel.send(
                    f"@{userID} posted a tweet, check it out: https://twitter.com/{userID}/status/{TweetID}", embed=em)


def setup(bot):
    bot.add_cog(Twitter(bot))
