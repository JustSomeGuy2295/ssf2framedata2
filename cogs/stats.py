from ast import Str

from typing import Literal

import discord
from discord import app_commands
from discord.ui import Button, View
from discord.ext import commands

import sqlite3

def ssf2_charinfo(char: str):
    '''
    The function used by the character commands to collect the data required
    
    Returns:
        A discord embed
    '''
    con = sqlite3.connect("data/academy.db")
    cur = con.cursor()

    db_char_id = cur.execute("SELECT id FROM characters WHERE name=?", (char,)).fetchone()[0]
    character_data = cur.execute("SELECT color, icon FROM characters WHERE name=?", (char,)).fetchone()
    color = int(character_data[0], 16)
    icon = character_data[1]

    char_info = cur.execute("""
        SELECT height, width, 
               weight, gravity, fall_speed, jumpsquat,
               g2a, dash_length, initial_dash, run_speed,
               idle_hurtbox,
               air_speed, air_accel
        FROM stats 
        WHERE char_id=?
    """, (db_char_id,)).fetchall()

    con.close()

    info = []

    for idx, row in enumerate(char_info):
        
        info = {
            'Height': row[0], 'Width': row[1], 
            'Weight': row[2], 'Gravity': row[3], 'Fall Speed': row[4], 'Max Airspeed': row[11], 'Air Acceleration': row[12], 'Jumpsquat': row[5],
            'Ground-to-Air': row[6], 'Dash Length': row[7], 'Dash Speed': row[8], 'Run Speed': row[9]
        }

        desc = "\n".join(f"{k}: {v}" for k, v in info.items() if v is not None)
        embed = discord.Embed(description=f'```py\n{desc}```', color=color)
        embed.set_image(url=row[10])
        embed.set_author(name=f'{char} Information', icon_url=icon)
        embed.set_footer(text='Up to date as of patch 1.4.0.1')

    return embed

class Stats(commands.Cog):
    """Send displays of idle stance, and character stats."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    characters = [
        'Bandana Dee', 'Black Mage', 'Bomberman', 'Bowser', 'Captain Falcon',
        'Chibi-Robo', 'Donkey Kong', 'Falco', 'Fox', 'Ganondorf',
        'Goku', 'Ichigo', 'Isaac', 'Jigglypuff', 'Kirby',
        'Krystal', 'Link', 'Lloyd', 'Lucario', 'Luffy',
        'Luigi', 'Mario', 'Marth', 'Mega Man', 'Meta Knight',
        'Mr. Game and Watch', 'Naruto', 'Ness', 'PAC-MAN', 'Peach',
        'Pichu', 'Pikachu', 'Pit', 'Rayman', 'Ryu',
        'Samus', 'Sandbag', 'Sheik', 'Simon', 'Sonic',
        'Sora', 'Tails', 'Waluigi', 'Wario', 'Yoshi',
        'Zelda', 'Zero Suit Samus', 'King Dedede'
    ]

    async def character_autocomplete(self, interaction: discord.Interaction, current: str):
        return [
            app_commands.Choice(name=char, value=char)
            for char in self.characters
            if current.lower() in char.lower()
        ][:25]

    @app_commands.command(name='stats')
    @app_commands.describe(character="Choose a character")
    @app_commands.autocomplete(character=character_autocomplete)
    async def stats(self, interaction: discord.Interaction, character: str):
        """Show frame data and hitbox info for a character."""
        ssf2_embed = ssf2_charinfo(character)
        await interaction.response.send_message(embed=ssf2_embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(Stats(bot))