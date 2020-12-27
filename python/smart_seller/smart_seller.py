import sys
import os
import grequests
import requests
from lxml import html

###
# Parameters
#       1       param_cancel_sales : setting this to 'True' will cancel all current market sales before processing the collection.
#       2       param_keep_single_character : setting this to 'True' will enable keeping one card of each character at each level, else only one card per character will be kept.
#       4       param_xp : setting this to 'True' will use xp to level up underleveled characters.
#       8       param_pay_for_xp : setting this to 'True' will allow paying for xp.
#       16      param_sell_doubles : setting this to 'True' will sell every double cards after processing the collection, at an optimal price.
#       32      param_verbose : setting this to 'True' will enable verbose mode.
#       64      param_log : setting this to 'True' keeps logs about cancelled market offers, characters leveled up and sales offers as raw textual return value from request functions.
#
# Call this program with the sum of the parameters you want to set as true as an argument.
#
# Useful values :
#       0       default
#       54      -cancel +keep_single +xp -pay_for_xp +sell_doubles +verbose -log
#       55      +cancel +keep_single +xp -pay_for_xp +sell_doubles +verbose -log
#       60      -cancel -keep_single +xp +pay_for_xp +sell_doubles +verbose -log
#       61      +cancel -keep_single +xp +pay_for_xp +sell_doubles +verbose -log
#       62      -cancel +keep_single +xp +pay_for_xp +sell_doubles +verbose -log
#       63      +cancel +keep_single +xp +pay_for_xp +sell_doubles +verbose -log
##

param_cancel_sales=False
param_keep_single_character=False
param_xp=False
param_pay_for_xp=False
param_sell_doubles=False
param_verbose=False
param_log=False

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

working_dir_path = os.getcwd()+"\\"

###
# Character object. Contains every information about a specific character.
#           - char_id : id of the character.
#           - quantity : possessed quantity of that character.
#           - player_char_ids : every iteration of that character stored as (collection_id, level).
#           - min/max_level : min/max stars of the character.
#           - name : the character's name, with underscores replacing spaces.
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
#           - char_list : list of possessed character.
###
class Collection:
    def __init__(self, cookies, navigation_headers, verbose=False):
        print('Retrieving collection...')
        print('\tRetrieving raw collection data...')
        self.char_list = {}
        session_requests = requests.session()
        page = session_requests.get('https://www.urban-rivals.com/collection/index.php', headers=navigation_headers, params=params, cookies=cookies)
        tree = html.fromstring(page.content)
        max_page = tree.xpath('//a[i/@class="fas fa-angle-double-right"]/@data-page')
        max_page = int(max_page[0])

        rs = []

        for i in range(max_page+1):
            tmp_params = (*params, ('page',str(i)))
            rs.append(grequests.get('https://www.urban-rivals.com/collection/index.php', headers=navigation_headers, params=tmp_params, cookies=cookies))

        if verbose==True:
            sys.stdout.write("\t\tSending requests...")
            sys.stdout.flush()

        pages = grequests.map(rs, size=100)

        if verbose==True:
            sys.stdout.write("\r\t\tRequests sent.      \n")
            sys.stdout.flush()

        chars_processed = 0
        pages_processed = 0
        for page in pages:
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

                if verbose == True:
                    sys.stdout.write("\r\t\t%i characters retrieved. Pages processed : %i/%i" % (chars_processed, pages_processed+1, max_page+1))
                    sys.stdout.flush()
                chars_processed+=1
            pages_processed+=1
                
        if verbose==True:
            print()
            
        print('\tRaw collection data retrieved.')
        self.levels_and_names(cookies, navigation_headers, verbose)
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
    def levels_and_names(self, cookies, navigation_headers, verbose):
        print('\tRetrieving levels and names...')
        chars_data_file={}
        if os.path.exists(working_dir_path+"data/chars_data.txt"):
            with open(working_dir_path+"data/chars_data.txt", 'r') as f:
                for line in f.readlines():
                    if line.strip(' \n')!="":
                        line.replace('\n','')
                        line_split=line.split(' ')
                        chars_data_file[int(line_split[0])]=(int(line_split[1]), int(line_split[2]), str(line_split[3]))
                f.close()

        rs_chars_data = []
        data_added=0
        for i in self.char_list.keys():
            i = int(i)
            if i in chars_data_file:
                self.char_list[i].min_level=chars_data_file[i][0]
                self.char_list[i].max_level=chars_data_file[i][1]
                self.char_list[i].name=chars_data_file[i][2]
            else:
                data_added+=1
                if verbose==True:
                    sys.stdout.write("\r\t\tMissing data for %i characters." % data_added)
                    sys.stdout.flush()
                rs_chars_data.append(grequests.get('https://www.urban-rivals.com/game/characters/?id_perso='+str(i), headers=navigation_headers, cookies=cookies))

        if data_added>0:
            if verbose==True:
                sys.stdout.write("\n\t\tRetrieving missing data.")
                sys.stdout.flush()
            chars_data_pages = grequests.map(rs_chars_data, size=100)
            for page in chars_data_pages:
                char_id = int(page.url.split('=')[1])
                if str(page.text) != "":
                    tree = html.fromstring(page.content)
                    tmp_levels = tree.xpath('//img[@class="card-picture js-lazyload"]/@data-original')
                    tmp_levels = [int(str(i)[-12:-11]) for i in tmp_levels]
                    tmp_min=min(tmp_levels)
                    tmp_max=max(tmp_levels)
                    tmp_name = tree.xpath('//h2[@class="page-header-responsive text-white text-center py-5 d-block d-lg-none"]/text()')
                    tmp_name = tmp_name[0].split(':')[1].strip(" \n").replace(' ','_')
                    chars_data_file[char_id]=(tmp_min, tmp_max, tmp_name)
                    self.char_list[char_id].min_level=tmp_min
                    self.char_list[char_id].max_level=tmp_max
                    self.char_list[char_id].name=tmp_name
            sys.stdout.write("\r\t\tAdded %i new entries to chars_data.txt            \n" % data_added)
            sys.stdout.flush()
            if not os.path.exists(working_dir_path+"data/"):
                os.mkdir(working_dir_path+"data/")
            with open(working_dir_path+"data/chars_data.txt", "w") as f:
                for i in sorted(chars_data_file):
                    f.write(str(i)+" "+str(chars_data_file[i][0])+" "+str(chars_data_file[i][1])+" "+str(chars_data_file[i][2]).strip('\n')+"\n")
            f.close()
            data_added=0
            print('\tLevels and names retrieved.')
        else:
            sys.stdout.write("\r\tLevels and names retrieved.\n")
            sys.stdout.flush()

    ###
    # Sorts every characters in 4 files :
    #           - possessed.txt : characters levels that are possessed (or needs level up from a double under-leveled card).
    #           - to_level.txt : characters that are possessed but underleveled.
    #           - missing.txt : characters levels that are missing.
    #           - to_sell.txt : doubles to sell.
    # Oldest cards are prioritized, even over the ones that already have the required level.
    ###
    def process_and_save_all_evos(self):
        print('Processing collection data...')

        filtered = {}
        if os.path.exists(working_dir_path+"filter/filter.txt"):
            with open(working_dir_path+"filter/filter.txt") as f:
                for line in f.readlines():
                    line = line.strip(' \n')
                    if line != '':
                        line_split = line.split(' ')
                        if len(line_split) == 1:
                            filtered[int(line_split[0])]=(0,5)
                        elif len(line_split) == 2:
                            filtered[int(line_split[0])]=(0,int(line_split[1]))
                        elif len(line_split) == 3:
                            filtered[int(line_split[0])]=(int(line_split[1]), int(line_split[2]))
            f.close()

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
                    for k in reversed(range(index+1,len(ids_to_keep))): # char level can only go up
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
                    if tmp_char.char_id in filtered:
                        if filtered[tmp_char.char_id][1]<char_level:
                            ids_to_sell[index].append(char_id)
                        elif char_level<filtered[tmp_char.char_id][0]:
                            possessed_chars_file+=str(tmp_char.char_id)+" "+str(char_id)+" "+str(tmp_char.name).strip('\n')+" "+str(char_level)+"* -> "+str(filtered[tmp_char.char_id][0])+"* FILTERED\n"
                            to_evolve_chars_file+= str(char_id)+" "+str(char_level)+" "+str(filtered[tmp_char.char_id][0])+" \n"
                        else:
                            possessed_chars_file+=str(tmp_char.char_id)+" "+str(char_id)+" "+str(tmp_char.name).strip('\n')+" "+str(char_level)+"* FILTERED\n"
                    else:
                        ids_to_sell[index].append(char_id)
                broke=False

            for j in range(len(ids_to_keep)):
                tmp_str=str(tmp_char.char_id)+" "+str(ids_to_keep[j])+" "+str(tmp_char.name).strip('\n')+" "
                if ids_to_keep[j]==0 and len(tmp_char.name.split('_L'))<2:
                    missing_chars_file+= str(tmp_char.char_id)+" "+str(tmp_char.name).strip('\n')+" "+str(tmp_min_level+j)+"*\n"
                elif ids_to_keep[j]>0 and possessed_chars[j]==0:
                    possessed_chars_file+= tmp_str+str(ids_to_keep_real_levels[j])+"* -> "+str(tmp_min_level+j)+"*\n"
                    to_evolve_chars_file+= str(ids_to_keep[j])+" "+str(ids_to_keep_real_levels[j])+" "+str(tmp_min_level+j)+" \n"
                else:
                    possessed_chars_file+= tmp_str+str(tmp_min_level+j)+"*\n"

            for j in range(len(ids_to_sell)):
                for k in range(len(ids_to_sell[j])):
                    double_chars_file+=str(tmp_char.char_id)+" "+str(ids_to_sell[j][k])+" "+str(tmp_char.name.strip('\n'))+" \n"

        if not os.path.exists(working_dir_path+"collection/"):
            os.mkdir(working_dir_path+"collection/")

        sys.stdout.write("\tUpdating possessed evolutions list...")
        sys.stdout.flush()
        with open(working_dir_path+"collection/collection.txt", 'w') as f:
            f.write(possessed_chars_file)
            f.close()
        sys.stdout.write("\r\tcollection.txt updated.                 \n")
        sys.stdout.flush()

        if len(to_evolve_chars_file)>0:
            sys.stdout.write("\tUpdating underleveled characters list...")
            sys.stdout.flush()
            with open(working_dir_path+"to_level.txt", 'w') as f:
                f.write(to_evolve_chars_file)
                f.close()
            sys.stdout.write("\r\tto_level.txt updated.                   \n")
            sys.stdout.flush()

        sys.stdout.write("\tUpdating missing evolutions list...")
        sys.stdout.flush()
        with open(working_dir_path+"collection/missing.txt", 'w') as f:
            f.write(missing_chars_file)
            f.close()
        sys.stdout.write("\r\tmissing.txt updated.               \n")
        sys.stdout.flush()

        if len(double_chars_file)>0:
            sys.stdout.write("\tUpdating double characters list...")
            sys.stdout.flush()
            double_chars_file+="0 0 0" # Needs this line to sell last character
            with open(working_dir_path+"to_sell.txt", 'w') as f:
                f.write(double_chars_file)
                f.close()
            sys.stdout.write("\r\tto_sell.txt updated.              \n")
            sys.stdout.flush()

        sys.stdout.write("Collection data processed.\n")
        sys.stdout.flush()

    ###
    # Sorts every characters in 3 files :
    #           - possessed.txt : characters that are possessed.
    #           - to_level.txt : characters that are possessed but underleveled.
    #           - to_sell.txt : doubles to sell.
    ###
    def process_and_save(self):
        print('Processing collection data...')

        filtered = {}
        if os.path.exists(working_dir_path+"filter/filter.txt"):
            with open(working_dir_path+"filter/filter.txt") as f:
                for line in f.readlines():
                    line = line.strip(' \n')
                    if line != '':
                        line_split = line.split(' ')
                        if len(line_split) == 1:
                            filtered[int(line_split[0])]=(0,5)
                        elif len(line_split) == 2:
                            filtered[int(line_split[0])]=(0,int(line_split[1]))
                        elif len(line_split) == 3:
                            filtered[int(line_split[0])]=(int(line_split[1]), int(line_split[2]))
            f.close()

        possessed_chars_file=""
        double_chars_file=""
        to_evolve_chars_file=""
        for i in sorted(self.char_list.keys()):
            tmp_char=self.char_list[i]
            tmp_max_level=tmp_char.max_level
            id_to_keep = 0
            id_to_keep_real_level = 0
            ids_to_sell = []
            found=False
            for char_id, char_level in tmp_char.player_char_ids:
                if found==False:
                    if char_level<tmp_max_level and id_to_keep==0:
                        id_to_keep=char_id
                        id_to_keep_real_level=char_level
                    elif char_level==tmp_max_level:
                        if id_to_keep>0:
                            if tmp_char.char_id in filtered:
                                if filtered[tmp_char.char_id][1]<char_level:
                                    ids_to_sell.append(id_to_keep)
                                else:
                                    possessed_chars_file+=str(tmp_char.char_id)+" "+str(char_id)+" "+str(tmp_char.name).strip('\n')+" "+str(char_level)+"* FILTERED\n"
                            else:
                                ids_to_sell.append(id_to_keep)
                        id_to_keep=char_id
                        found=True
                    else:
                        if tmp_char.char_id in filtered:
                            if filtered[tmp_char.char_id][1]<char_level:
                                ids_to_sell.append(char_id)
                            else:
                                possessed_chars_file+=str(tmp_char.char_id)+" "+str(char_id)+" "+str(tmp_char.name).strip('\n')+" "+str(char_level)+"* FILTERED\n"
                        else:
                            ids_to_sell.append(char_id)
                else:
                    if tmp_char.char_id in filtered:
                        if filtered[tmp_char.char_id][1]<char_level:
                            ids_to_sell.append(char_id)
                        else:
                            possessed_chars_file+=str(tmp_char.char_id)+" "+str(char_id)+" "+str(tmp_char.name).strip('\n')+" "+str(char_level)+"* FILTERED\n"
                    else:
                        ids_to_sell.append(char_id)

            if id_to_keep>0:
                if found == True:
                    possessed_chars_file+=str(tmp_char.char_id)+" "+str(id_to_keep)+" "+str(tmp_char.name).strip('\n')+" "+str(tmp_max_level)+"* \n"
                else:
                    possessed_chars_file+=str(tmp_char.char_id)+" "+str(id_to_keep)+" "+str(tmp_char.name).strip('\n')+" "+str(id_to_keep_real_level)+"* -> "+str(tmp_max_level)+"* \n"
                    to_evolve_chars_file+=str(id_to_keep)+" "+str(id_to_keep_real_level)+" "+str(tmp_max_level)+" \n"

            if len(ids_to_sell)>0:
                for j in range(len(ids_to_sell)):
                    double_chars_file+=str(tmp_char.char_id)+" "+str(ids_to_sell[j])+" "+str(tmp_char.name.strip('\n'))+" \n"

        if not os.path.exists(working_dir_path+"collection/"):
            os.mkdir(working_dir_path+"collection/")

        sys.stdout.write("\tUpdating possessed characters list (keeping one of each card only)...")
        sys.stdout.flush()
        with open(working_dir_path+"collection/collection.txt", 'w') as f:
            f.write(possessed_chars_file)
            f.close()
        sys.stdout.write("\r\tcollection.txt updated.                                              \n")
        sys.stdout.flush()

        if len(to_evolve_chars_file)>0:
            sys.stdout.write("\tUpdating underleveled characters list...")
            sys.stdout.flush()
            with open(working_dir_path+"to_level.txt", 'w') as f:
                f.write(to_evolve_chars_file)
                f.close()
            sys.stdout.write("\r\tto_level.txt updated.                   \n")
            sys.stdout.flush()

        if len(double_chars_file)>0:
            sys.stdout.write("\tUpdating double characters list...")
            sys.stdout.flush()
            double_chars_file+="0 0 0" # Needs this line to sell last character
            with open(working_dir_path+"to_sell.txt", 'w') as f:
                f.write(double_chars_file)
                f.close()
            sys.stdout.write("\r\tto_sell.txt updated.              \n")
            sys.stdout.flush()

        sys.stdout.write("Collection data processed.\n")
        sys.stdout.flush()

    ###
    # Saves the collection to a raw_collection.txt file
    ###
    def save(self):
        sys.stdout.write("Saving pre-processed collection...")
        sys.stdout.flush()

        if not os.path.exists(working_dir_path+"collection/"):
            os.mkdir(working_dir_path+"collection/")

        with open(working_dir_path+"collection/raw_collection.txt", 'w') as f:
            f.write(str(self))
            f.close()

        sys.stdout.write("\rPre-processed collection saved to raw_collection.txt\n")
        sys.stdout.flush()

    def __str__(self):
        tmp_str=""
        for character in sorted(self.char_list.values()):
            tmp_str += str(character) + '\n'
        return tmp_str

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
        with open(working_dir_path+"logs/log_cancels.txt",'w') as f:
            f.write(cancels)
            f.close()
    sys.stdout.write("Cancelled offers for %i characters.     \n" % total)
    sys.stdout.flush()

###
# Sells every card described in a to_sell.txt file.
###
def sell_cards(cookies, navigation_headers, action_headers, verbose=False, log=False):

    to_sell = []

    if os.path.exists(working_dir_path+"to_sell.txt"):
        with open(working_dir_path+"to_sell.txt", 'r') as f:
            for line in f.readlines():
                line=line.strip('\n')
                if line!='':
                    to_sell.append(line)
        os.remove(working_dir_path+"to_sell.txt")
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
                line_split=line.split(' ')
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
            price_index=0

            for i in range(processed_index, len(to_sell)):
                line = to_sell[i]
                line_split=line.split(' ')
                if int(line_split[0])!=previous_id:
                    if previous_id!=0:
                        page = prices_pages[price_index]
                        price_index+=1
                        tree = html.fromstring(page.content)
                        tmp_price = str(tree.xpath('//td[@class="align-middle" and img/@title="Clintz"]/text()')[0]).replace('\n','')
                        price=0
                        if tmp_price == []:
                            price = 2000000000
                        else:
                            tmp_price = tmp_price.replace(' ','')
                            price = int(tmp_price)-1
                        total+=len(sales)*price
                        if verbose == True:
                            print("\t\tPreparing offer for "+str(len(sales))+"x "+str(previous_name)+" ("+str(previous_id)+") price="+str(price)+"/u total="+str(len(sales)*price))
                        for j in range(len(sales)):
                            data = {}
                            data['price'] = str(price)+'^'
                            data['action'] = 'sellToPublic^'
                            data['id_perso_joueur']=str(sales[j])
                            rs_sales.append(grequests.post('https://www.urban-rivals.com/ajax/collection/sell_card.php', data=data, cookies=cookies, headers=action_headers))
                    previous_id=int(line_split[0])
                    previous_name=line_split[2].strip('\n')
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
            with open(working_dir_path+"logs/log_sales.txt", "w") as f:  
                f.write(sales_file)
                f.close()

        print(str(total_cards)+" cards put for sale. Total value : "+str(total))

###
# Levels characters given a to_xp.txt file.
###
def xp_cards(cookies, action_headers, pay_for_xp=False, verbose=False, log=False):
    to_level=[]
    xp_reserve=0
    if os.path.exists(working_dir_path+"to_level.txt"):
        with open(working_dir_path+"to_level.txt", 'r') as f:
            lines = f.readlines()
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
        f.close()
        os.remove(working_dir_path+"to_level.txt")

    if len(to_level)==0:
        print("No card to level up.")
        return

    rs_xp = []
    xp_file=""
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
                    print("\t\tGave "+str(prev_xp_reserve-xp_reserve)+"xp to "+line_split[0]+", "+str(xp_reserve)+"xp remain in reserve.")
                total_cards+=1
            elif pay_for_xp == True:
                if xp_reserve>0:
                    data={}
                    data['action'] = 'addxpfromreserve'
                    data['characterInCollectionID'] = line_split[0]
                    requests.post('https://www.urban-rivals.com/ajax/collection/', headers=action_headers, cookies=cookies, data=data)
                    if verbose==True:
                        print("\t\tGave "+str(xp_reserve)+"xp to "+line_split[0]+", reserve is now empty.")
                    print("\tPreparing requests...")
                    data={}
                    data['action'] = 'addXPForClintz'
                    data['characterInCollectionID'] = line_split[0]
                    data['buyXP'] = 'true'
                    rs_xp.append(grequests.post('https://www.urban-rivals.com/ajax/collection/', headers=action_headers, cookies=cookies, data=data))                             
                    if verbose==True:
                        print("\t\tPreparing to add "+str(xp_tiers[xp_index]-xp_reserve)+"xp to "+line_split[0]+".")
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
                        print("\t\tPreparing to add "+str(xp_tiers[xp_index])+"xp to "+line_split[0]+".")
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
        for xp in logs:
            xp_file+=xp.text[0:101]+'\n'
        with open(working_dir_path+"logs/log_xp.txt", 'w') as f:
            f.write(xp_file)
            f.close()

    prnt_str = str(total_cards)+" cards leveled up"
    if pay_for_xp == True:
        prnt_str+= " for a total cost of "+str(total_clintz)+" clintz."
    else:
        prnt_str+= "."
    print(prnt_str)

###
# Decodes a binary encoding of the parameters
# See the top of the file.
###
def decode_parameters(n):
    global param_cancel_sales, param_keep_single_character, param_xp, param_pay_for_xp, param_sell_doubles, param_verbose, param_log
    parameters = [0,0,0,0,0,0,0]
    for i in range(7):
        parameters[i] = n%(2**(i+1))
        n-=n%(2**(i+1))

    if parameters[0] > 0:
        param_cancel_sales=True
    else:
        param_cancel_sales=False

    if parameters[1] > 0:
        param_keep_single_character=True
    else:
        param_keep_single_character=False

    if parameters[2] > 0:
        param_xp=True
    else:
        param_xp=False

    if parameters[3] > 0:
        param_pay_for_xp=True
    else:
        param_pay_for_xp=False

    if parameters[4] > 0:
        param_sell_doubles=True
    else:
        param_sell_doubles=False

    if parameters[5] > 0:
        param_verbose=True
    else:
        param_verbose=False

    if parameters[6] > 0:
        param_log=True
    else:
        param_log=False

###
# Does a full update of the collection :
#           1. Cancels every current market offers if cancel_sales is set to 'True'.
#           2. Retrieve collection.
#           3. Updates the lists.
#              - If keeps_evos is set to 'True' : keeps one card of each character at each level.
#              - Else, keeps one card of each character.
#           4. Levels up cards to reach their kept level if xp is set to 'True'. If xp_reserve_only is 'True', will only level from xp reserve.
#           5. Sells every double cards if sell_doubles is set to 'True'.
###
def update(cookies, navigation_headers, action_headers, mode):
    global param_cancel_sales, param_keep_single_character, param_xp, param_pay_for_xp, param_sell_doubles, param_verbose, param_log

    print("\n=== URBot v.2 - smart_seller ===")

    session_requests = requests.session()
    page = session_requests.get('https://www.urban-rivals.com/collection/index.php', headers=navigation_headers, params=params, cookies=cookies)
    tree = html.fromstring(page.content)
    max_page = tree.xpath('//a[i/@class="fas fa-angle-double-right"]/@data-page')
    try:
        max_page = int(max_page[0])
    except IndexError:
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
            \t\'collection-filters\': \'^{^%^22nb_per_page^%^22:^%^2248^%^22^}\',\n\
            \t\'cnil\': \'true\',\n\
            \t\'ur_token\': \'long alphanumeric string\',\n\
            \t\'UR_SESSID\': \'long alphanumeric string\',\n\
            \t\'csrf-token\': \'long alphanumeric string\',\n\
        }\n")
        sys.stdout.flush()
        return

    decode_parameters(mode)

    print("\nChosen parameters :")
    print("\tparam_cancel_sales "+str(param_cancel_sales).upper())
    print("\tparam_keep_single_character "+str(param_keep_single_character).upper())
    print("\tparam_xp "+str(param_xp).upper())
    print("\tparam_pay_for_xp "+str(param_pay_for_xp).upper())
    print("\tparam_sell_doubles "+str(param_sell_doubles).upper())
    print("\tparam_verbose "+str(param_verbose).upper())
    print("\tparam_log "+str(param_log).upper())
    if param_keep_single_character==True and param_sell_doubles==True:
        print("WARNING keeping evolutions is OFF (param_keep_single_character) and selling is ON (param_sell_doubles), \
this could result in losing a part of your collection. \nPress any key to continue. \nPress CTRL-C to abort.")
        try:
            input()
        except KeyboardInterrupt:
            sys.exit()

    if param_log==True and not os.path.exists(working_dir_path+"logs/"):
        os.mkdir(working_dir_path+"logs/")

    if param_cancel_sales == True:
        cancel_all_sales(cookies, navigation_headers, action_headers, param_verbose, param_log)

    collection = Collection(cookies, navigation_headers, param_verbose)

    if param_keep_single_character == False:
        collection.process_and_save_all_evos()
    else:
        collection.process_and_save()
    if param_xp == True:
        xp_cards(cookies, action_headers, param_pay_for_xp, param_verbose, param_log)
                    
    if param_sell_doubles == True:
        sell_cards(cookies, navigation_headers, action_headers, param_verbose, param_log)

    try:
        print("Press ENTER to quit.")
        input()
    except KeyboardInterrupt:
        sys.exit() 