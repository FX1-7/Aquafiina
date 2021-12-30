import discord
import os
from discord.ext import commands
import asyncio
from asyncio import sleep
import re
from config import GREEN, RED, MUTED
import datetime as dt
from typing import Union

class moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, user: discord.Member, reason=None):
        """
            Kicks a user from the server
        """
        await ctx.guild.kick(user, reason=reason)
        await ctx.message.delete(delay=5)

        em = discord.Embed(colour=RED, title="User has been kicked!",
                           description=f"{user.mention} has been kicked from the server by {ctx.author.mention}")
        em.set_footer(icon_url=ctx.guild.icon_url, text=ctx.guild.name)
        em.set_thumbnail(url=ctx.guild.icon_url)
        em.timestamp = dt.datetime.utcnow()
        await ctx.send(embed=em)

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, user: Union[discord.Member, int], time, *, reason="Not set"):
        """
               Ban a user for a period of time
               Time must be a number followed by either m for minutes, h for hours or d for days or s for seconds
        """

        rex = re.match(r"(\d+) ?([smdh])", time.lower())
        if not rex:  # if no match
            raise commands.BadArgument

        value = int(rex.group(1))
        unit = rex.group(2)
        if unit == "m":
            value = value * 60  # convert to seconds
            unit = "minutes"
        elif unit == "h":
            value = value * 60 * 60  # convert to seconds
            unit = "hours"
        elif unit == "d":
            value = value * 60 * 60 * 24  # convert to seconds
            unit = "days"
        elif unit == "s":
            value = value
            unit = "seconds"

        if isinstance(user, int):
            person = self.bot.get_user(user)
            await ctx.guild.ban(person, reason=reason)
            await ctx.message.delete(delay=5)
            em = discord.Embed(colour=RED, title="User has been kicked!",
                               description=f"{person.mention} has been banned from the server by {ctx.author.mention}"
                                           f"for **'{reason}'** for {rex.group(1)} {unit}!")
            em.set_footer(icon_url=ctx.guild.icon_url, text=ctx.guild.name)
            em.set_thumbnail(url=ctx.guild.icon_url)
            em.timestamp = dt.datetime.utcnow()
            await ctx.send(embed=em)
            if value == 0:
                await ctx.guild.ban(person, reason=reason)
            else:
                await sleep(value) # wait for the specified time
                await ctx.guild.unban(person, reason="Timed unban") # unban
        else:
            await ctx.guild.ban(user, reason=reason)
            await ctx.message.delete(delay=5)

            em = discord.Embed(colour=RED, title="User has been kicked!",
                           description=f"{user.mention} has been banned from the server by {ctx.author.mention}"
                                       f"for **'{reason}'** for {rex.group(1)} {unit}!")
            em.set_footer(icon_url=ctx.guild.icon_url, text=ctx.guild.name)
            em.set_thumbnail(url=ctx.guild.icon_url)
            em.timestamp = dt.datetime.utcnow()
            await ctx.send(embed=em)

            if value == 0:
                await ctx.guild.ban(user, reason=reason)
            else:
                await sleep(value)  # wait for the specified time
                await ctx.guild.unban(user, reason="Timed unban")  # unban

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, member: discord.User):
        """
        Unbans a member
        """
        await ctx.guild.unban(member)
        em = discord.Embed(colour=GREEN, title="Success",
                           description=f"{member.name} is now unbanned!")
        em.set_footer(icon_url=ctx.guild.icon_url, text=ctx.guild.name)
        em.set_thumbnail(url=ctx.guild.icon_url)
        em.timestamp = dt.datetime.utcnow()
        await ctx.send(embed=em)

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def unmute(self, ctx, member: discord.Member):
        """
            Unmutes a member
        """

        role = ctx.guild.get_role(MUTED)

        if role not in member.roles:
            em = discord.Embed(colour=RED, title="⛔ Error!",
                               description=f"{member.mention} is not muted!")
            em.set_footer(icon_url=ctx.guild.icon_url, text=ctx.guild.name)
            em.set_thumbnail(url=ctx.guild.icon_url)
            em.timestamp = dt.datetime.utcnow()
            await ctx.send(embed=em)
        else:
            await member.remove_roles(role)
            em = discord.Embed(colour=GREEN, title="Success",
                               description=f"{member.mention} is now unmuted!")
            em.set_footer(icon_url=ctx.guild.icon_url, text=ctx.guild.name)
            em.set_thumbnail(url=ctx.guild.icon_url)
            em.timestamp = dt.datetime.utcnow()
            await ctx.send(embed=em)

    @commands.command(aliases=["tmute"])
    @commands.has_permissions(ban_members=True)
    async def mute(self, ctx, member: discord.Member, *, time):
        """
        Mute a user for a period of time
        Time must be a number followed by either m for minutes, h for hours or d for day or s for seconds
        """

        rex = re.match(r"(\d+) ?([smdh])", time.lower())
        if not rex:  # if no match
            raise commands.BadArgument

        value = int(rex.group(1))
        unit = rex.group(2)
        if unit == "m":
            value = value * 60  # convert to seconds
            unit = "minutes"
        elif unit == "h":
            value = value * 60 * 60  # convert to seconds
            unit = "hours"
        elif unit == "d":
            value = value * 60 * 60 * 24  # convert to seconds
            unit = "days"
        elif unit == "s":
            value = value
            unit = "seconds"
        role = ctx.guild.get_role(MUTED)
        await member.add_roles(role)
        em = discord.Embed(colour=RED, title="User has been muted!",
                           description=f"🔇 {ctx.author.mention} muted {member.mention} for {rex.group(1)} {unit}")
        em.set_footer(icon_url=ctx.guild.icon_url, text=ctx.guild.name)
        em.set_thumbnail(url=ctx.guild.icon_url)
        em.timestamp = dt.datetime.utcnow()
        await ctx.send(embed=em)

        if value == 0:
            return
        else:
            await sleep(value)  # wait for the specified time
            await member.remove_roles(role)  # unmute

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def purge(self, ctx, amount: int):
        """
        Purges messages.
        """
        await ctx.channel.purge(limit=amount+1)
        await ctx.send(f'{amount} Messages cleared by {ctx.author.mention}', delete_after=6)


def setup(bot):
    bot.add_cog(moderation(bot))
