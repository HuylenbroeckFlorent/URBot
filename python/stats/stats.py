import sys
import requests
from lxml import html

i=0
params = (
    ('deck_format', '54363'),
    ('showmytournament', '1'),
    ('page',i)
)

def stats(cookies, headers):
    session_requests = requests.session()
    page = session_requests.get('https://www.urban-rivals.com/player/?id_player=3527368', headers=headers, cookies=cookies)
    tree = html.fromstring(page.content)
    data = tree.xpath("//div/span/@data-counter")
    print(str(data))
    with open('D:/Documents/URBot/stats.txt', 'w') as f:
        f.write(data[0]+'\n')
        f.write(data[1]+'\n')
        f.write(data[2]+'\n')
        f.write(data[3]+'\n')
        f.write(data[4]+'\n')
        f.write(data[5]+'\n')
        f.close()

    #page = session_requests.get('https://www.urban-rivals.com/game/rankings/history/tournaments.php', headers=headers, params=params, cookies=cookies)
       

if __name__ == '__main__':
    stats()
