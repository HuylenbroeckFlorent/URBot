import sys
import requests
from lxml import html

def get_player_page_data(cookies, headers):
    session_requests = requests.session()
    page = session_requests.get('https://www.urban-rivals.com/player/?id_player=3527368', headers=headers, cookies=cookies)
    tree = html.fromstring(page.content)
    data = tree.xpath("//div/span/@data-counter")

    return [int(j) for j in data]