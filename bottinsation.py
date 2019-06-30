'''
MIT License

Copyright (c) 2019 Nofil Qasim

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE
'''

#Importing APIs
import discord
import youtube_dl
import asyncio

#Specific Imports from discord api to enable bot commands
from discord.ext import commands

myself = '''I.... Am Bottinsation....
         Leader of the Discord Bots'''

#Command prefix for interfacing with bot in discord 
bot = commands.Bot(command_prefix='?', description = myself)

#Bot readout / Login descriptor
@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)

#MISC MISC MISC MISC MISC MISC MISC MISC MISC MISC MISC MISC MISC MISC  

#User initiated command to send some pinoy trashtalk
@bot.command()
async def pinoy(ctx, member: discord.Member):
    await ctx.send('{0.name} is a goblok anjing'.format(member))

#User initiated command to do a basic arithimatic calculation
@bot.command    
async def calc(ctx, num1:int, op:chr, num2:int):
    if op == '+':
        await ctx.send(num1 + num2) 
    elif op == '-':
        await ctx.send(num1 - num2) 
    elif op == 'x' or op == '*':
        await ctx.send(num1 * num2)
    elif op == '/':
        await ctx.send(num1 / num2)
    else: 
         ctx.send('Invalid operator. Go back to kindergarten') 


#MUSIC MUSIC MUSIC MUSIC MUSIC MUSIC MUSIC MUSIC MUSIC MUSIC MUSIC

# Suppress noise about console usage from errors
youtube_dl.utils.bug_reports_message = lambda: ''

#Format options for youtube_dl
ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': False,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
}

#ffmpeg.exe options
ffmpeg_options = {
    'options': '-vn'
}

#Applying youtube_dl format options
ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

#Volume control for bot
class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=1.0):
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

#Class for accepting music commands and initializing bot for music 
class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

#Move bot to voice channel where the user who initiated command is 
    @commands.command()
    async def join(self, ctx, *, channel: discord.VoiceChannel):
        if ctx.voice_client is not None:
            return await ctx.voice_client.move_to(channel)

        await channel.connect()

#Stream from Youtube
    @commands.command()
    async def play(self, ctx, *, url):
        async with ctx.typing():
            player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
            ctx.voice_client.play(player, after=lambda e: print('Player error: %s' % e) if e else None)

        await ctx.send('Now playing: {}'.format(player.title))

#Stop playing
    @commands.command()
    async def stop(self, ctx):
        await ctx.voice_client.stop()

#Pause playing
    @commands.command()
    async def pause(self, ctx):
        await ctx.voice_client.pause()

#Disconnect from voice channel 
    @commands.command()
    async def leave(self, ctx):
        await ctx.voice_client.disconnect()



#Run bot (String is bot token)
#Fake token here because repo is public
bot.run('fake')