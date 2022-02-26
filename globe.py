import discord
from discord.ext import commands
import config

# Set config colour based off user set hex code
COLOUR = discord.Colour(value=config.COLOUR)
