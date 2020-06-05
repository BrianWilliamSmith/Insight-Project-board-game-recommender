import pandas as pd
import numpy as np
from surprise import Reader, Dataset
from surprise.model_selection import train_test_split
from surprise import accuracy
from surprise import SVD, accuracy, KNNWithMeans, KNNBasic, KNNWithZScore, KNNBaseline
from surprise import NormalPredictor, BaselineOnly

# Compare different recommenders

# Load two datasets to be combined
bgg_users_games = pd.read_csv('bgg_users_games.csv', index_col=0)
steam_users_games = pd.read_csv('steam_users_games.csv', index_col=0)

steam_users_games = steam_users_games[['user', 'appid', 'playtime_forever']]

# Dedupe both datasets
bgg_users_games.drop_duplicates(inplace=True, ignore_index=True)
steam_users_games.drop_duplicates(inplace=True, ignore_index=True)

# From steam data, remove games with zero playtime or extreme playtimes
stdev_playtime = steam_users_games.playtime_forever.std()
mean_playtime = steam_users_games.playtime_forever.mean()
playtime_cutoff = 3*stdev_playtime+mean_playtime

steam_users_games = steam_users_games[steam_users_games.playtime_forever>0]
steam_users_games = steam_users_games[steam_users_games.playtime_forever<playtime_cutoff]

steam_users_games.reset_index(inplace=True)
bgg_users_games.reset_index(inplace=True)
len(bgg_users_games),len(steam_users_games)

# Use this csv as a lookup key to add names for comparison with bgg users
steam_user_lookup = pd.read_csv('steam_users.txt', index_col=0)
steam_user_lookup = steam_user_lookup[['steam_id','avatar']]
steam_user_lookup.drop_duplicates(inplace=True)

steam_users_games = steam_users_games.merge(steam_user_lookup,
                                            how='left',
                                            left_on='user',
                                            right_on='steam_id',
                                            sort=False)

# Identify users in both data sets
shared_users = set(steam_users_games.avatar).intersection(set(bgg_users_games.user))

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
steam_ratings = np.log(steam_ratings)
steam_ratings[steam_ratings>10] = 10
steam_ratings[steam_ratings<1] = 1
steam_ratings.mean()
bgg_ratings = bgg_users_games.rating.astype('float64')
ratings = list(bgg_ratings) + list(steam_ratings)
len(bgg_ratings), len(steam_ratings), len(ratings)

# A vector to keep track of source (just in case)
steam_source = ['steam' for element in steam_ratings]
bgg_source = ['bgg' for element in bgg_ratings]
source = bgg_source + steam_source
len(source)

# Combine everything into magnificent df
d = {'user':users, 'game':games, 'rating':ratings, 'source':source}
bgg_steam_data = pd.DataFrame(d)
len(bgg_steam_data)

# Identify games with 3 or more reviews
common_games = bgg_steam_data.game.value_counts()
common_games.describe()
common_games.head(10)

common_games = common_games.where((common_games>5)&(common_games<200)).dropna().index.tolist()

# Identify users with 3 or more reviews
active_users = bgg_steam_data.user.value_counts()
active_users = active_users.where(active_users>2).dropna().index.tolist()

bgg_steam_data = bgg_steam_data[(bgg_steam_data.game.isin(common_games))&
                                (bgg_steam_data.user.isin(active_users))]

u_i_matrix = bgg_steam_data.pivot_table(index = 'game', columns = 'user', values = 'rating')
u_i_matrix = u_i_matrix.fillna(0)

from numpy import count_nonzero
sparsity = (1.0 - count_nonzero(u_i_matrix) / u_i_matrix.size)*100
print(sparsity)

# Time for a recommender
# loading data

reader = Reader(rating_scale=(1,10))
data = Dataset.load_from_df(bgg_steam_data[['user', 'game', 'rating']], reader)

trainset, testset = train_test_split(data, test_size=0.25)
algo = SVD()
algo.fit(trainset)
predictions = algo.test(testset)
algo.test(testset, verbose=True)
print(accuracy.rmse(predictions))

testset

algo.fit(trainset)

users_25 = list(bgg_steam_data.user.unique()[:80])

bool_is_training = ~((bgg_steam_data.user.isin(users_25))&(bgg_steam_data.source=='bgg'))

trainset2 = bgg_steam_data[bool_is_training]
trainset2 = Dataset.load_from_df(trainset2[['user', 'game', 'rating']], reader)
trainset2 = trainset2.build_full_trainset()

testset2 = bgg_steam_data[~bool_is_training]
testset2 = Dataset.load_from_df(testset2[['user', 'game', 'rating']], reader)
testset2 = testset2.build_full_trainset()
testset2 = testset2.build_testset()

algo = SVD()
algo.fit(trainset2)
predictions = algo.test(testset2)
print(accuracy.rmse(predictions))

# A dumb baseline -- guess 5
testvals = [c for (a,b,c) in testset]
dumb_RMSE = (sum([(val-5)**2 for val in testvals])/len(testvals))**.5

print("Just guessing 5 gives you RMSE of %s"%dumb_RMSE+", not much better...")

algo = KNNBasic()
algo.fit(trainset2)
predictions = algo.test(testset2)
print(accuracy.rmse(predictions))

algo = KNNBaseline()
algo.fit(trainset2)
predictions = algo.test(testset2)
print(accuracy.rmse(predictions))

algo = KNNWithZScore()
algo.fit(trainset2)
predictions = algo.test(testset2)
print(accuracy.rmse(predictions))

algo = KNNWithMeans()
algo.fit(trainset2)
predictions = algo.test(testset2)
print(accuracy.rmse(predictions))

algo = NormalPredictor()
algo.fit(trainset2)
predictions = algo.test(testset2)
print(accuracy.rmse(predictions))

algo = BaselineOnly()
algo.fit(trainset2)
predictions = algo.test(testset2)
print(accuracy.rmse(predictions))

trainset3 = bgg_steam_data[~bgg_steam_data.user.isin(users_25)]
trainset3 = Dataset.load_from_df(trainset3[['user', 'game', 'rating']], reader)
trainset3 = trainset3.build_full_trainset()

testset3 = bgg_steam_data[bgg_steam_data.user.isin(users_25)]
testset3 = Dataset.load_from_df(testset3[['user', 'game', 'rating']], reader)
testset3 = testset3.build_full_trainset()
testset3 = testset3.build_testset()

algo = BaselineOnly()
algo.fit(trainset3)
predictions = algo.test(testset3)
print(accuracy.rmse(predictions))

algo = NormalPredictor()
algo.fit(trainset3)
predictions = algo.test(testset3)
print(accuracy.rmse(predictions))


## What is after this even??


# Process data only include played games
# Dedupe
# Slice off 2 sigma outliers
df2 = df[df.playtime_forever>0]
df2 = df2.drop_duplicates()
df2 = df2[df2.playtime_forever < df2.playtime_forever.mean()+2*df2.playtime_forever.std()]

# Descriptive stats
# No. unique users
# No. unique games
df2.describe()
df2.user.nunique()
df2.appid.nunique()

# No. installs
install_counts = df2['name'].value_counts()/df2.user.nunique()
install_counts = install_counts.sort_values(ascending=False)
ic = pd.DataFrame({"game":install_counts.index,"proportion of players":install_counts})
f, ax = plt.subplots(figsize=(8, 10))
ic.head(1000)
sns.distplot(ic['proportion of players'])
plt.show()
ic25 = ic.sort_values(by='proportion of players',ascending=False).head(25)
ic25.head()
ax = sns.barplot(x='proportion of players', y='game', data=ic25)
ax.set(title='Most installed games among boardgamers',ylabel='game', xlabel='proportion of players with game')
plt.show()

no_of_games = df2['user'].value_counts()
sns.set(style="whitegrid")
ax = sns.distplot(no_of_games)
ax.set(title='Distribution of game ownership', xlabel='no of games')
plt.show()
no_of_games.mode()
game_info = pd.read_csv('steam_games.csv')
game_info['genre'] = game_info.popular_tags.str.replace('[,].+$','')

ic = pd.merge(ic, game_info, how='left', left_on='game', right_on='name')
genre_counts = ic.groupby('genre', as_index=False).count()
sns.set(style="whitegrid")
f, ax = plt.subplots(figsize=(8, 10))
#sns.barplot(x='proportion of players', y='game', hue='genre', data=ic)
ax = sns.barplot(x="game", y="genre", data=genre_counts)
ax.set(title='Distribution of tags in \ntop 50 products among board gamers',ylabel='genre', xlabel='count')
plt.savefig("temp.png")
plt.show()

# histogram of installs
unique_users = list(df.user.unique())
df2.columns
len(unique_users)

playtime=df2.groupby(by='name', as_index=False).playtime_forever.mean()
pt= playtime.sort_values("playtime_forever", ascending=False)
pt = pt.head(10)
sns.set(style="whitegrid")
f, ax = plt.subplots(figsize=(6, 15))
sns.barplot(x='playtime_forever', y='name', data=pt)

sns.distplot(pt.playtime_forever)
plt.show()
plt.savefig("temp.png")

user_list = []
for steam_id in unique_users:
    avatar = urllib.parse.quote_plus(avatar)
    req = rq.get('http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key={key}&steamids={id}'.format(key=my_key, id=steam_id))
    user_info = json.loads(req.text).get('response').get('players')
    user_list += user_info
    print(steam_id)

df_users = pd.DataFrame(user_list)
df_users.head()

unique_apps = list(df.appid.unique())
app_list = []
for app_id in unique_apps:
    req = rq.get('https://store.steampowered.com/api/appdetails/?appids={id}'.format(id=str(app_id)))
    app = json.loads(req.text).get(str(app_id)).get('data')
    app_list += app
    timer.sleep(2)
    print(app_id)

df_apps = pd.DataFrame(app_list)
df_apps.head()



# make user, item matrix
# check sparsity
# train recommender

# step 1: access games list

# step 2: normalize playtime data

# step 3: get list of games
# filter out video games