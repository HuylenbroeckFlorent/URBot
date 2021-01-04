import sys
from glob import glob

from web.headers import navigation_headers, action_headers
from smart_seller.smart_seller import update
from stats.stats import stats
from deck_saver.deck_saver import save_deck

run=True 

try:
	from web.cookies import cookies
except ImportError:
	run=False
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
		\t\'collection-filters\': \'^{^%^22nb_per_page^%^22:^%^2248^%^22^}\',\n\
		\t\'cnil\': \'true\',\n\
		\t\'ur_token\': \'long alphanumeric string\',\n\
		\t\'UR_SESSID\': \'long alphanumeric string\',\n\
		\t\'csrf-token\': \'long alphanumeric string\',\n\
	}\n")
	sys.stdout.flush()


if __name__ == '__main__' and run==True:
	if len(sys.argv)==2:
		if sys.argv[1]=="stats":
			stats(cookies, navigation_headers)
		elif sys.argv[1]=="update":
			try:
				update(cookies, navigation_headers, action_headers, int(sys.argv[2]))
			except ValueError:
				print("ERROR : Illegal argument : \""+sys.argv[2]+"\". Requires integer. See the top of smart_seller/smart_seller.py")
			except Exception:
				try:
					print("Press ENTER to quit.")
					input()
				except KeyboardInterrupt:
					sys.exit()
	elif len(sys.argv)==3:
		if sys.argv[1]=="deck":
			for deck in glob(sys.argv[2]):
				save_deck(cookies, action_headers, deck)
