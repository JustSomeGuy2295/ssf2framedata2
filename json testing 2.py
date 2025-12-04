import json

char = 'Bandana Dee'
move = 'Dash Attack'

with open('data/characters.json', 'r') as c:
    charidentifier = json.load(c)

with open(f'data/info/{char}.json', 'r') as f:
    charinfo = json.load(f)

embeds = []
gif_pairs = []  # (fullspeed_url, slowmo_url)
hits = []

# Character info for embed title, author, etc
for idx, identifier in enumerate(charidentifier[char]):
    print(f'{identifier} {charidentifier[char][identifier]}')
                        # charidentifier[char][identifier] returns characters id, color, icon

# Move info for embed description    
for i, hit in enumerate(charinfo[move]["Hitboxes"]):
    # Iterates through the different hits the move has
    #hits.append(hit)
    print(hit)
    
    # For every value listed in each hit prints the value name and value value
    for idx, info in enumerate(charinfo[move]["Hitboxes"][f'{hit}']):
        desc = "".join(f'{info}: {charinfo[move]["Hitboxes"][f'{hit}'][f'{info}']}')
        print(desc)
    
    # Extract images
    print(f'Image: {charinfo[move]["Images"]["Full Speed"][f"{hit}"]}')
    print(f'Slowmo: {charinfo[move]["Images"]["Slowmo"][f"{hit}"]}')