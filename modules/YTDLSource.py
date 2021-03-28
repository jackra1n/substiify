from discord import PCMVolumeTransformer, FFmpegPCMAudio
import youtube_dl
import asyncio

class PlaylistHelper:
    @classmethod
    def checkIfYoutubePlayList(cls, url: str):
        if "list=" in url:
            return True
        else:
            return False

class YTDLSource(PCMVolumeTransformer):
    ytdl_format_options = {
        'format': 'bestaudio/best',
        'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
        'restrictfilenames': True,
        'nocheckcertificate': True,
        'ignoreerrors': False,
        'logtostderr': False,
        'quiet': True,
        'no_warnings': True,
        'default_search': 'auto',
        'source_address': '0.0.0.0',  # bind to ipv4 since ipv6 addresses cause issues sometimes
        'noplaylist': False,
        'flat-playlist': True
    }
    ytdl = youtube_dl.YoutubeDL(ytdl_format_options)
    ffmpeg_options = {
        'options': '-vn'
    }

    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data
        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: cls.ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else cls.ytdl.prepare_filename(data)
        return cls(FFmpegPCMAudio(filename, **cls.ffmpeg_options), data=data)

    @classmethod
    def get_playlist_info(self, url: str):
        # in case of a radio playist, restrict the number of songs that are downloaded
        # if we received just the id, it is an id starting with 'RD'
        # if its a url, the id is behind a '&list='
        #if song_utils.is_radio(self.target):
        #    self.ydl_opts['playlistend'] = self.musiq.base.settings.max_playlist_items

        with youtube_dl.YoutubeDL(self.ytdl_format_options) as ydl:
            self.info_dict = ydl.extract_info(url=url, download=False, process=False)

        if self.info_dict['_type'] != 'playlist' or 'entries' not in self.info_dict:
            raise Exception('Not a Playlist')

        playlist_info = {}
        playlist_info['id'] = self.info_dict['id']
        playlist_info['urls'] = []
        if 'title' in self.info_dict:
            playlist_info['title'] = self.info_dict['title']
        for entry in self.info_dict['entries']:
            playlist_info['urls'].append('https://www.youtube.com/watch?v=' + entry['id'])
        return playlist_info