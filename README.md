# URBot v.2
Bot for Urban Rivals by Huylenbroeck Florent.  
This bot will not be distributed. It won't work on any computer except mine.  
  
Smart seller is usable. see **Smart seller**.
  
# Smart seller
## Requirement ##
- python3
- python3  *requests*
- python3  *lxml*
- builder tools for Microsoft Visual Sudio
- python3  *grequests*  
- Setting up *.../URBot/python/web/cookies.py* (launch the smart_seller once to see a complete guide)  

*grequests* needs python3 *requests* and builder tools for Microsoft Visual Sudio, install them first.  
## Parameters ##
### Command ###
Call this program by navigating to '*.../URBot/python/* ' and using the command  
*python3 ./urbot_scraping.py update **sum***.  
&nbsp;&nbsp;&nbsp;&nbsp;where **sum** is the sum of the desired *True* arguments (**n** below):
n  | Parameter | Effect
------------- | ------------- | -------------
 1 | *param_cancel_sales* | Setting this to 'True' will cancel all current market sales before processing the collection.
 2 | *param_keep_single_character* | Setting this to 'True' will enable keeping one card of each character at each level, else only one card per character will be kept.
 4 | *param_xp* | Setting this to 'True' will use xp to level up underleveled characters.
 8 | *param_pay_for_xp* | Setting this to 'True' will allow paying for xp.
 16 | *param_sell_doubles* | Setting this to 'True' will sell every double cards after processing the collection, at an optimal price.
 32 | *param_verbose* | Setting this to 'True' will enable verbose mode.
 64 | *param_log* | Setting this to 'True' keeps logs about cancelled market offers, characters leveled up and sales offers as raw textual return value from request functions. Logs are put in '*.../URBot/python/logs/* ' folder.
### Useful arguments ###
sum  | usage  
------------- | -------------
0 | Default
54 | Level up kept underleveled characters with XP reserve then sell everything but one of each character.
55 | Cancel market sales, level up kept underleveled characters with XP reserve then sell everything but one of each character.
60 | Level up kept underleveled characters with XP reserve and clintz then sell everything but one of each character's evolution, keeping the oldest ones by id.
61 | Cancel market sales, level up kept underleveled characters with XP reserve and clintz then sell everything but one of each character's evolution, keeping the oldest ones by id.
62 | Level up kept underleveled characters with XP reserve and clintz then sell everything but one of each character.
63 | Cancel market sales, level up kept underleveled characters with XP reserve and clintz then sell everything but one of each character.
96 | Create or update *.../URBot/python/data/chars_data.txt* only.  
## Output ##
Additionally to the parameter's effect, smart_seller.py generates 2 to 3 files depending on the chosen parameters. They are located under '*.../URBot/python/collection/* '.
- **raw_collection.txt**  
This file contains every character of the player's collection including the ones that are put on the market.  
Example file :
<details>
  <summary><i>raw_collection.txt</i></summary>

      123 Natrang (x3) 1*-3*  
          616551985 1*  
          616719940 2*  
          129544906 3*  
      124 Sai_San (x4) 1*-4*  
          618514010 1*  
          622856929 2*  
          623232901 3*  
          425765630 4*  
      125 Tatane (x3) 1*-3*  
          615869020 1*  
          622662152 2*  
          170485662 3*  
      126 Nanook (x3) 1*-3*  
          619323141 1*  
          620587122 2*  
          9616941 3*  
      127 Akiko (x3) 1*-3*  
          612725422 1*  
          ...  
          616675942 2*  
      2051 Kola (x2) 1*-4*  
          624165264 1*  
          616559394 4*  
      2052 Gerdah (x4) 2*-5*  
          623219351 2*  
          624242421 3*  
          624165253 4*  
          622159315 5*  
      2053 Jakobs (x2) 1*-3*  
          623215595 1*  
          622160696 3*  
      2054 Matheo (x3) 1*-3*  
          623219356 1*  
          624165283 2*  
          622155128 3*  
      2055 Superpaquito (x2) 1*-4*  
          624165261 1*  
          622161676 4*  
      2056 El_D10S (x1) 3*-5*  
          625715329 5*  
</details>

- **collection.txt**  
This file contains every character of the player's collection, depending on the parameter **param_keep_single**.
This files also keeps track of the character that were leveled up or needs to. Their level is of the form "1* -> 2*".  
Example file with **param_keep_single**=*False* :
<details>
  <summary><i>collection.txt</i></summary>

      123 616551985 Natrang 1*  
      123 616719940 Natrang 2*  
      123 129544906 Natrang 3*  
      124 618514010 Sai_San 1*  
      124 622856929 Sai_San 2*  
      124 623232901 Sai_San 3*  
      124 425765630 Sai_San 4*  
      125 615869020 Tatane 1*  
      125 622662152 Tatane 2*  
      125 170485662 Tatane 3*  
      126 619323141 Nanook 1*  
      126 620587122 Nanook 2*  
      126 9616941 Nanook 3*  
      127 612725422 Akiko 1*  
      127 618547639 Akiko 1* -> 2*  
      127 432385009 Akiko 3*  
      128 622898813 Berserkgirl_Cr 1*  
      128 519421601 Berserkgirl_Cr 3*  
      129 615952306 Pino 1*  
      129 433507838 Pino 2*  
      ...  
      2048 616290277 Lom 2*  
      2049 622155131 El_Cascabel 3*  
      2049 624165249 El_Cascabel 4*  
      2049 616644292 El_Cascabel 5*  
      2050 623219354 Drivel 1*  
      2050 616675942 Drivel 2*  
      2051 624165264 Kola 1*  
      2051 616559394 Kola 4*  
      2052 623219351 Gerdah 2*  
      2052 624242421 Gerdah 3*  
      2052 624165253 Gerdah 1* -> 4*  
      2052 622159315 Gerdah 5*  
      2053 623215595 Jakobs 1*  
      2053 622160696 Jakobs 3*  
      2054 623219356 Matheo 1*  
      2054 624165283 Matheo 2*  
      2054 622155128 Matheo 3*  
      2055 624165261 Superpaquito 1*  
      2055 622161676 Superpaquito 4*  
      2056 625715329 El_D10S 5*  
</details>

- **missing.txt***  
This last file is optional. It is created if **param_keep_single** is *False*. It contains every missing evolutions of the possessed characters. It does not account for the characters the player doesn't possess nor Ld's evolutions.  
Example file :  
<details>
  <summary><i>missing.txt</i></summary>

    128 Berserkgirl_Cr 2*  
    158 Shawoman_Cr 2*  
    160 Yayoi_Cr 2*  
    162 Rass_Cr 2*  
    166 Zatman_Cr 1*  
    166 Zatman_Cr 2*  
    168 Armanda_Mt 1*  
    168 Armanda_Mt 2*  
    172 Ratanah_Mt 1*  
    172 Ratanah_Mt 2*  
    172 Ratanah_Mt 3*  
    182 Jackie_Cr 2*  
    182 Jackie_Cr 3*  
    187 Vermyn_N 2*  
    189 Lyse_Teria_Mt 1*  
    189 Lyse_Teria_Mt 2*  
    190 Vickie_Cr 2*  
    190 Vickie_Cr 3*  
    195 Lao_Cr 3*  
    195 Lao_Cr 4*  
    ...  
    2026 Palamu 3*  
    2026 Palamu 4*  
    2029 Timbo_K 3*  
    2029 Timbo_K 4*  
    2036 Glaxo 3*  
    2036 Glaxo 4*  
    2037 Miss_Denna 2*  
    2039 Edmund 1*  
    2041 Zinzinxxt 2*  
    2041 Zinzinxxt 3*  
    2043 C-Ortez 3*  
    2044 Banzai 2*  
    2046 Divus 1*  
    2046 Divus 2*  
    2051 Kola 2*  
    2051 Kola 3*  
    2053 Jakobs 2*  
    2055 Superpaquito 2*  
    2055 Superpaquito 3*  
    2056 El_D10S 3*  
    2056 El_D10S 4*  
</details>

# History
- **v.2.0**  
Done up to fighting + wheeling. Freezes at any non-expected event. Can run for ~30min.  
https://youtu.be/eXpFje_zFZM  
  
- **v.2.1**  
Most common unexpected events covered. Sometimes doesn't count rounds well. Can run for ~2h.  
https://youtu.be/_aADsqrScQg  
  
- **v.2.2**  
One or two unexpected events can still freeze the bot. Can run for ~12h.  
https://youtu.be/adtv3N9-JuE  
Added an auto-seller for the huge amount of card generated. Sells card for card's price -1 clintz. Sells a card every ~3s.  
https://youtu.be/SzbS91i63ow  
  
- **v.2.3**  
Still can freeze sometimes. Can run for ~12h.  
Improved auto-seller, made the choice of sorting easier. No console showing. Operates faster. Sells a card every 2.0s.  
https://youtu.be/Una60nVkD3E  

- **v.2.4**  
The client being not perfect, the bot can still freeze at the rarest unexpected events.  
Added a reset timer, now the fighting client is forced to relaunch after a maximum of 65 minutes.  
Can run indefinitely.  
Now also keep the stats of the session in '*.../URBOT/save/ '*  folder.  
    <details>
  <summary><i>.../URBOT/save/stats_2020-12-22_12h09.txt</i></summary>

        === STATS ===  
        Start    2020/12/21 21:00:57  
        End      2020/12/22 12:09:04  
        Duration            14:37:00  
        Views    1  
        Points   5277  
        Fights   485  
        Wins     252  
        Loses    229  
        Draws    4  
        WR       52%  
        === DEBUG ===  
        Time until next reset (min)                           27min.   
        Winkills $timer > 60                                  28  
        Winkills $timer > 68                                  0  
        Winkills from fight not launching                     0  
        Winkills from ennemy left/already in matchmaking      0  
        Winkills from fight not expiring                      0  
        Winkills from unable to play card                     0  
        Winkills from your missions panel on wheeling client  2  
        Winkill total                                         30  
        =============  
    </details>  
    Fastest auto-seller possible. Sells a card every ~1.33s (while retrieving prices 48 at a time).   
    https://youtu.be/Si6ZsKSgh5o  
  
- **v.2.5 (FINAL)**  
The bot is now done. It can run for indefinite amount of time with very little errors.  
https://youtu.be/pMdf05AL-y0  
It now takes multiple strategies into account. 
To input strategies, make a *.../URBot/strategies/example_strategy.txt* file as follow and put the name of the chosen strategy file (here *example_strategy*) in *.../URBot/strategies/chosen_strategy.txt*.  
Example strategy files :  
  <details>  
  <summary><i>.../URBOT/strategy/example_strategy.txt</i></summary>  

        ff
        1234 3333 2  
        2134 3333 2  
        3124 3333 2  
        1324 3333 2  
        2314 3333 2  
        3214 3333 2  
        3241 3333 2  
        2341 3333 2  
        4321 3333 2  
        3421 3333 2  
        2431 3333 2  
        4231 3333 2  
        4132 3333 2  
        1432 3333 2  
        3412 3333 2  
        4312 3333 2  
        1342 3333 2  
        3142 3333 2  
        2143 3333 2  
        1243 3333 2  
        4213 3333 2  
        2413 3333 2  
        1423 3333 2  
        4123 3333 2  
  </details>  
  where *ff* is the chosen room (*ff*,*t1*,*t2* or *t3*),  
  then every line is formatted as follow :  
  *cccc pppp o*  
  with  *cccc* the order of the picked cards, *pppp* the number of pillz for each round and *o* the pillz offset, for the randomizer.
  Every strategy is equally likely.
  
   <details>  
  <summary><i>.../URBOT/strategy/chosen_strategy.txt</i></summary>  
  
    example_strategy  
  </details>   
  Replaced auto-seller  with smart-seller, a python program that can xp/sell cards, cancel market sales and keep track of your collection (single characters or all evolutions). Sells a card every ~0.1s.  
  https://youtu.be/f4JNvxpbe7U   
