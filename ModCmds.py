import datetime

import asyncio
import discord
from discord.ext import commands


class ModCmds(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.time = datetime.datetime.today().strftime('%d/%m/%Y')

    class ActionReason(commands.Converter):
        async def convert(self, ctx, argument):
            ret = f'{ctx.author} (ID: {ctx.author.id}): {argument}'

            if len(ret) > 512:
                reason_max = 512 - len(ret) - len(argument)
                raise commands.BadArgument(f'reason is too long ({len(argument)}/{reason_max})')
            return ret

    class BanDays(commands.Converter):
        async def convert(self, ctx, argument):
            ret = f'{argument}'
            try:
                ret = int(ret)
            except ValueError:
                return 'Error: delete_message_days needs a number from 1,7'
            if ret >= 7:
                return 'delete_message_days needs a value from 0,7.\nDefault is 0 to delete none'
            elif ret:
                return ret

    @commands.command()
    @commands.has_permissions(kick_members=True)
    @commands.guild_only()
    async def kick(self, ctx, user: discord.Member, reason: ActionReason = None):
        """Kicks a member from the server.
        In order for this to work, the bot must have Kick Member permissions.
        To use this command you must have Kick Members permission.
        Args:
            <user> <reason:optional>
        Example:
            ?kick Nothing 'because nothing'
        """

        if user.id == ctx.author.id:
            await ctx.send(f"Don't be so harsh on yourself {ctx.author.name} :heart:")
            user = None
        try:

            if reason is None:
                reasona = f'Action done by {ctx.author} (ID: {ctx.author.id})'
                await user.kick(reason=reasona)
            elif reason:
                await user.kick(reason=reason)
                await ctx.send(f":warning: Error: {e}")
            embed = discord.Embed(title=f"{ctx.command}",
                                  description=f"{user} has been kicked from the server!\nReason: {reason}",
                                  colour=0x24FF00)
            embed.set_footer(text=f"Requested by {ctx.author} • {self.time} ")
            await ctx.send(embed=embed)
            await user.send(f"You have been **kicked** from"
                            f" **{ctx.guild}**\nReason: {reason}\nResponsible: {ctx.author}.")
        except discord.Forbidden:
            if user.id == self.bot.user.id:
                await ctx.send(f"T-that's meannnnnnn :( I can't {ctx.command}"
                               f" myself and I hope you don't want to either :(")
            else:
                await ctx.send(":warning: Missing kick permissions")
        except discord.NotFound:
            await ctx.send(":warning: User not found")
        except Exception as e:
            await ctx.send(f":warning: Error: {e}")

    @commands.command()
    @commands.has_permissions(ban_members=True)
    @commands.guild_only()
    async def ban(self, ctx, user: discord.Member, reason: ActionReason = None, delete_message_days: BanDays = 0):
        """Bans a member from the server.
        In order for this to work, the bot must have Ban Member permissions.
        To use this command you must have Ban Members permission.
        Args:
            <user> <reason:optional> <number of days worth of messages to delete from the user:optional>
        Example:
            ?ban Nothing 'Because Nothing' 2"""
        if user.id == ctx.author.id:
            await ctx.send(f"Don't be so harsh on yourself {ctx.author.name} :heart:")
            user = None
        try:
            if reason is None:
                await user.ban(reason=reason)
            elif reason:
                if delete_message_days == 0:
                    await user.ban(reason=reason)
                elif delete_message_days:
                    await user.ban(reason=reason, delete_message_days=delete_message_days)
            embed = discord.Embed(title=f"{ctx.command}",
                                  description=f"{user} has been banned from the server!\nReason: {reason}",
                                  colour=0x24FF00)
            embed.set_footer(text=f"Requested by {ctx.author} •  {self.time}")
            await ctx.send(embed=embed)
            await user.send(
                f"You have been **banned** from **{ctx.guild}**\nReason: {reason}\nResponsible: {ctx.author}")
        except discord.NotFound:
            await ctx.send(":warning: User not found")
        except discord.Forbidden:
            if user.id == self.bot.user.id:
                await ctx.send("T-that's meannnnnnn :( I can't ban myself and I hope you don't want to either :(")
            else:
                await ctx.send(":warning: Missing ban permissions")
        except Exception as e:
            await ctx.send(f":warning: Error: {e}")

    @commands.command()
    @commands.has_permissions(kick_members=True)
    @commands.guild_only()
    async def softban(self, ctx, user: discord.Member, reason: ActionReason = None):
        """Bans & Unbans to purge messages from user
        Useful for someone who spammed loads of channels
        In order for this to work, the bot must have Ban Member permissions
        To use this command you must have Kick Member permissions
        Args:
            <user> <reason:optional>
        Example:
            ?softban Nothing 'No poop from you'
            """
        if user.id == ctx.author.id:
            await ctx.send(f"Don't be so harsh on yourself {ctx.author.name} :heart:")
            user = None
        try:
            await user.ban(reason=reason)
            await user.unban(reason=f"Softban\n{reason}")
            embed = discord.Embed(title=f"{ctx.command}",
                                  description=f"{user} has been softbanned from the server!\nReason: {reason}",
                                  colour=0x24FF00)
            embed.set_footer(text=f"Requested by {ctx.author} •  {self.time}")
            await ctx.send(embed=embed)
            await user.send(f"You have been **softbanned** from **{ctx.guild}**\n"
                            f"Reason: {reason}\nResponsible: {ctx.author}")
        except discord.NotFound:
            await ctx.send(":warning: User not found")
        except discord.Forbidden:
            if user.id == self.bot.user.id:
                await ctx.send(f"T-that's meannnnnnn :( I can't {ctx.command} myself"
                               f" and I hope you don't want to either :(")
            else:
                await ctx.send(":warning: Missing Ban Member permissions")
        except Exception as e:
            await ctx.send(f":warning: Error: {e}")

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    @commands.guild_only()
    async def purge(self, ctx, amount):
        """Deletes <x> amount of messages in the channel
        In order for this command to work, the bot must have Manage Messages permissions
        To use this command, you must have Manage Messages permissions
        Args:
            <amount>
        Example:
            ?purge 30"""
        try:
            amount = int(amount)
            deleted = await ctx.channel.purge(limit=amount)
            embed = discord.Embed(title=f"{ctx.command}",
                                  description=f"{len(deleted)} messages have been deleted", colour=0x24FF00)
            embed.set_footer(text=f"Requested by {ctx.author} •  {self.time}")
            a = await ctx.send(embed=embed)
            await asyncio.sleep(2)
            await a.delete()
        except discord.Forbidden:
            await ctx.send(":warning: Missing Manage Messages permissions")
        except ValueError:
            await ctx.send(f":x: `{amount}` is not numerical for amount")
        except Exception as e:
            await ctx.send(f":warning: Error: {e}")

    @commands.command()
    @commands.has_permissions(manage_roles=True)
    @commands.guild_only()
    async def role(self, ctx, option, target: discord.Member, value, reason: ActionReason = None):
        """Adds/Removes roles from target
        In order for this yo work, the bot must have Manage Roles permissions
        To use this command, you must have Manage roles permissions
        Args:
            <add/remove> <user> <role/roles> <reason:optional>
        Example:
            ?role add Nothing Muted,Warning 'Do I need to reason?'
        """
        try:
            value = value.split(",")
            if option == 'add':
                for x in value:
                    x = discord.utils.get(ctx.guild.roles, name=x)
                    await target.add_roles(x, reason=reason)
            if option == 'remove':
                for x in value:
                    x = discord.utils.get(ctx.guild.roles, name=x)
                    await target.remove_roles(x, reason=reason)
        except discord.NotFound:
            await ctx.send("Could not find role/user")
        except discord.Forbidden:
            await ctx.send("Missing manage roles permission")

        embed = discord.Embed(title=f"{ctx.command}",
                              description=f"{target} has had the {value} role {option}", colour=0x24FF00)
        embed.set_footer(text=f"Requested by {ctx.author} •  {self.time}")
        await ctx.send(embed=embed)

    @commands.command()
    @commands.has_permissions(ban_members=True)
    @commands.guild_only()
    async def unban(self, ctx, user, reason: ActionReason = None):
        """Unbans the target from the guild
        In order for this to work, the bot must have Ban member permissions
        To use this command, you must hve Ban member permissions
        Args:
            <user> <reason:optional>
        Example:
            ?unban testbot 'I need to test darnit'
        """
        try:
            bans = await ctx.guild.bans()
            for ban in bans:
                if ban.user.name == str(user):
                    await ctx.guild.unban(ban.user, reason=reason)
                elif ban.user.id == int(user):
                    await ctx.guild.unban(ban.user, reason=reason)
            embed = discord.Embed(title=f"{ctx.command}",
                                  description="User has been unbanned", colour=0x24FF00)
            embed.set_footer(text=f"Requested by {ctx.author} •  {self.time} ")
            await ctx.send(embed=embed)
        except discord.NotFound:
            await ctx.send(":warning: User not found")
        except discord.Forbidden:
            await ctx.send(":warning: Missing Ban Member permissions")
        except Exception as e:
            await ctx.send(f":warning: Error: {e}")

    @commands.command()
    @commands.has_permissions(manage_roles=True)
    @commands.guild_only()
    async def roles(self, ctx):
        """Get a list of roles in the server
        To use this command, you need Manage Roles Permissions
        Args:
            None
        Example:
            ?roles
        """
        embed = discord.Embed(title=f"{ctx.command}",
                              description=f"Total number of roles: {len(ctx.guild.roles)}\nRoles:", colour=0x24FF00)
        embed.set_footer(text=f"Requested by {ctx.author} •  {self.time} ")
        for role in ctx.guild.roles:
            embed.add_field(name=f"{role}ﾠ", value=f"\n{role.id}", inline=True)
        await ctx.send(embed=embed)

    @commands.command()
    @commands.has_permissions(manage_channels=True)
    @commands.guild_only()
    async def lockchat(self, ctx):
        """Lock a channel
        In order for this command to work, the bot needs Manage Channel permissions
        To use this command, you need the Manage Channel permissions
        Args:
            None
        Example:
            ?lockchat "Because nothing"
        """
        try:
            channel = ctx.channel
            role = discord.utils.get(ctx.guild.roles, name="@everyone")
            await channel.send(f"This channel has been locked by {ctx.author}")
            await channel.set_permissions(role, send_messages=False)
        except discord.Forbidden:
            await ctx.send(":warning: Missing Manage Channel permission")
        except Exception as e:
            await ctx.send(f":warning: Error: {e}")


def setup(bot):
    bot.add_cog(ModCmds(bot))
