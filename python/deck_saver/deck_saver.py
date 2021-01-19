import requests
import os
import sys
import re
from lxml import html

###
# Saves a preset located under path in user's presets.
###
def import_deck(cookies, navigation_headers, action_headers, path):

    preset_name = ""
    preset = []
    with open(path, 'r') as f:
        first=True
        for line in f.readlines():
            if line != "":
                if first:
                    preset_name=line.strip('\n')
                    first=False
                else:
                    line = line.strip('\n').split()
                    preset.append((line[0], line[1]))
        f.close()

    preset_id = exists(cookies, navigation_headers, action_headers, preset)

    if preset_id>0:
        print("Preset \""+preset_name+"\" already exists and has id "+str(preset_id)+".")
        return preset_id
    else:
        data = {
          'action': 'presetsave',
          'presetId': '0',
        }
        data['presetName']=preset_name
        charactersData = ""
        for character in preset:
            charactersData+=character[0]+"-"+character[1]+"-1,"
        charactersData.strip(',')
        data['charactersData']=charactersData

        requests.post('https://www.urban-rivals.com/ajax/collection.pro/', headers=action_headers, cookies=cookies, data=data)

        preset_id = id_from_name(cookies, navigation_headers, preset_name)
        print("Preset\""+preset_name+"\" created with id "+str(preset_id)+".")

    return preset_id

###
# Returns a preset's id if it already exists in user's presets
###
def exists(cookies, navigation_headers, action_headers, preset):

    page = requests.get("https://www.urban-rivals.com/collection/", headers=navigation_headers, cookies=cookies, params={'view':'deck'})
    tree = html.fromstring(page.content)
    presets_id = [j.attrib.get("value") for j in tree.xpath('//select[@name="id_deck"]/option')]

    pages = []
    for preset_id in presets_id:
        ret = requests.post('https://www.urban-rivals.com/ajax/collection/load_deck.php', headers=action_headers, cookies=cookies, params={'id_deck':str(preset_id)})
        if "error" in ret.text:
            pages.append("")
        else:
            pages.append(requests.get("https://www.urban-rivals.com/collection/", headers=navigation_headers, cookies=cookies, params={'view':'deck'}))


    for i in range(len(pages)):
        page = pages[i]
        if page == "": 
            continue

        tree = html.fromstring(page.content)
        characters = [j.replace("/game/characters/?id_perso=",'').replace("&id_pj=%23",' ').replace('-', ' ').split(' ')[0] for j in  tree.xpath('//a[contains(@class, "card-layer layer-")]/@href')]
        characters_level = [int(str(j[-12:-11])) for j in tree.xpath('//img[@class="card-picture js-lazyload"]/@data-original')]
        preset_name = tree.xpath('//button[@class="btn btn-danger js-form-delete-deck"]/@data-presetname')

        for char in preset:
            for j in range(len(characters)):
                if str(characters[j])==str(char[0]) and str(characters_level[j])==str(char[1]):
                    del characters[j]
                    del characters_level[j]
                    break
        if len(characters)==0 and len(characters_level)==0:
            return int(presets_id[i])
    return 0

###
# Gives a preset id given it's name
###
def id_from_name(cookies, navigation_headers, preset_name):
    page = requests.get("https://www.urban-rivals.com/collection/", headers=navigation_headers, cookies=cookies, params={'view':'deck'})
    tree = html.fromstring(page.content)
    presets = tree.xpath('//select[@name="id_deck"]/option')
    presets_name = [j.attrib.get("data-preset-name") for j in presets]
    presets_id = [j.attrib.get("value") for j in presets]

    for i in range(len(presets_name)):
        if presets_name[i]==preset_name:
            return int(presets_id[i])
    return 0

###
# Imports a preset if it does not already exists in user's presets, then set it as active deck
###
def set_deck(cookies, headers, preset_id):
    if preset_id>0:
        requests.post('https://www.urban-rivals.com/ajax/collection/load_deck.php', headers=headers, cookies=cookies, params={'id_deck':str(preset_id)})
    print("Preset "+str(preset_id)+" set as active deck.")

###
# Saves every preset the user has
###
def export_decks(cookies, navigation_headers, action_headers, decks_path):
    page = requests.get("https://www.urban-rivals.com/collection/", headers=navigation_headers, cookies=cookies, params={'view':'deck'})
    tree = html.fromstring(page.content)
    presets_id = [j.attrib.get("value") for j in tree.xpath('//select[@name="id_deck"]/option')]

    pages = []
    for preset_id in presets_id:
        ret = requests.post('https://www.urban-rivals.com/ajax/collection/load_deck.php', headers=action_headers, cookies=cookies, params={'id_deck':str(preset_id)})
        if "error" in ret.text:
            pages.append("")
        else:
            pages.append(requests.get("https://www.urban-rivals.com/collection/", headers=navigation_headers, cookies=cookies, params={'view':'deck'}))


    for i in range(len(pages)):
        page = pages[i]
        if page == "": 
            continue

        tree = html.fromstring(page.content)
        characters = [j.replace("/game/characters/?id_perso=",'').replace("&id_pj=%23",' ').replace('-', ' ').split(' ')[0] for j in  tree.xpath('//a[contains(@class, "card-layer layer-")]/@href')]
        characters_level = [int(str(j[-12:-11])) for j in tree.xpath('//img[@class="card-picture js-lazyload"]/@data-original')]
        preset_name = tree.xpath('//button[@class="btn btn-danger js-form-delete-deck"]/@data-presetname')[0]
        

        if os.path.exists(decks_path):
            deck_str=str(preset_name)+"\n"
            for j in range(len(characters)):
                deck_str+=str(characters[j])+" "+str(characters_level[j])+"\n"
            with open(os.path.join(decks_path, re.sub('[^A-Za-z0-9]+', '_', preset_name)+".txt"), 'w') as f:
                f.write(deck_str)
                f.close()

        print("Saved preset \""+str(preset_name)+"\" to '"+str(os.path.join(decks_path, re.sub('[^A-Za-z0-9]+', '_', preset_name)))+".txt'")