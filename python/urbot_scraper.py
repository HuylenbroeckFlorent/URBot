import sys
import os
from glob import glob
import grequests
import requests
from lxml import html

from web.headers import navigation_headers, action_headers
import collection.collection as collection
import stats.stats as stats
import deck_saver.deck_saver as deck_saver
import market.market as market

try:
	from web.cookies import cookies
except ImportError:
	sys.stdout.write("ERROR : cookies not found.\n\
	To generate cookies in cookies.py : \n\
	\n\
	1 - Go to https://www.urban-rivals.com/ and login.\n\
	2 - Open your browser\'s developper tools (F12).\n\
	3 - Go to the network tab.\n\
	4 - Refresh the page.\n\
	5 - Right click the site request (the request that has the URL that matches yours : https://www.urban-rivals.com/) and go to copy -> copy as cURL(cmd) (might be (windows) or else).\n\
	6 - Go to this site which converts cURL into python requests: https://curl.trillworks.com/\n\
	7 - Take the generated cookies and place them in a file under \'/URBot/python/web/cookies.py\'.\n\
	\n\
	It should look like this :\n\
	\n\
	cookies = {\n\
		\t\'collection-filters\': \'^{^%^22nb_per_page^%^22:^%^2248^%^22^}\', (MIGHT BE OMITTED)\n\
		\t\'cnil\': \'true\', (MIGHT BE OMITTED)\n\
		\t\'ur_token\': \'long alphanumeric string\',\n\
		\t\'UR_SESSID\': \'long alphanumeric string\',\n\
		\t\'csrf-token\': \'long alphanumeric string\',\n\
	}\n")
	sys.stdout.flush()
	sys.exit(1)

working_dir_path = os.getcwd()

###
# Decodes a binary encoding : returns an array of 0's or 1's given an integer
###
def decode_binary(n, length):
	parameters = [0] * length
	for i in range(length):
		parameters[i] = n%(2**(i+1))
		n-=n%(2**(i+1))

	return parameters

###
if __name__ == '__main__':
	###
	# Checks for cookies validity.
	###
	session_requests = requests.session()
	page = session_requests.get('https://www.urban-rivals.com/collection/index.php', headers=navigation_headers, cookies=cookies)
	tree = html.fromstring(page.content)
	test_string = tree.xpath('//a[@data-view="collection"]/text()')[0]
	if test_string!="Collection":
		sys.stdout.write("\nERROR : cookies outdated.\n\
		To generate cookies in cookies.py : \n\
		\n\
		1 - Go to https://www.urban-rivals.com/ and login.\n\
		2 - Open your browser\'s developper tools (F12).\n\
		3 - Go to the network tab.\n\
		4 - Refresh the page.\n\
		5 - Right click the site request (the request that has the URL that matches yours : https://www.urban-rivals.com/) and go to copy -> copy as cURL(cmd) (might be (windows) or else).\n\
		6 - Go to this site which converts cURL into python requests: https://curl.trillworks.com/\n\
		7 - Take the generated cookies replace the ones in the file \'/URBot/python/web/cookies.py\'.\n\
		\n\
		It should look like this :\n\
		\n\
		cookies = {\n\
			\t\'collection-filters\': \'^{^%^22nb_per_page^%^22:^%^2248^%^22^}\', (MIGHT BE OMITTED)\n\
			\t\'cnil\': \'true\', (MIGHT BE OMITTED)\n\
			\t\'ur_token\': \'long alphanumeric string\',\n\
			\t\'UR_SESSID\': \'long alphanumeric string\',\n\
			\t\'csrf-token\': \'long alphanumeric string\',\n\
		}\n")
		sys.stdout.flush()
		sys.exit(1)

	if len(sys.argv)>1:
		###
		# Used by UR_Bot to get stats
		###
		if sys.argv[1]=="stats":
			if not os.path.exists(os.path.join(working_dir_path, "data")):
				os.mkdir(os.path.join(working_dir_path, "data"))
			stats.get_player_page_data(cookies, navigation_headers, os.path.join(working_dir_path, "data", "player_page_data.txt"))

		###
		# Prints a summary of market sales history and generates data/buyers_data.txt
		###
		elif sys.argv[1]=="buyers":
			print("\n=== URBot's scraper v.2 - buyers ===")
			if not os.path.exists(os.path.join(working_dir_path, "data")):
				os.mkdir(os.path.join(working_dir_path, "data"))
			market.sales_history(cookies, navigation_headers, os.path.join(os.getcwd(), "data", "buyers_data.txt"))

		###
		# Decks management
		###
		elif sys.argv[1]=="preset":
			###
			# Loads one or more preset to player's collection
			###
			if sys.argv[2]=="import":
				print("\n=== URBot's scraper v.2 - preset import ===")
				if len(sys.argv)>3:
					for deck in glob(sys.argv[3]):
						deck_saver.import_deck(cookies, navigation_headers, action_headers, deck)
				else:
					print("Function 'deck load' requires one argument : (string path_to_deck_files).")
			###
			# Saves one preset to player's collection and sets it as active deck
			###
			elif sys.argv[2]=="set":
				print("\n=== URBot's scraper v.2 - preset set ===")
				if len(sys.argv)>3 and len(glob(sys.argv[3]))==1:
					deck_saver.set_deck(cookies, action_headers, deck_saver.import_deck(cookies, navigation_headers, action_headers, sys.argv[3]))
				else:
					print("Function 'deck set' requires strictly one argument : (string path_to_deck_file).")
					sys.exit(1)

			###
			# Retrieves all player's preset to data/decks/
			###
			elif sys.argv[2]=="export":
				print("\n=== URBot's scraper v.2 - preset export ===")
				deck_saver.export_decks(cookies, navigation_headers, action_headers, os.path.join(working_dir_path, "data", "decks"))
			else:
				print("No specified mode for function 'deck'. Use 'import', 'set' or 'export'.")

		###
		# Does a full update of the collection :
		#		   1. Cancels every current market offers if cancel_sales is set to 'True'.
		#		   2. Retrieve collection.
		#		   3. Updates the lists.
		#			  - If keeps_evos is set to 'True' : keeps one card of each character at each level.
		#			  - Else, keeps one card of each character.
		#		   4. Levels up cards to reach their kept level if xp is set to 'True'. If xp_reserve_only is 'True', will only level from xp reserve.
		#		   5. Sells every double cards if sell_doubles is set to 'True'.
		###
		elif sys.argv[1]=="update":

			if len(sys.argv)<3:
				sys.stdout.write("update function needs an argument (int).\n\
To generate this argument, sum the ids of the following actions you want 'update' to perform:\n\
\t1   Cancel all current market sales before processing the collection.\n\
\t2   Keep one card of each character at each level, else only one card per character will be kept.\n\
\t4   Use xp to level up underleveled characters.\n\
\t8   Allow paying for xp.\n\
\t16  Sell every double cards after processing the collection, at an optimal price.\n\
\t32  Disable verbose mode.\n\
\t64  Keep logs about cancelled market offers, characters leveled up and sales offers as raw textual return value from request functions.\n\
\n\
Then call 'urbot_scraper update argument'.")
				sys.exit(1)

			param_cancel_sales=False
			param_keep_single_character=False
			param_xp=False
			param_pay_for_xp=False
			param_sell_doubles=False
			param_verbose=False
			param_log=False

			print("\n=== URBot's scraper v.2 - update ===")

			parameters = []

			###
			# Decodes parameters from 2nd argument
			###
			try:
				parameters = decode_binary(int(sys.argv[2]), 7)
			except ValueError as ve:
				print("Invalid argument for function 'update' : "+ sys.argv[2])
				print("ERROR : "+str(ve))
				sys.exit(1)

			param_cancel_sales=bool(parameters[0])
			param_keep_single_character=bool(parameters[1])
			param_xp=bool(parameters[2])
			param_pay_for_xp=bool(parameters[3])
			param_sell_doubles=bool(parameters[4])
			param_verbose=(not bool(parameters[5]))
			param_log=bool(parameters[6])

			print("\nChosen actions :")
			if param_cancel_sales==True:
				print("\tCancel sales.")
			if param_keep_single_character==True:
				print("\tKeep single characters.")
			else:
				print("\tKeep one of each evo's.")
			if param_xp==True:
				if param_pay_for_xp==True:
					print("\tGive XP to underleveled characters, and allow paying for XP.")
				else:
					print("\tGive XP to underleveled characters.")
			if param_sell_doubles==True:
				print("\tSell doubles")
			if param_log==True:
				print("\tLogs will be kept in 'data/logs/'.")

			###
			# if a players tries to sell while not accounting for evo's, action must be confirmed.
			###
			if param_keep_single_character==True and param_sell_doubles==True:
				print("WARNING keeping evolutions is OFF (param_keep_single_character) and selling is ON (param_sell_doubles), \
this could result in losing a part of your collection. \nPress any key to continue. \nPress CTRL-C to abort.")
				try:
					input()
				except KeyboardInterrupt:
					sys.exit()

			if param_log==True and not os.path.exists(os.path.join(working_dir_path, "data", "logs")):
				os.mkdir(os.path.join(working_dir_path, "data", "logs"))

			if param_cancel_sales == True:
				market.cancel_all_sales(cookies, navigation_headers, action_headers, param_verbose, param_log)

			player_collection = collection.Collection(cookies, navigation_headers, param_verbose)

			filter_path=""
			if os.path.exists(os.path.join(working_dir_path, "market", "filters", "filter.txt")):
				filter_path=os.path.join(working_dir_path, "market", "filters", "filter.txt")
			if param_keep_single_character == False:
				player_collection.process_and_save_all_evos(filter_path)
			else:
				player_collection.process_and_save(filter_path)

			if param_xp == True:
				collection.xp_cards(cookies, action_headers, os.path.join(working_dir_path, "data", "to_level.txt"), param_pay_for_xp, param_verbose, param_log)
							
			if param_sell_doubles == True:
				market.sell_cards(cookies, navigation_headers, action_headers, os.path.join(working_dir_path, "data", "to_sell.txt"), param_verbose, param_log)

			try:
				print("Press ENTER to quit.")
				input()
			except KeyboardInterrupt:
				sys.exit()
	else:
		sys.stdout.write("\n=== URBot's scraper v.2 ===\n\
Functions list:\n\
\t- buyers: process the player's sales history and outputs the total sold cards, total clintz and a summary of every buyers in 'data/buyers_data.txt'.\n\
\t- preset\n\
\t\t import(path_to_preset_file): imports one or more presets from files to player's presets. Use * for multiple imports.\n\
\t\t export: exports player's presets to files in 'data/decks/'.\n\
\t\t set(path_to_preset_file): imports one preset if it does not exists in player's presets then sets it as active deck.\n\
\t- update(mode): updates the player's collection. Use update without argument to see a detailed guide.\n\
\n\
To use a function, call urbot_scraper.py with the function name as argument followed by function mode (e.g. deck import) then arguments.\n")
		sys.stdout.flush()
		sys.exit(0)