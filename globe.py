import discord
from discord.ext import commands
import config

# Set config colour based off user set hex code
COLOUR = discord.Colour(value=config.COLOUR)

def get_guild(bot: commands.Bot):
    return bot.get_guild(config.GUILD_ID)


def make_bar(num, den, size):
    """
    Create a progress bar
    den (denominator) is the 100% mark - max value of the chart
    num (numerator) is the progress that has been made
    size is how many characters the graph should be
    """
    progress = int(num / den * size)
    remain = int(size - progress)
    return "{}{}".format("▰" * progress, "▱" * remain)
