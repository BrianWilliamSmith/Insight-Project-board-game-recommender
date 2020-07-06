import requests as rq
import re
import time
import pandas as pd
from scraping_cleaning_normalizing.games_api_functions import get_steam_player_info

# This script creates a list of Steam ids, and then looks up player info on Steam
# It outputs a csv of steam users with info

# Get a list of steam ids for reviewers of Tabletop simulator
# The cursor business is in there because you have to send the last cursor value
# of the previous page of results to get the next page of results

table_top_simulator_id = '286160'
new_cursor = '*'
old_cursor = ''
reviewers=[]

while old_cursor != new_cursor:
    r = rq.get('https://store.steampowered.com/appreviews/{game}?json=1&filter=recent&purchase_type=all&num_per_page=100&cursor={cursor}'.format(game=table_top_simulator_id, cursor=new_cursor))
    old_cursor = new_cursor
    new_cursor = json.loads(r.text)['cursor']
    new_cursor = rq.compat.quote_plus(new_cursor) # Encode special characters
    reviewers += re.findall('(?<=steamid":").*?(?=",)', r.text)
    time.sleep(2) # Annoying but necessary due to inconsistent API call limits
    print('%s reviewers so far' % len(reviewers))

with open('scraping_cleaning_normalizing/steam_ids_to_check/steam_ids_for_Tabletop_Simulator_reviewers, 'w+') as file:
    file.write('\n'.join(reviewers))

# Get player info for all of the ids contained in the folder 'steam_ids_to_check'
# Check 100 at a time

my_steam_key = open('./key.txt').read()
steam_users = []
for file_name in glob.glob('scraping_cleaning_normalizing/steam_ids_to_check/*.txt'):
    steam_ids = open(file_name,'r').read().split('\n')
    while len(steam_ids) > 0:
        set_of_ids = ','.join(steam_ids[0:100]) # Check 100 at a time
        del steam_ids[0:100]
        print('{} users left in {}'.format(len(steam_ids),file_name))
        steam_users += get_steam_player_info(set_of_ids, my_steam_key)
        time.sleep(2) # Annoying but necessary due to API call limits

steam_users_df = pd.DataFrame(steam_users)

# Add username column, which matches persona name, unless there's a vanity url
# If there's a vanity url, use that as the username

steam_users_df['user_name'] = steam_users_df.personaname
bool_has_a_vanity_url = steam_users_df.profileurl.str.contains('/id/')
extract_vanity_from_url = lambda x: re.search('(?<=/id/)(.*)(?=/)', x)[0]
steam_users_df.loc[bool_has_a_vanity_url, 'user_name'] = \
    steam_users_df.loc[bool_has_a_vanity_url, 'profileurl'].apply(extract_vanity_from_url)
steam_users_df.user_name = steam_users_df.user_name.str.lower()

# De-dupe
steam_users_df.drop_duplicates(inplace=True)

# Remove avatars that are used more than once
steam_users_df = steam_users_df[~steam_users_df.user_name.duplicated()]

# Remove hidden profiles
steam_users_df = steam_users_df[steam_users_df.communityvisibilitystate==3]

# Rename columns and save
steam_users_df.rename(columns={'steamid':'steam_id'}, inplace=True)
keep_these_columns = ['steam_id', 'user_name']
steam_users_df = steam_users_df[keep_these_columns]

steam_users_df.to_csv('scraping_cleaning_normalizing/users_from_steam.csv')