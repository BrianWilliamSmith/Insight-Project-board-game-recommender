import requests as rq
import time
import json
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Load key and steam ids to lookup
my_key = open('key.txt', 'r').read()
steam_ids = open("group_steam_ids.txt", "r").read().split()

all_users = []
counter = 0
for steam_id in steam_ids:
    req = rq.get('https://api.steampowered.com/IPlayerService/GetOwnedGames/v1/?key={key}&steamid={id}&include_played_free_games=1&include_appinfo=1'.format(key=my_key, id=steam_id))
    if json.loads(req.text).get('response').get('games') != None:
        games_list = json.loads(req.text).get('response').get('games')
        for game in games_list:
            game.update({'user': steam_id})
        all_users += games_list
    time.sleep(2)
    counter += 1
    print(counter + ": requested user " + steam_id)
df = pd.DataFrame(all_users)
df.to_csv('df.csv')

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
