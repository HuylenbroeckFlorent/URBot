### https://stackoverflow.com/a/61140905
# To generate cookies in cookies.py :
#
# 1 - Go to https://www.urban-rivals.com/ and login.
# 2 - Open your browser's developper tools (F12).
# 3 - Go to the network tab.
# 4 - Refresh the page.
# 5 - Right click the site request (the request that has the URL that matches yours : https://www.urban-rivals.com/) and go to copy -> copy as cURL(cmd) (might be (windows) or else).
# 6 - Go to this site which converts cURL into python requests: https://curl.trillworks.com/
# 7 - Take the generated cookies and place them in a file at the same level as this one called 'cookies.py'.
#
# It should look like this :
#
# cookies = {
#     'collection-filters': '^{^%^22nb_per_page^%^22:^%^2248^%^22^}',
#     'cnil': 'true',
#     'ur_token': 'long alphanumeric string',
#     'UR_SESSID': 'long alphanumeric string',
#     'csrf-token': 'long alphanumeric string',
# }
#
###

### https://stackoverflow.com/a/61140905
# To generate navigation_headers :
#
# 1 - Go to https://www.urban-rivals.com/ and login.
# 2 - Open your browser's developper tools (F12).
# 3 - Go to the network tab.
# 4 - Refresh the page.
# 5 - Right click the site request (the request that has the URL that matches yours : https://www.urban-rivals.com/) and go to copy -> copy as cURL(cmd) (might be (windows) or else).
# 6 - Go to this site which converts cURL into python requests: https://curl.trillworks.com/
# 7 - Take the generated headers.
###

navigation_headers = {
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36 OPR/73.0.3856.284',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-User': '?1',
    'Sec-Fetch-Dest': 'document',
    'Referer': 'https://www.urban-rivals.com/',
    'Accept-Language': 'en-GB,en;q=0.9,fr;q=0.8,en-US;q=0.7',
}

### https://stackoverflow.com/a/61140905
# To generate action_headers :
#
# 1 - Go to https://www.urban-rivals.com/ and login.
# 2 - Go to your collection and proceed selling a character. Stop before clicking the "sell" button.
# 3 - Open your browser's developper tools (F12).
# 4 - Go to the network tab.
# 5 - Click the sell button.
# 6 - Right click request (https://www.urban-rivals.com/ajax/collection/sell_card.php) and go to copy -> copy as cURL(cmd) (might be (windows) or else).
# 7 - Go to this site which converts cURL into python requests: https://curl.trillworks.com/
# 8 - Take the generated headers.
###

action_headers = {
    'Connection': 'keep-alive',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'X-Csrf-Token': 'a47ca3f967aac7a5f57bd876cfa00b3fab86447afda62b278c9bdeba4c661a39',
    'X-Requested-With': 'XMLHttpRequest',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36 OPR/73.0.3856.284',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'Origin': 'https://www.urban-rivals.com',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Dest': 'empty',
    'Referer': 'https://www.urban-rivals.com/collection/index.php',
    'Accept-Language': 'en-GB,en;q=0.9,fr;q=0.8,en-US;q=0.7',
}