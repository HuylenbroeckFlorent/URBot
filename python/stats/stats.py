import sys
import requests
from lxml import html

def stats(cookies, headers):
    session_requests = requests.session()
    page = session_requests.get('https://www.urban-rivals.com/player/?id_player=3527368', headers=headers, cookies=cookies)
    tree = html.fromstring(page.content)
    data = tree.xpath("//div/span/@data-counter")
    with open('D:/Documents/GitHub/URBot/stats.txt', 'w') as f:
        f.write(data[0]+'\n')
        f.write(data[1]+'\n')
        f.write(data[2]+'\n')
        f.write(data[3]+'\n')
        f.write(data[4]+'\n')
        f.write(data[5]+'\n')
        f.close()