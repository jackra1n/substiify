from discord.ext import commands

from helper.music import queue

from helper.music.player import Player

import datetime as dt
import re
import typing as t

import logging
import aiohttp
import discord
import wavelink

logger = logging.getLogger(__name__)

URL_REGEX = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
LYRICS_URL = "https://some-random-api.ml/lyrics?title="

class Music(commands.Cog, wavelink.WavelinkMixin):
    def __init__(self, bot):
        self.bot = bot
        self.wavelink = wavelink.Client(bot=bot)
        self.bot.loop.create_task(self.start_nodes())

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if not member.bot and after.channel is None:
            # check if the bot is in the before voice channel
            if not self.bot.user in before.channel.members:
                return
            if not [m for m in before.channel.members if not m.bot]:
                logger.info('[music]: on_voice_state_update disconnecting the player')
                await self.get_player(member.guild).teardown()

    @wavelink.WavelinkMixin.listener()
    async def on_node_ready(self, node):
        logger.info(f"Wavelink node `{node.identifier}` ready.")

    @wavelink.WavelinkMixin.listener("on_track_stuck")
    @wavelink.WavelinkMixin.listener("on_track_end")
    @wavelink.WavelinkMixin.listener("on_track_exception")
    async def on_player_stop(self, node, payload):
        if payload.player.queue.repeat_mode == queue.RepeatMode.ONE:
            await payload.player.repeat_track()
        else:
            await payload.player.advance()

    async def cog_check(self, ctx):
        if isinstance(ctx.channel, discord.DMChannel):
            await ctx.send("Music commands are not available in DMs.")
            return False

        return True

    async def start_nodes(self):
        await self.bot.wait_until_ready()

        nodes = {
            "MAIN": {
                "host": "127.0.0.1",
                "port": 2333,
                "rest_uri": "http://127.0.0.1:2333",
                "password": "youshallnotpass",
                "identifier": "MAIN",
                "region": "europe",
            }
        }

        for node in nodes.values():
            await self.wavelink.initiate_node(**node)

    def get_player(self, obj):
        if isinstance(obj, commands.Context):
            return self.wavelink.get_player(obj.guild.id, cls=Player, context=obj)
        elif isinstance(obj, discord.Guild):
            return self.wavelink.get_player(obj.id, cls=Player)

    @commands.command(name="connect", aliases=["join"])
    async def connect_command(self, ctx, *, channel: t.Optional[discord.VoiceChannel]):
        player = self.get_player(ctx)

        channel = await player.connect(ctx, channel)
        await ctx.send(f"Connected to {channel.name}.", delete_after = 30)
        await ctx.message.delete()

    @connect_command.error
    async def connect_command_error(self, ctx, exc):
        if isinstance(exc, AlreadyConnectedToChannel):
            await ctx.send("Already connected to a voice channel.", delete_after = 30)
        elif isinstance(exc, NoVoiceChannel):
            await ctx.send("No suitable voice channel was provided.", delete_after = 30)

    @commands.command(name="stop", aliases=["leave"])
    async def disconnect_command(self, ctx):
        player = self.get_player(ctx)
        await player.teardown()
        await ctx.send("Disconnected.", delete_after = 30)
        await ctx.message.delete()

    @commands.command(name="play", aliases=["p"])
    async def play_command(self, ctx, *, query: t.Optional[str]):
        player = self.get_player(ctx)

        if not player.is_connected:
            await player.connect(ctx)

        if query is None:
            if player.queue.is_empty:
                raise QueueIsEmpty

            await player.set_pause(False)
            await ctx.send("Playback resumed.", delete_after = 30)

        else:
            query = query.strip("<>")
            if not re.match(URL_REGEX, query):
                query = f"ytsearch:{query}"

            await player.add_tracks(ctx, await self.wavelink.get_tracks(query))
        await ctx.message.delete()

    @play_command.error
    async def play_command_error(self, ctx, exc):
        if isinstance(exc, QueueIsEmpty):
            await ctx.send("No songs to play as the queue is empty.", delete_after = 30)
        elif isinstance(exc, NoVoiceChannel):
            await ctx.send("No suitable voice channel was provided.", delete_after = 30)

    @commands.command(name="pause")
    async def pause_command(self, ctx):
        player = self.get_player(ctx)

        if player.is_paused:
            raise PlayerIsAlreadyPaused

        await player.set_pause(True)
        await ctx.send("Playback paused.", delete_after = 30)

    @pause_command.error
    async def pause_command_error(self, ctx, exc):
        if isinstance(exc, PlayerIsAlreadyPaused):
            await ctx.send("Already paused.", delete_after = 30)

    @commands.command(name="skip", aliases=["next"])
    async def next_command(self, ctx):
        player = self.get_player(ctx)

        if not player.queue.upcoming:
            raise NoMoreTracks

        await player.stop()
        await ctx.send("Playing next track in queue.", delete_after = 30)
        await ctx.message.delete()

    @next_command.error
    async def next_command_error(self, ctx, exc):
        if isinstance(exc, QueueIsEmpty):
            await ctx.send("This could not be executed as the queue is currently empty.", delete_after = 30)
        elif isinstance(exc, NoMoreTracks):
            await ctx.send("There are no more tracks in the queue.", delete_after = 30)

    @commands.command(name="shuffle")
    async def shuffle_command(self, ctx):
        player = self.get_player(ctx)
        player.queue.shuffle()
        await ctx.send("Queue shuffled.", delete_after = 30)
        await ctx.message.delete()

    @shuffle_command.error
    async def shuffle_command_error(self, ctx, exc):
        if isinstance(exc, QueueIsEmpty):
            await ctx.send("The queue could not be shuffled as it is currently empty.", delete_after = 30)

    @commands.command(name="repeat")
    async def repeat_command(self, ctx, mode: str = None):
        if mode not in ("none", "1", "all"):
            raise InvalidRepeatMode

        player = self.get_player(ctx)
        player.queue.set_repeat_mode(mode)
        await ctx.send(f"The repeat mode has been set to `{mode}`.", delete_after = 30)

    @repeat_command.error
    async def repeat_command_error(self, ctx, exc):
        if isinstance(exc, InvalidRepeatMode):
            await ctx.send("Please provide one of the repeat modes: `1`, `none`, `all`", delete_after = 30)
            await ctx.message.delete()

    @commands.group(name="queue", aliases=["q"], invoke_without_command = True)
    async def queue_command(self, ctx):
        player = self.get_player(ctx)
        show_index = 0

        if player.queue.is_empty:
            raise QueueIsEmpty

        embed = await self.create_queue_embed(ctx, player.queue, show_index)
        queue_message = await ctx.send(embed=embed, delete_after = 150)
        await ctx.message.delete()
        
        await queue_message.add_reaction("⏮")
        await queue_message.add_reaction("⏭")
        await queue_message.add_reaction("❌")

        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) in ("⏮", "⏭", "❌") and reaction.message.id == queue_message.id

        while True:
            reaction, user = await self.bot.wait_for("reaction_add", timeout=120.0, check=check)
            if str(reaction.emoji) == "❌":
                await queue_message.delete()
                break
            elif str(reaction.emoji) == "⏮":
                if show_index <= 9:
                    show_index = 0
                else:
                    show_index -= 10
            elif str(reaction.emoji) == "⏭":
                if show_index + 10 <= player.queue.length:
                    show_index += 10
            edit_embed = await self.create_queue_embed(ctx, player.queue, show_index)
            await queue_message.edit(embed=edit_embed)

    async def create_queue_embed(self, ctx, queue, show_index):
        embed = discord.Embed(
            title=f"Queue ({len(queue.upcoming)})",
            description=f"Showing up to next 10 tracks",
            colour=ctx.author.colour,
            timestamp=dt.datetime.utcnow()
        )
        embed.set_footer(text=f"Requested by {ctx.author.display_name}", icon_url=ctx.author.avatar_url)
        embed.add_field(
            name="Currently playing",
            value=getattr(queue.current_track, "title", "No tracks currently playing."),
            inline=False
        )
        if upcoming := queue.upcoming:
            upcoming_songs_string = ""
            show_to = show_index + 10 if show_index + 10 < queue.length else queue.length
            for index, track in enumerate(upcoming[show_index:show_to]):
                upcoming_songs_string += f"`{index + 1 + show_index}`. {track.title}\n"
            embed.add_field(
                name="Next up",
                value=upcoming_songs_string,
                inline=False
            )
        return embed

    @queue_command.command(name="song", aliases=["track"])
    async def queue_song_command(self, ctx, index: int):
        player = self.get_player(ctx)

        if player.queue.is_empty:
            raise QueueIsEmpty

        if index < 1 or index > len(player.queue.upcoming):
            raise InvalidIndex

        track = player.queue.upcoming[index - 1]
        embed = discord.Embed(
            title=f"{index}. {track.title}",
            description=f"{track.author}",
            colour=ctx.author.colour,
            timestamp=dt.datetime.utcnow()
        )
        embed.set_author(name="Query Results")
        embed.set_footer(text=f"Requested by {ctx.author.display_name}", icon_url=ctx.author.avatar_url)
        embed.add_field(name="Duration", value=f"{track.duration / 1000}s", inline=False)
        embed.add_field(name="URL", value=f"[Click here]({track.uri})", inline=False)

        await ctx.send(embed=embed, delete_after = 60)
        await ctx.message.delete()

    @queue_command.command(name="move")
    async def queue_move_command(self, ctx, index: int, new_index: int):
        player = self.get_player(ctx)

        if index < 0 or new_index < 0:
            raise InvalidIndex

        if index >= player.queue.length:
            raise InvalidIndex

        if new_index >= player.queue.length:
            raise InvalidIndex

        moved_track = player.queue.move_track(index+1, new_index+1)
        await ctx.send(f"Track `{moved_track}` moved.", delete_after = 30)
        await ctx.message.delete()

    @queue_command.error
    async def queue_command_error(self, ctx, exc):
        if isinstance(exc, QueueIsEmpty):
            await ctx.send("The queue is currently empty.", delete_after = 30)
        elif isinstance(exc, InvalidIndex):
            await ctx.send("Please provide valid position.", delete_after = 30)
            await ctx.message.delete()

    @queue_move_command.error
    async def queue_command_error(self, ctx, exc):
        if isinstance(exc, InvalidIndex):
            await ctx.send("Please provide valid position.", delete_after = 30)

    # Requests -----------------------------------------------------------------

    @commands.command(name="lyrics")
    async def lyrics_command(self, ctx, name: t.Optional[str]):
        player = self.get_player(ctx)
        name = name or player.queue.current_track.title
        author = f" {player.queue.current_track.author}" or ""

        async with ctx.typing():
            async with aiohttp.request("GET", LYRICS_URL + name + author, headers={}) as r:
                if not 200 <= r.status <= 299:
                    raise NoLyricsFound

                data = await r.json()

                if len(data["lyrics"]) > 4000:
                    await ctx.send(f"<{data['links']['genius']}>")
                    return await ctx.message.delete()

                embed = discord.Embed(
                    title=data["title"],
                    description=data["lyrics"],
                    colour=ctx.author.colour,
                    timestamp=dt.datetime.utcnow(),
                )
                embed.set_thumbnail(url=data["thumbnail"]["genius"])
                embed.set_author(name=data["author"])
                await ctx.send(embed=embed, delete_after = 120)
                await ctx.message.delete()

    @lyrics_command.error
    async def lyrics_command_error(self, ctx, exc):
        if isinstance(exc, NoLyricsFound):
            await ctx.send("No lyrics could be found.", delete_after = 30)

    @commands.command(name="now", aliases=["currentsong"])
    async def playing_command(self, ctx):
        player = self.get_player(ctx)

        if not player.is_playing:
            raise PlayerIsAlreadyPaused

        embed = discord.Embed(
            title="Now playing",
            colour=ctx.author.colour,
            timestamp=dt.datetime.utcnow(),
        )
        embed.set_footer(text=f"Requested by {ctx.author.display_name}", icon_url=ctx.author.avatar_url)
        embed.add_field(name="Track title", value=player.queue.current_track.title, inline=False)

        position = divmod(player.position, 60000)
        length = divmod(player.queue.current_track.length, 60000)
        embed.add_field(
            name="Timestamp",
            value=f"{int(position[0])}:{round(position[1]/1000):02}/{int(length[0])}:{round(length[1]/1000):02}",
            inline=True
        )
        embed.add_field(name="Artist", value=player.queue.current_track.author, inline=True)

        await ctx.send(embed=embed, delete_after = 30)
        await ctx.message.delete()

    @playing_command.error
    async def playing_command_error(self, ctx, exc):
        if isinstance(exc, PlayerIsAlreadyPaused):
            await ctx.send("There is no track currently playing.", delete_after = 30)

    @commands.command(name="skipto", aliases=["playindex"])
    async def skipto_command(self, ctx, index: int):
        player = self.get_player(ctx)

        if player.queue.is_empty:
            raise QueueIsEmpty

        if not 0 <= index <= player.queue.length:
            raise NoMoreTracks

        player.queue.position = index - 2
        await player.stop()
        await ctx.send(f"Playing track in position `{index}`.", delete_after = 30)
        await ctx.message.delete()

    @skipto_command.error
    async def skipto_command_error(self, ctx, exc):
        if isinstance(exc, QueueIsEmpty):
            await ctx.send("There are no tracks in the queue.", delete_after = 30)
        elif isinstance(exc, NoMoreTracks):
            await ctx.send("That index is out of the bounds of the queue.", delete_after = 30)

    @commands.command(name="restart")
    async def restart_command(self, ctx):
        player = self.get_player(ctx)

        if player.queue.is_empty:
            raise QueueIsEmpty

        await player.seek(0)
        await ctx.send("Track restarted.", delete_after = 30)
        await ctx.message.delete()

    @restart_command.error
    async def restart_command_error(self, ctx, exc):
        if isinstance(exc, QueueIsEmpty):
            await ctx.send("There are no tracks in the queue.", delete_after = 30)


class InvalidIndex(commands.CommandError):
    pass

class AlreadyConnectedToChannel(commands.CommandError):
    pass

class NoVoiceChannel(commands.CommandError):
    pass

class QueueIsEmpty(commands.CommandError):
    pass

class NoTracksFound(commands.CommandError):
    pass

class PlayerIsAlreadyPaused(commands.CommandError):
    pass

class NoMoreTracks(commands.CommandError):
    pass

class NoPreviousTracks(commands.CommandError):
    pass

class InvalidRepeatMode(commands.CommandError):
    pass

class NoLyricsFound(commands.CommandError):
    pass


def setup(bot):
    bot.add_cog(Music(bot))