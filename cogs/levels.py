from discord.ext import commands
import discord
from random import randint
import aiosqlite
from copy import deepcopy
import datetime as dt
from globe import COLOUR, make_bar, get_guild

# values to use to calculate xp/levels
# completely arbitrary - just something that creates a decent difficulty curve
exponent = (1893.0 / 4500.0)
coef = 0.31


def xp_to_level(xp):
    return int(coef * xp ** exponent)


def root(base, value):
    """
    Reverse of **
    a ** b = c   =>    root(b, c) = a
    """
    return value ** (1. / base)


def level_to_xp(level):
    return int(root(exponent, level / coef))


class Levels(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, ctx: discord.Message):
        if ctx.author.bot or ctx.guild is None:  # bots dont get xp or in DM
            return
        elif randint(0, 2) > 0:  # 2/3 chance this doesn't run
            return

        user = ctx.author
        id = user.id

        async with aiosqlite.connect("data.db") as db:
            fetch = await db.execute("SELECT ID,Level,XP,xp_time FROM levels WHERE ID=?", (id,))
            fetch = deepcopy(await fetch.fetchone())

            if not fetch:  # if user has no entry
                data = (id, 1, 0, "1970-01-01T00:00:00.00")  # template data
                # insert entry into db
                await db.execute("INSERT INTO levels (ID, Level, XP, xp_time) VALUES (?,?,?,?)", data)
                fetch = data

            fetch = list(fetch)
            now = dt.datetime.utcnow()
            last_xp = dt.datetime.strptime(fetch[3], "%Y-%m-%dT%H:%M:%S.%f")  # get the time the xp was last given

            if now >= last_xp + dt.timedelta(minutes=2):  # if its 2 min since user last got xp
                fetch[2] += randint(15, 25)  # give 15-25 xp

                if fetch[2] >= level_to_xp(fetch[1]):  # if enough xp to level up
                    fetch[2] -= level_to_xp(fetch[1])  # "purchase" a level using the xp
                    fetch[1] += 1  # add 1 level

                # level, xp, xp_time, ID
                # we have added XP, so save timestamp
                data = (fetch[1], fetch[2], now.isoformat(), fetch[0])
                await db.execute("UPDATE levels SET Level=?,XP=?,xp_time=? WHERE ID=?", data)  # insert data
            await db.commit()  # save changes

    @commands.command(aliases=["profile", "lvl"])
    async def level(self, ctx, member: discord.Member = None):
        """
        Shows a user's level, XP and progress towards the next level
        If no user is specified, your info will be shown
        """
        if member is None:
            member = ctx.author

        async with aiosqlite.connect("data.db") as db:  # get XP and Level
            fetch = await db.execute("SELECT XP, Level FROM levels WHERE ID=?", (member.id,))
            fetch = deepcopy(await fetch.fetchone())

        if not fetch:  # no entry for that user
            fetch = [0, 1]  # default 0xp level 1

        embed = discord.Embed(colour=COLOUR)
        embed.set_author(name=member.display_name, icon_url=member.display_avatar.url)
        embed.add_field(name="Level", value=fetch[1])
        bar = make_bar(fetch[0], level_to_xp(fetch[1]), 15)
        embed.add_field(name="XP", value=bar + f" {fetch[0]}/{level_to_xp(fetch[1])}")

        await ctx.send(embed=embed)

    @commands.command(aliases=["top", "top10", "lb"])
    async def leaderboard(self, ctx):
        """
        Shows the top 10 users with the most XP/Levels
        """

        async with aiosqlite.connect("data.db") as db:
            # get all users sorted by level then by xp
            fetch = await db.execute("SELECT ID, Level, XP FROM levels ORDER BY Level DESC,XP DESC")
            fetch = await fetch.fetchall()
        fetch = deepcopy(list(fetch))

        if not fetch:  # if no db entries | probably wont happen but lets not risk anything
            await ctx.send("No users have any xp currently")
            return

        # make sure users are in guild
        in_guild = []
        for member in fetch:
            if get_guild(self.bot).get_member(member[0]) is not None:  # if user object instead of None
                in_guild.append(member)
        top = in_guild[:10]  # crop to 10 entries max

        # create markdown codeblock
        line = f"{get_guild(self.bot).name} Leaderboard"
        output = f"```md\n{line}\n{len(line) * '='}\n\n"

        # add the actual leaderboard
        for i in range(len(top)):
            user = top[i]
            name = get_guild(self.bot).get_member(user[0]).name
            output += f"{i + 1}. {name} < Level {user[1]} {user[2]} xp >\n"
        output += "```"
        await ctx.send(output)

    @commands.command(aliases=["xptotal", "allxp", "xpall"])
    async def totalxp(self, ctx, member: discord.Member = None):
        """
        Show all the XP you have gotten over time
        """

        if not member:
            member = ctx.author

        async with aiosqlite.connect("data.db") as db:
            fetch = await db.execute("SELECT Level, XP from levels WHERE ID=?", (member.id,))
            fetch = await fetch.fetchone()

        total_xp = 0  # in case the user isnt in the db, set a default
        if fetch:
            level = int(fetch[0])
            xp = int(fetch[1])

            for i in range(level):  # each level has its own xp that needs to be accounted for
                total_xp += level_to_xp(i)
            total_xp += xp

        embed = discord.Embed(colour=COLOUR, description=f"Total XP: **{total_xp}**")
        embed.set_author(name=member.display_name, icon_url=member.display_avatar.url)

        await ctx.send(embed=embed)

    @commands.command(aliases=["pos"])
    async def position(self, ctx, *, member: discord.Member = None):
        """
        Shows the leaderboard but centered around either you or a mentioned user
        """
        if member is None:
            member = ctx.author

        async with aiosqlite.connect("data.db") as db:
            # get all users sorted by level then by xp
            fetch = await db.execute("SELECT ID, Level, XP FROM levels ORDER BY Level DESC,XP DESC")
            fetch = await fetch.fetchall()
        fetch = deepcopy(list(fetch))

        if not fetch:  # if no db entries | probably wont happen but lets not risk anything
            await ctx.send("No users have any xp currently")
            return

        # make sure users are in guild
        in_guild = []
        user_index = None
        for user in fetch:
            if get_guild(self.bot).get_member(user[0]) is not None:  # if user object instead of None
                in_guild.append(user)
            if user[0] == member.id:
                user_index = len(in_guild) - 1

        if user_index is None:  # if user doesnt have an entry
            data = (member.id, 1, 0)  # template data
            in_guild.append(data)
            user_index = len(in_guild) - 1

        # get index of ends of list cropped to the user
        start = user_index - 4
        end = user_index + 5
        # make sure the start and end are within bounds
        if start < 0:
            start = 0
            end = 9
        if end >= len(in_guild):
            end = len(in_guild) - 1

        top = in_guild[start:end+1]  # not actually top but i copied the code so now it is :p

        # create markdown codeblock
        line = f"{get_guild(self.bot).name} Leaderboard"
        output = f"```md\n{line}\n{len(line) * '='}\n\n"

        # add the actual leaderboard
        for i in range(len(top)):
            user = top[i]
            name = get_guild(self.bot).get_member(user[0]).name
            output += f"{i + 1 + start}. {name} < Level {user[1]} {user[2]} xp >\n"
        output += "```"
        await ctx.send(output)


def setup(bot):
    bot.add_cog(Levels(bot))
