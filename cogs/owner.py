import discord
from discord.ext import commands
import ast
import copy
from utils.utils import *
from config import *
import re
import datetime as dt
from bson.objectid import ObjectId
import psutil
import asyncio
from typing import Union


def bytes2human(n, f="%(value).1f%(symbol)s"):
    symbols = ('B', 'K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y')
    prefix = {}
    for i, s in enumerate(symbols[1:]):
        prefix[s] = 1 << (i + 1) * 10
    for symbol in reversed(symbols[1:]):
        if n >= prefix[symbol]:
            value = float(n) / prefix[symbol]
            return f % locals()
    return f % dict(symbol=symbols[0], value=n)


def as_percent(a, b):
    return str(round(((a / b) * 100), 1)) + "%"


def insert_returns(body):
    # insert return stmt if the last expression is a expression statement
    if isinstance(body[-1], ast.Expr):
        body[-1] = ast.Return(body[-1].value)
        ast.fix_missing_locations(body[-1])

    # for if statements, we insert returns into the body and the orelse
    if isinstance(body[-1], ast.If):
        insert_returns(body[-1].body)
        insert_returns(body[-1].orelse)

    # for with blocks, again we insert returns into the body
    if isinstance(body[-1], ast.With):
        insert_returns(body[-1].body)


class Owner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.is_owner()
    async def reload(self, ctx, cog):
        """
        Reloads a cog and updates changes to it
        """
        try:
            self.bot.reload_extension("cogs." + cog)
            self.bot.dispatch("load", cog)
        except Exception as error:
            await ctx.send(f"```py\n{error}```")
            return
        await ctx.send("✅")
        print(f"------------Reloaded {cog}------------")

    @commands.command(aliases=["runas"])
    @commands.is_owner()
    async def invokeas(self, ctx, member: discord.Member, *, command):
        """
        Run a command as if it was sent by someone else
        """
        message: discord.Message = copy.copy(ctx.message)
        message.author = member
        message.content = ctx.prefix + command
        context = await self.bot.get_context(message, cls=type(ctx))

        if context.command is None:
            await ctx.send(f"🖥️ Command {context.invoked_with} not found")
        else:
            await context.command.invoke(context)

    @commands.command()
    @commands.is_owner()
    async def run(self, ctx, *, code: str):
        """
        Run python stuff
        """
        fn_name = "_eval_expr"

        code = code.strip("` ")  # get rid of whitespace and code blocks
        if code.startswith("py\n"):
            code = code[3:]

        try:
            # add a layer of indentation
            cmd = "\n".join(f"    {i}" for i in code.splitlines())

            # wrap in async def body
            body = f"async def {fn_name}():\n{cmd}"

            parsed = ast.parse(body)
            body = parsed.body[0].body

            insert_returns(body)

            env = {
                'bot': self.bot,
                'ctx': ctx,
                'message': ctx.message,
                'server': ctx.message.guild,
                'channel': ctx.message.channel,
                'author': ctx.message.author,
                'commands': commands,
                'discord': discord,
                'guild': ctx.message.guild,
            }
            env.update(globals())

            exec(compile(parsed, filename="<ast>", mode="exec"), env)

            result = (await eval(f"{fn_name}()", env))

            out = ">>> " + code + "\n"
            output = "```py\n{}\n\n{}```".format(out, result)

            if len(output) > 2000:
                await ctx.send("The output is too long?")
            else:
                await ctx.send(output.format(result))
        except Exception as e:
            await ctx.send("```py\n>>> {}\n\n\n{}```".format(code, e))

    @commands.command(aliases=["osem"])
    @commands.is_owner()
    async def oneshot_embed(self, ctx, channel: discord.TextChannel, title, *, description):
        """
        Quick embed t.osem "<title>" <description>(*)
        """

        title = str.strip(title)
        embed = discord.Embed(title=title, description=description, colour=GREEN)
        embed.set_footer(icon_url=ctx.guild.icon.url, text=ctx.guild.name)
        embed.set_thumbnail(url=ctx.guild.icon.url)
        embed.timestamp = dt.datetime.utcnow()
        await channel.send(embed=embed)

    @commands.command(aliases=["raise"])
    @commands.is_owner()
    async def _raise(self, ctx):
        """
        Literally just raise an exception to test exception logging
        """
        raise Exception

    @commands.command()
    @commands.is_owner()
    async def reactionadd(self, ctx, emoji):
        """
         Adds a reaction to a message
        """

def setup(bot):
    bot.add_cog(Owner(bot))