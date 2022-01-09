import sys
import os
import grequests
import requests
from lxml import html

working_dir_path = os.getcwd()

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
        self.min_level=5
        self.max_level=1
        self.name=""
        self.rarity=""

    def __str__(self):
        tmp_str = str(self.char_id)+" "+str(self.name.strip('\n'))+" (x"+str(self.quantity)+") "+str(self.min_level)+"*-"+str(self.max_level)+"*"
        for i in sorted(self.player_char_ids, key=lambda x: (int(x[1]),int(x[0]))):
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
    def __init__(self, cookies, navigation_headers, char_name="", verbose=False):
        print('Retrieving collection...')
        print('\tRetrieving raw collection data...')
        self.char_list = {}
        session_requests = requests.session()
        params = (
            ('view', 'collection'),
            ('sortby', 'date'),
            ('orderby', 'desc'),
            ('group', 'all'),
            ('nb_per_page', '48')
        )
        if len(char_name)>0:
            params = (*params, ('search', char_name))
        page = session_requests.post('https://www.urban-rivals.com/collection/collection_page.php', headers=navigation_headers, data=params, cookies=cookies)
        tree = html.fromstring(page.content)
        max_page = tree.xpath('//a[@class="page-link"]/@data-page')
        try:
            max_page = int(max_page[-1])
        except IndexError:
            max_page = 1

        rs = []

        for i in range(max_page+1):
            tmp_params = (*params, ('page',str(i)))
            rs.append(grequests.post('https://www.urban-rivals.com/collection/collection_page.php', headers=navigation_headers, data=tmp_params, cookies=cookies))

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
            characters = tree.xpath('//a[contains(@class, "card-layer layer-")]/@href')
            characters_level = [str(j[-12:-11]) for j in tree.xpath('//img[@class="card-picture js-lazyload"]/@data-original')]
            for i in range(len(characters_level)):
                if characters_level[i]=='T':
                    characters_level[i]=int(str(tree.xpath('//img[@class="card-picture js-lazyload"]/@data-original')[i][-18:-17]))
                else:
                    characters_level[i] = int(characters_level[i])
            for j in range(len(characters_level)): # HERE WAS  for j in range(len(charatecers)):
                character = characters[j]
                character = character.replace("/game/characters/?id_perso=",'')
                character = character.replace("&id_pj=%23",' ')
                character = character.replace('-', ' ')
                character_split = character.split(' ')

                print(character_split,"1")
                
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
        chars_data_file=[]

        if os.path.exists(os.path.join(working_dir_path, "data", "chars_data.txt")):
            with open(os.path.join(working_dir_path, "data", "chars_data.txt"), 'r') as f:
                for line in f.readlines():
                    if line.strip(' \n')!="":
                        line.replace('\n','')
                        line_split=line.split(' ')
                        chars_data_file.append((int(line_split[0]),line_split[1],int(line_split[2]),line_split[3],line_split[4],line_split[5],line_split[6],line_split[7]))
                f.close()

        rs_chars_data = []
        data_added=0
        for i in self.char_list.keys():
            i = int(i)
            found=False
            for j in range(len(chars_data_file)):
                if int(i)==chars_data_file[j][0]:
                    self.char_list[i].min_level=min(self.char_list[i].min_level, chars_data_file[j][2])
                    self.char_list[i].max_level=max(self.char_list[i].max_level, chars_data_file[j][2])
                    self.char_list[i].name=chars_data_file[j][1]
                    self.char_list[i].rarity=chars_data_file[j][3]
                    found=True
            if found==False:
                data_added+=1
                if verbose==True:
                    sys.stdout.write("\r\t\tMissing data for %i evolutions." % data_added)
                    sys.stdout.flush()
                rs_chars_data.append(grequests.get('https://www.urban-rivals.com/game/characters/?id_perso='+str(i), headers=navigation_headers, cookies=cookies))
            found=False

        if data_added>0:

            if verbose==True:
                sys.stdout.write("\n\t\tRetrieving missing data.")
                sys.stdout.flush()
            chars_data_pages = grequests.map(rs_chars_data, size=100)

            for page in chars_data_pages:
                tree = html.fromstring(page.content)
                character_id = int(str(page.url)[-4:].strip('='))
                character_name = tree.xpath('//h2[@class="page-header-responsive text-white text-center py-5 d-block d-lg-none"]/text()')[0].split(':')[1].strip(" \n").replace(' ','_')
                character_levels = [str(j[-12:-11]) for j in tree.xpath('//img[@class="card-picture js-lazyload"]/@data-original')]
                for i in range(len(character_levels)):
                    if character_levels[i]=='T':
                        character_levels[i]=int(str(tree.xpath('//img[@class="card-picture js-lazyload"]/@data-original')[i][-18:-17]))
                    else:
                        character_levels[i] = int(character_levels[i])
                character_clans = [int(str(j)[-2:].strip('=')) for j in tree.xpath('//div/a[img/@class="card-clan img-fluid"]/@href')]
                character_abilities = [j.replace(' ','_') for j in tree.xpath('//div[@class="card-bottom"]/div[contains(@class, "card-ability")]/text()')]
                character_powers = [int(j) for j in tree.xpath('//div[@class="h5 card-power m-0"]/text()')]
                character_damages = [int(j) for j in tree.xpath('//div[@class="h5 card-damage m-0"]/text()')]
                character_rarity = str(tree.xpath('//div[contains(@class, "card-top card-top-")]/@class')[0])[-2:].strip('-')
                self.char_list[character_id].min_level=min(character_levels)
                self.char_list[character_id].max_level=max(character_levels)
                self.char_list[character_id].name=character_name
                self.char_list[character_id].rarity=character_rarity
                if len(character_levels)>1:
                    for j in range(len(character_levels)):   
                        chars_data_file.append((character_id, character_name, character_levels[j], character_rarity, character_clans[j], character_powers[j], character_damages[j], character_abilities[j]))    

            chars_data_file.sort(key=lambda x: (int(x[0]), int(x[2])))

            if not os.path.exists(os.path.join(working_dir_path,"data")):
                os.mkdir(os.path.join(working_dir_path, "data"))
            with open(os.path.join(working_dir_path, "data", "chars_data.txt"), "w") as f:
                for i in range(len(chars_data_file)):
                    f.write(str(chars_data_file[i][0])+" "+str(chars_data_file[i][1])+" "+str(chars_data_file[i][2])+" "+str(chars_data_file[i][3])+" "+str(chars_data_file[i][4])+" "+str(chars_data_file[i][5])+" "+str(chars_data_file[i][6])+" "+str(chars_data_file[i][7])+" \n")
                f.close()
            
            sys.stdout.write("\r\t\tAdded %i new entries to chars_data.txt            \n" % data_added)
            data_added=0
            sys.stdout.flush()
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
    def process_and_save_all_evos(self, filter_path=""):
        print('Processing collection data...')

        filtered, redirected = self.load_filter(filter_path)
       

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
            filtered_chars_file=""
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
                        if filtered[tmp_char.char_id][1]<char_level or filtered[tmp_char.char_id][2]==0:
                            ids_to_sell[index].append(char_id)
                        elif filtered[tmp_char.char_id][2]!=0:
                            if char_level<filtered[tmp_char.char_id][0]:
                                filtered_chars_file+=str(tmp_char.char_id)+" "+str(char_id)+" "+str(tmp_char.name).strip('\n')+" "+str(char_level)+"* -> "+str(filtered[tmp_char.char_id][0])+"* FILTERED\n"
                                to_evolve_chars_file+= str(char_id)+" "+str(char_level)+" "+str(filtered[tmp_char.char_id][0])+" \n"
                            else:
                                filtered_chars_file+=str(tmp_char.char_id)+" "+str(char_id)+" "+str(tmp_char.name).strip('\n')+" "+str(char_level)+"* FILTERED\n"
                            filtered[tmp_char.char_id] = (filtered[tmp_char.char_id][0], filtered[tmp_char.char_id][1], filtered[tmp_char.char_id][2]-1)
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
                if tmp_char.char_id in redirected:
                    for k in range(len(ids_to_sell[j])):
                        double_chars_file+= str(tmp_char.char_id)+" "+str(ids_to_sell[j][k])+" "+str(tmp_char.name.strip('\n'))+" "+str(redirected[tmp_char.char_id][0])+" "+str(redirected[tmp_char.char_id][1])+" \n"
                else:
                    for k in range(len(ids_to_sell[j])):
                        double_chars_file+= str(tmp_char.char_id)+" "+str(ids_to_sell[j][k])+" "+str(tmp_char.name.strip('\n'))+" \n"

            if filtered_chars_file!="":
                possessed_chars_file+=filtered_chars_file

        if not os.path.exists(os.path.join(working_dir_path,"data")):
            os.mkdir(os.path.join(working_dir_path,"data"))

        if not os.path.exists(os.path.join(working_dir_path, "data", "collection_data")):
            os.mkdir(os.path.join(working_dir_path, "data", "collection_data"))

        sys.stdout.write("\tUpdating possessed evolutions list...")
        sys.stdout.flush()
        with open(os.path.join(working_dir_path, "data", "collection_data", "collection.txt"), 'w') as f:
            f.write(possessed_chars_file)
            f.close()
        sys.stdout.write("\r\tcollection.txt updated.                 \n")
        sys.stdout.flush()

        if len(to_evolve_chars_file)>0:
            sys.stdout.write("\tUpdating underleveled characters list...")
            sys.stdout.flush()
            with open(os.path.join(working_dir_path, "data","to_level.txt"), 'w') as f:
                f.write(to_evolve_chars_file)
                f.close()
            sys.stdout.write("\r\tto_level.txt updated.                   \n")
            sys.stdout.flush()

        sys.stdout.write("\tUpdating missing evolutions list...")
        sys.stdout.flush()
        with open(os.path.join(working_dir_path, "data","collection_data", "missing.txt"), 'w') as f:
            f.write(missing_chars_file)
            f.close()
        sys.stdout.write("\r\tmissing.txt updated.               \n")
        sys.stdout.flush()

        if len(double_chars_file)>0:
            sys.stdout.write("\tUpdating double characters list...")
            sys.stdout.flush()
            double_chars_file+="0 0 0" # Needs this line to sell last character
            with open(os.path.join(working_dir_path, "data", "to_sell.txt"), 'w') as f:
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
    def process_and_save(self, filter_path=""):
        print('Processing collection data...')

        filtered, redirected = self.load_filter(filter_path)

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
                                if filtered[tmp_char.char_id][1]<id_to_keep_real_level or filtered[tmp_char.char_id][2]==0:
                                    ids_to_sell.append(id_to_keep)
                                elif filtered[tmp_char.char_id][2]!=0:
                                    if id_to_keep_real_level<filtered[tmp_char.char_id][0]:
                                        possessed_chars_file+=str(tmp_char.char_id)+" "+str(id_to_keep)+" "+str(tmp_char.name).strip('\n')+" "+str(id_to_keep_real_level)+"* -> "+str(filtered[tmp_char.char_id][0])+"* FILTERED\n"
                                        to_evolve_chars_file+= str(id_to_keep)+" "+str(id_to_keep_real_level)+" "+str(filtered[tmp_char.char_id][0])+" \n"
                                    else:
                                        possessed_chars_file+=str(tmp_char.char_id)+" "+str(id_to_keep)+" "+str(tmp_char.name).strip('\n')+" "+str(id_to_keep_real_level)+"* FILTERED\n"
                                    filtered[tmp_char.char_id] = (filtered[tmp_char.char_id][0], filtered[tmp_char.char_id][1], filtered[tmp_char.char_id][2]-1)
                            else:
                                ids_to_sell.append(id_to_keep)
                        id_to_keep=char_id
                        found=True
                    else:
                        if tmp_char.char_id in filtered:
                            if filtered[tmp_char.char_id][1]<char_level or filtered[tmp_char.char_id][2]==0:
                                ids_to_sell.append(char_id)
                            elif filtered[tmp_char.char_id][2]!=0:
                                if char_level<filtered[tmp_char.char_id][0]:
                                    possessed_chars_file+=str(tmp_char.char_id)+" "+str(char_id)+" "+str(tmp_char.name).strip('\n')+" "+str(char_level)+"* -> "+str(filtered[tmp_char.char_id][0])+"* FILTERED\n"
                                    to_evolve_chars_file+= str(char_id)+" "+str(char_level)+" "+str(filtered[tmp_char.char_id][0])+" \n"
                                else:
                                    possessed_chars_file+=str(tmp_char.char_id)+" "+str(char_id)+" "+str(tmp_char.name).strip('\n')+" "+str(char_level)+"* FILTERED\n"
                                filtered[tmp_char.char_id] = (filtered[tmp_char.char_id][0], filtered[tmp_char.char_id][1], filtered[tmp_char.char_id][2]-1)
                        else:
                            ids_to_sell.append(char_id)
                else:
                    if tmp_char.char_id in filtered:
                        if filtered[tmp_char.char_id][1]<char_level or filtered[tmp_char.char_id][2]==0:
                            ids_to_sell.append(char_id)
                        elif filtered[tmp_char.char_id][2]!=0:
                            if char_level<filtered[tmp_char.char_id][0]:
                                possessed_chars_file+=str(tmp_char.char_id)+" "+str(char_id)+" "+str(tmp_char.name).strip('\n')+" "+str(char_level)+"* -> "+str(filtered[tmp_char.char_id][0])+"* FILTERED\n"
                                to_evolve_chars_file+= str(char_id)+" "+str(char_level)+" "+str(filtered[tmp_char.char_id][0])+" \n"
                            else:
                                possessed_chars_file+=str(tmp_char.char_id)+" "+str(char_id)+" "+str(tmp_char.name).strip('\n')+" "+str(char_level)+"* FILTERED\n"
                            filtered[tmp_char.char_id] = (filtered[tmp_char.char_id][0], filtered[tmp_char.char_id][1], filtered[tmp_char.char_id][2]-1)
                    else:
                        ids_to_sell.append(char_id)

            if id_to_keep>0:
                if found == True:
                    possessed_chars_file+=str(tmp_char.char_id)+" "+str(id_to_keep)+" "+str(tmp_char.name).strip('\n')+" "+str(tmp_max_level)+"* \n"
                else:
                    possessed_chars_file+=str(tmp_char.char_id)+" "+str(id_to_keep)+" "+str(tmp_char.name).strip('\n')+" "+str(id_to_keep_real_level)+"* -> "+str(tmp_max_level)+"* \n"
                    to_evolve_chars_file+=str(id_to_keep)+" "+str(id_to_keep_real_level)+" "+str(tmp_max_level)+" \n"

            if len(ids_to_sell)>0:
                if tmp_char.char_id in redirected:
                    for j in range(len(ids_to_sell)):
                        double_chars_file+=str(tmp_char.char_id)+" "+str(ids_to_sell[j])+" "+str(tmp_char.name.strip('\n'))+" "+str(redirected[tmp_char.char_id][0])+" "+str(redirected[tmp_char.char_id][1])+" \n"
                else:
                    for j in range(len(ids_to_sell)):
                        double_chars_file+=str(tmp_char.char_id)+" "+str(ids_to_sell[j])+" "+str(tmp_char.name.strip('\n'))+" \n"

        if not os.path.exists(os.path.join(working_dir_path,"data")):
            os.mkdir(os.path.join(working_dir_path,"data"))

        if not os.path.exists(os.path.join(working_dir_path, "data", "collection_data")):
            os.mkdir(os.path.join(working_dir_path, "data", "collection_data"))


        sys.stdout.write("\tUpdating possessed characters list (keeping one of each card only)...")
        sys.stdout.flush()
        with open(os.path.join(working_dir_path, "data", "collection_data", "collection.txt"), 'w') as f:
            f.write(possessed_chars_file)
            f.close()
        sys.stdout.write("\r\tcollection.txt updated.                                              \n")
        sys.stdout.flush()

        if len(to_evolve_chars_file)>0:
            sys.stdout.write("\tUpdating underleveled characters list...")
            sys.stdout.flush()
            with open(os.path.join(working_dir_path, "data", "to_level.txt"), 'w') as f:
                f.write(to_evolve_chars_file)
                f.close()
            sys.stdout.write("\r\tto_level.txt updated.                   \n")
            sys.stdout.flush()

        if len(double_chars_file)>0:
            sys.stdout.write("\tUpdating double characters list...")
            sys.stdout.flush()
            double_chars_file+="0 0 0" # Needs this line to sell last character
            with open(os.path.join(working_dir_path, "data", "to_sell.txt"), 'w') as f:
                f.write(double_chars_file)
                f.close()
            sys.stdout.write("\r\tto_sell.txt updated.              \n")
            sys.stdout.flush()

        sys.stdout.write("Collection data processed.\n")
        sys.stdout.flush()

    ###
    # Extracts filtering data from filter_path file
    ###
    def load_filter(self, filter_path):

        filtered={}
        redirected={}

        if filter_path!="":
            with open(filter_path, 'r') as f:
                for line in f.readlines():
                    line = line.strip(' \n')
                    if line != '':

                        # filter out comments
                        if "#" in line:
                            line=line.split("#")[0].strip(" ")

                        # checks if line contains a redirection instruction
                        line_redirect = []
                        to_redirect=False
                        if "to" in line:
                            to_redirect=True
                            line_redirect=line.split("to")
                            line = line_redirect[0].strip(" ")

                        line_split = line.split(' ') 
                        if len(line_split) == 1 and not to_redirect:
                            filtered[int(line_split[0])]=(0,5,-1)
                        elif len(line_split) == 2:
                            filtered[int(line_split[0])]=(0,int(line_split[1]), -1)
                        elif len(line_split) == 3:
                            filtered[int(line_split[0])]=(int(line_split[1]), int(line_split[2]), -1)
                        elif len(line_split) == 4:
                            filtered[int(line_split[0])]=(int(line_split[1]), int(line_split[2]), int(line_split[3]))

                        # if line contains 'to', redirects sale to specified player
                        if line_redirect!=[]:
                            line_redirect=line_redirect[1].strip(" ").split(' ')
                            redirected[int(line_split[0])]=(line_redirect[0], int(line_redirect[1]))
            f.close()

        return filtered, redirected



    ###
    # Saves the collection to a raw_collection.txt file
    ###
    def save(self):
        sys.stdout.write("Saving pre-processed collection...")
        sys.stdout.flush()

        if not os.path.exists(os.path.join(working_dir_path, "data")):
            os.mkdir(os.path.join(working_dir_path, "data"))

        if not os.path.exists(os.path.join(working_dir_path, "data", "collection_data")):
            os.mkdir(os.path.join(working_dir_path, "data", "collection_data"))

        with open(os.path.join(working_dir_path, "data", "collection_data", "raw_collection.txt"), 'w') as f:
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
# Levels characters given a to_level_path file.
###
def xp_cards(cookies, action_headers, to_level_path, pay_for_xp=False, verbose=False, log=False):
    to_level=[]
    xp_reserve=0
    if os.path.exists(to_level_path):
        with open(to_level_path, 'r') as f:
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
        os.remove(to_level_path)

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