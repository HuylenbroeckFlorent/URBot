import sys
import requests
from lxml import html

params = (
    ('view', 'collection'),
    ('page', '0')
)

def retrieve_prices(cookies, headers, sortby='date', orderby='desc', group='evolve', nb_per_page='48'):
    global params
    session_requests = requests.session()
    params = (*params, ('sortby',sortby))
    params = (*params, ('orderby',orderby))
    params = (*params, ('group',group))
    params = (*params, ('nb_per_page',nb_per_page))
    cookies['collection-filters']='^{^%^22nb_per_page^%^22:^%^22'+nb_per_page+'^%^22^}'
    #print(cookies)
    print(params)
    page = session_requests.get('https://www.urban-rivals.com/collection/index.php', headers=headers, params=params, cookies=cookies)
    tree = html.fromstring(page.content)
    card_prices = tree.xpath('//small[@class="card-price"]/text()')
    card_rarities = tree.xpath("//div[contains(@class, 'ur-card card-')]/@class")
    with open('D:/Documents/GitHub/URBot/prices.txt', 'w') as f:
        i=0
        for price in card_prices:
            if card_rarities[i] == "ur-card card-c" or card_rarities[i]== "ur-card card-u":
                f.write("0")
                f.close()
                return
            i=i+1
            pricestr = str(price)
            if pricestr == "No Offers":
                pricestr="2000000001"
            priceint = int(''.join(pricestr.split()))
            priceint= priceint-1
            print(priceint)
            f.write(str(priceint))
            if i<int(nb_per_page):
                f.write("\n")
            else:
                f.close()
                return

