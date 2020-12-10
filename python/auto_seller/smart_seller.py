import sys
import requests
from lxml import html

def sell_card(id_perso_joueur, price, action='sellToPublic', buyer_name=''):
    global params
    
    data = {}
    data['price'] = str(price)+'^'
    data['action'] = str(action)+'^'
    if buyer_name!='':
        data['buyer_name']=str(buyer_name)+'^'
    data['id_perso_joueur']=str(id_perso_joueur)
    ret = requests.post('https://www.urban-rivals.com/ajax/collection/sell_card.php', data=data, cookies=cookies, headers=headers)
    print(ret.text)
    

