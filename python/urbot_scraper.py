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
			# Exit
			###
			if command_line_split[0]=="quit" or command_line_split[0]=="exit":
				sys.exit(0)

			###
			# Displays help informations
			###
			if command_line_split[0]=="help":
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
			# Used by UR_Bot to get stats
			###
			elif command_line_split[0]=="stats":
				if not os.path.exists(os.path.join(working_dir_path, "data")):
					os.mkdir(os.path.join(working_dir_path, "data"))
				stats.get_player_page_data(cookies, navigation_headers, os.path.join(working_dir_path, "data", "player_page_data.txt"))

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
\t32  Disable verbose mode.\n\
\t64  Keep logs about cancelled market offers, characters leveled up and sales offers as raw textual return value from request functions.\n\
\n\
Then call 'urbot_scraper update argument'.")
					command_line_split=[]
					continue

				param_cancel_sales=False
				param_keep_single_character=False
				param_xp=False
				param_pay_for_xp=False
				param_sell_doubles=False
				param_verbose=False
				param_log=False

				print("=== URBot's scraper v.3 - update ===")

				parameters = []

				###
				# Decodes parameters from 2nd argument
				###
				try:
					parameters = decode_binary(int(command_line_split[1]), 7)
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
				print()
			
			else:
				print("Function '"+command_line_split[0]+"' does not exist. Type help for help.")
		try:
			command_line = input()
			command_line_split = command_line.split()
		except KeyboardInterrupt:
			sys.exit()