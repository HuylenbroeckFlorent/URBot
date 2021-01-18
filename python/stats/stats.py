import sys
import requests
from lxml import html

def get_player_page_data(cookies, headers, player_data_file_path):
    session_requests = requests.session()
    page = session_requests.get('https://www.urban-rivals.com/player/?id_player=3527368', headers=headers, cookies=cookies)
    tree = html.fromstring(page.content)
    data = tree.xpath("//div/span/@data-counter")

    with open(player_data_file_path, 'w') as f:
        f.write(data[0]+'\n')
        f.write(data[1]+'\n')
        f.write(data[2]+'\n')
        f.write(data[3]+'\n')
        f.write(data[4]+'\n')
        f.write(data[5]+'\n')
        f.close()