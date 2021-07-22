import discord
import json
from discord.ext import commands
from config import GREEN


class Verification(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.member.bot:
            pass
        else:
            with open('./verification.json') as react_file:
                data = json.load(react_file)
                for x in data:
                    if x['emoji'] == payload.emoji.name:
                        role = discord.utils.get(self.bot.get_guild(
                            payload.guild_id).roles, id=x['role_id'])
                        await payload.member.add_roles(role)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):

        with open('./verification.json') as react_file:
            data = json.load(react_file)
            for x in data:
                if x['emoji'] == payload.emoji.name:
                    role = discord.utils.get(self.bot.get_guild(
                        payload.guild_id).roles, id=x['role_id'])

                    await self.bot.get_guild(payload.guild_id).get_member(payload.user_id).remove_roles(role)

    @commands.command()
    @commands.is_owner()
    async def verification(self, ctx, emoji, role: discord.Role):

        emb = discord.Embed(colour=GREEN, title="How to verify",
                            description="In order to verify please click the 👍 emoji below!\n\n"
                                        "**Please make sure you've read the rules above before entering the server**")
        msg = await ctx.channel.send(embed=emb)
        await msg.add_reaction(emoji)

        with open('./verification.json') as json_file:
            data = json.load(json_file)

            new_react_role = {'role_name': role.name,
                              'role_id': role.id,
                              'emoji': emoji,
                              'message_id': msg.id}

            data.append(new_react_role)

        with open('./verification.json', 'w') as f:
            json.dump(data, f, indent=4)


def setup(bot):
    bot.add_cog(Verification(bot))
