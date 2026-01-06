import json
from sys import version
from typing import Literal

import discord
from discord.ext import commands

print(f'Python {version}\n'
      f'discord.py {discord.__version__} | ')


class MyBot(commands.Bot):

    def __init__(self, *, intents: discord.Intents):
        super().__init__(
            activity=discord.CustomActivity(name='Jigglypuff just added!'),
            command_prefix=commands.when_mentioned,
            intents=intents
        )
    
    async def setup_hook(self):
        cogs = [
            'hitboxes',  # Frame data and hitbox commands
            'info',      # Links and info commands
#            'servers',   # Links region servers
            'stats',     # Gives info about character stats
#            'faq'        # Answers commonly asked questions about the bot
        ]
        for cog in cogs:
            await self.load_extension(f'cogs.{cog}')
            print(f'Loaded {cog} cog...')
        print(f'Logged in as {bot.user}\nUser ID: {bot.user.id}')


intents = discord.Intents.default()
intents.members = True
bot = MyBot(intents=intents)
bot.remove_command('help')

# Sync commands
@bot.command()
@commands.guild_only()
@commands.is_owner()
async def sync(ctx: commands.Context, scope: Literal['global', 'guild']):
    """Sync global or guild commands"""
    async with ctx.channel.typing():
        if scope == 'global':
            synced = await ctx.bot.tree.sync()
            txt = 'globally'
        elif scope == 'guild':
            synced = await ctx.bot.tree.sync(guild=ctx.guild)
            txt = 'to the current guild'
    await ctx.send(f'Synced {len(synced)} commands {txt}')

# 'Secret' commands

@bot.command()
async def jmac(ctx):
    await ctx.send('Hey guys it\'s me jmac and I really like chairs. You can sit on them, like what the heck! What would we even do without chairs? #chairs\n\n'
                    'Hey guys it\'s me, Jmac again. Tillur said he doesn\'t like chairs! Can you believe it? He must\'ve had a bad time with chairs. Bean bags are cool too. #equality\n\n'
                    'Hey everyone, Jmac here. Paradox just said that tables and the floor are better. I disagree! The chairs are essential for the table. Maybe the floor is also good since it supports the chair! Paradox is on to something. #science\n\n'
                    'Hello guys, it\'s me jmac! captain falco says that stairs are better than chairs. While it does rhyme (which is very cool) I think chairs are better. #chai rs\n\n'
                    'Hi guys! I am jmac. Hida says that when you\'re gaming you sit on chairs. I completely agree. Who stands while gaming? Someone who doesn\'t know the true value of chairs. #purpose\n\n')
    
@bot.command()
async def zashy(ctx):
    await ctx.send('https://tenor.com/view/di-bad-bad-di-di-directional-influence-smash-gif-21670494')

@bot.command()
async def do(ctx: commands.Context):
    if 'do a barrel roll' in ctx.message.content:
        await ctx.send('https://tenor.com/view/star-fox-star-fox-64-starfox-do-a-barrel-roll-rick-may-gif-3633857843406436610')
    
@bot.command()
async def fakenews(ctx):
    await ctx.send('@matchmaking')

# Event logging    
@bot.event
async def on_command_error(ctx, error):
    err_log_channel = await bot.fetch_channel(keys['ERRORLOG'])
    error = getattr(error, 'original', error)
    error_message = str(error)
    if err_log_channel:
        await err_log_channel.send(error_message)

@bot.event
async def on_interaction(interaction: discord.Interaction):
    cmd_log_channel = await bot.fetch_channel(keys['COMMANDLOG'])
    if cmd_log_channel:
        await cmd_log_channel.send(f"Slash command '{interaction.command.name}' used  in '{interaction.guild}'")
        
# Bot login
with open('KEYS.json', 'r') as f:
    keys = json.load(f)
    
if __name__ == '__main__':
    bot.run(keys['TOKEN'])  # API Key from KEYS.json
