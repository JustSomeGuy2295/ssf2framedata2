from ast import Str

from typing import Literal

import discord
from discord import app_commands
from discord.ui import Button, View
from discord.ext import commands

import sqlite3

class Servers(commands.Cog):
    """Send information about different SSF2 servers and gives an invite link."""
    # Create button class
    
    # Define embeds, titles, etc


async def setup(bot: commands.Bot):
    await bot.add_cog(Servers(bot))