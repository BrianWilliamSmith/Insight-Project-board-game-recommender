import requests as rq
import time
import json
import pandas as pd
import urllib.parse
import xml.etree.ElementTree as ET

# Load key and steam ids to lookup
df = pd.read_csv('csvs/shared_users_from_steam.csv', index_col=0)
df.head()
steam_ids = df.steam_id
my_key = open('key.txt', 'r').read()

games_for_all_users = []
for steam_id in steam_ids:
    next_user = get_steam_games(steam_id, my_key)
    if next_user != None:
        games_for_all_users += get_steam_games(steam_id, my_key)
    print(steam_id, games_for_all_users)

games_users_from_steam = pd.DataFrame(all_users)
games_users_from_steam.to_csv("steam_users_games.csv")

# Load key and games from bgg to lookup
df = pd.read_csv('bgg_users_steam_ids.csv', index_col=0)
steam_ids = df.steam_id
my_key = open('key.txt', 'r').read()

# Look up vgs from bgg users
all_users = []
counter = 0
for steam_id in steam_ids:
    if steam_id != 'none' and steam_id != None:
        next_user = get_steam_games(steam_id, my_key)
        if next_user != None:
            all_users += next_user
        counter += 1
    time.sleep(1)
    print('counter: '+ str(counter))

len(all_users)
all_users

bgg_users_video_games = pd.DataFrame(all_users)
bgg_users_video_games.to_csv("bgg_users_video_games.csv")
bgg_users_video_games.steam_id.nunique()

bgg_users = pd.read_csv('bgg_users_steam_ids.csv', index_col=0)
bgg_user_name_steam_id_key = bgg_users[['user_name', 'steam_id']]
bgg_user_name_steam_id_key.drop_duplicates(inplace=True)

crossplat_bgg_users = bgg_users_video_games
crossplat_bgg_users = crossplat_bgg_users.merge(bgg_user_name_steam_id_key, how='left', on='steam_id')
crossplat_bgg_users = crossplat_bgg_users.user_name.unique()



###
steam_bgg_ids = pd.concat([df.steam_id, df.avatar], axis=1)
steam_bgg_ids.drop_duplicates(inplace=True)
good_steam_users = good_steam_users.merge(steam_bgg_ids, how='left', on='steam_id')

###

shared_users_from_bgg = pd.DataFrame(all_users)
shared_users_from_bgg.steam_id.nunique()
shared_users_from_bgg.to_csv("shared_users_from_bgg_with_vgs.csv")

#

good_steam_users = list(games_users_from_steam.user.unique())
good_steam_users = pd.DataFrame(good_steam_users, columns = ['steam_id'])

steam_bgg_ids = pd.concat([df.steam_id, df.avatar], axis=1)
steam_bgg_ids.drop_duplicates(inplace=True)
good_steam_users = good_steam_users.merge(steam_bgg_ids, how='left', on='steam_id')

# Look up user on BGG by user_name
def get_bgg_collection(user_name):
    user_name = urllib.parse.quote_plus(user_name)
    r = rq.get("https://api.geekdo.com/xmlapi2/collection?username={}&rated=1&stats=1&brief=1&subtype=boardgame".format(user_name))
    return(r.text)

game_dict = {}
list_to_collect = crossplat_bgg_users
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
    if '<items totalitems="0"' not in game_dict[user_name]:
        test = ET.fromstring(game_dict[user_name])
        for game in test.findall('item'):
            game_name = game.find('name').text
            game_rating = game.find('stats').find('rating').attrib['value']
            list_of_games.append((user_name, game_name, game_rating))

bgg_users_games_2 = pd.DataFrame(list_of_games, columns=['user', 'game', 'rating'])
bgg_users_games_2.drop_duplicates(inplace=True)
bgg_users_games_2.to_csv('bgg_users_games_2.csv')

bgg_users_games = pd.DataFrame(list_of_games, columns=['user', 'game', 'rating'])
bgg_users_games.drop_duplicates(inplace=True)
bgg_users_games.to_csv('bgg_users_games.csv')

# Load bgg shared users 1
bgg_users_games = pd.read_csv('csvs/bgg_users_games.csv', index_col=0)
bgg_users_games_2 = pd.read_csv('csvs/bgg_users_games_2.csv', index_col=0)
bgg_users_games_2.user.nunique()

# Identify users in both sets of users -- remove them!!
shared_users = set(bgg_users_games.user).intersection(bgg_users_games_2.user)
bgg_users_games_2 = bgg_users_games_2[~bgg_users_games_2.user.isin(shared_users)]
bgg_users_games_final = pd.concat([bgg_users_games, bgg_users_games_2],
                                  ignore_index=True,
                                  axis=0)

bgg_users_games_final.to_csv('bgg_users_games_final.csv')

# Do the same thing for video games
steam_users_games = pd.read_csv('csvs/steam_users_games.csv', index_col=0)
steam_users_games.rename(columns={'user':'steam_id'}, inplace=True)
steam_users_games_2 = pd.read_csv('csvs/bgg_users_video_games.csv', index_col=0)

shared_users = set(steam_users_games.steam_id).intersection(steam_users_games_2.steam_id)
steam_users_games_2 = steam_users_games_2[~steam_users_games_2.steam_id.isin(shared_users)]
steam_users_games_final = pd.concat([steam_users_games, steam_users_games_2],
                                  ignore_index=True,
                                  axis=0)
steam_users_games_final.to_csv('steam_users_games_final.csv')