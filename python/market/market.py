import sys
import os
import grequests
import requests
from lxml import html

###
# Sells every card described in a to_sell_path file.
###
def sell_cards(cookies, navigation_headers, action_headers, to_sell_path, verbose=False, log=False):

    to_sell = []

    if os.path.exists(os.path.join(to_sell_path)):
        with open(to_sell_path, 'r') as f:
            for line in f.readlines():
                line=line.strip('\n')
                if line!='':
                    to_sell.append(line)
        os.remove(to_sell_path)
    else:
        print("No card to sell.")
        return

    if len(to_sell)>1:
        print("Selling cards ...")

        processed_index = 0
        sales_file=""
        total=0
        total_cards=-1

        while processed_index < len(to_sell):

            rs_prices = []
            previous_id=0

            for i in range(processed_index, len(to_sell)):
                line = to_sell[i]
                line_split=line.strip(' ').split(' ')
                if len(line_split)>3:
                    continue
                if int(line_split[0])!=previous_id:
                    if previous_id > 0:
                        rs_prices.append(grequests.get('https://www.urban-rivals.com/market/?id_perso='+str(int(previous_id)), headers=navigation_headers, cookies=cookies))
                    previous_id=int(line_split[0])
                    if i>processed_index+100:
                        break
                       
            if verbose == True:
                sys.stdout.write("\tRetrieving price for "+str(len(rs_prices))+" characters...")
                sys.stdout.flush()

            prices_pages = grequests.map(rs_prices, size=100)

            if verbose == True:
                sys.stdout.write("\r\tCharacters prices retrieved.                           \n")
                sys.stdout.flush() 
                print("\tPreparing offers...")

            rs_sales = []
            sales = []
            previous_id=0
            previous_name=""
            previous_buyer=""
            price_index=0

            for i in range(processed_index, len(to_sell)):
                line = to_sell[i]
                line_split=line.strip(' ').split(' ')
                if int(line_split[0])!=previous_id:
                    if previous_id!=0:
                        price = 0

                        if len(previous_buyer)==0:
                            page = prices_pages[price_index]
                            price_index+=1
                            tree = html.fromstring(page.content)
                            tmp_price=0
                            try:
                                tmp_price = str(tree.xpath('//td[@class="align-middle" and img/@title="Clintz"]/text()')[0]).replace('\n','')
                            except IndexError:
                                tmp_price = []
                            if tmp_price == []:
                                price = 2000000000
                            else:
                                tmp_price = tmp_price.replace(' ','')
                                price = int(tmp_price)-1
                        
                        
                        if len(previous_buyer)==0:
                            total+=len(sales)*price
                            if verbose == True:
                                print("\t\t{:4d}x {:22s} {:21s} {:16s}".format(len(sales), str(previous_name)+" ("+str(previous_id)+")", "price="+f"{price:,}"+"/u", "total="+f"{len(sales)*price:,}"))
                        else:
                            total+=len(sales)*previous_price
                            if verbose == True:
                                print("\t\t{:4d}x {:22s} {:21s} {:16s} TO: {:33s}".format(len(sales), str(previous_name)+" ("+str(previous_id)+")", "price="+f"{previous_price:,}"+"/u", "total="+f"{len(sales)*previous_price:,}", previous_buyer))


                        for j in range(len(sales)):
                            data = {}
                            data['id_perso_joueur']=str(sales[j])
                            if len(previous_buyer)==0:
                                data['action'] = 'sellToPublic'
                                data['price'] = str(price)         
                                rs_sales.append(grequests.post('https://www.urban-rivals.com/ajax/collection/sell_card.php', data=data, cookies=cookies, headers=action_headers))
                            else:
                                data['action'] = 'sellToFriend'
                                data['buyer_name'] = previous_buyer
                                data['price'] = previous_price
                                rs_sales.append(grequests.post('https://www.urban-rivals.com/ajax/collection/sell_card.php', data=data, cookies=cookies, headers=action_headers))

                    previous_id=int(line_split[0])
                    previous_name=line_split[2].strip('\n')
                    if len(line_split)>4:
                        previous_buyer=line_split[3]
                        previous_price=int(line_split[4])
                    else:
                        previous_buyer=""
                        previous_price=2000000000
                    sales=[]
                    sales.append(line_split[1])
                    if i>processed_index+100:
                        processed_index=i
                        break
                else:
                    sales.append(line_split[1])

                total_cards+=1

                if i==len(to_sell)-1:
                    processed_index = len(to_sell)
                    break

            if verbose == True:
                sys.stdout.write("\tSending offers...")
                sys.stdout.flush() 

            logs = grequests.map(rs_sales, size=100)

            if log==True:
                for sale in logs:
                    sales_file+=sale.text+"\n"

            if verbose == True:
                sys.stdout.write("\r\tOffers sent.       \n")
                sys.stdout.flush() 

        if log==True:
            if not os.path.exists(os.path.join(working_dir_path, "data", "logs")):
                os.mkdir(os.path.join(working_dir_path, "data", "logs"))
            with open(os.path.join(working_dir_path, "data", "logs", "logs_sales.txt"), "w") as f:  
                f.write(sales_file)
                f.close()

        print(str(total_cards)+" cards put for sale. Total value : "+f"{total:,}"+" clintz.")

###
# Cancels every current market sales.
###
def cancel_all_sales(cookies, navigation_headers, action_headers, verbose=False, log=False):
    print('Cancelling current market offers...')
    session_requests = requests.session()
    page = session_requests.get('https://www.urban-rivals.com/market/?action=currentsale', headers=navigation_headers, cookies=cookies)
    tree = html.fromstring(page.content)
    max_page = 0
    tmp_max_page = [int(i) for i in tree.xpath('//a[i/@class="fas fa-angle-double-right"]/@data-page')]
    if tmp_max_page == []:
        max_page=0
    else:
        max_page = max(tmp_max_page)

    rs_pages = []
    for i in range(max_page+1):
        rs_pages.append(grequests.get('https://www.urban-rivals.com/market/?action=currentsale', headers=navigation_headers, cookies=cookies, params={'page':str(i)}))

    pages = grequests.map(rs_pages, size=100)

    rs_ids = []
    total=0
    cancels = ""
    for page in pages:
        tree = html.fromstring(page.content)
        char_ids = tree.xpath('//div[@class="bg-light market-card media media-card-purchase mb-1"]/div/a/@href')
        if char_ids == []:
            char_ids = tree.xpath('//div[@class="bg-light market-card-single media media-card-purchase mb-1"]/div/a/@href')

        for j in char_ids:
            char_id = str(j).split('=')[1].strip(" \n")
            data={}
            data['action']='cancel_all_sales'
            data['id']=char_id
            rs_ids.append(grequests.post('https://www.urban-rivals.com/ajax/market/', data=data, cookies=cookies, headers=action_headers))
            total+=1
            if verbose == True:
                sys.stdout.write("\r\tFound offers for %i different characters." % total)
                sys.stdout.flush()
            

    if len(rs_ids)>0:
        if verbose == True:
            sys.stdout.write("\n\tSending cancel requests...")
            sys.stdout.flush()

        logs = grequests.map(rs_ids)

        if verbose == True:
            sys.stdout.write("\r\tCancel requests sent.     \n")
            sys.stdout.flush()

    if log==True:
        for l in logs:
            cancels += l.text+'\n'
        if not os.path.exists(os.path.join(working_dir_path, "data", "logs")):
                os.mkdir(os.path.join(working_dir_path, "data", "logs"))
        with open(os.path.join(working_dir_path, "data", "logs", "logs_cancel.txt"),'w') as f:
            f.write(cancels)
            f.close()
    sys.stdout.write("Cancelled offers for %i characters.     \n" % total)
    sys.stdout.flush()

###
# Analyzes the whole sales history and computes the total clintz generated, total card solds and generate a summary of every buyers.
###
def sales_history(cookies, headers, path):
    page = requests.get("https://www.urban-rivals.com/market/history.php", cookies=cookies, headers=headers, params={'action':'salehistory'})
    tree = html.fromstring(page.content)
    max_page = tree.xpath('//a[@class="page-link"]/@data-page')
    max_page = int(max_page[-1])
    
    rs = []
    for i in range(max_page):
        rs.append(grequests.get("https://www.urban-rivals.com/market/history.php", cookies=cookies, headers=headers, params={'action':'salehistory', 'page':str(i)}))

    pages = grequests.map(rs, size=100)

    total = 0
    total_cards = 0
    buyers_total = {'undefined':(0,0)}
    for page in pages:
        tree = html.fromstring(page.content)
        prices = [int(j.replace(' ','').replace('\n','')) for j in tree.xpath('//tr/td[img/@title="Clintz"]/text()') if str(j).strip(' \n')!='']
        buyers = tree.xpath('//tr/td/a[contains(@class, "text-player playerID")]/text()')
        for j in range(len(prices)):
            total_cards+=1
            total+=prices[j]
            try:
                if buyers[j] not in buyers_total:
                    buyers_total[buyers[j]]=(0,0)
            except IndexError:
                buyers_total['undefined']=(buyers_total['undefined'][0]+1,buyers_total['undefined'][1]+prices[j])
                continue
            buyers_total[buyers[j]]=(buyers_total[buyers[j]][0]+1,buyers_total[buyers[j]][1]+prices[j])

    with open(path, 'w', encoding="utf-8") as f:
        f.write("total cards  : "+f"{total_cards:,}"+"\n")
        f.write("total clintz : "+f"{total:,}"+"\n\n")
        f.write("buyers list :\n")
        for buyer, data in sorted(buyers_total.items(), key=lambda x:x[1], reverse=True):
            f.write('\t{:33s} {:4d}  {:10s} \n'.format(buyer, data[0], f"{data[1]:,}"))
        f.close()

    print("Total cards : "+f"{total_cards:,}")
    print("Total clintz : "+f"{total:,}")
    print("Saved buyers list in "+path)