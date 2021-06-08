from helper.YTDLSource import YTDLSource
from helper.MusicPlayer import MusicPlayer
from discord.ext import commands
from urllib.parse import urlparse
from urllib.parse import parse_qs
from random import shuffle
import itertools
import logging
import asyncio
import discord
import os

async def userIsInBotVC(ctx):
    if not ctx.voice_client == None:
        members = ctx.voice_client.channel.voice_states.keys()
        if ctx.author.id in members:
            return True
        await ctx.send(f'You are not in the VC!')
        return False

async def userIsInAnyVC(ctx):
    if ctx.author.voice:
        return True
    await ctx.send('You are not in a VC!')
    return False

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.players = {}

    async def cleanup(self, guild):
        try:
            await guild.voice_client.disconnect()
        except AttributeError:
            pass

        try:
            self.players[guild.id].stopping = True
            del self.players[guild.id]

        except KeyError:
            pass

    def get_player(self, ctx):
        try:
            player = self.players[ctx.guild.id]
        except KeyError:
            player = MusicPlayer(ctx)
            self.players[ctx.guild.id] = player
        return player

    def checkIfYoutubePlaylist(self, url):
        return 'list=' in url

    async def parseUrl(self, ctx, player, url):
        if url.startswith('<'):
            url = url[1:-1]
        if self.checkIfYoutubePlaylist(url):
            # return
            parsed = urlparse(url)
            newUrl = f'https://youtube.com/playlist?list={parse_qs(parsed.query)["list"][0]}'
            urls = YTDLSource.get_playlist_info(newUrl)['urls']
            await player.queue.put(YTDLSource(urls.pop(0), ctx.author))
            await ctx.message.delete()
            for entry in urls:
                await player.queue.put(YTDLSource(entry, ctx.author))
            await ctx.send(f'Queued **{len(urls)}** songs')
        else:
            song = YTDLSource(url, ctx.author)
            await ctx.message.delete()
            await player.queue.put(song)
            await ctx.send(f"Queued **{song.data['title']}**")


    @commands.command(aliases=["p"])
    async def play(self, ctx, *, url):
        vc = ctx.voice_client
        play = False
        if not vc and await userIsInAnyVC(ctx):
            await ctx.invoke(self.connect)
            play = True
        elif await userIsInBotVC(ctx):
            play = True

        if play:
            player = self.get_player(ctx)
            await self.parseUrl(ctx, player, url)

    @commands.command()
    @commands.check(userIsInBotVC)
    async def pause(self, ctx):
        """Pause the currently playing song."""
        botsVc = ctx.voice_client
        if not botsVc or not botsVc.is_playing():
            return await ctx.send('I am not currently playing anything!', delete_after=30)
        elif botsVc.is_paused():
            return
        botsVc.pause()
        await ctx.send(f'**`{ctx.author}`**: Paused the song!')

    @commands.command()
    @commands.check(userIsInBotVC)
    async def resume(self, ctx):
        """Resume the currently paused song."""
        botsVc = ctx.voice_client
        if not botsVc or not botsVc.is_connected():
            return await ctx.send('I am not currently playing anything!', delete_after=30)
        elif not botsVc.is_paused():
            return
        botsVc.resume()
        await ctx.send(f'**`{ctx.author}`**: Resumed the song!')

    @commands.command()
    @commands.check(userIsInBotVC)
    async def skip(self, ctx):
        """Skip the song."""
        botsVc = ctx.voice_client
        if not botsVc or not botsVc.is_connected():
            return await ctx.send('I am not currently playing anything!', delete_after=30)
        if botsVc.is_paused():
            pass
        elif not botsVc.is_playing():
            return
        botsVc.stop()
        await ctx.send(f'**`{ctx.author}`**: Skipped the song!')

    @commands.command(name='queue', aliases=['q'])
    async def queue_info(self, ctx):
        """Retrieve a basic queue of upcoming songs."""
        botsVc = ctx.voice_client
        if not botsVc or not botsVc.is_connected():
            return await ctx.send('I am not currently connected to voice!', delete_after=30)
        player = self.get_player(ctx)
        if player.queue.empty():
            return await ctx.send('There are currently no more queued songs.')
        # Grab up to 5 entries from the queue...
        upcoming = list(itertools.islice(player.queue._queue, 0, 10))
        fmt = '\n'.join(f'#{index+1} | **`{song.data["title"]}`**' for index, song in enumerate(upcoming))
        embed = discord.Embed(title=f'Upcoming - Next {len(upcoming)}', description=fmt)
        await ctx.send(embed=embed)

    @commands.command(aliases=['currentsong', 'now'])
    async def now_playing(self, ctx):
        """Display information about the currently playing song."""
        botsVc = ctx.voice_client
        if not botsVc or not botsVc.is_connected():
            return await ctx.send('I am not currently connected to voice!', delete_after=30)
        player = self.get_player(ctx)
        if not player.current:
            return await ctx.send('I am not currently playing anything!')
        try:
            # Remove our previous now_playing message.
            await player.np.delete()
        except discord.HTTPException:
            pass
        player.np = await ctx.send(f'**Now Playing:** `{botsVc.source.title}` requested by `{botsVc.source.requester}`')

    @commands.command()
    @commands.check(userIsInBotVC)
    async def stop(self, ctx):
        """Stop the currently playing song and destroy the player."""
        botsVc = ctx.voice_client
        if not botsVc or not botsVc.is_connected():
            return await ctx.send('I am not currently playing anything!', delete_after=30)
        await self.cleanup(ctx.guild)
        await ctx.message.delete()

    @commands.command()
    @commands.check(userIsInBotVC)
    async def shuffle(self, ctx: commands.Context):
        if self.get_player(ctx).queue.qsize() == 0:
            return await ctx.send('Empty queue.')

        shuffle(self.get_player(ctx).queue._queue)
        await ctx.message.delete()
        await ctx.send('Queue has been shuffled', delete_after=15)

    @commands.command()
    async def connect(self, ctx, *, channel: discord.VoiceChannel=None):
        if not channel:
            try:
                channel = ctx.author.voice.channel
            except AttributeError:
                raise InvalidVoiceChannel('No channel to join. Please either specify a valid channel or join one.')

        botsVc = ctx.voice_client
        if botsVc:
            if botsVc.channel.id == channel.id:
                return
            try:
                await botsVc.move_to(channel)
            except asyncio.TimeoutError:
                raise VoiceConnectionError(f'Moving to channel: <{channel}> timed out.')
        else:
            try:
                await channel.connect()
            except asyncio.TimeoutError:
                raise VoiceConnectionError(f'Connecting to channel: <{channel}> timed out.')

        await ctx.send(f'Connected to: **{channel}**', delete_after=30)

def setup(bot):
    bot.add_cog(Music(bot))