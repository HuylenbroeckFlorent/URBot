import sys
from os import path
import requests
from lxml import html

###
# Parameters
#       param_cancel_sales : setting this to true will cancel all current market sales before processing the collection.
#       param_keep_evos : setting this to true will enable keeping one card of eache character at each level, else only one card per character will be kept.
#		param_xp : setting this to true will spend clintz to level up underleveled characters.
#       param_sell_doubles : setting this to true will sell every double cards after processing the collection, at an optimal price.
###

param_cancel_sales=False
param_keep_evos=True
param_xp=True
param_sell_doubles=False

### https://stackoverflow.com/a/61140905
# To generate cookies and navigation_headers :
#
# 1 - Go to https://www.urban-rivals.com/ and login.
# 2 - Open your browser's developper tools (F12).
# 3 - Go to the network tab.
# 4 - Refresh the page.
# 5 - Right click the site request (the request that has the URL that matches yours : https://www.urban-rivals.com/) and go to copy -> copy as cURL(cmd) (might be (windows) or else).
# 6 - Go to this site which converts cURL into python requests: https://curl.trillworks.com/
# 7 - Take the generated cookies and headers (do not change params and action_headers).
###

cookies = {
    'cnil': 'true',
    'ur_token': '27afff83d057594efb874f4441a7c03a05fcfbc86',
    'collection-filters': '{%22nb_per_page%22:%2248%22}',
    'viewed_profiles': '24158066',
    'csrf-token': 'ebdc062a13c9d3137907554835e0767894353f4208a19e665d1d1c7108458821',
    'UR_SESSID': '98e86328d7c4cf2a901ad0a50198d898',
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
# 8 - Take the generated headers (do not change params, navigation_headers and cookies).
###

action_headers = {
    'Connection': 'keep-alive',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'X-Csrf-Token': 'ebdc062a13c9d3137907554835e0767894353f4208a19e665d1d1c7108458821',
    'X-Requested-With': 'XMLHttpRequest',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36 OPR/72.0.3815.400',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'Origin': 'https://www.urban-rivals.com',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Dest': 'empty',
    'Referer': 'https://www.urban-rivals.com/collection/pro.php',
    'Accept-Language': 'en-GB,en;q=0.9,fr;q=0.8,en-US;q=0.7',
}

###
# Never change anything past this point.
###

params = (
	('view', 'collection'),
	('sortby', 'date'),
	('orderby', 'desc'),
	('group', 'all'),
	('nb_per_page', '48')
)

###
# Character object. Contains every information about a specific character.
# 		- char_id : id of the character.
#		- quantity : possessed quantity of that character.
# 		- player_char_ids : every iteration of that character stored as (collection_id, level).
# 		- min/max_level : min/max stars of the character.
# 		- name : the character's name, with underscores replacing spaces.
###
class Character:
	def __init__(self, char_id):
		self.char_id=int(char_id)
		self.quantity=0
		self.player_char_ids = []
		self.min_level=0
		self.max_level=0
		self.name=""

	def __str__(self):
		tmp_str = str(self.char_id)+" "+str(self.name.strip('\n'))+" (x"+str(self.quantity)+") "+str(self.min_level)+"*-"+str(self.max_level)+"*"
		for i in self.player_char_ids:
			tmp_str += "\n\t"+str(i[0])+" "+str(i[1])+"*"
		return tmp_str

	def __cmp__(self, other):
		return cmp(self.char_id, other.char_id)

	def __lt__(self, other):
		return self.char_id < other.char_id
###
# Collection object. Contains every single card in the player's collection.
# 		- char_list : list of possessed character.
###
class Collection:
	def __init__(self):
		print('Retrieving collection...')
		print('\tRetrieving raw collection data...')
		self.char_list = {}
		session_requests = requests.session()
		page = session_requests.get('https://www.urban-rivals.com/collection/index.php', headers=navigation_headers, params=params, cookies=cookies)
		tree = html.fromstring(page.content)
		max_page = tree.xpath('//a[i/@class="fas fa-angle-double-right"]/@data-page')
		max_page = int(max_page[0])

		for i in range(0, max_page+1):
			tmp_params = (*params, ('page',str(i)))
			page = session_requests.get('https://www.urban-rivals.com/collection/index.php', headers=navigation_headers, params=tmp_params, cookies=cookies)
			tree = html.fromstring(page.content)
			characters = tree.xpath('//a[img/@class="card-picture js-lazyload"]/@href')
			characters_level = [int(str(j[-12:-11])) for j in tree.xpath('//img[@class="card-picture js-lazyload"]/@data-original')]
			for j in range(len(characters)):
				character = characters[j]
				character = character.replace("/game/characters/?id_perso=",'')
				character = character.replace("&id_pj=%23",' ')
				character = character.replace('-', ' ')
				character_split = character.split(' ')
				
				self.add(int(character_split[0]), int(character_split[1]), int(characters_level[j]))
		print('\tRaw collection data retrieved.')
		self.levels_and_names()
		print('Collection retrieved.')
		self.save()
		


	###
	# Adds a character to the collection, whether if it's a double or a new character.
	###
	def add(self, char_id, player_char_id, level):
		if char_id not in self.char_list:
			self.char_list[int(char_id)]=Character(int(char_id))
		self.char_list[int(char_id)].quantity+=1
		self.char_list[int(char_id)].player_char_ids.append((int(player_char_id),int(level)))
		self.char_list[int(char_id)].player_char_ids.sort(key=lambda x: (int(x[1]),int(x[0])))

	###
	# Retrieves the name, the minimum and maximum levels for every unique character in the collection.
	###
	def levels_and_names(self):
		print('\tRetrieving levels and names...')
		chars_data_file={}
		if path.exists("chars_data.txt"):
			with open("chars_data.txt", 'r') as f:
				for line in f.readlines():
					if line.strip(' \n')!="":
						line.replace('\n','')
						line_split=line.split(' ')
						chars_data_file[int(line_split[0])]=(int(line_split[1]), int(line_split[2]), str(line_split[3]))
				f.close()

		data_added=0
		for i in self.char_list.keys():
			i = int(i)
			if i in chars_data_file:
				self.char_list[i].min_level=chars_data_file[i][0]
				self.char_list[i].max_level=chars_data_file[i][1]
				self.char_list[i].name=chars_data_file[i][2]
			else:
				session_requests = requests.session()
				page = session_requests.get('https://www.urban-rivals.com/game/characters/?id_perso='+str(i), headers=navigation_headers, cookies=cookies)
				if str(page.text) != "":
					tree = html.fromstring(page.content)
					tmp_levels = tree.xpath('//img[@class="card-picture js-lazyload"]/@data-original')
					tmp_levels = [int(str(i)[-12:-11]) for i in tmp_levels]
					tmp_min=min(tmp_levels)
					tmp_max=max(tmp_levels)
					tmp_name = tree.xpath('//h2[@class="page-header-responsive text-white text-center py-5 d-block d-lg-none"]/text()')
					tmp_name = tmp_name[0].split(':')[1].strip(" \n").replace(' ','_')
					chars_data_file[i]=(tmp_min, tmp_max, tmp_name)
					data_added+=1
					self.char_list[i].min_level=tmp_min
					self.char_list[i].max_level=tmp_max
					self.char_list[i].name=tmp_name

		if data_added>0:
			print("\t\tAdded "+str(data_added)+" new entries to chars_data.txt")
			with open("chars_data.txt", "w") as f:
				for i in sorted(chars_data_file):
					f.write(str(i)+" "+str(chars_data_file[i][0])+" "+str(chars_data_file[i][1])+" "+str(chars_data_file[i][2]).strip('\n')+"\n")
			f.close()
			data_added=0
		print('\tLevels and names retrieved...')

	###
	# Sorts every characters in 3 lists :
	# 		- possessed : characters levels that are possessed (or needs level up from a double under-leveled card).
	# 		- missing : characters levels that are missing.
	# 		- to_sell : doubles to sell.
	# Oldest cards are prioritized, even over the ones that already have the required level.
	###
	def process_and_save_all_evos(self):
		print('Processing collection data...')
		possessed_chars_file=""
		missing_chars_file=""
		double_chars_file=""
		to_evolve_chars_file=""
		for i in sorted(self.char_list.keys()):
			tmp_char=self.char_list[i]
			tmp_min_level=tmp_char.min_level
			tmp_max_level=tmp_char.max_level
			possessed_chars = [0 for _ in range(tmp_max_level-tmp_min_level+1)]
			ids_to_keep = [0 for _ in range(tmp_max_level-tmp_min_level+1)]
			ids_to_keep_real_levels = [0 for _ in range(tmp_max_level-tmp_min_level+1)]
			ids_to_sell = [ [] for i in range(tmp_max_level-tmp_min_level+1)]
			tmp_char_ids=tmp_char.player_char_ids
			all_found=False
			broke=False
			for char_id, char_level in tmp_char_ids:
				index=char_level-tmp_min_level
				if all_found==False:
					all_found=True
					for j in ids_to_keep:
						if j==0:
							all_found=False

				if ids_to_keep[index]==0: #if level not possessed and card is level
					ids_to_keep[index]=char_id
					ids_to_keep_real_levels[index]=char_level
					possessed_chars[index]=char_id
					continue
				elif char_id < ids_to_keep[index]: #if level possessed but char is older
					tmp_char_ids.append((ids_to_keep[index],ids_to_keep_real_levels[index]))
					ids_to_keep[index]=char_id
					ids_to_keep_real_levels[index]=char_level
					if possessed_chars[index]==0:
						possessed_chars[index]=char_id
					continue
				elif char_level<tmp_max_level: #if char is not maxed
					for k in reversed(range(index,len(ids_to_keep))): # char level can only go up
						if ids_to_keep[k]==0:
							ids_to_keep[k]=char_id
							ids_to_keep_real_levels[k]=char_level
							broke=True
							break # no char fills more than one slot
						elif all_found==True and char_id<ids_to_keep[k]:
							tmp_char_ids.append((ids_to_keep[k],ids_to_keep_real_levels[k]))
							ids_to_keep[k]=char_id
							ids_to_keep_real_levels[k]=char_level
							possessed_chars[k]=0
							broke=True
							break
				if char_id not in ids_to_sell[index] and broke==False:
					ids_to_sell[index].append(char_id)
				broke=False

			for j in range(len(ids_to_keep)):
				tmp_str=str(tmp_char.char_id)+" "+str(ids_to_keep[j])+" "+str(tmp_char.name).strip('\n')+" "
				if ids_to_keep[j]==0 and len(tmp_char.name.split('_L'))<2:
					missing_chars_file+= str(tmp_char.char_id)+" "+str(tmp_char.name).strip('\n')+" "+str(tmp_min_level+j)+"*\n"
				elif ids_to_keep[j]>0 and possessed_chars[j]==0:
					possessed_chars_file+= tmp_str+str(tmp_min_level+ids_to_keep_real_levels[j]-1)+"* -> "+str(tmp_min_level+j)+"*\n"
					to_evolve_chars_file+= str(ids_to_keep[j])+" "+str(ids_to_keep_real_levels[j]-tmp_min_level+j)+" \n"
				else:
					possessed_chars_file+= tmp_str+str(tmp_min_level+j)+"*\n"

			for j in range(len(ids_to_sell)):
				for k in range(len(ids_to_sell[j])):
					double_chars_file+=str(tmp_char.char_id)+" "+str(ids_to_sell[j][k])+" "+str(tmp_char.name.strip('\n'))+" \n"

		print("\tUpdating possessed evolutions list...")
		with open("collection.txt", 'w') as f:
			f.write(possessed_chars_file)
			f.close()
		print("\tcollection.txt updated.")

		print("\tUpdating underleveled characters list...")
		with open("to_level.txt", 'w') as f:
			f.write(to_evolve_chars_file)
			f.close()
		print("\tto_level.txt updated.")

		print("\tUpdating missing evolutions list...")
		with open("missing.txt", 'w') as f:
			f.write(missing_chars_file)
			f.close()
		print("\tmissing.txt updated.")

		print("\tUpdating double characters list...")
		double_chars_file+="0 0 0" # Needs this line to sell last character
		with open("to_sell.txt", 'w') as f:
			f.write(double_chars_file)
			f.close()
		print("\tto_sell.txt updated.")
		print("Collection data processed.")

        ###
	# Sorts every characters in 2 lists :
	# 		- possessed : characters that are possessed.
	# 		- to_sell : doubles to sell.
	###
	def process_and_save(self):
		print('Processing collection data...')
		possessed_chars_file=""
		double_chars_file=""
		for i in sorted(self.char_list.keys()):
			tmp_char=self.char_list[i]
			tmp_max_level=tmp_char.max_level
			id_to_keep = 0
			ids_to_sell = []
			found=False
			for char_id, char_level in tmp_char.player_char_ids:
				if found==False:
					if char_level<tmp_max_level and id_to_keep==0:
						id_to_keep=char_id
					elif char_level==tmp_max_level:
						id_to_keep=char_id
						found=True
					else:
						ids_to_sell.append(char_id)
				else:
					ids_to_sell.append(char_id)

			if id_to_keep>0:
				possessed_chars_file+=str(tmp_char.char_id)+" "+str(id_to_keep)+" "+str(tmp_char.name).strip('\n')+"\n"

			if len(ids_to_sell)>0:
				for j in range(len(ids_to_sell)):
					double_chars_file+=str(tmp_char.char_id)+" "+str(ids_to_sell[j])+" "+str(tmp_char.name.strip('\n'))+" \n"

		print("\tUpdating possessed characters list (keeping one of each card only)...")
		with open("collection.txt", 'w') as f:
			f.write(possessed_chars_file)
			f.close()
		print("\tcollection.txt updated.")

		print("\tUpdating double characters list...")
		double_chars_file+="0 0 0" # Needs this line to sell last character
		with open("to_sell.txt", 'w') as f:
			f.write(double_chars_file)
			f.close()
		print("\tto_sell.txt updated.")
		print("Collection data processed.")

	###
	# Saves the collection to a collection.txt file
	###
	def save(self):
		print('Saving pre-processed collection...')
		with open("raw_collection.txt", 'w') as f:
			f.write(str(self))
			f.close()
		print('Pre-processed collection saved to raw_collection.txt')

	def __str__(self):
		tmp_str=""
		for character in sorted(self.char_list.values()):
			tmp_str += str(character) + '\n'
		return tmp_str

###
# Cancels every current market sales.
###
def cancel_all_sales(cookies, headers):
	print('Cancelling current market offers...')
	session_requests = requests.session()
	page = session_requests.get('https://www.urban-rivals.com/market/?action=currentsale', headers=navigation_headers, cookies=cookies)
	tree = html.fromstring(page.content)
	max_page = 0
	tmp_max_page = [int(i) for i in tree.xpath('//a[i/@class="fas fa-angle-double-right"]/@data-page')]
	if tmp_max_page == []:
		max_page = 0
	else:
		max_page = max(tmp_max_page)
	i=0
	cancels = ""
	for _ in range(max_page+1):
		page = session_requests.get('https://www.urban-rivals.com/market/?action=currentsale', headers=navigation_headers, cookies=cookies)
		tree = html.fromstring(page.content)
		char_ids = tree.xpath('//div[@class="bg-light market-card media media-card-purchase mb-1"]/div/a/@href')
		if char_ids == []:
			char_ids = tree.xpath('//div[@class="bg-light market-card-single media media-card-purchase mb-1"]/div/a/@href')
		for j in char_ids:
			data={}
			data['action']='cancel_all_sales'
			data['id']=str(j).split('=')[1].strip(" \n")
			ret = requests.post('https://www.urban-rivals.com/ajax/market/', data=data, cookies=cookies, headers=headers)
			cancels += str(j).split('=')[1].strip(" \n") +" "+str(ret.text)+'\n'
			i+=1
	with open("log_cancels.txt",'w') as f:
		f.write(cancels)
		f.close()
	print("Cancelled offers for "+str(i)+" characters.")

###
# Sells a single card.
###
def sell_card(cookies, headers, id_perso_joueur, price, action='sellToPublic', buyer_name=''):
	data = {}
	data['price'] = str(price)+'^'
	data['action'] = str(action)+'^'
	if buyer_name!='':
		data['buyer_name']=str(buyer_name)+'^'
	data['id_perso_joueur']=str(id_perso_joueur)
	ret = requests.post('https://www.urban-rivals.com/ajax/collection/sell_card.php', data=data, cookies=cookies, headers=headers)
	return ret.text

###
# Sells every card described in a to_sell.txt file.
###
def sell_cards(cookies, headers):
	print("Selling cards ...")
	sales_file=""
	total=0
	total_cards=-1
	previous_id=0
	previous_name=""
	sales=[]

	if path.exists("to_sell.txt"):
		with open("to_sell.txt", 'r') as f:
			for line in f.readlines():
				line=line.strip('\n')
				if line!='':
					line_split=line.split(' ')
					if int(line_split[0])!=previous_id:
						if previous_id!=0:
							session_requests = requests.session()
							page = session_requests.get('https://www.urban-rivals.com/market/?id_perso='+str(int(previous_id)), headers=navigation_headers, cookies=cookies)
							tree = html.fromstring(page.content)
							tmp_price = str(tree.xpath('//td[@class="align-middle" and img/@title="Clintz"]/text()')[0]).replace('\n','')
							price=0
							if tmp_price == []:
								price = 2000000000
							else:
								tmp_price = tmp_price.replace(' ','')
								price = int(tmp_price)-1
							total+=len(sales)*price
							print("\t"+str(len(sales))+"x "+str(previous_name)+" ("+str(previous_id)+")  price="+str(price)+"/u  total="+str(len(sales)*price))
							for i in range(len(sales)):
								ret = sell_card(cookies, headers, sales[i], price)
								sales_file+=str(line_split[1])+" "+str(ret)+'\n'
						previous_id=int(line_split[0])
						previous_name=line_split[2].strip('\n')
						sales=[]
						sales.append(line_split[1])
					else:
						sales.append(line_split[1])
					total_cards+=1

			f.close()

	with open("log_sales.txt", "w") as f:
		f.write(sales_file)
		f.close()

	print(str(total_cards)+" cards put for sale. Total value : "+str(total))

###
# Levels characters given a to_xp.txt file.
###
def xp_cards(cookies, headers):
	print("Adding xp to underleveled cards...")
	xp_file=""
	total=0
	if path.exists("to_level.txt"):
		with open("to_level.txt", 'r') as f:
			for line in f.readlines():
				line=line.strip('\n')
				if line!='':
					line_split=line.split(' ')
					for i in range(int(line_split[1])):
						data={}
						data['action'] = 'addXPForClintz'
						data['characterInCollectionID'] = line_split[0]
						data['buyXP'] = 'true'
						ret = requests.post('https://www.urban-rivals.com/ajax/collection/', headers=headers, cookies=cookies, data=data)
						xp_file+=str(ret.text)
						total+=1
			f.close()

	with open("log_xp.txt", 'w') as f:
		f.write(xp_file)
		f.close()

	print(str(total)+" cards leveled up.")
###
# Does a full update of the collection :
# 		1. Cancels every current market offers if cancel_sales is set to true.
# 		2. Retrieve collection.
#		3. Updates the lists.
#                       - If keeps_evos is set to true : keeps one card of eache character at each level.
#                       - Else, keeps one card of each character.
#		4. Sells every double cards if sell_doubles is set to true.
###
def full_update(cancel_sales=False, keep_evos=True, xp=False, sell_doubles=False):
	if keep_evos==False and sell_doubles==True:
		print("WARNING keeping evolutions is OFF and selling is ON, this could result in losing a part of your collection. \nPress any key to continue. \nPress CTRL-C to abort.")
		try:
		    input()
		except KeyboardInterrupt:
		    sys.exit()
	if cancel_sales == True:
		cancel_all_sales(cookies, action_headers)
	collection = Collection()
	if keep_evos == True:
		collection.process_and_save_all_evos()
		if xp == True:
			xp_cards(cookies, action_headers)
	else:
		collection.process_and_save()
	if sell_doubles == True:
		sell_cards(cookies, action_headers)


if __name__ == "__main__":
	full_update(cancel_sales=param_cancel_sales, keep_evos=param_keep_evos, xp=param_xp, sell_doubles=param_sell_doubles)
	try:
		print("Press ENTER to quit.")
		input()
	except KeyboardInterrupt:
		sys.exit()
