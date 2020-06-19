import pandas as pd
import requests as rq
import urllib.parse
import time
from games_api_functions import get_steam_id
from games_api_functions import get_user_info_bgg

steam_users_df = pd.read_csv('users_from_steam.csv', index_col=0)
bgg_users_df = pd.read_csv('users_from_bgg.csv', index_col=0)

steam_users_df['user_name'] = steam_users_df.user_name.str.lower()
bgg_users_df['user_name'] = bgg_users_df.user_name.str.lower()

shared_users_df = pd.merge(steam_users_df, bgg_users_df, on='user_name',
                           how='outer', validate='1:1')

shared_users_df = shared_users_df[0:100]

# Get bgg info for the shared users
# This takes a long time
bgg_user_info_tuples = []
for user_name in shared_users_df.user_name:
    print(user_name)
    bgg_user_info_tuples.append(get_user_info_bgg(user_name))
    time.sleep(2)
pd.DataFrame()

bgg_id_df = pd.DataFrame(bgg_user_info_tuples, columns=['bgg_id',
                                                        'bgg_state',
                                                        'bgg_country',
                                                        'bgg_steam_name'])

shared_users_df = pd.concat([shared_users_df, bgg_id_df], axis=1)

# Remove folks without a bgg profile
shared_users_df = shared_users_df[shared_users_df.bgg_id!='none']
shared_users_df.reset_index(drop=True, inplace=True)

# Fill in steam user_name column for folks who don't have one
# Use steam name from bgg if a user has that, otherwise
# assume steam name=bgg name


# Get steam ids for users without them
for i in range(len(shared_users_df)):
    if shared_users_df.steam_id[i] in ['none', 'NaN', np.nan, None]:
        new_steam_id = get_steam_id(shared_users_df.steam_user_name[i])
        shared_users_df.steam_id[i] = new_steam_id
        time.sleep(2)

# Remove folks without a steam id
shared_users_df = shared_users_df[shared_users_df.steam_id!='none']
shared_users_df.reset_index(drop=True, inplace=True)

shared_users.to_csv('users_crossplat.csv')