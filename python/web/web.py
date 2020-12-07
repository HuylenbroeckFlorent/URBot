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
# 5 - Right click the site request (the request that has the URL that matches yours : https://www.urban-rivals.com/) and go to copy -> copy as cURL (windows) (or shell).
# 6 - Go to this site which converts cURL into python requests: https://curl.trillworks.com/
# 7 - Take the generated cookies and headers (do not change params).
###

cookies = {
    'collection-filters': '^{^%^22nb_per_page^%^22:^%^2248^%^22^}',
    'cnil': 'true',
    'ur_token': '6445b56898ad4f22815ddfc17bd4ee4e05fc679df',
    'UR_SESSID': '2decf21bb2e310a3201ad127d198c0b5',
    'csrf-token': 'ea77526432e9dd7111120b85e784981a602518863a1f6f9eb40243d9e67e69e9',
}

headers = {
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36 OPR/72.0.3815.400',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-User': '?1',
    'Sec-Fetch-Dest': 'document',
    'Referer': 'https://www.urban-rivals.com/',
    'Accept-Language': 'en-GB,en;q=0.9,fr;q=0.8,en-US;q=0.7',
}
