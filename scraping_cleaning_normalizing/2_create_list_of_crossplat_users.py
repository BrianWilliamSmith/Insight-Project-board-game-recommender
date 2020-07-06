import pandas as pd
import time
from scraping_cleaning_normalizing.games_api_functions import get_steam_id, get_user_info_bgg, get_steam_player_info
import numpy as np

# This script loads in the lists of bgg users and steam users, and then looks up
# the users on both platforms, identifying shared users
# It ouputs a csv of cross platform users

# Load users from each platform
steam_users_df = pd.read_csv('scraping_cleaning_normalizing/users_from_steam.csv', index_col=0)
bgg_users_df = pd.read_csv('scraping_cleaning_normalizing/users_from_bgg.csv', index_col=0)

# Match case and merge
steam_users_df['user_name'] = steam_users_df.user_name.str.lower()
bgg_users_df['user_name'] = bgg_users_df.user_name.str.lower()

shared_users_df = pd.merge(bgg_users_df, steam_users_df, on='user_name',
                           how='left', validate='1:1')

# Get bgg info for the shared users
# This takes a long time
bgg_user_info_tuples = []
for user_name in shared_users_df.user_name:
    print(user_name)
    bgg_user_info_tuples.append(get_user_info_bgg(user_name))
    time.sleep(2)

bgg_id_df = pd.DataFrame(bgg_user_info_tuples, columns=['bgg_id',
                                                        'bgg_state',
                                                        'bgg_country',
                                                        'bgg_steam_name'])

shared_users_df = pd.concat([shared_users_df, bgg_id_df], axis=1)

# Remove folks without a bgg profile
shared_users_df = shared_users_df[shared_users_df.bgg_id!='none']
shared_users_df.reset_index(drop=True, inplace=True)

# See if any bgg users have list steam names that don't match user_name
shared_users_df['bgg_steam_name'] = shared_users_df.bgg_steam_name.str.lower()
bool_same_steam_names = (shared_users_df.user_name.eq(shared_users_df.bgg_steam_name))
bool_has_a_bgg_steam_name = (shared_users_df.bgg_steam_name != '')
bool_wrong_steam_name = (bool_has_a_bgg_steam_name) & (~bool_same_steam_names)

# Steam_name = user_name unless steam_name is listed on bgg
shared_users_df['steam_user_name'] = shared_users_df.user_name
shared_users_df.loc[bool_wrong_steam_name, 'steam_user_name'] = \
    shared_users_df.loc[bool_wrong_steam_name, 'bgg_steam_name']

# Reset steam ids for folks who had wrong steam_names
shared_users_df.loc[bool_wrong_steam_name, 'steam_id'] = np.nan

# Indicate confidence in crossplatform match
# bgg_steam_name = the steam name is listed on bgg
shared_users_df['crossplat_match'] = ''
shared_users_df.loc[shared_users_df.bgg_steam_name != '', 'crossplat_match'] = 'bgg_steam_name'

# Get steam ids for users without them
my_steam_key = open('./key.txt').read()
steam_ids = []
for i in range(6678, len(shared_users_df)):
    old_steam_id = shared_users_df.steam_id[i]
    if old_steam_id in ['', 'nan', 'NaN', None] or np.isnan(old_steam_id):
        steam_ids.append(get_steam_id(shared_users_df.steam_user_name[i], my_steam_key))
        time.sleep(2)
    else:
        steam_ids.append(old_steam_id)
    print(str(len(shared_users_df)-i) + ' to go')

shared_users_df['steam_id'] = steam_ids

# Remove users who don't have a steam id
shared_users_df = shared_users_df[shared_users_df.steam_id!='none']
shared_users_df.reset_index(drop=True, inplace=True)

# There's one duplicate username (can't figure out why)
# Remove him by taking a slice that doesn't contain duplicates
shared_users_df[shared_users_df.steam_user_name.duplicated(keep=False)]
shared_users_df = shared_users_df[~shared_users_df.steam_user_name.duplicated(keep='last')]

# There's one duplicate steam id -- which is a girlfriend who used her bf's
# id or something
shared_users_df[shared_users_df.steam_id.duplicated(keep=False)]
get_steam_id('darthprefect&#039;sgirl', my_steam_key)
shared_users_df = shared_users_df[~shared_users_df.steam_id.duplicated(keep='last')]

# Get steam player info 100 at a time
# Especially important: profile visibility to determine if user
# has a hidden profile
steam_infos = []
while len(steam_ids) > 0:
    set_of_ids = ','.join(steam_ids[0:100])  # Check 100 at a time
    del steam_ids[0:100]
    print('{} users left to check'.format(len(steam_ids)))
    steam_infos += get_steam_player_info(set_of_ids, my_steam_key)
    time.sleep(2)  # Annoying but necessary due to API call limits

# Create a dataframe with the user info
steam_infos_df = pd.DataFrame(steam_infos)
steam_infos_df.columns

keep_these_columns = ['steamid',
                      'realname',
                      'loccountrycode',
                      'locstatecode',
                      'loccityid',
                      'communityvisibilitystate']

steam_infos_df = steam_infos_df[keep_these_columns]

steam_infos_df.rename(columns={'steamid':'steam_id',
                               'realname':'steam_real_name',
                               'loccountrycode':'steam_country',
                               'locstatecode':'steam_state',
                               'loccityid':'steam_city',
                               'communityvisibilitystate':'steam_profile_visibility'},
                      inplace=True)

#Duplicate check and merge
steam_infos_df[steam_infos_df.steam_id.duplicated(keep=False)]

shared_users_df = shared_users_df.merge(steam_infos_df,
                                        how='inner',
                                        on='steam_id',
                                        validate='1:1')

# Only keep users with profile visibility = 3 (public profile)
shared_users_df = shared_users_df[shared_users_df.steam_profile_visibility == 3]
shared_users_df.reset_index(drop=True, inplace=True)

# Check list against blacklist.csv -- a list of users that have been tagged as
# having common names

blacklist = pd.read_csv('blacklist.csv', index_col=0)
blacklist = blacklist.loc[(blacklist["brian thinks it's probably a dupe"]=='x')|\
                          (blacklist["aaron"]=='x'),'0']

shared_users_df = shared_users_df[~shared_users_df.steam_user_name.isin(blacklist)]

# Save the crossplatform user list
shared_users_df.to_csv('scraping_cleaning_normalizing/users_crossplat.csv')