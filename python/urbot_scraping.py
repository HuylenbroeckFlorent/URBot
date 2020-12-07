from web.web import cookies, headers
from auto_seller.auto_seller import retrieve_prices
from stats.stats import stats

import sys

if __name__ == '__main__':
    if len(sys.argv)>1:
        if sys.argv[1]=="update" or sys.argv[1]=="stats":
            stats(cookies, headers)
        if sys.argv[1]=="update" or sys.argv[1]=="prices":
            if len(sys.argv)==6:
                retrieve_prices(cookies, headers, sortby=sys.argv[2], orderby=sys.argv[3], group=sys.argv[4], nb_per_page=sys.argv[5])
            elif len(sys.argv)==2:
                retrieve_prices(cookies, headers)

