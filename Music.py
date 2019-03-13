import asyncio

import discord
import youtube_dl

from discord.ext import commands

# Suppress noise about console usage from errors
youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'  # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)


class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)


class Song(discord.PCMVolumeTransformer):
    def __init__(self, song_info):
        self.info = song_info.info
        self.requester = song_info.requester
        self.channel = song_info.channel
        self.filename = song_info.filename


class Playlist:
    def __iter__(self):
        return self._queue.__iter__()

    def clear(self):
        self._queue.clear

    def add_song(self, song):
        self.put.nowait()

    def __str__(self):
        info = 'Current playlist:\n'
        info_len = len(info)
        for song in self:
            s = str(song)
            l = len(s) + 1  # Counting the extra \n
            if info_len + l > 1995:
                info += '[...]'
                break
            info += f'{s}\n'
            info_len += l
        return info


class MusicState:
    def __init__(self, loop):
        self.playlist = Playlist()

    @property
    def current_song(self):
        return self.voice_client.source

    @property
    def volume(self):
        return self.player_volume

    @volume.setter
    def volume(self, value):
        self.player_volume = value
        if self.voice_client:
            self.voice_client.source.volume = value

    async def stop(self):
        self.playlist.clear()
        if self.voice_client:
            await self.voice_client.disconnect()
            self.voice_client = None

    async def play_next(self, song=None, error=None):
        if error:
            await self.current.song.channel.send(f'An error has occurred while playing {self.current_song}: {error}')
        if self.playlist.empty():
            await self.voice_client.disconnect()
        else:
            next_song_info = self.playlist.get_song()
            await next_song_info.wait_until_downloaded()
            source = Song(next_song_info)
            source.volume = self.player_volume
            self.voice_client.play(source, after=lambda e: asyncio.run_coroutine_threadsafe(
                self.play_next_song(next_song_info, e), self.loop).result())
            await next_song_info.channel.send(f'Now playing {next_song_info}')


class ActionMethod:
    async def call_embed(self, ctx):
        em = discord.Embed(title=f"{ctx.command}", description=None)
        em.add_field()


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    class JoinChannel(commands.Converter):
        async def convert(self, ctx, argument):
            ret = {ctx.author.voice.channel}
            return ret

    @commands.command()
    async def join(self, ctx, *, channel: JoinChannel = None):
        """Joins a voice channel"""

        if ctx.voice_client is not None:
            return await ctx.voice_client.move_to(channel)

        await channel.connect()

    @commands.command()
    async def mstatus(self, ctx):
        em = discord.Embed(title=f"{ctx.command}", description=None)
        em.add_field(name="Is Playing", value=f"{ctx.voice.client.is_playing()}")

    @commands.command()
    async def pause(self, ctx):
        """Pauses the player"""
        ctx.voice_client.pause()

    @commands.command()
    async def resume(self, ctx):
        """Resumes player"""
        ctx.voice_client.resume()

    @commands.command()
    async def play(self, ctx, *, url):
        """Plays from a url"""

        async with ctx.typing():
            player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
            ctx.voice_client.play(player, after=lambda e: print('Player error: %s' % e) if e else None)

        await ctx.send('Now playing: {}'.format(player.title))

    @commands.command()
    async def volume(self, ctx, volume: int):
        """Changes the player's volume"""

        if ctx.voice_client is None:
            return await ctx.send("Not connected to a voice channel.")
        if volume < 0 or volume > 120:
            await ctx.send(f":x: {ctx.author.name},Volume needs to be between 1 and 120")
        else:
            ctx.voice_client.source.volume = volume / 100
            await ctx.send("Changed volume to {}%".format(volume))

    @commands.command()
    async def stop(self, ctx):
        """Stops and disconnects the bot from voice"""
        ctx.voice_client.stop()
        await ctx.voice_client.disconnect()

    @play.before_invoke
    async def ensure_voice(self, ctx):
        if ctx.voice_client is None:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
            else:
                await ctx.send("You are not connected to a voice channel.")
                raise commands.CommandError("Author not connected to a voice channel.")
        elif ctx.voice_client.is_playing():
            ctx.voice_client.stop()


def setup(bot):
    bot.add_cog(Music(bot))
