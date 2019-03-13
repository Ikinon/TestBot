import discord
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
import time
import random
import requests
import datetime
import config
import asyncio
import aiohttp


class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.time = datetime.datetime.today().strftime('%d/%m/%Y')

    @commands.command()
    @commands.cooldown(1, 2, BucketType.user)
    async def ping(self,ctx):
        start = time.perf_counter()
        message=await ctx.send('Ping...')
        end = time.perf_counter()
        duration = (end - start) * 1000

        await message.edit(content='Pong! {:.2f}ms'.format(duration))

    @commands.command()
    @commands.cooldown(1, 3, BucketType.user)
    async def flip(self, ctx):
        """Heads or Tails?"""
        flip = ["Heads", "Tails"]
        fliprandom = random.choice(flip)
        await ctx.channel.send(f"I get {fliprandom}")

    @commands.command()
    @commands.cooldown(1, 10, BucketType.user)
    async def dog(self, ctx):
        """Get a random dog image!"""
        isVideo = True
        while isVideo:
            async with aiohttp.ClientSession() as cs:
                async with cs.get('https://random.dog/woof.json') as r:
                    res = await r.json()
                    res = res['url']
                    await cs.close()
            if res.endswith('.mp4'):
                pass
            else:
                isVideo = False
        em = discord.Embed(title=f"{ctx.command}", description=":dog: Here is your random dog!")
        em.set_image(url=res['url'])
        em.set_footer(text=f"Requested by {ctx.author} •  {self.time}")
        await ctx.send(embed=em)

    @commands.command()
    @commands.cooldown(1, 3, BucketType.user)
    async def info(self, ctx):
        """Bot infomation"""
        a = 0
        for user in self.bot.users:
            if user.bot == True:
                pass
            else:
                a = a + 1
        em = discord.Embed(title=f"{ctx.command}", description=None)
        em.set_thumbnail(url=f"{self.bot.user.avatar_url}")
        em.add_field(name="Username", value=f"{self.bot.user}", inline=True)
        em.add_field(name="ID", value=f"{self.bot.user.id}")
        em.add_field(name="Guilds", value=f"{len(self.bot.guilds)}", inline=True)
        em.add_field(name="Users", value=f"{a}")
        em.add_field(name="Version", value=f"{config.VERSION}", inline=True)
        em.add_field(name="Owner", value="<@209595566408073216>", inline=True)
        em.set_footer(text=f'Python | Discord.py {discord.__version__} • Requested by {ctx.author}')
        await ctx.send(embed=em)

    @commands.command()
    @commands.cooldown(1, 3, BucketType.user)
    @commands.guild_only()
    async def guildinfo(self, ctx):
        a = 0
        for user in ctx.guild.members:
            if user.bot == True:
                pass
            else:
                a = a + 1
        em = discord.Embed(title=f"{ctx.command}", description=f"Information about {ctx.guild}")
        em.set_thumbnail(url=f"{ctx.guild.icon_url}")
        em.add_field(name="Guild ID", value=f"{ctx.guild.id}")
        em.add_field(name="Members", value=f"{a}")
        em.add_field(name="Channels", value=f"{len(ctx.guild.channels)}")
        em.add_field(name="Roles", value=f"{len(ctx.guild.roles)}")
        em.add_field(name="Owner", value=f"{ctx.guild.owner.mention}")
        em.set_footer(text=f"Requested by {ctx.author} •  {self.time}")
        await ctx.send(embed=em)

    @commands.command()
    @commands.cooldown(1, 3, BucketType.user)
    async def feedback(self, ctx, *, content: str):
        """Gives feedback about the bot
        This is a quick way to request features or bugs
        without being in the bot's server"""
        em = discord.Embed(title='User Feedback', colour=0x738bd7)
        channel = self.bot.get_channel(515221729078018048)
        em.set_author(name=ctx.author, icon_url=ctx.author.avatar_url)
        em.description = content
        em.timestamp = ctx.message.created_at
        if ctx.guild is not None:
            em.add_field(name='Guild', value=f'{ctx.guild.name} (ID: {ctx.guild.id})', inline=False)
        em.add_field(name='Channel', value=f'{ctx.channel} (ID: {ctx.channel.id})', inline=False)
        em.set_footer(text=f'Author ID: {ctx.author.id}')
        await channel.send(embed=em)
        await ctx.send(f'{ctx.author.name} Successfully sent feedback!')

    @commands.command()
    @commands.cooldown(1, 3, BucketType.user)
    async def remindme(self, ctx, time, *, message):
        """Remind you in X time
        Example:
            ?remindme 3h to do that """
        x = list(time)
        timead = 0
        if "m" in x:
            timead = int(x[0]) * 60
        if "s" in x:
            timead = int(x[0])
        if "h" in x:
            timead = int(x[0]) * 3600
        await ctx.send(f"✅ I have set a reminder for **{message}** in {time} {ctx.author.name}")
        await ctx.message.delete()
        await asyncio.sleep(timead)
        await ctx.send(f"{ctx.author.mention}, you asked me to remind you {time} ago to {message}")


def setup(bot):
    bot.add_cog(General(bot))
