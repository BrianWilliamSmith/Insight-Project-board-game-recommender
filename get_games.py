import requests as rq
import time
import json
import pandas as pd
import urllib.parse
import xml.etree.ElementTree as ET

df = pd.read_csv('shared_users_from_steam.csv',index_col=0)
df.head()
steam_ids = df.steam_id

# Load key and steam ids to lookup
my_key = open('key.txt', 'r').read()
all_users = []
counter = 0
for steam_id in steam_ids:
    req = rq.get('https://api.steampowered.com/IPlayerService/GetOwnedGames/v1/?key={key}&steamid={id}&include_played_free_games=1&include_appinfo=1'.format(key=my_key, id=steam_id))
    if json.loads(req.text).get('response').get('games') != None:
        games_list = json.loads(req.text).get('response').get('games')
        for game in games_list:
            game.update({'user': steam_id})
        all_users += games_list
    counter += 1
    print(str(counter) + "/" + str(len(steam_ids)) + ": requested user " + str(steam_id))

# 1/3 steam users have accessible games
games_users_from_steam = pd.DataFrame(all_users)
games_users_from_steam.to_csv("steam_users_games.csv")

good_steam_users = list(games_users_from_steam.user.unique())
good_steam_users = pd.DataFrame(good_steam_users, columns = ['steam_id'])

steam_bgg_ids = pd.concat([df.steam_id, df.avatar], axis=1)
steam_bgg_ids.drop_duplicates(inplace=True)
good_steam_users = good_steam_users.merge(steam_bgg_ids, how='left', on='steam_id')

# Check steam users on BGG
def get_bgg_collection(user_name):
    user_name = urllib.parse.quote_plus(user_name)
    r = rq.get("https://api.geekdo.com/xmlapi2/collection?username={}&rated=1&stats=1&brief=1&subtype=boardgame".format(user_name))
    return(r.text)

game_dict = {}
list_to_collect = good_steam_users.avatar[1000:2000]
for user_name in list_to_collect:
    get_bgg_collection(user_name)
    print(user_name)
    time.sleep(1)
for user_name in list_to_collect:
    collection = get_bgg_collection(user_name)
    game_dict[user_name] = collection
    print('encore une fois ' + user_name)
    time.sleep(1)

list_of_games=[]
for user_name in game_dict.keys():
    if '<items totalitems="0"' not in dict[user_name]:
        test = ET.fromstring(dict[user_name])
        for game in test.findall('item'):
            game_name = game.find('name').text
            game_rating = game.find('stats').find('rating').attrib['value']
            list_of_games.append((user_name, game_name, game_rating))

bgg_users_games = pd.DataFrame(list_of_games, columns=['user', 'game', 'rating'])
bgg_users_games.drop_duplicates(inplace=True)
bgg_users_games.to_csv('bgg_users_games.csv')