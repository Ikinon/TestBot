import io
import os
import textwrap
import traceback
from contextlib import redirect_stdout

import discord
from discord.ext import commands

import config


class Owner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def __local_check(self, ctx):
        if ctx.author.id in config.OWNER_ID:
            return await ctx.bot.is_owner(ctx.author)
        else:
            None

    @commands.command()
    async def restart(self, ctx):
        await ctx.message.add_reaction('✅')
        os.startfile(r"C:\Users\Admin\PycharmProjects\TestBot2\Main.py")
        await self.bot.logout()

    @commands.command(hidden=True)
    async def test(self, ctx):
        await ctx.send("Here: <a:discordsomething:523609317971329025>")

    @commands.command()
    async def shutdown(self, ctx):
        """Exits the bot"""
        await ctx.message.add_reaction('✅')
        await self.bot.logout()
        await self.bot.close()

    @commands.command()
    async def loadext(self, ctx, value):
        try:
            self.bot.load_extension(value)
            await ctx.message.add_reaction('✅')
        except Exception as e:
            await ctx.message.add_reaction("\N{CROSS MARK}")
            await ctx.send(e)

    @commands.command()
    async def unloadext(self, ctx, value):
        try:
            self.bot.unload_extension(value)
            await ctx.message.add_reaction('✅')
        except Exception as e:
            await ctx.message.add_reaction("\N{CROSS MARK}")
            await ctx.send(e)

    @commands.command(name='eval')
    async def _eval(self, ctx, *, body: str):
        """Evaluates a code"""

        env = {
            'bot': self.bot,
            'ctx': ctx,
            'channel': ctx.channel,
            'author': ctx.author,
            'guild': ctx.guild,
            'message': ctx.message,
        }

        env.update(globals())

        stdout = io.StringIO()

        to_compile = f'async def func():\n{textwrap.indent(body, "  ")}'

        try:
            exec(to_compile, env)
        except Exception as e:
            return await ctx.send(f'```py\n{e.__class__.__name__}: {e}\n```')

        func = env['func']
        try:
            with redirect_stdout(stdout):
                ret = await func()
        except Exception as e:
            value = stdout.getvalue()
            await ctx.send(f'```py\n{value}{traceback.format_exc()}\n```')
        else:
            value = stdout.getvalue()
            try:
                await ctx.message.add_reaction('\u2705')
            except:
                pass

            if ret is None:
                if value:
                    await ctx.send(f'```py\n{value}\n```')
            else:
                self._last_result = ret
                await ctx.send(f'```py\n{value}{ret}\n```')

    @_eval.error
    async def eval_error(self, ctx, error):
        if isinstance(error, discord.ext.commands.errors.MissingRequiredArgument):
            await ctx.send("Eval something at least smh!")

    @commands.command()
    async def stats(self, ctx):
        em = discord.Embed(title="System info")


def setup(bot):
    bot.add_cog(Owner(bot))
