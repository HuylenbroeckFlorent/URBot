import requests
import sys

###
# Saves a deck located under path in user's presets.
###
def save_deck(cookies, headers, path):
    data = {
      'action': 'presetsave',
      'presetId': '0',
    }

    with open(path, 'r') as f:
        first=True
        charactersData = ""
        for line in f.readlines():
            if line != "":
                if first:
                    data['presetName']=line.strip('\n')
                    first=False
                else:
                    charactersData+=line.strip('\n').replace(' ','-')+"-1,"
    f.close()
    charactersData.strip(',')
    data['charactersData']=charactersData

    print(requests.post('https://www.urban-rivals.com/ajax/collection.pro/', headers=headers, cookies=cookies, data=data).text)