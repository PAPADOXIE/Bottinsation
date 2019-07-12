'''
MIT License

Copyright (c) 2019 Nofil Qasim and Faaiq Bilal

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
import random

#Specific Imports from discord api to enable bot commands
from discord.ext import commands

#BOT STARTUP BOT STARTUP BOT STARTUP BOT STARTUP BOT STARTUP BOT STARTUP BOT STARTUP 

#Bot description
myself = '''I.... Am Bottinsation....
         Leader of the Discord Bots'''

#Command prefix for interfacing with bot in discord 
bot = commands.Bot(command_prefix='?', description = myself)


#MISC MISC MISC MISC MISC MISC MISC MISC MISC MISC MISC MISC MISC MISC

#User initiated command to send some pinoy trashtalk
pinoyresponse = [                    
                    '{0.name} is a goblok anjing', 
                    '{0.name} should go back to playing juggy like the fag dula', 
                    '{0.name} please stop blocking my camp u r like mad all over again', 
                    '{0.name} stop now or fbi will be called :rage:',
                    '{0.name} is fag like zob :thinking:'                  
                ]   
@bot.command()
async def pinoy(ctx, member: discord.Member):
    await ctx.send(random.choice(pinoyresponse).format(member))


#User initiated command to do a basic arithimatic calculation
@bot.command()    
async def calc(ctx, num1:int, op, num2:int):
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

#User initiated command to send ayaya.png
@bot.command()
async def ayaya(ctx, self):
    await bot.send(file=discord.File('ayaya.png'))


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
    'source_address': '0.0.0.0'
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
class Music(commands.Cog, discord.Client):
    def __init__(self, bot):
        self.bot = bot

#Creating song queue
    songs = asyncio.Queue()
#Creating event to switch to next song
    play_next_song = asyncio.Event()

#Creating a task to play the music
    async def go(self):
        x = True
        while x == True:
            if loop.repeat == True:
                Music.play_next_song.clear()
                current = await Music.songs.get()
                Music.play.ctx.voice_client.play(current, after=Music.toggle_next)
                await Music.play.ctx.send('Now playing: {}'.format(current.title))
                Music.songs.put(current)
                await Music.play_next_song.wait()
            else:
                Music.play_next_song.clear()
                current = await Music.songs.get()
                Music.play.ctx.voice_client.play(current, after=Music.toggle_next)
                await Music.play.ctx.send('Now playing: {}'.format(current.title))
                await Music.play_next_song.wait()

 #Point to next song   
    def toggle_next():
        bot.loop.call_soon_threadsafe(play_next_song.set)

#Move bot to voice channel where the user who initiated command is
    @commands.command()
    async def join(self, ctx, *, channel: discord.VoiceChannel):
        if ctx.voice_client is not None:
            return await ctx.voice_client.move_to(channel)

        await channel.connect()

#Play/Add user requested song to queue
    @commands.command()
    async def play(self, ctx, *, url):
        ctx = ctx
        async with ctx.typing():
            player = await YTDLSource.from_url(url, loop=self.bot.loop)
            await Music.songs.put(player)
            
        await ctx.send('Added : {} to the queue'.format(player.title))
        print('Added : {} to the queue'.format(player.title))

#Stop playing
    @commands.command()
    async def stop(self, ctx):
        await ctx.voice_client.stop()

#Pause playing
    @commands.command()
    async def pause(self, ctx):
        await ctx.voice_client.pause()

#Resume playing 
    @commands.command()
    async def resume(self,ctx):
        await ctx.voice_client.resume()

#Show queue
    @commands.command()
    async def queue(self,ctx):
        async with ctx.typing():
            if Music.songs.qsize() == 0:
                await ctx.send('No songs in queue')
            else:
                for i in range (0, Music.songs.qsize()):   
                    q = await Music.songs.get()
                    await ctx.send('{} : {}'.format(i+1, q.title))
                    await Music.songs.put(q)

#Repeat the queue
    @commands.command()
    async def loop(self, ctx, repeat):
        if repeat == 'on':
            repeat = True 
            await ctx.send('Queue will now repeat')
        elif repeat == 'off':
            repeat == False
            await ctx.send('Queue will not repeat now')

#Disconnect from voice channel 
    @commands.command()
    async def leave(self, ctx):
        await ctx.voice_client.disconnect()

#Dont play when user isn't connected to voice channel
#Stop playing when no one is connected to the voice channel
    @play.before_invoke
    async def ensure_voice(self, ctx):
        if ctx.voice_client is None:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
            else:
                await ctx.send("Dont try to waste my bandwidth and connect to a voice channel.")
                raise commands.CommandError("Author not connected to a voice channel.")
        elif ctx.voice_client.is_playing():
            print('Still Connected')


class MusicClient(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)   
#Creating music background task
        self.bg_task = self.loop.create_task(self.music_background_task())

    async def music_background_task(self):
        await self.wait_until_ready()
        print('Music is Ready')
        counter = 0       
        while not self.is_closed():
            counter += 1
            print('Counting {}'.format(counter))
            await Music.go(Music)
            await asyncio.sleep(1)

self_bot = False


#Add music cog
music_client = MusicClient()
bot.add_cog(Music(bot))

#Bot login status
@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')
#Update bot activity status
    activity = discord.Activity(name='over Kingar Nugar', type=discord.ActivityType.watching)
    await bot.change_presence(activity=activity)
#Run music client
    await music_client.start('fake')
    

#Run bot (String is bot token)
#Fake token here because repo is public
bot.run('fake')