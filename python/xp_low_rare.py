import sys
import os
import grequests
import requests
from lxml import html
import getpass

from web.headers import navigation_headers, action_headers
import collection.collection as collection

###
# This code got me banned.
###

###
# Levels characters given a to_level_path file.
###
def xp_cards(cookies, action_headers, to_xp, pay_for_xp=False, verbose=False, log=False):
    to_level=[]
    xp_reserve=0

    lines=to_xp.split('\n')
    if len(lines)>0: # Retrieve xp reserve
        print("Adding xp to underleveled cards...")
        ret = requests.post('https://www.urban-rivals.com/ajax/collection/', headers=action_headers, cookies=cookies, data={'action':'addXPForClintz', 'characterInCollectionID':0, 'buyXP':'true'})
        ret = ret.text.split(':')
        for i in range(len(ret)):
            if ret[i]=="{\"currentXP\"":
                xp_reserve=int(ret[i+1].split(',')[0])
                break
        for line in lines:
            line=line.strip('\n')
            if line!='':
                to_level.append(line)

    if len(to_level)==0:
        print("No card to level up.")
        return

    rs_xp = []
    xp_tiers=[500,1500,3000,5000]
    total_cards=0
    total_clintz=0

    for line in to_level:
        line_split=line.split(' ')
        char_level = int(line_split[1])
        for i in range(int(line_split[2])-char_level):
            xp_index = char_level-1+i
            if xp_reserve>xp_tiers[xp_index]:
                data={}
                data['action'] = 'addxpfromreserve'
                data['characterInCollectionID'] = line_split[0]
                ret = requests.post('https://www.urban-rivals.com/ajax/collection/', headers=action_headers, cookies=cookies, data=data)
                ret = ret.text.split(':')
                prev_xp_reserve = xp_reserve
                for i in range(len(ret)):
                    if ret[i]=="{\"currentXP\"":
                        xp_reserve=int(ret[i+1].split(',')[0])
                if verbose==True:
                    print("\t\tGave "+f"{prev_xp_reserve-xp_reserve:,}"+"xp to "+line_split[0]+", "+str(xp_reserve)+"xp remain in reserve.")
                total_cards+=1
            elif pay_for_xp == True:
                if xp_reserve>0:
                    data={}
                    data['action'] = 'addxpfromreserve'
                    data['characterInCollectionID'] = line_split[0]
                    requests.post('https://www.urban-rivals.com/ajax/collection/', headers=action_headers, cookies=cookies, data=data)
                    if verbose==True:
                        print("\t\tGave "+f"{xp_reserve:,}"+"xp to "+line_split[0]+", reserve is now empty.")
                    print("\tPreparing requests...")
                    data={}
                    data['action'] = 'addXPForClintz'
                    data['characterInCollectionID'] = line_split[0]
                    data['buyXP'] = 'true'
                    rs_xp.append(grequests.post('https://www.urban-rivals.com/ajax/collection/', headers=action_headers, cookies=cookies, data=data))                             
                    if verbose==True:
                        print("\t\tPreparing to add "+f"{xp_tiers[xp_index]-xp_reserve:,}"+"xp to "+line_split[0]+".")
                    total_cards+=1
                    total_clintz+=(xp_tiers[xp_index]-xp_reserve)*2
                    xp_reserve=0
                else:
                    data={}
                    data['action'] = 'addXPForClintz'
                    data['characterInCollectionID'] = line_split[0]
                    data['buyXP'] = 'true'
                    rs_xp.append(grequests.post('https://www.urban-rivals.com/ajax/collection/', headers=action_headers, cookies=cookies, data=data))
                    if verbose==True:
                        print("\t\tPreparing to add "+f"{xp_tiers[xp_index]:,}"+"xp to "+line_split[0]+".")
                    total_cards+=1
                    total_clintz+=xp_tiers[xp_index]*2

    if verbose == True:
        sys.stdout.write("\tSending requests...")
        sys.stdout.flush() 

    logs = grequests.map(rs_xp, size=100)

    if verbose == True:
        sys.stdout.write("\r\tRequests sent.       \n")
        sys.stdout.flush() 

    if log==True:
        xp_file=""
        for xp in logs:
            xp_file+=xp.text[0:101]+'\n'
        if not os.path.exists(os.path.join(working_dir_path, "data", "logs")):
            os.mkdir(os.path.join(working_dir_path, "data", "logs"))
        with open(os.path.join(working_dir_path, "data", "logs", "logs_xp.txt"), 'w') as f:
            f.write(xp_file)
            f.close()

    prnt_str = str(total_cards)+" cards leveled up"
    if pay_for_xp == True:
        prnt_str+= " for a total cost of "+str(total_clintz)+" clintz."
    else:
        prnt_str+= "."
    print(prnt_str)

if __name__ == '__main__':
	###
	# Generating cookies
	###
	cookies={}

	while not cookies: #Empty dict evaluates to false

		signin_data = {
			'action':'signin',
		}
		print()
		signin_data['login'] = input("Player's username : ")
		signin_data['password'] = getpass.getpass("Player's password : ")
		signin = requests.post('https://www.urban-rivals.com/ajax/player/account/', headers=action_headers, data=signin_data)

		if "Unable" in str(signin.content):
			try:
				print("Invalid username or password.\nPress any key to try again.\nPress CTRL+C to abort.")
				input()
			except KeyboardInterrupt:
				sys.exit(0)
		else:
			for cookie in signin.cookies:
				cookies[cookie.name]=cookie.value

		player_collection = collection.Collection(cookies, navigation_headers, verbose=True)

		to_xp = ""

		with open("data/to_sell.txt", 'r') as f:
			for line in f:
				line_split = line.split(' ')
				if int(line_split[0]) in player_collection.char_list.keys():
					if int(line_split[1]) in [x[0] for x in player_collection.char_list[int(line_split[0])].player_char_ids]:
						#if player_collection.char_list[int(line_split[0])].rarity in ['c','u','r']:
						print("HIT : "+str(player_collection.char_list[int(line_split[0])].name)+" ("+str(player_collection.char_list[int(line_split[0])].rarity)+")")
						to_xp+=line_split[1]+" 1 5 \n"

		xp_cards(cookies, action_headers, to_xp, True, True, False)
