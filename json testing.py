import json

with open('data/info/BandanaDee.json', 'r') as f:
    charinfo = json.load(f)
    
#print(charinfo['1'])

for i, j in enumerate(charinfo['1']):
    print(charinfo['1'][f'{j}'])