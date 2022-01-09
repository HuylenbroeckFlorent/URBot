import sys
import os
from glob import glob
import grequests
import requests
from lxml import html
import getpass

from web.headers import navigation_headers, action_headers
import collection.collection as collection
import stats.stats as stats
import deck_saver.deck_saver as deck_saver
import market.market as market
import market.bm as bm

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

	command_line_split = sys.argv[1:]
	print()
	if len(command_line_split)<2:
		print("Type help for help.")

	while True:
		if len(command_line_split)>0:

			###
			# Launches the bot
			###
			if command_line_split[0]=="launch":
				data_labels = ["Views","Points","Fights","Wins","Loses","Draws"]
				start_data = stats.get_player_page_data(cookies, navigation_headers)
				os.system(os.path.join(working_dir_path, "..", "bot_UR.exe"))
				end_data = stats.get_player_page_data(cookies, navigation_headers)
				data_output = ""
				for i in range(len(data_labels)):
					data_output+="{:6s} : {:7d}\n".format(data_labels[i], end_data[i]-start_data[i])
				print(data_output)

			###
			# Exit
			###
			elif command_line_split[0]=="quit" or command_line_split[0]=="exit":
				sys.exit(0)

			###
			# Displays help informations
			###
			elif command_line_split[0]=="help":
				sys.stdout.write("=== URBot's scraper v.3 - help ===\n\
Functions list:\n\
\t- history: process the player's sales history and outputs the total sold cards, total clintz and a summary of every buyers in 'data/buyers_data.txt'.\n\
\t- preset\n\
\t\t import(path_to_preset_file): imports one or more presets from files to player's presets. Use * for multiple imports.\n\
\t\t export: exports player's presets to files in 'data/decks/'.\n\
\t\t set(path_to_preset_file): imports one preset if it does not exists in player's presets then sets it as active deck.\n\
\t- update(mode): updates the player's collection. Use update without argument to see a detailed guide.\n\
\n\
To use a function, call the function name followed by function mode (e.g. deck import) then arguments.")
				print()

			###
			# Prints a summary of market sales history and generates data/buyers_data.txt
			###
			elif command_line_split[0]=="history":
				print("=== URBot's scraper v.3 - history ===")
				if not os.path.exists(os.path.join(working_dir_path, "data")):
					os.mkdir(os.path.join(working_dir_path, "data"))
				market.sales_history(cookies, navigation_headers, os.path.join(os.getcwd(), "data", "buyers_data.txt"))
				print()

			###
			# Decks management
			###
			elif command_line_split[0]=="preset":
				###
				# Loads one or more preset to player's collection
				###
				if len(command_line_split)>1:
					if command_line_split[1]=="import":
						if len(command_line_split)>2:
							print("=== URBot's scraper v.3 - preset import ===")
							for deck in glob(command_line_split[2]):
								deck_saver.import_deck(cookies, navigation_headers, action_headers, deck)
						else:
							print("ERROR: Function 'preset load' requires one argument : (string path_to_deck_files).")
					###
					# Saves one preset to player's collection and sets it as active deck
					###
					elif command_line_split[1]=="set":
						if len(command_line_split)>2 and len(glob(command_line_split[2]))==1:
							print("=== URBot's scraper v.3 - preset set ===")
							deck_saver.set_deck(cookies, action_headers, deck_saver.import_deck(cookies, navigation_headers, action_headers, command_line_split[2]))
						else:
							print("ERROR: Function 'preset set' requires strictly one argument : (path_to_deck_file).")
							command_line_split=[]
							continue

					###
					# Retrieves all player's preset to data/decks/
					###
					elif command_line_split[1]=="export":
						print("=== URBot's scraper v.3 - preset export ===")
						deck_saver.export_decks(cookies, navigation_headers, action_headers, os.path.join(working_dir_path, "data", "decks"))
					else:
						print("ERROR: Invalid mode for function 'preset'. Use 'import', 'set' or 'export'.")
				else:
					print("ERROR: Function 'preset' require mode. Use 'preset import path_to_presets_file', 'preset set path_to_preset_file' or 'preset export'")
				print()

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
			elif command_line_split[0]=="update":

				if len(command_line_split)<2:
					sys.stdout.write("ERROR: update function needs an argument (int).\n\
To generate this argument, sum the ids of the following actions you want 'update' to perform:\n\
\t1   Cancel all current market sales before processing the collection.\n\
\t2   Keep one card of each character at each level, else only one card per character will be kept.\n\
\t4   Use xp to level up underleveled characters.\n\
\t8   Allow paying for xp.\n\
\t16  Sell every double cards after processing the collection, at an optimal price.\n\
\t32  Estimates the total value of cards to sell (does not work ).\n\
\t64  Disable verbose mode.\n\
\t128 (DEBUG) Keep logs about cancelled market offers, characters leveled up and sales offers as raw textual return value from request functions.\n\
\n\
Then call 'urbot_scraper update argument'.\n")
					command_line_split=[]
					continue

				param_cancel_sales=False
				param_keep_single_character=False
				param_xp=False
				param_pay_for_xp=False
				param_sell_doubles=False
				param_estimate=False
				param_verbose=False
				param_log=False

				print("=== URBot's scraper v.3 - update ===")

				parameters = []

				###
				# Decodes parameters from 2nd argument
				###
				try:
					parameters = decode_binary(int(command_line_split[1]), 8)
				except ValueError as ve:
					print("Invalid argument for function 'update' : "+ command_line_split[1])
					print("ERROR : "+str(ve))
					command_line_split=[]
					continue

				param_cancel_sales=bool(parameters[0])
				param_keep_single_character=bool(parameters[1])
				param_xp=bool(parameters[2])
				param_pay_for_xp=bool(parameters[3])
				param_sell_doubles=bool(parameters[4])
				param_estimate=(bool(parameters[5]) and not param_sell_doubles)
				param_verbose=(not bool(parameters[6]))
				param_log=bool(parameters[7])

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
					print("\tSell doubles.")
				elif param_estimate==True:
					print("\tEstimate doubles value.")
				if param_log==True:
					print("\tLogs will be kept in 'data/logs/'.")

				###
				# if a players tries to sell while not accounting for evo's, action must be confirmed.
				###
				if param_keep_single_character==True and param_sell_doubles==True:
					print("WARNING you are about to sell doubles while only keeping single characters, \
this could result in losing a part of your collection. \nPress any key to continue. \nPress CTRL-C to abort.")
					try:
						input()
					except KeyboardInterrupt:
						command_line_split=[]
						continue

				if param_log==True and not os.path.exists(os.path.join(working_dir_path, "data", "logs")):
					os.mkdir(os.path.join(working_dir_path, "data", "logs"))

				if param_cancel_sales == True:
					market.cancel_all_sales(cookies, navigation_headers, action_headers, param_verbose, param_log)

				player_collection = collection.Collection(cookies, navigation_headers, verbose=param_verbose)

				filter_path=""
				if os.path.exists(os.path.join(working_dir_path, "market", "filters", "filter.txt")):
					filter_path=os.path.join(working_dir_path, "market", "filters", "filter.txt")
				if param_keep_single_character == False:
					player_collection.process_and_save_all_evos(filter_path)
				else:
					player_collection.process_and_save(filter_path)

				if param_xp == True:
					collection.xp_cards(cookies, action_headers, os.path.join(working_dir_path, "data", "to_level.txt"), param_pay_for_xp, param_verbose, param_log)
								
				if param_sell_doubles == True or param_estimate == True:
					market.sell_cards(cookies, navigation_headers, action_headers, os.path.join(working_dir_path, "data", "to_sell.txt"), estimate=param_estimate, verbose=param_verbose, log=param_log)
				print()

			elif command_line_split[0]=="sell":
				if len(command_line_split)>0:
					filter_path=""
					if os.path.exists(os.path.join(working_dir_path, "market", "filters", "filter.txt")):
						filter_path=os.path.join(working_dir_path, "market", "filters", "filter.txt")
					collection_char = collection.Collection(cookies, navigation_headers, char_name=command_line_split[1], verbose=False)
					collection_char.process_and_save_all_evos(filter_path)
					market.sell_cards(cookies, navigation_headers, action_headers, os.path.join(working_dir_path, "data", "to_sell.txt"), verbose=True)

			elif command_line_split[0]=="bm":
				bm_type = input("Type of reward ?\n\
1. cards of specified rarity (except collector)\n\
2. $, $$ or $$$ collectors\n\
3. cryptocoinz\n\
4. tickets\n\n\
Enter the number and press ENTER : ")

				print("======")
				print()
				if bm_type == "1":
					rarity = input("Rarity ?\n\
1. Common\n\
2. Uncommon\n\
3. Rares\n\
4. Leader\n\
5. Oculus\n\
6. Mythic\n\n\
Enter the number and press ENTER : ")

					if rarity in ["1","2","3","4","5","6"]:
						if rarity == "1":
							rarity = "c"
						elif rarity == "2":
							rarity = "u"
						elif rarity == "3":
							rarity = "r"
						elif rarity == "4":
							rarity = "er"
						elif rarity == "5":
							rarity = "us"
						elif rarity == "6":
							rarity = "m"

						n = input("How many cards rewarded ? Enter number and press ENTER : ")
						value = input("How much clintz invested ? Enter amount and press ENTER : ")
				
						bm.BM(bm.rarity_avg_price(cookies, navigation_headers, rarity), int(n), int(value))

					else:
						print("Selection outside of range, please try again.")

				elif bm_type == "2":
					category = input("Which class of collector ?\n\
1. Any\n\
2. $\n\
3. $$\n\
4. $$$\n\n\
Enter the number and press ENTER : ")

					if category in ["1","2","3","4"]:
						if category == "1":
							category = 7
						elif category == "2":
							category = 1
						elif category == "3":
							category = 2
						elif category == "4":
							category = 4

						n = input("How many cards rewarded ? Enter number and press ENTER : ")
						value = input("How much clintz invested ? Enter amount and press ENTER : ")

						bm.BM(bm.crs_avg_price(cookies, navigation_headers, category), int(n), int(value))

				elif bm_type == "3":
					price_pack = int(input("Cryptocoinz pack price ? Enter number and press ENTER : "))
					n = input("How many cryptocoinz rewarded ? Enter number and press ENTER : ")
					value = input("How much clintz invested ? Enter amount and press ENTER : ")

					bm.BM(bm.crypto_avg_price(cookies, navigation_headers, price_pack), int(n), int(value), n_sample=10000)

				elif bm_type == "4":
					price_pack = int(input("Cryptocoinz pack price ? Enter number and press ENTER : "))
					n = input("How many tickets rewarded ? Enter number and press ENTER : ")
					value = input("How much clintz invested ? Enter amount and press ENTER : ")

					wheel, weights = bm.open_wheel(cookies, navigation_headers, "data/wheels/ticket_wheel.txt", price_pack)
					bm.BM(wheel, int(n), int(value), n_sample=10000, weighted=True, weights=weights)
			else:
				print("Function '"+command_line_split[0]+"' does not exist. Type help for help.")
		try:
			command_line = input()
			command_line_split = command_line.split()
		except KeyboardInterrupt:
			sys.exit()