import requests as rq
import time
import json
import pandas as pd
import urllib.parse
import xml.etree.ElementTree as ET
from scraping_cleaning_normalizing.games_api_functions import get_steam_games

# This script takes a list of cross platform users and gets their game collections
# It outputs two csvs: boardgame_ratings.csv and steam_playtimes.csv
# These csvs contain all of the user-game-rating info

# Load steam api key and users
my_key = open('key.txt', 'r').read()
users = pd.read_csv('scraping_cleaning_normalizing/users_crossplat.csv', index_col=0)

# Get steam game playtimes for all users
steam_playtimes = []
counter=0
for steam_id in users.steam_id:
    playtimes_to_add = get_steam_games(steam_id, my_key)
    if playtimes_to_add != None:
        steam_playtimes += playtimes_to_add
    counter += 1
    time.sleep(2)
    print('checked: '+ str(counter) + ' remaining:' + str(len(users.steam_id)-counter))

# Convert steam playtimes into dataframe and save to csv
games_users_steam_df = pd.DataFrame(steam_playtimes)
games_users_steam_df.to_csv("scraping_cleaning_normalizing/steam_playtimes.csv")

# Get bgg ratings for all users
# Due to how BGG api calls work, this requires sending two requests per user

# A function to grab a bgg collection for a username
# Note -- everything is returned as a boardgame. it's a bug!
def get_bgg_collection(user_name):
    user_name = urllib.parse.quote_plus(user_name)
    r = rq.get("https://api.geekdo.com/xmlapi2/collection?username={}&rated=1&stats=1&brief=1".format(user_name))
    return(r.text)

# Get board game collection for each user
# Save results in a dictionary where key = user, value = raw xml
# First api call queues up the user info in database
for user_name in users.user_name:
    get_bgg_collection(user_name)
    print('first time: ' + user_name)
    time.sleep(1)

#Second api call accesses
boardgame_dict = {}
for user_name in users.user_name:
    collection = get_bgg_collection(user_name)
    boardgame_dict[user_name] = collection
    print('second time: ' + user_name)
    time.sleep(1)

# Go through the dictionary and create a list of tuples, where every tuple
# is (user_name, game_id, boardgame, rating) (these tuples will turn into a df later)

boardgame_ratings = []
for user_name in boardgame_dict.keys():
    print(user_name)
    if '<items totalitems="0"' not in boardgame_dict[user_name]:
        test = ET.fromstring(boardgame_dict[user_name])
        for game in test.findall('item'):
            game_name = game.find('name').text
            game_id = game.find('object_id').text
            game_rating = game.find('stats').find('rating').attrib['value']
            boardgame_ratings.append((user_name, game_id, game_name, game_rating))

# Convert list of tuples into dataframe
games_users_bgg_df = pd.DataFrame(boardgame_ratings, columns=['user', 'game_id', 'game', 'rating'])
games_users_bgg_df.drop_duplicates(inplace=True)

# Add steam ids back in
games_users_bgg_df = games_users_bgg_df.merge(users, left_on= 'user',
                                               right_on = 'user_name',
                                               how = 'left')

games_users_bgg_df.to_csv('scraping_cleaning_normalizing/boardgame_ratings.csv')