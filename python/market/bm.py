import sys
import os
import grequests
import requests
from lxml import html
import getpass
import math
import random

working_dir_path = os.getcwd()

def rarity_avg_price(cookies, headers, rarity, filter_new_blood=True, rejected_ids=[]):
    ids = []
    new_bloods_filter = []
    if filter_new_blood==True:
        new_bloods_filter=new_bloods(cookies, headers)

    if os.path.exists(os.path.join(working_dir_path, "data", "chars_data.txt")):
        with open(os.path.join(working_dir_path, "data", "chars_data.txt"), 'r') as f:
            previous_name = ""
            for line in f.readlines():
                if line.strip(' \n')!="":
                    line.replace('\n','')
                    line_split=line.split(' ')
                    if line_split[3]==rarity and int(line_split[0]) not in rejected_ids and int(line_split[0]) not in new_bloods_filter:
                        if line_split[1]!=previous_name:
                            #print(line_split[0]+" "+line_split[1]) #DEBUG
                            ids.append(line_split[0])
                            previous_name=line_split[1]
            f.close()

    rs=[]
    for i in ids:
        rs.append(grequests.get('https://www.urban-rivals.com/market/?id_perso='+str(int(i)), headers=headers, cookies=cookies))

    pages = grequests.map(rs, size=100)

    total_char = len(pages)
    total_clintz = 0

    data = []
    prices = []
    mean_price = 0
    median_price = 0

    for i in range(len(pages)):
        page = pages[i]
        tree = html.fromstring(page.content)
        tmp_price=0
        try:
            tmp_price = str(tree.xpath('//td[@class="align-middle" and img/@title="Clintz"]/text()')[0]).replace('\n','')
        except IndexError:
            tmp_price = []
        if tmp_price == []:
            data.append((ids[i], 0))
        else:
            tmp_price = tmp_price.replace(' ','')
            data.append((ids[i], int(tmp_price)))
            prices.append(int(tmp_price))
            mean_price+=int(tmp_price)

    mean_price = int(mean_price/len(pages))

    prices = sorted(prices)
    median_price = prices[int(len(prices)/2)]

    print("Mean price for rarity '"+rarity+"' is "+f"{mean_price:,}")
    print("Median price for rarity '"+rarity+"' is "+f"{median_price:,}")

    return prices

def new_bloods(cookies, headers):
    page = requests.get("https://www.urban-rivals.com/game/newblood.php", cookies=cookies, headers=headers)
    tree = html.fromstring(page.content)
    new_bloods = tree.xpath('//a[contains(@href, "/game/characters/?id_perso=")]/@href')
    new_bloods = [int(j[-4:].strip("=")) for j in new_bloods]

    return new_bloods

def crs_avg_price(cookies, headers, category=0):
    ids = []
    n=category
    categories = [0,0,0]
    for i in range(len(categories)):
        categories[i] = n%(2**(i+1))
        n-=n%(2**(i+1))

    if os.path.exists(os.path.join(working_dir_path, "data", "crs_data.txt")):
        with open(os.path.join(working_dir_path, "data", "crs_data.txt"), 'r') as f:
            previous_id = 0
            for line in f.readlines():
                if line.strip(' \n')!="":
                    line.replace('\n','')
                    line_split=line.split(' ')
                    if int(line_split[0])!=previous_id:
                        if line_split[1].strip(" \n")=='1' and categories[0]>0:
                            ids.append(line_split[0])
                        elif line_split[1].strip(" \n")=='2' and categories[1]>0:
                            ids.append(line_split[0])
                        elif line_split[1].strip(" \n")=='3' and categories[2]>0:
                            ids.append(line_split[0])
                        previous_id=int(line_split[0])
            f.close()

    rs=[]
    for i in ids:
        rs.append(grequests.get('https://www.urban-rivals.com/market/?id_perso='+str(int(i)), headers=headers, cookies=cookies))

    pages = grequests.map(rs, size=100)

    total_char = len(pages)
    total_clintz = 0

    prices = []
    mean_price = 0
    median_price = 0

    for i in range(len(pages)):
        page = pages[i]
        tree = html.fromstring(page.content)
        tmp_price=0
        try:
            tmp_price = str(tree.xpath('//td[@class="align-middle" and img/@title="Clintz"]/text()')[0]).replace('\n','')
        except IndexError:
            tmp_price = []
        if tmp_price == []:
            continue
        else:
            tmp_price = tmp_price.replace(' ','')
            prices.append(int(tmp_price))
            mean_price+=int(tmp_price)

    mean_price = int(mean_price/len(pages))

    sorted_prices = sorted(prices)
    median_price = prices[int(len(sorted_prices)/2)]

    if category == 1:
        print("Mean price for $ collectors is "+f"{mean_price:,}")
        print("Median price for $ collectors is "+f"{median_price:,}")
    elif category == 2:
        print("Mean price for $$ collectors is "+f"{mean_price:,}")
        print("Median price for $$ collectors is "+f"{median_price:,}")
    elif category == 4:
        print("Mean price for $$$ collectors is "+f"{mean_price:,}")
        print("Median price for $$$ collectors is "+f"{median_price:,}")
    elif category == 7:
        print("Mean price for collectors is "+f"{mean_price:,}")
        print("Median price for collectors is "+f"{median_price:,}")

    return prices


def crypto_avg_price(cookies, headers, pack_price):
    ids = []
    cr_mult = []

    if os.path.exists(os.path.join(working_dir_path, "data", "crs_data.txt")):
        with open(os.path.join(working_dir_path, "data", "crs_data.txt"), 'r') as f:
            previous_id = 0
            for line in f.readlines():
                if line.strip(' \n')!="":
                    line.replace('\n','')
                    line_split=line.split(' ')
                    if int(line_split[0])!=previous_id:
                        if line_split[1].strip(" \n")=='1':
                            cr_mult.append(65)
                        elif line_split[1].strip(" \n")=='2':
                            cr_mult.append(25)
                        elif line_split[1].strip(" \n")=='3':
                            cr_mult.append(10)
                        elif line_split[1].strip(" \n")=='4':
                            cr_mult.append(10)

                        ids.append(line_split[0])
                        previous_id=int(line_split[0])
            f.close()

    rs=[]
    for i in ids:
        rs.append(grequests.get('https://www.urban-rivals.com/market/?id_perso='+str(int(i)), headers=headers, cookies=cookies))

    pages = grequests.map(rs, size=100)

    total_char = len(pages)
    total_clintz = 0

    prices = []
    mean_price = 0
    median_price = 0

    for i in range(len(pages)):
        page = pages[i]
        tree = html.fromstring(page.content)
        tmp_price=0
        try:
            tmp_price = str(tree.xpath('//td[@class="align-middle" and img/@title="Clintz"]/text()')[0]).replace('\n','')
        except IndexError:
            tmp_price = []
        if tmp_price == []:
            continue
        else:
            tmp_price = tmp_price.replace(' ','')
            prices.append(int(tmp_price))
            mean_price+=int(tmp_price)

    mean_price = int(mean_price/len(pages))

    sorted_prices = sorted(prices)
    median_price = prices[int(len(sorted_prices)/2)]

    print("Mean price for collectors is "+f"{mean_price:,}")
    print("Median price for collectors is "+f"{median_price:,}"+'\n')

    weighted_prices = []
    for i in range(len(prices)):
        for j in range(cr_mult[i]):
            weighted_prices.append(prices[i])

    weighted_mean_price = int(sum(weighted_prices)/len(weighted_prices))
    cryptocoinz_price = (weighted_mean_price/pack_price)

    print("1 cryptocoinz = "+f"{round(cryptocoinz_price):,}"+" clintz if packs cost "+str(pack_price)+" cryptocoinz")
    print("Mean price for crypto pack is "+f"{weighted_mean_price:,}"+'\n')

    return weighted_prices


def open_wheel(cookies, headers, wheel_file, crypto_pack_price):
    wheel=[]
    weights=[]

    total = 0
    total_slot = 0

    tickets_slot = 0
    
    with open(wheel_file, 'r') as f:
        for line in f.readlines():
                if line.strip(' \n')!="":
                    line.replace('\n','')
                    line_split=line.split(' ')
                    if line_split[0]=="jackpot":
                        for i in range(int(line_split[1])):
                            wheel.append(1250000)
                            weights.append(1/30)
                    elif line_split[0]=="ticket":
                        for i in range(int(line_split[1])):
                            wheel.append('t')
                            weights.append(0.01)
                    elif line_split[0]=="respin":
                        for i in range(int(line_split[1])):
                            wheel.append('r')
                            weights.append(0.01)
                    elif line_split[0]=="crypto":
                        weighted_prices = crypto_avg_price(cookies, headers, crypto_pack_price)
                        weighted_mean_price = int(sum(weighted_prices)/len(weighted_prices))
                        cryptocoinz_price = int(weighted_mean_price/int(crypto_pack_price))
                        for crypto_amount in [int(j) for j in line_split[1:]]:
                            wheel.append(crypto_amount*cryptocoinz_price)
                            weights.append(1/30)
                    elif line_split[0]=="$$$":
                        prices = crs_avg_price(cookies, headers, category=4)
                        for i in range(int(line_split[1])):
                            wheel.append(prices)
                            weights.append(1/30)
                    elif line_split[0]=="$$":
                        prices = crs_avg_price(cookies, headers, category=2)
                        for i in range(int(line_split[1])):
                            wheel.append(prices)
                            weights.append(1/30)
                    elif line_split[0]=="$":
                        prices = crs_avg_price(cookies, headers, category=1)
                        for i in range(int(line_split[1])):
                            wheel.append(prices)
                            weights.append(1/30)
                    elif line_split[0]=="clintz":
                        for clintz_amount in [int(j) for j in line_split[1:]]:
                            wheel.append(clintz_amount)
                            weights.append(1/30)
                    else:
                        prices = rarity_avg_price(cookies, headers, line_split[0])
                        for i in range(int(line_split[1])):
                            wheel.append(prices)
                            weights.append(1/30)

    mean = 0
    for i in wheel:
        if isinstance(i, list):
            mean += sum(i)/len(i)
        elif isinstance(i,int):
            mean += i
    mean = round((mean/30)*1.02)

    print("Mean price for ticket is "+f"{mean:,}"+" clintz.")

    return wheel, weights

def BM(prices, n, value, n_sample=100000, weighted=False, weights=[]):
    t=0
    prob=0

    while t<n_sample:
        t+=1
        tmp_sum = 0
        i=0
        while i<n:
            tmp=None
            if weighted==True:
                tmp = random.choices(prices, weights=weights, k=1)[0]
            else:
                tmp = random.choice(prices)
            if isinstance(tmp, list):
                tmp = random.choice(tmp)
            elif tmp=='r':
                continue
            elif tmp=='t':
                i=-1
                continue
            i+=1
            tmp_sum+=tmp
        if tmp_sum > value:
            prob+=1
        sys.stdout.write("\rBM profit probability is {:3.1%} for investment of ".format(round(prob/t, 3))+f"{value:,}"+" clintz.   ")
        sys.stdout.flush()