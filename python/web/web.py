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
    'ur_token': 'fd4ccfdc2f969f41e5bcbc295f99b32d05fd8fbc5',
    'UR_SESSID': 'a3c73ea96a87c337201acdd581990f90',
    'csrf-token': 'e38dac2fdf4f3e1135709c469e80c98018780b18d3ec2f697b7c3806cdab3a19',
}

navigation_headers = {
    'Connection': 'keep-alive',
    'Cache-Control': 'max-age=0',
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

action_headers = {
    'Connection': 'keep-alive',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'X-Csrf-Token': 'bbd502630f107b688dbdf880612cf1e9ae8442c53dbb0032507edf7615521e3a',
    'X-Requested-With': 'XMLHttpRequest',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36 OPR/72.0.3815.400',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'Origin': 'https://www.urban-rivals.com',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Dest': 'empty',
    'Referer': 'https://www.urban-rivals.com/collection/index.php?view=collection^&page=0^&sortby=date^&orderby=desc^&group=evolve^&nb_per_page=48',
    'Accept-Language': 'en-GB,en;q=0.9,fr;q=0.8,en-US;q=0.7',
}
