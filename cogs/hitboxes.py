import json
from typing import Literal
import discord
from discord import app_commands
from discord.ui import Button, View
from discord.ext import commands

### Buttons ###

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
    
    with open('data/characters.json', 'r') as c:
        charidentifier = json.load(c)

    with open(f'data/info/{char}.json', 'r') as f:
        charinfo = json.load(f)
    
    embeds = []
    gif_pairs = []  # (fullspeed_url, slowmo_url)
    hits = []

    # Move info for embed description    
    for i, hit in enumerate(charinfo[move]["Hitboxes"]):
        # Iterates through the different hits the move has
        hits.append(hit)
         
    # Move info for embed description    
    for i, hit in enumerate(charinfo[move]["Hitboxes"]):
        # Iterates through the different hits the move has
        
        # For every value listed in each hit prints the value name and value value
        desc = ""
        for idx, info in enumerate(charinfo[move]["Hitboxes"][f'{hit}']):
            desc += f'{info}: {charinfo[move]["Hitboxes"][f'{hit}'][f'{info}']}\n'
            
        embed = discord.Embed(description=f'```\n{desc}```', color=int(charidentifier[char]["color"], 16))
        if len(hits)>1:
            hit_text = f" ({hit})"
        else:
            hit_text = ""
        embed.set_author(name=f'{char} {move}{hit_text}', icon_url=charidentifier[char]["icon"])
        embed.set_footer(text='Up to date as of patch 1.4.0.1')
        embed.set_image(url=f'{charinfo[move]["Images"]["Full Speed"][f"{hit}"]}')  # Default to fullspeed       
    
        embeds.append(embed)
        gif_pairs.append((f'{charinfo[move]["Images"]["Full Speed"][f"{hit}"]}', f'{charinfo[move]["Images"]["Slowmo"][f"{hit}"]}'))  # (fullspeed, slowmo)
    
    view = HitboxView(embeds, gif_pairs, hits, user)        
    return embeds, view 

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
        await interaction.response.send_message(embed=ssf2_embed[0], view=view)
        
async def setup(bot: commands.Bot):
    await bot.add_cog(Hitboxes(bot))