import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Load two datasets to be combined
bgg_users_games = pd.read_csv('csvs/bgg_users_games_final.csv', index_col=0)
steam_users_games = pd.read_csv('csvs/steam_users_games_final.csv', index_col=0)

steam_users_games = steam_users_games[['steam_id', 'appid', 'playtime_forever']]

# Dedupe both datasets
bgg_users_games.drop_duplicates(inplace=True, ignore_index=True)
steam_users_games.drop_duplicates(inplace=True, ignore_index=True)

# From steam data, remove games with zero playtime or extreme playtimes
# stdev_playtime = steam_users_games.playtime_forever.std()
# mean_playtime = steam_users_games.playtime_forever.mean()
# playtime_cutoff = 3*stdev_playtime+mean_playtime
#
# steam_users_games = steam_users_games[steam_users_games.playtime_forever>0]
# steam_users_games = steam_users_games[steam_users_games.playtime_forever<playtime_cutoff]

steam_users_games.reset_index(inplace=True)
bgg_users_games.reset_index(inplace=True)
len(bgg_users_games),len(steam_users_games)

# Use this csv as a lookup key to add names for comparison with bgg users
steam_user_lookup = pd.read_csv('steam_users.txt', index_col=0)
steam_user_lookup_2 = pd.read_csv('bgg_users_steam_ids.csv', index_col=0)
steam_user_lookup.head()
steam_user_lookup_2.head()

steam_user_lookup_2.rename(columns={'user_name':'avatar'}, inplace=True)

steam_user_lookup = steam_user_lookup[['steam_id','avatar']]
steam_user_lookup_2 = steam_user_lookup_2[['steam_id','avatar']]
lookup_key_3
steam_user_lookup_final = pd.concat([steam_user_lookup, steam_user_lookup_2, lookup_key_3],
                                    ignore_index=True, axis=0)
steam_user_lookup_final = pd.concat([steam_user_lookup, steam_user_lookup_2],
                                    ignore_index=True, axis=0)
steam_user_lookup_final
steam_user_lookup_final.drop_duplicates(inplace=True)
steam_user_lookup_final.to_csv('users_from_steam.csv')

steam_user_lookup = pd.read_csv('users_from_steam.csv', index_col=0)
steam_user_lookup = steam_user_lookup[steam_user_lookup!='none']
steam_user_lookup.dropna(inplace=True)

steam_user_lookup.steam_id = steam_user_lookup.steam_id.astype('str')

missing_from_key = set(steam_users_games.steam_id.astype('str')).difference(set(steam_user_lookup.steam_id))
len(missing_from_key)

# Merge user names
steam_users_games['steam_id'] = steam_users_games.steam_id.astype('str')
steam_user_lookup['avatar'] = steam_user_lookup.avatar.str.lower()

steam_users_games = steam_users_games.merge(steam_user_lookup,
                                            how='left',
                                            on='steam_id',
                                            sort=False)

missing_from_key = set(steam_users_games.avatar.astype('str')).difference(set(steam_user_lookup.avatar))
missing_from_key

# Identify users in both data sets
bgg_users_games['user'] = bgg_users_games.user.str.lower()
shared_users = set(steam_users_games.avatar).intersection(set(bgg_users_games.user))
len(shared_users)
not_shared_users = set(steam_users_games.avatar).difference(set(bgg_users_games.user))
len(not_shared_users)

# Include only shared users
bgg_users_games = bgg_users_games[bgg_users_games.user.isin(shared_users)]
steam_users_games = steam_users_games[steam_users_games.avatar.isin(shared_users)]
print(bgg_users_games.user.nunique(), steam_users_games.avatar.nunique())

# Create a new dataframe with both bgg data and steam data
# First, create the user series
users = list(bgg_users_games.user) + list(steam_users_games.avatar)
len(users)
len(bgg_users_games), len(steam_users_games)

# Then create the game series
steam_games = steam_users_games.appid
bgg_games = bgg_users_games.game

games = list(bgg_games) + ['steam'+ str(game) for game in steam_games]
len(bgg_games), len(steam_games)

# Combine ratings and transformed playtimes
steam_ratings = steam_users_games.playtime_forever.astype('float64')
bgg_ratings = bgg_users_games.rating.astype('float64')
ratings = list(bgg_ratings) + list(steam_ratings)

# A vector to keep track of source (just in case)
steam_source = ['steam' for element in steam_ratings]
bgg_source = ['bgg' for element in bgg_ratings]
source = bgg_source + steam_source
len(source)

# Combine everything into magnificent df
d = {'user':users, 'game':games, 'rating':ratings, 'source':source}
d
bgg_steam_data = pd.DataFrame(d)
len(bgg_steam_data)
bgg_steam_data.to_csv('games_users_final.csv')

bgg_steam_data = pd.read_csv('csvs/games_users_final.csv', index_col=0)

# Drop zero playtimes
bgg_steam_data = bgg_steam_data[bgg_steam_data.rating>0]

# Common games are reviewed or played by at least 10 users
common_games = bgg_steam_data.game.value_counts()
common_games = common_games.where(common_games>9).dropna().index.tolist()

# Identify users with 3 or more reviews
just_steam_data = bgg_steam_data[bgg_steam_data.source=='steam']
active_steam_users = just_steam_data.user.value_counts()
active_steam_users = active_steam_users.where(active_steam_users>2).dropna().index.tolist()

just_bgg_data = bgg_steam_data[bgg_steam_data.source=='bgg']
active_bgg_users = just_bgg_data.user.value_counts()
active_bgg_users = active_bgg_users.where(active_bgg_users>2).dropna().index.tolist()

active_users = set(active_steam_users).intersection(active_bgg_users)

# Only common games and active users
bgg_steam_data = bgg_steam_data[(bgg_steam_data.game.isin(common_games))&
                                (bgg_steam_data.user.isin(active_users))]

bgg_steam_data.to_csv('bgg_steam_data_pruned.csv')

bgg_steam_data=pd.read_csv('csvs/bgg_steam_data_pruned.csv', index_col=0)

blacklist = pd.read_csv('blacklist.csv', index_col=0)
blacklist = blacklist.loc[(blacklist["brian thinks it's probably a dupe"]=='x')|\
                          (blacklist['aaron']=='x'),'0']
bgg_steam_data = bgg_steam_data[~bgg_steam_data.user.isin(blacklist)]


# Log-transform steam playtimes
just_steam_data = bgg_steam_data[bgg_steam_data.source=='steam'].copy()
just_steam_data = just_steam_data[just_steam_data.rating>0]
just_steam_data['rating'] = np.log(just_steam_data.rating)

# Prune >3ds above mean rating
mean_rating = just_steam_data['rating'].mean()
std_rating = just_steam_data['rating'].std()
max_cutoff = mean_rating + 3*std_rating
just_steam_data = just_steam_data[just_steam_data.rating <= max_cutoff]

just_steam_data.rating.hist()
plt.show()

#Caclulate average by user
average_rating_by_user_steam = just_steam_data.groupby('user').mean().rating
sd_by_user_steam = just_steam_data.groupby('user').std().rating
just_steam_data.reset_index(inplace=True)

# Divide by .75 sds so the standard deviation is 1.5

steam_ratings_normed=[]
for i in range(len(just_steam_data)):
    user = just_steam_data.user[i]
    mean = average_rating_by_user_steam[user]
    sd = sd_by_user_steam[user]
    rating = just_steam_data.rating[i]
    new_rating = (rating - mean)/(.75*sd+0.0000000000001)
    new_rating = new_rating + 5.5
    steam_ratings_normed.append(new_rating)

just_steam_data['rating_normed'] = steam_ratings_normed

just_steam_data.loc[just_steam_data.rating_normed < 1, 'rating_normed'] = 1
just_steam_data.loc[just_steam_data.rating_normed > 10, 'rating_normed'] = 10

just_steam_data.rating_normed.hist()
just_steam_data.rating_normed.describe()

# Get mean rating for each player from bgg and transform
just_bgg_data = bgg_steam_data[bgg_steam_data.source=='bgg'].copy()
just_bgg_data.dropna(inplace=True)
just_bgg_data.describe()

no_expansions = pd.read_csv('csvs/bgg_GameItem.csv')
no_expansions = set(no_expansions.name)
just_bgg_data = just_bgg_data[just_bgg_data.game.isin(no_expansions)]

average_rating_by_user_bgg = just_bgg_data.groupby('user').mean().rating
sd_by_user_bgg = just_bgg_data.groupby('user').std().rating
just_bgg_data.reset_index(inplace=True)

bgg_ratings_normed=[]
for i in range(len(just_bgg_data)):
    user = just_bgg_data.user[i]
    mean = average_rating_by_user_bgg[user]
    sd = sd_by_user_bgg[user] # No divide by zero
    rating = just_bgg_data.rating[i]
    new_rating = (rating - mean)/(.75*sd+0.0000000000001)
    new_rating = new_rating + 5.5
    bgg_ratings_normed.append(new_rating)

just_bgg_data['rating_normed'] = bgg_ratings_normed

just_bgg_data.loc[just_bgg_data.rating_normed < 1, 'rating_normed'] = 1
just_bgg_data.loc[just_bgg_data.rating_normed > 10, 'rating_normed'] = 10

just_bgg_data.rating_normed.hist()
just_bgg_data.rating_normed.describe()

# Combine the two sets of normed ratings

shared_users = set(just_bgg_data.user).intersection(just_steam_data.user)

just_steam_data = just_steam_data[just_steam_data.user.isin(shared_users)]
just_bgg_data = just_bgg_data[just_bgg_data.user.isin(shared_users)]

just_bgg_data = just_bgg_data[['user', 'rating', 'rating_normed', 'source', 'game']]
just_steam_data = just_steam_data[['user', 'rating', 'rating_normed', 'source', 'game']]

# Combine and write
bgg_steam_data_normed = pd.concat([just_steam_data, just_bgg_data], axis=0,ignore_index=True)
bgg_steam_data_normed.to_csv('bgg_steam_data_normed.csv')