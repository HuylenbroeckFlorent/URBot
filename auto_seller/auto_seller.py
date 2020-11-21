import sys
import requests
from lxml import html

cookies = {
    'collection-filters': '{%22nb_per_page%22:%2248%22}',
    'cnil': 'true',
    'UR_SESSID': '8474177eb08d7325e01adb99f1986b57',
    'csrf-token': 'fe7f7f0c1399a3707391207090f67e9720c42584fd0f18208f94baf39224ca8f',
    'ur_token': '8b4640a14975bdfd6c5307ad7e94b1a505fb3f957',
}

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:83.0) Gecko/20100101 Firefox/83.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-GB,en;q=0.5',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Cache-Control': 'max-age=0',
}

params = (
    ('view', 'collection'),
    ('page', '0'),
    ('sortby', 'date'),
    ('orderby', 'desc'),
    ('group', 'evolve'),
    ('nb_per_page', '48'),
)

session_requests = requests.session()
page = session_requests.get('https://www.urban-rivals.com/collection/index.php?view=collection&page=0&sortby=date&orderby=desc&group=evolve&nb_per_page=48', headers=headers, params=params, cookies=cookies)
tree = html.fromstring(page.content)
first_card_prices = tree.xpath('//small[@class="card-price"]/text()')
with open('D:/Documents/URBot/prices.txt', 'w') as f:
    i=0
    for price in first_card_prices:
        i=i+1
        pricestr = str(price)
        priceint = int(''.join(pricestr.split()))
        priceint= priceint-1
        f.write(str(priceint))
        if i<48:
            f.write("\n")
    f.close()
