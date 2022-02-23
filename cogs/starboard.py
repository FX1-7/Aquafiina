import discord
from discord.utils import get
from discord.ext import commands
from config import MAIN
import datetime as dt

class Starboard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.emoji.name == "⭐":
            starboard = self.bot.get_channel(867007259200716800)
            channel = self.bot.get_channel(payload.channel_id)
            message = await channel.fetch_message(payload.message_id)
            reaction = get(message.reactions, emoji=payload.emoji.name)
            if reaction and reaction.count > 6:
                print(reaction, reaction.count)
                em = discord.Embed(colour=MAIN,
                                   description=f"{message.content}")
                em.set_author(name=message.author.display_name, icon_url=message.author.avatar.url)
                em.timestamp = dt.datetime.utcnow()
                await starboard.send(f"A message in <#{channel.id}> was starred!", embed=em)
            else:
                return

def setup(bot):
    bot.add_cog(Starboard(bot))