from discord.ext import commands
import discord
from config import star_threshold, STARBOARD_ID, GUILD_ID
from globe import COLOUR
import aiosqlite

STAR = "⭐"


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def get_emoji(reactions, emoji):
    """
    Get an reaction object via the emote string
    """
    for i in reactions:
        if str(i.emoji) == emoji:
            return i
    return None


class Cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        if not payload.guild_id or payload.guild_id != GUILD_ID:  # only listen in configured server
            return

        if str(payload.emoji) == STAR and payload.user_id != self.bot.user.id:  # if reacted with a star
            # try and get the message from the bot cache to reduce api calls, otherwise just fetch the message
            message = discord.utils.get(self.bot.cached_messages, id=payload.message_id)
            if not message:
                message = await self.bot.get_channel(payload.channel_id).fetch_message(payload.message_id)

            # get the reaction object from the emoji string
            reaction = get_emoji(message.reactions, str(payload.emoji))

            count = len([x for x in await reaction.users().flatten() if
                         not x.id == message.author.id])  # get the number of star reacts, excluding author

            # check if the message has already been starred
            cached = False
            async with aiosqlite.connect("data.db") as db:
                fetch = await db.execute("SELECT Destination FROM starmap WHERE Message=? AND Channel=?",
                                         (payload.message_id, payload.channel_id))
                fetch = await fetch.fetchone()

                if fetch:
                    star_id = fetch[0]
                    if star_id is None:
                        return
                    cached = True

            if count >= star_threshold and not cached:  # if reacts above threshold and not cached
                channel = self.bot.get_channel(STARBOARD_ID)

                author = message.author
                link = message.jump_url
                embed = discord.Embed(description=message.content, colour=COLOUR)
                embed.set_author(name=author.display_name, icon_url=author.display_avatar.url)
                embed.add_field(name="Details", value=f"[LINK]({link})")

                if message.attachments:  # insert image from message, if it exists
                    embed.set_image(url=message.attachments[0].url)
                msg = await channel.send(
                    f"{STAR}{count} | Message in {message.channel.mention} by {author.mention} was starred",
                    embed=embed)

                # either add the message to the database, otherwise increase the counter by 1
                async with aiosqlite.connect("data.db") as db:
                    await db.execute("INSERT INTO starmap (Message,Channel,Destination) VALUES (?,?,?)",
                                     (message.id, message.channel.id, msg.id))
                    await db.commit()

            elif cached:  # if the message is cached
                try:
                    msg = await self.bot.get_channel(STARBOARD_ID).fetch_message(star_id)
                    # increase the counter in the message by 1
                    text = "⭐" + str(count) + " " + " ".join(msg.content.split(" ")[1:])
                    await msg.edit(content=text)
                except discord.NotFound:  # if the starboard message no longer exists, delete the entry
                    async with aiosqlite.connect("data.db") as db:
                        await db.execute("DELETE FROM starmap WHERE Message=? AND Channel=?",
                                   (payload.message_id, payload.channel_id))
                        await db.commit()


def setup(bot):
    bot.add_cog(Cog(bot))
