import json, requests
from typing import Literal

import discord
from discord import app_commands
from discord.ui import Button, View
from discord.ext import commands
from tabulate import tabulate

import sqlite3

class HitboxView(View):
    def __init__(self, embeds, gif_pairs, hits, user: discord.User):
        super().__init__()
        self.embeds = embeds  # list of discord.Embed objects
        self.gif_pairs = gif_pairs  # list of tuples: (fullspeed_url, slowmo_url)
        self.hits = hits
        self.current_hit = 0
        self.user = user

        # GIF Speed Buttons
        self.add_item(GIFSpeedToggle("Full Speed", True, self))
        self.add_item(GIFSpeedToggle("Slow", False, self))
        
        # Hit buttons
        for idx, embed in enumerate(embeds):
            hit_name = hits[idx] if hits[idx] else f"Hit {idx+1}"
            if len(hits)>1: self.add_item(MoveSelect(hit_name, idx, self))

    def get_current_embed(self):
        return self.embeds[self.current_hit]

    def get_current_gif(self, slowmo: bool):
        urls = self.gif_pairs[self.current_hit]
        return urls[1] if slowmo else urls[0]

class GIFSpeedToggle(Button):
    def __init__(self, name: str, is_fullspeed: bool, view: HitboxView):
        self.is_fullspeed = is_fullspeed
        self.custom_view = view
        style = discord.ButtonStyle.blurple
        super().__init__(label=name, style=style)

    async def callback(self, interaction: discord.Interaction):
        if interaction.user != self.custom_view.user:
            await interaction.response.send_message("You're not allowed to use this button.", ephemeral=True)
            return

        idx = self.custom_view.current_hit
        embed = self.custom_view.get_current_embed()
        embed.set_image(url=self.custom_view.get_current_gif(slowmo=not self.is_fullspeed))
        await interaction.response.edit_message(embed=embed, view=self.custom_view)
        
class MoveSelect(Button):
    def __init__(self, name: str, index: int, view: HitboxView):
        self.index = index
        self.custom_view = view
        super().__init__(label=name, style=discord.ButtonStyle.gray)

    async def callback(self, interaction: discord.Interaction):
        if interaction.user != self.custom_view.user:
            await interaction.response.send_message("You're not allowed to use this button.", ephemeral=True)
            return

        self.custom_view.current_hit = self.index
        embed = self.custom_view.get_current_embed()
        # Set default image to full speed
        embed.set_image(url=self.custom_view.get_current_gif(slowmo=False))
        await interaction.response.edit_message(embed=embed, view=self.custom_view)


def ssf2_hitbox(char: str, move: str, user: discord.User):
    '''
    The function used by the character commands to collect the data required
    
    Returns:
        A discord embed
    '''
    con = sqlite3.connect("data/academy.db")
    cur = con.cursor()

    db_char_id = cur.execute("SELECT id FROM characters WHERE name=?", (char,)).fetchone()[0]
    db_move_id = cur.execute("SELECT id FROM moves WHERE display_name=?", (move,)).fetchone()[0]
    character_data = cur.execute("SELECT color, icon FROM characters WHERE name=?", (char,)).fetchone()
    color = int(character_data[0], 16)
    icon = character_data[1]

    hitboxes = cur.execute("""
        SELECT hit, startup, active, endlag, damage, first_actionable_frame, landing_lag, image, 
               sourspot_damage, sweetspot_damage, tipper_damage, notes,
               intangible, invulnerable, armored, slowmo, angle, cooldown, autocancel_window
        FROM hitboxes 
        WHERE char_id=? AND move_id=?
    """, (db_char_id, db_move_id)).fetchall()

    con.close()

    embeds = []
    gif_pairs = []  # (fullspeed_url, slowmo_url)
    hits = []

    for idx, row in enumerate(hitboxes):
        hits.append(row[0])
        
        info = {
            'Startup': row[1], 'Active': row[2], 'Endlag': row[3],
            'Damage': row[4], 'FAF': row[5], 'Landing Lag': row[6], 'Autocancel': row[18],
            'Sweetspot Damage': row[9], 'Tipper Damage': row[10], 'Sourspot Damage': row[8],
            'Angle': row[16], 'Cooldown': row[17],
            'Intangible': row[12], 'Invulnerable': row[13], 'Armored': row[14],
            'Notes': row[11]
        }

        desc = "\n".join(f"{k}: {v}" for k, v in info.items() if v is not None)
        embed = discord.Embed(description=f'```\n{desc}```', color=color)
        hit_text = f" ({row[0]})" if row[0] else ""
        embed.set_author(name=f'{char} {move}{hit_text}', icon_url=icon)
        embed.set_footer(text='Up to date as of patch 1.4.0.1')
        embed.set_image(url=row[7])  # Default to fullspeed

        embeds.append(embed)
        gif_pairs.append((row[7], row[15]))  # (fullspeed, slowmo)

    view = HitboxView(embeds, gif_pairs, hits, user)
    return embeds[0], view

class Hitboxes(commands.Cog):
    """Send displays of frame data, character, and hitbox info."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # Bandana Dee
    moves = Literal[
        'Jab', 'Dash Attack',
        'Down Tilt', 'Up Tilt', 'Forward Tilt',
        'Neutral Air', 'Down Air', 'Up Air', 'Forward Air', 'Back Air',
        'Down Smash', 'Up Smash', 'Forward Smash', 
        'Up Special', 'Neutral Special',
        'Down Special', 'Side Special',
        'Grab', 'Forward Throw', 'Back Throw', 'Up Throw', 'Down Throw'
    ]

    @app_commands.command(name='bandanadee')
    async def bandanadee(self, interaction: discord.Interaction, attack: moves):
        """Bandana Dee frame data and hitbox info"""
        ssf2_embed, view = ssf2_hitbox('Bandana Dee', attack, interaction.user)
        await interaction.response.send_message(embed=ssf2_embed, view=view)
    
    # Captain Falcon
    moves = Literal[
        'Jab', 'Dash Attack',
        'Down Tilt', 'Up Tilt', 'Forward Tilt',
        'Neutral Air', 'Down Air', 'Up Air', 'Forward Air', 'Back Air',
        'Down Smash', 'Up Smash', 'Forward Smash', 
        'Up Special', 'Neutral Special',
        'Down Special', 'Side Special',
        'Grab', 'Forward Throw', 'Back Throw', 'Up Throw', 'Down Throw'
    ]

    @app_commands.command(name='captainfalcon')
    async def captainfalcon(self, interaction: discord.Interaction, attack: moves):
        """Captain Falcon frame data and hitbox info"""
        ssf2_embed, view = ssf2_hitbox('Captain Falcon', attack, interaction.user)
        await interaction.response.send_message(embed=ssf2_embed, view=view)
        
    # Donkey Kong
    moves = Literal[
        'Jab', 'Dash Attack',
        'Down Tilt', 'Up Tilt', 'Forward Tilt',
        'Neutral Air', 'Down Air', 'Up Air', 'Forward Air', 'Back Air',
        'Down Smash', 'Up Smash', 'Forward Smash', 
        'Up Special', 'Neutral Special',
        'Down Special', 'Side Special',
        'Grab', 'Forward Throw', 'Back Throw', 'Up Throw', 'Down Throw'
    ]

    @app_commands.command(name='donkeykong')
    async def donkeykong(self, interaction: discord.Interaction, attack: moves):
        """Donkey Kong frame data and hitbox info"""
        ssf2_embed, view = ssf2_hitbox('Donkey Kong', attack, interaction.user)
        await interaction.response.send_message(embed=ssf2_embed, view=view)
        
    # Ganondorf
    moves = Literal[
        'Jab', 'Dash Attack',
        'Down Tilt', 'Up Tilt', 'Forward Tilt',
        'Neutral Air', 'Down Air', 'Up Air', 'Forward Air', 'Back Air',
        'Down Smash', 'Up Smash', 'Forward Smash', 
        'Up Special', 'Neutral Special',
        'Down Special', 'Side Special',
        'Grab', 'Forward Throw', 'Back Throw', 'Up Throw', 'Down Throw'
    ]

    @app_commands.command(name='ganondorf')
    async def ganondorf(self, interaction: discord.Interaction, attack: moves):
        """Ganondorf frame data and hitbox info"""
        ssf2_embed, view = ssf2_hitbox('Ganondorf', attack, interaction.user)
        await interaction.response.send_message(embed=ssf2_embed, view=view)

    # Goku
    moves = Literal[
        'Jab', 'Dash Attack',
        'Down Tilt', 'Up Tilt', 'Forward Tilt',
        'Neutral Air', 'Down Air', 'Up Air', 'Forward Air', 'Back Air',
        'Down Smash', 'Up Smash', 'Forward Smash', 
        'Up Special', 'Neutral Special',
        'Down Special', 'Side Special',
        'Grab', 'Forward Throw', 'Back Throw', 'Up Throw', 'Down Throw'
    ]

    @app_commands.command(name='goku')
    async def goku(self, interaction: discord.Interaction, attack: moves):
        """Goku frame data and hitbox info"""
        ssf2_embed, view = ssf2_hitbox('Goku', attack, interaction.user)
        await interaction.response.send_message(embed=ssf2_embed, view=view)
    
    # Ichigo
    moves = Literal[
        'Jab', 'Dash Attack',
        'Down Tilt', 'Up Tilt', 'Forward Tilt',
        'Neutral Air', 'Down Air', 'Up Air', 'Forward Air', 'Back Air',
        'Down Smash', 'Up Smash', 'Forward Smash', 
        'Up Special', 'Neutral Special',
        'Down Special', 'Side Special',
        'Grab', 'Forward Throw', 'Back Throw', 'Up Throw', 'Down Throw'
    ]

    @app_commands.command(name='ichigo')
    async def ichigo(self, interaction: discord.Interaction, attack: moves):
        """Ichigo frame data and hitbox info"""
        ssf2_embed, view = ssf2_hitbox('Ichigo', attack, interaction.user)
        await interaction.response.send_message(embed=ssf2_embed, view=view)

    # Isaac
        
    moves = Literal[
        'Jab', 'Dash Attack',
        'Down Tilt', 'Up Tilt', 'Forward Tilt',
        'Neutral Air', 'Down Air', 'Up Air', 'Forward Air', 'Back Air',
        'Down Smash', 'Up Smash', 'Forward Smash', 
        'Up Special', 'Neutral Special',
        'Down Special', 'Side Special',
        'Grab', 'Forward Throw', 'Back Throw', 'Up Throw', 'Down Throw'
    ]

    @app_commands.command(name='isaac')
    async def isaac(self, interaction: discord.Interaction, attack: moves):
        """Isaac frame data and hitbox info"""
        ssf2_embed, view = ssf2_hitbox('Isaac', attack, interaction.user)
        await interaction.response.send_message(embed=ssf2_embed, view=view)
    
    # Kirby
    moves = Literal[
        'Jab', 'Dash Attack',
        'Down Tilt', 'Up Tilt', 'Forward Tilt',
        'Neutral Air', 'Down Air', 'Up Air', 'Forward Air', 'Back Air',
        'Down Smash', 'Up Smash', 'Forward Smash', 
        'Up Special', 'Neutral Special',
        'Down Special', 'Side Special',
        'Grab', 'Forward Throw', 'Back Throw', 'Up Throw', 'Down Throw'
    ]

    @app_commands.command(name='kirby')
    async def kirby(self, interaction: discord.Interaction, attack: moves):
        """Kirby frame data and hitbox info"""
        ssf2_embed, view = ssf2_hitbox('Kirby', attack, interaction.user)
        await interaction.response.send_message(embed=ssf2_embed, view=view)

    # Link
    moves = Literal[
        'Jab', 'Dash Attack',
        'Down Tilt', 'Up Tilt', 'Forward Tilt',
        'Neutral Air', 'Down Air', 'Up Air', 'Forward Air', 'Back Air', 'Z Aerial',
        'Down Smash', 'Up Smash', 'Forward Smash', 
        'Up Special', 'Neutral Special',
        'Down Special', 'Side Special',
        'Grab', 'Forward Throw', 'Back Throw', 'Up Throw', 'Down Throw'
    ]   
    
    @app_commands.command(name='link')
    async def link(self, interaction: discord.Interaction, attack: moves):
        """Link frame data and hitbox info"""
        ssf2_embed, view = ssf2_hitbox('Link', attack, interaction.user)
        await interaction.response.send_message(embed=ssf2_embed, view=view)

    # Lloyd
    moves = Literal[
        'Jab', 'Dash Attack',
        'Down Tilt', 'Up Tilt', 'Forward Tilt',
        'Neutral Air', 'Down Air', 'Up Air', 'Forward Air', 'Back Air',
        'Down Smash', 'Up Smash', 'Forward Smash', 
        'Up Special', 'Neutral Special',
        'Down Special', 'Side Special',
        'Grab', 'Forward Throw', 'Back Throw', 'Up Throw', 'Down Throw'
    ]   
    
    @app_commands.command(name='lloyd')
    async def link(self, interaction: discord.Interaction, attack: moves):
        """Lloyd frame data and hitbox info"""
        ssf2_embed, view = ssf2_hitbox('Lloyd', attack, interaction.user)
        await interaction.response.send_message(embed=ssf2_embed, view=view)

    # Luffy
    moves = Literal[
        'Jab', 'Dash Attack',
        'Down Tilt', 'Up Tilt', 'Forward Tilt',
        'Neutral Air', 'Down Air', 'Up Air', 'Forward Air', 'Back Air',
        'Down Smash', 'Up Smash', 'Forward Smash', 
        'Up Special', 'Neutral Special',
        'Down Special', 'Side Special',
        'Grab', 'Forward Throw', 'Back Throw', 'Up Throw', 'Down Throw'
    ]   
    
    @app_commands.command(name='luffy')
    async def luffy(self, interaction: discord.Interaction, attack: moves):
        """Luffy frame data and hitbox info"""
        ssf2_embed, view = ssf2_hitbox('Luffy', attack, interaction.user)
        await interaction.response.send_message(embed=ssf2_embed, view=view)

    # Luigi
    moves = Literal[
        'Jab', 'Dash Attack',
        'Down Tilt', 'Up Tilt', 'Forward Tilt',
        'Neutral Air', 'Down Air', 'Up Air', 'Forward Air', 'Back Air',
        'Down Smash', 'Up Smash', 'Forward Smash', 
        'Up Special', 'Neutral Special',
        'Down Special', 'Side Special',
        'Grab', 'Forward Throw', 'Back Throw', 'Up Throw', 'Down Throw',
        'Taunt'
    ]   
   
    @app_commands.command(name='luigi')
    async def luigi(self, interaction: discord.Interaction, attack: moves):
        """Luigi frame data and hitbox info"""
        ssf2_embed, view = ssf2_hitbox('Luigi', attack, interaction.user)
        await interaction.response.send_message(embed=ssf2_embed, view=view)

    # Mario
    moves = Literal[
        'Jab', 'Dash Attack',
        'Down Tilt', 'Up Tilt', 'Forward Tilt',
        'Neutral Air', 'Down Air', 'Up Air', 'Forward Air', 'Back Air',
        'Down Smash', 'Up Smash', 'Forward Smash', 
        'Up Special', 'Neutral Special',
        'Down Special', 'Side Special',
        'Grab', 'Forward Throw', 'Back Throw', 'Up Throw', 'Down Throw'
    ]   
    
    @app_commands.command(name='mario')
    async def mario(self, interaction: discord.Interaction, attack: moves):
        """Mario frame data and hitbox info"""
        ssf2_embed, view = ssf2_hitbox('Mario', attack, interaction.user)
        await interaction.response.send_message(embed=ssf2_embed, view=view)
        
    # Marth
    moves = Literal[
        'Jab', 'Dash Attack',
        'Down Tilt', 'Up Tilt', 'Forward Tilt',
        'Neutral Air', 'Down Air', 'Up Air', 'Forward Air', 'Back Air',
        'Down Smash', 'Up Smash', 'Forward Smash', 
        'Up Special', 'Neutral Special',
        'Down Special', 'Side Special',
        'Grab', 'Forward Throw', 'Back Throw', 'Up Throw', 'Down Throw'
    ]   
    
    @app_commands.command(name='marth')
    async def marth(self, interaction: discord.Interaction, attack: moves):
        """Marth frame data and hitbox info"""
        ssf2_embed, view = ssf2_hitbox('Marth', attack, interaction.user)
        await interaction.response.send_message(embed=ssf2_embed, view=view)
        
    # Mr. Game and Watch
    moves = Literal[
        'Jab', 'Dash Attack',
        'Down Tilt', 'Up Tilt', 'Forward Tilt',
        'Neutral Air', 'Down Air', 'Up Air', 'Forward Air', 'Back Air',
        'Down Smash', 'Up Smash', 'Forward Smash', 
        'Up Special', 'Neutral Special',
        'Down Special', 'Side Special',
        'Grab', 'Forward Throw', 'Back Throw', 'Up Throw', 'Down Throw'
    ]

    @app_commands.command(name='mrgameandwatch')
    async def mrgameandwatch(self, interaction: discord.Interaction, attack: moves):
        """Mr. Game and Watch frame data and hitbox info"""
        ssf2_embed, view = ssf2_hitbox('Mr. Game and Watch', attack, interaction.user)
        await interaction.response.send_message(embed=ssf2_embed, view=view)
        
    # Naruto
    moves = Literal[
        'Jab', 'Dash Attack',
        'Down Tilt', 'Up Tilt', 'Forward Tilt',
        'Neutral Air', 'Down Air', 'Up Air', 'Forward Air', 'Back Air',
        'Down Smash', 'Up Smash', 'Forward Smash', 
        'Up Special', 'Neutral Special',
        'Down Special', 'Side Special',
        'Grab', 'Forward Throw', 'Back Throw', 'Up Throw', 'Down Throw'
    ]

    @app_commands.command(name='naruto')
    async def naruto(self, interaction: discord.Interaction, attack: moves):
        """Naruto frame data and hitbox info"""
        ssf2_embed, view = ssf2_hitbox('Naruto', attack, interaction.user)
        await interaction.response.send_message(embed=ssf2_embed, view=view)
        
    # PAC-MAN
    moves = Literal[
        'Jab', 'Dash Attack',
        'Down Tilt', 'Up Tilt', 'Forward Tilt',
        'Neutral Air', 'Down Air', 'Up Air', 'Forward Air', 'Back Air',
        'Down Smash', 'Up Smash', 'Forward Smash', 
        'Up Special', 'Neutral Special',
        'Down Special', 'Side Special',
        'Grab', 'Forward Throw', 'Back Throw', 'Up Throw', 'Down Throw'
    ]

    @app_commands.command(name='pacman')
    async def pacman(self, interaction: discord.Interaction, attack: moves):
        """PAC-MAN frame data and hitbox info"""
        ssf2_embed, view = ssf2_hitbox('PAC-MAN', attack, interaction.user)
        await interaction.response.send_message(embed=ssf2_embed, view=view)

    # Pit
    moves = Literal[
        'Jab', 'Dash Attack',
        'Down Tilt', 'Up Tilt', 'Forward Tilt',
        'Neutral Air', 'Down Air', 'Up Air', 'Forward Air', 'Back Air',
        'Down Smash', 'Up Smash', 'Forward Smash', 
        'Up Special', 'Neutral Special',
        'Down Special', 'Side Special',
        'Grab', 'Forward Throw', 'Back Throw', 'Up Throw', 'Down Throw'
    ]

    @app_commands.command(name='pit')
    async def pit(self, interaction: discord.Interaction, attack: moves):
        """Pit frame data and hitbox info"""
        ssf2_embed, view = ssf2_hitbox('Pit', attack, interaction.user)
        await interaction.response.send_message(embed=ssf2_embed, view=view)

    # Samus
    moves = Literal[
        'Jab', 'Dash Attack',
        'Down Tilt', 'Up Tilt', 'Forward Tilt',
        'Neutral Air', 'Down Air', 'Up Air', 'Forward Air', 'Back Air', 'Z Aerial',
        'Down Smash', 'Up Smash', 'Forward Smash', 
        'Up Special', 'Neutral Special',
        'Down Special', 'Side Special',
        'Grab', 'Forward Throw', 'Back Throw', 'Up Throw', 'Down Throw'
    ]   
    
    @app_commands.command(name='samus')
    async def samus(self, interaction: discord.Interaction, attack: moves):
        """Samus frame data and hitbox info"""
        ssf2_embed, view = ssf2_hitbox('Samus', attack, interaction.user)
        await interaction.response.send_message(embed=ssf2_embed, view=view)    
        
    # Sandbag
    moves = Literal[
        'Jab', 'Dash Attack',
        'Down Tilt', 'Up Tilt', 'Forward Tilt',
        'Neutral Air', 'Down Air', 'Up Air', 'Forward Air', 'Back Air',
        'Down Smash', 'Up Smash', 'Forward Smash', 
        'Up Special', 'Neutral Special',
        'Down Special', 'Side Special',
        'Grab', 'Forward Throw', 'Back Throw', 'Up Throw', 'Down Throw'
    ]   
    
    @app_commands.command(name='sandbag')
    async def sandbag(self, interaction: discord.Interaction, attack: moves):
        """Sandbag frame data and hitbox info"""
        ssf2_embed, view = ssf2_hitbox('Sandbag', attack, interaction.user)
        await interaction.response.send_message(embed=ssf2_embed, view=view)

    # Simon
    moves = Literal[
        'Jab', 'Dash Attack',
        'Down Tilt', 'Up Tilt', 'Forward Tilt',
        'Neutral Air', 'Down Air', 'Up Air', 'Forward Air', 'Back Air',
        'Down Smash', 'Up Smash', 'Forward Smash', 
        'Up Special', 'Neutral Special',
        'Down Special', 'Side Special',
        'Grab', 'Forward Throw', 'Back Throw', 'Up Throw', 'Down Throw'
    ]   
    
    @app_commands.command(name='simon')
    async def simon(self, interaction: discord.Interaction, attack: moves):
        """Simon frame data and hitbox info"""
        ssf2_embed, view = ssf2_hitbox('Simon', attack, interaction.user)
        await interaction.response.send_message(embed=ssf2_embed, view=view)

    # Sonic
    moves = Literal[
        'Jab', 'Dash Attack',
        'Down Tilt', 'Up Tilt', 'Forward Tilt',
        'Neutral Air', 'Down Air', 'Up Air', 'Forward Air', 'Back Air',
        'Down Smash', 'Up Smash', 'Forward Smash', 
        'Up Special', 'Neutral Special',
        'Down Special', 'Side Special',
        'Grab', 'Forward Throw', 'Back Throw', 'Up Throw', 'Down Throw'
    ]   
    
    @app_commands.command(name='sonic')
    async def sonic(self, interaction: discord.Interaction, attack: moves):
        """Sonic frame data and hitbox info"""
        ssf2_embed, view = ssf2_hitbox('Sonic', attack, interaction.user)
        await interaction.response.send_message(embed=ssf2_embed, view=view)
        
    # Wario
    moves = Literal[
        'Jab', 'Dash Attack',
        'Down Tilt', 'Up Tilt', 'Forward Tilt',
        'Neutral Air', 'Down Air', 'Up Air', 'Forward Air', 'Back Air',
        'Down Smash', 'Up Smash', 'Forward Smash', 
        'Up Special', 'Neutral Special',
        'Down Special', 'Side Special',
        'Grab', 'Forward Throw', 'Back Throw', 'Up Throw', 'Down Throw'
    ]   
    
    @app_commands.command(name='wario')
    async def wario(self, interaction: discord.Interaction, attack: moves):
        """Wario frame data and hitbox info"""
        ssf2_embed, view = ssf2_hitbox('Wario', attack, interaction.user)
        await interaction.response.send_message(embed=ssf2_embed, view=view)
        
    # ZSS
    moves = Literal[
        'Jab', 'Dash Attack',
        'Down Tilt', 'Up Tilt', 'Forward Tilt',
        'Neutral Air', 'Down Air', 'Up Air', 'Forward Air', 'Back Air',
        'Down Smash', 'Up Smash', 'Forward Smash', 
        'Up Special', 'Neutral Special',
        'Down Special', 'Side Special',
        'Grab', 'Forward Throw', 'Back Throw', 'Up Throw', 'Down Throw'
    ]   
    
    @app_commands.command(name='zerosuitsamus')
    async def zerosuitsamus(self, interaction: discord.Interaction, attack: moves):
        """Zero Suit Samus frame data and hitbox info"""
        ssf2_embed, view = ssf2_hitbox('Zero Suit Samus', attack, interaction.user)
        await interaction.response.send_message(embed=ssf2_embed, view=view)

async def setup(bot: commands.Bot):
    await bot.add_cog(Hitboxes(bot))
