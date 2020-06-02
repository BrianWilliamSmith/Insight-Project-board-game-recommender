import pandas as pd
import requests as rq
import urllib.parse
import time

steam_users = pd.read_csv('steam_users.txt', index_col=0)
steam_users = steam_users[steam_users.hidden_prof==3].reset_index(drop=True)

def lookup_on_bgg(avatar):
    ''''''
    avatar = urllib.parse.quote_plus(avatar)
    r = rq.get('https://www.boardgamegeek.com/xmlapi2/user?name={user_url}'.format(user_url=avatar))
    if '<user id=""' in r.text:
        bgg_id, bgg_state, bgg_country, bgg_steam_id = 'none', 'none', 'none', 'none'
    else:
        bgg_id = re.search('(?<=user id=")[0-9]*?(?=")', r.text).group(0)
        bgg_country = re.search('(?<=<stateorprovince value=").*?(?=")', r.text).group(0)
        bgg_state = re.search('(?<=<country value=").*?(?=")', r.text).group(0)
        bgg_steam_id = re.search('(?<=steamaccount value=").*?(?=")', r.text).group(0)
    return(bgg_id, bgg_state, bgg_country, bgg_steam_id)

bgg_id = []
for user in steam_users.avatar:
    out = lookup_on_bgg(user)
    bgg_id.append(out)
    print(user + ' is on bgg? ' + str(out))
    time.sleep(2)

bgg_id_df = pd.DataFrame(bgg_id, columns=['bgg_id', 'bgg_state', 'bgg_country', 'bgg_steam_id'])
crossref_users = pd.concat(steam_users, bgg_id_df], axis=0)