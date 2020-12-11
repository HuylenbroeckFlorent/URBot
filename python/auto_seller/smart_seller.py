import sys
import requests
from lxml import html

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

params = (
	('view', 'collection'),
	('sortby', 'date'),
	('orderby', 'desc'),
	('group', 'all'),
	('nb_per_page', '48')
)

class Character:
	def __init__(self, char_id):
		self.char_id=int(char_id)
		self.quantity=0
		self.player_char_ids = []
		self.price=0
		self.min_level=0
		self.max_level=0

	def __str__(self):
		tmp_str = "Character "+str(self.char_id)+" (x"+str(self.quantity)+") "+str(self.min_level)+"*-"+str(self.max_level)+"*"
		for i in self.player_char_ids:
			tmp_str += "\n\t"+str(i[0])+" "+str(i[1])+"*"
		return tmp_str

	def __cmp__(self, other):
		return cmp(self.char_id, other.char_id)

	def __lt__(self, other):
		return self.char_id < other.char_id

class Collection:
	def __init__(self):
		print('Retrieving collection...')
		self.char_list = {}
		session_requests = requests.session()
		page = session_requests.get('https://www.urban-rivals.com/collection/index.php', headers=navigation_headers, params=params, cookies=cookies)
		tree = html.fromstring(page.content)
		max_page = tree.xpath('//a[i/@class="fas fa-angle-double-right"]/@data-page')
		max_page = int(max_page[0])

		for i in range(0, max_page):
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
		print('Retrieving levels...')
		self.levels()
		print('Saving collection...')
		self.save()


	def add(self, char_id, player_char_id, level):
		if char_id not in self.char_list:
			self.char_list[int(char_id)]=Character(char_id)
		self.char_list[int(char_id)].quantity+=1
		self.char_list[int(char_id)].player_char_ids.append((int(player_char_id),int(level)))
		self.char_list[int(char_id)].player_char_ids.sort(key=lambda x: (int(x[1]),int(x[0])))

	def levels(self):
		levels_file={}
		with open("levels.txt", "r") as f:
			for line in f.readlines():
				line.replace('\n','')
				line_split=line.split(' ')
				levels_file[int(line_split[0])]=(int(line_split[1]), int(line_split[2]))
			f.close()

		levels_added=0
		for i in self.char_list.keys():
			i = int(i)
			if i in levels_file:
				self.char_list[i].min_level=levels_file[i][0]
				self.char_list[i].max_level=levels_file[i][1]
			else:
				session_requests = requests.session()
				page = session_requests.get('https://www.urban-rivals.com/game/characters/?id_perso='+str(i), headers=navigation_headers, cookies=cookies)
				if str(page.text) != "":
					tree = html.fromstring(page.content)
					tmp_levels = tree.xpath('//img[@class="card-picture js-lazyload"]/@data-original')
					tmp_levels = [int(str(i)[-12:-11]) for i in tmp_levels]
					tmp_min=min(tmp_levels)
					tmp_max=max(tmp_levels)
					levels_file[i]=(tmp_min, tmp_max)
					levels_added+=1

		if levels_added>0:
			print("added "+str(levels_added)+" levels to levels.txt")
			with open("levels.txt", "w") as f:
				for i in sorted(levels_file):
					f.write(str(i)+" "+str(levels_file[i][0])+" "+str(levels_file[i][1])+"\n")
			f.close()
			levels_added=0


	def list_doubles(self):
		print('Listing doubles...')
		possessed_chars_file=""
		missing_chars_file=""
		double_chars_file=""
		for i in sorted(self.char_list.keys()):
			tmp_char=self.char_list[i]
			tmp_min_level=tmp_char.min_level
			tmp_max_level=tmp_char.max_level
			possessed_chars = [0 for _ in range(tmp_max_level-tmp_min_level+1)]
			ids_to_keep = [0 for _ in range(tmp_max_level-tmp_min_level+1)]
			ids_to_sell = [ [] for i in range(tmp_max_level-tmp_min_level+1)]
			all_found=False
			sold=False
			price=0
			for char_id, char_level in tmp_char.player_char_ids:
				index=char_level-tmp_min_level ### ?????
				if ids_to_keep[index]==0:
					ids_to_keep[index]=char_id
					possessed_chars[index]=char_id
				elif char_id < ids_to_keep[index]:
					ids_to_sell[index].append(ids_to_keep[index])
					sold=True
					ids_to_keep[index]=char_id
					if possessed_chars[index]==0:
						possessed_chars[index]=char_id
				elif all_found==False:
					for k in reversed(range(len(ids_to_keep))):
						if ids_to_keep[k]==0:
							ids_to_keep[k]=char_id
						elif char_id<ids_to_keep[k]:
							ids_to_sell[index].append(ids_to_keep[k])
							sold=True
							ids_to_keep[k]=char_id
							possessed_chars[k]=0
					for j in ids_to_keep:
						all_found=True
						if j==0:
							all_found=False

				else:
					ids_to_sell[index].append(char_id)
					sold=True
				'''
				if sold==True:
					if price==0:
						session_requests = requests.session()
						page = session_requests.get('https://www.urban-rivals.com/market/?id_perso='+str(tmp_char.char_id), headers=navigation_headers, cookies=cookies)
						tree = html.fromstring(page.content)
						tmp_price = str(tree.xpath('//td[@class="align-middle" and img/@title="Clintz"]/text()')[0]).replace('\n','')
						if tmp_price == []:
							tmp_price = 2000000
						else:
							tmp_price = tmp_price.replace(' ','')
							price = int(tmp_price)-1
				'''
				sold=False

			for j in range(len(ids_to_keep)):
				if ids_to_keep[j]==0:
					missing_chars_file+=str(tmp_char.char_id)+" "+str(j+1)+"*\n"
				elif ids_to_keep[j]>0 and possessed_chars[j]==0:
					possessed_chars_file+=str(tmp_char.char_id)+" "+str(j+1)+"* (TO LEVEL)\n"
				else:
					possessed_chars_file+=str(tmp_char.char_id)+" "+str(j+1)+"*\n"

			for j in range(len(ids_to_sell)):
				for k in range(len(ids_to_sell[j])):
					double_chars_file+=str(tmp_char.char_id)+" "+str(j+tmp_min_level)+" "+str(ids_to_sell[j][k])+" 1 "+str(price)+"\n"

		with open("possessed.txt", 'w') as f:
			f.write(possessed_chars_file)
			f.close()

		with open("missing.txt", 'w') as f:
			f.write(missing_chars_file)
			f.close()

		with open("to_sell.txt", 'w') as f:
			f.write(double_chars_file)
			f.close()


				


	def __str__(self):
		tmp_str=""
		for character in sorted(self.char_list.values()):
			tmp_str += str(character) + '\n'
		return tmp_str

	def save(self):
		with open("collection.txt", 'w') as f:
			f.write(str(self))
			f.close()

def retrieve_card_levels(char_ids):
	levels=""
	for i in char_ids:
		session_requests = requests.session()
		page = session_requests.get('https://www.urban-rivals.com/game/characters/?id_perso='+str(i), headers=navigation_headers, cookies=cookies)
		if str(page.text) != "":
			tree = html.fromstring(page.content)
			tmp_levels = tree.xpath('//img[@class="card-picture js-lazyload"]/@data-original')
			tmp_levels = [int(str(i)[-12:-11]) for i in tmp_levels]
			levels+=str(i)+" "+str(min(tmp_levels))+" "+str(max(tmp_levels))+"\n"

	with open("levels"+min[char]+"-"+str(end)+".txt", 'w') as f: 
		f.write(levels)
		f.close()

def sell_card(cookies, headers, id_perso_joueur, price, action='sellToPublic', buyer_name=''):
	data = {}
	data['price'] = str(price)+'^'
	data['action'] = str(action)+'^'
	if buyer_name!='':
		data['buyer_name']=str(buyer_name)+'^'
	data['id_perso_joueur']=str(id_perso_joueur)
	ret = requests.post('https://www.urban-rivals.com/ajax/collection/sell_card.php', data=data, cookies=cookies, headers=headers)
	return ret.text

def sell_cards(cookies, headers):
	print("Selling cards ...")
	data = {}
	data['action']='selectionsell'
	data['type']='public'
	#data['recipient']=''
	sales_file=""
	total=0
	total_cards=0
	previous_id=0
	sales=[]
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
							price = 2000000
						else:
							tmp_price = tmp_price.replace(' ','')
							price = int(tmp_price)-1
						total+=len(sales)*price
						print("Selling x"+str(len(sales))+" id="+str(line_split[0])+" price="+str(price)+" total price="+str(len(sales)*price))
						for i in range(len(sales)):
							ret = sell_card(cookies, headers, sales[i], price) #
							sales_file+=str(ret)+'\n'
					previous_id=int(line_split[0])
					sales=[]
					sales.append(line_split[2])
				else:
					sales.append(line_split[2])
				total_cards+=1

		f.close()

	with open("sales.txt", "w") as f:
		f.write(sales_file)
		f.close()

	return total_cards, total


	'''
	sale["id"]=int(line_split[0])
	sale["level"]=int(line_split[1])
	sale["idCollection"]=int(line_split[2])
	sale["quantity"]=int(line_split[3])
	sale["price_unit"]=int(line_split[4])
	sales.append(sale)
	data['sales']=str(sales)
	ret = requests.post('https://www.urban-rivals.com/ajax/collection/sell_card.php', data=data, cookies=cookies, headers=headers)
	'''

def cancel_all_sales(cookies, headers):
	with open("to_sell.txt", 'r') as f:
		previous_id=0
		for line in f.readlines():
			line_split=line.split(' ')
			if int(line_split[0])!=previous_id:
				if previous_id!=0:
					data={}
					data['action']='cancel_all_sales'
					data['id']=str(line_split[0])
					ret = requests.post('https://www.urban-rivals.com/ajax/market/', data=data, cookies=cookies, headers=headers)
					print(ret.text)
				previous_id=int(line_split[0])
	f.close()

if __name__ == "__main__":
	collection = Collection()
	collection.list_doubles()
	total_cards, total = sell_cards(cookies, action_headers) # will sell cards
	print("Done.\nTotal card sold : "+str(total_cards)+"\nTotal value : "+str(total))
	#cancel_all_sales(cookies, action_headers)