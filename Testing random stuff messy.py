import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

dict1 = {'a':1, 'b':2, 'c':3}
dict2 = {'a':1, 'b':3, 'c':4, 'd':5}
df = pd.DataFrame([dict1, dict2])
df
df.append(dict3, ignore_index=True)

bgg_info = pd.read_csv('bgg_info.txt')
list_of_bgs = bgg_info.Name
plotty = pd.read_csv('steam_users_games.csv')
plotty.playtime_forever.hist()

pd.Series(np.log1p(plotty.playtime_forever)).hist()

plt.show()
len(bgg_steam_data[bgg_steam_data.game.isin(list_of_bgs)])


bgg_steam_data.to_csv('bgg_steam_data.csv')
bgg_steam_data = bgg_steam_data[(bgg_steam_data.source=='steam')|
                                (bgg_steam_data.game.isin(list_of_bgs))]
bgg_steam_data_pruned = bgg_steam_data
bgg_steam_data_pruned.to_csv('bgg_steam_data_pruned.csv')
len(bgg_steam_data_pruned)

bgg_steam_data_pruned.describe()

# games_ratings = {dictionary.get('appid'):dictionary.get('playtime_forever') for dictionary in glist}
# new_ratings = {game:games_ratings.get('game') for game in list_of_games}
# df.append(new_ratings, ignore_index=True)
#
# list_of_games = bgg_steam_data.game
# new_user_games_ratings = {game: key for game in list_of_games}
#
# df = bgg_steam_data[['game','rating']]
# new_user_ratings.rating = np.log(new_user_rating.playtime_forever)
#
# # ADD USER
#
# # RETRAIN
#
# # Test every boardgame
#
# list_of_games =
# df.append(dict4, ignore_index=True)
#
# test
# set2 = bgg_steam_data[~bool_is_training]
#
# [pd.DataFrame([i], columns=['A']) for i in range(5)]
#
# pd.concat([df1,df2],join_axes=[df1.columns])
#
#
#
# df.columns.intersection

app = 286160
req = rq.get('http://store.steampowered.com/appreviews/{appid}?json=1'.format(appid=app))
reviews = json.loads(req.text)
reviewers = pd.DataFrame([dict.get('author') for dict in reviews.get('reviews')])
reviewers.columns
reviewers.describe()
len(reviewers)
x= reviewers.num_reviews/reviewers.num_games_owned
x = x[x<=1]
x = x[x>=0]
fig = sns.distplot(x, kde = False, bins=20, norm_hist=True)
fig.set(xlabel="Proportion of games reviewed", ylabel="Number of players")
plt.show()

steamusers = pd.read_csv('steam_users_games.csv')
steamusers = steamusers[steamusers.playtime_forever<15000]
x = steamusers.groupby('user').playtime_forever.sum()
x = x[x>0]
x = x[x<1000000]
steamusers
x = x/60
sns.set_style('whitegrid')
fig = sns.distplot(x)
fig.set(xlabel="Total playtime (hours)", ylabel="Proportion of players")
x.median()
x.mean()
plt.show()
