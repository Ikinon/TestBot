import datetime

from discord.ext import commands
import discord
from Cogs import Converters


class MuteCommand(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.time = datetime.datetime.today().strftime('%d/%m/%Y')

    @commands.command()
    @commands.has_permissions(kick_members=True)
    @commands.guild_only()
    async def mute(self, ctx, target: discord.Member, reason: Converters.ActionReason = None):
        """Mutes a user
        Adds the muted role to a user, or creates one
        Args:
            <target> <reason:optional>
        Example:
            ?mute Nothing "because nothing"
        """
        embedMute = discord.Embed(title=f"{ctx.command}",
                                  description=f"{target} has been muted\n"
                                  f"**The user could not be muted in voice**", colour=0x24FF00)
        embed = discord.Embed(title=f"{ctx.command}",
                              description=f"{target} has been muted", colour=0x24FF00)
        embed.set_footer(text=f"Requested by {ctx.author} •  {self.time} ")
        embedMute.set_footer(text=f"Requested by {ctx.author} •  {self.time} ")
        if target.id == ctx.author.id:
            await ctx.send(f"Don't be so harsh on yourself {ctx.author.name} :heart:"
                           f"\n*I'm not going to {ctx.command} you*")
        if target.id == self.bot.user.id:
            await ctx.send("I'm not going to mute myself-!")
        else:
            try:
                a = discord.utils.get(ctx.guild.roles, name="Muted")
                await target.add_roles(a, reason=reason)
                try:
                    await target.edit(mute=True, reason=reason)
                except:
                    await ctx.send(embed=embedMute)
                else:
                    await ctx.send(embed=embed)
            except AttributeError:
                await ctx.send("Muted role not found, creating role")
                txt = f"Creating muted role for Mute command, initiated by {ctx.author} with {ctx.command}"
                role = await ctx.guild.create_role(name="Muted", reason=txt,
                                                   permissions=discord.Permissions(permissions=0))
                for channel in ctx.guild.channels:
                    if type(channel) == discord.channel.TextChannel:
                        await channel.set_permissions(role, send_messages=False, reason=txt)
                    if type(channel) == discord.channel.VoiceChannel:
                        await channel.set_permissions(role, connect=False, reason=txt)
                    else:
                        pass
                await target.add_roles(role, reason=reason)
                try:
                    await target.edit(mute=True, reason=reason)
                except:
                    await ctx.send(embed=embedMute)
                else:
                    await ctx.send(embed=embed)

    @mute.error
    async def mute_error(self, ctx, error):
        if isinstance(error, discord.ext.commands.errors.CommandInvokeError):
            if "Muted" in ctx.guild.roles:
                await ctx.send(":warning: I don't have permission to do that!\n"
                               "Please Check the Manage Roles permission")
            else:
                await ctx.send(":warning: I don't have permission to do that!\n"
                               "Please Check the Manage Roles and Manage Channels permissions")
        if isinstance(error, discord.ext.commands.errors.BadArgument):
            await ctx.send(f":warning: {error}")
        else:
            await ctx.send(f":warning: Unexpected Error: {error}")


def setup(bot):
    bot.add_cog(MuteCommand(bot))
