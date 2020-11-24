import sys
import requests
from lxml import html

### https://stackoverflow.com/a/61140905
# To generate cookies and headers :
#
# 1 - Go to https://www.urban-rivals.com/ and login.
# 2 - Open your browser's developper tools (F12).
# 3 - Go to the network tab.
# 4 - Refresh the page.
# 5 - Right click the site request (the request that has the URL that matches yours : https://www.urban-rivals.com/) and go to copy -> copy as cURL (windows).
# 6 - Go to this site which converts cURL into python requests: https://curl.trillworks.com/
# 7 - Take the generated cookies and headers (do not change params).
###

cookies = {
    'collection-filters': '{%22nb_per_page%22:%2248%22}',
    'cnil': 'true',
    'viewed_profiles': '35277531%3A8389552%3A2770112%3A5149178%3A3548482%3A9045164%3A30975598%3A415543%3A7124194%3A601538%3A2509997%3A614458%3A35438649%3A8224566',
    'ur_token': '2acc96fef5c56ffcdc5b60c173db87f205fbd3888',
    'UR_SESSID': '480d2a98cf690f9ac01adaccf1987e07',
    'csrf-token': '33130b45565cbed2754fcfde254fa86d724fae6cc6fc88b50a72d9d120731959',
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
    ('page', '0')
)

def retrieve_prices(sortby='date', orderby='desc', group='evolve', nb_per_page='48'):
    global params
    session_requests = requests.session()
    params = (*params, ('sortby',sortby))
    params = (*params, ('orderby',orderby))
    params = (*params, ('group',group))
    params = (*params, ('nb_per_page',nb_per_page))
    cookies['collection-filters']='{%22nb_per_page%22:%22'+nb_per_page+'%22}'
    #print(cookies)
    print(params)
    page = session_requests.get('https://www.urban-rivals.com/collection/index.php', headers=headers, params=params, cookies=cookies)
    tree = html.fromstring(page.content)
    card_prices = tree.xpath('//small[@class="card-price"]/text()')
    with open('D:/Documents/URBot/prices.txt', 'w') as f:
        i=0
        for price in card_prices:
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
                break

if __name__ == '__main__':
    if len(sys.argv)==5:
        retrieve_prices(sortby=sys.argv[1], orderby=sys.argv[2], group=sys.argv[3], nb_per_page=sys.argv[4])
    elif len(sys.argv)==1:
        retrieve_prices()
