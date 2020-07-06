import pandas as pd
import seaborn

def make_game_tag_matrix(dataframe):
    '''
    :param input: a dataframe with two columns: name and tags
    :return: a game x tags matrix with one-hot encoding
    '''
    game_tags = []
    for game in dataframe.name:
        tags = dataframe.loc[dataframe.name==game, 'tags'].values[0]
        try:
            tags = tags.split(',')
            tags = [tag for tag in tags if tag != '']
            dict = {tag: 1 for tag in tags}
            dict['game'] = game
        except:
            dict = {'game':game}
        game_tags.append(dict)
    game_tag_matrix = pd.DataFrame(game_tags)
    game_tag_matrix.fillna(0, inplace=True)
    return game_tag_matrix

steam_games = pd.read_csv('../csvs/steam_games.csv')
steam_games = steam_games[['url', 'popular_tags']]
steam_games['url'] = steam_games.url.str.extract(r'.*/app/([0-9]*?)/.*$',
                                                 expand=False)
steam_games['url'] = ['steam'+ str(game) for game in list(steam_games.url)]
steam_games.rename(columns={'popular_tags':'tags', 'url':'name'}, inplace=True)

bgg_games = pd.read_csv('../scraping_cleaning_normalizing/bgg_GameItem.csv')
bgg_games = bgg_games[['name', 'mechanic', 'category', 'game_type', 'family']]
bgg_games = bgg_games.fillna('')
bgg_games['tags'] = bgg_games['mechanic'] + ',' + \
                   bgg_games['category'] + ',' + \
                   bgg_games['game_type'] + ',' + \
                   bgg_games['family']
bgg_games['tags']
bgg_games['tags'] = bgg_games.tags.str.split()

steam_game_tag_matrix = make_game_tag_matrix(steam_games)
steam_game_tag_matrix.to_csv('steam_game_tag_matrix.csv')

bgg_game_tag_matrix = make_game_tag_matrix(bgg_games)
bgg_game_tag_matrix.to_csv('bgg_game_tag_matrix.csv')

bgg_steam_data = pd.read_csv(
    '../scraping_cleaning_normalizing/bgg_steam_data_normed.csv', index_col=0)
bgg_game_tag_matrix = pd.read_csv('../csvs/bgg_game_tag_matrix.csv', index_col=0)
steam_game_tag_matrix = pd.read_csv('../csvs/steam_game_tag_matrix.csv', index_col=0)

bgg_game_tag_matrix_pruned = bgg_game_tag_matrix[bgg_game_tag_matrix.game.isin(set(bgg_steam_data.game))]
steam_game_tag_matrix_pruned = steam_game_tag_matrix[steam_game_tag_matrix.game.isin(set(bgg_steam_data.game))]

# There are 377 steam tags
# Only keep the 100 most frequent tags
counts = steam_game_tag_matrix_pruned.drop(columns=['game']).sum()
counts.sort_values(ascending=False, inplace=True)
steam_tags_whitelist = counts[0:100].index

# There are 1000+ bgg tags!
counts = bgg_game_tag_matrix_pruned.drop(columns=['game']).sum()
counts.sort_values(ascending=False, inplace=True)
bgg_tags_whitelist = counts[0:100].index

bgg_tags_whitelist = bgg_game_tag_matrix_pruned.columns[bgg_game_tag_matrix_pruned.columns.str.contains('^1...$')]

bgg_game_tag_matrix_pruned = bgg_game_tag_matrix_pruned[['game'] + list(bgg_tags_whitelist)]
steam_game_tag_matrix_pruned = steam_game_tag_matrix_pruned[['game'] + list(steam_tags_whitelist)]

bgg_game_tag_matrix_pruned.to_csv('bgg_game_tag_matrix.pruned.csv')
steam_game_tag_matrix_pruned.to_csv('steam_game_tag_matrix.pruned.csv')

import pandas as pd
bgg_steam_data = pd.read_csv(
    '../scraping_cleaning_normalizing/bgg_steam_data_normed.csv', index_col=0)
bgg_game_tag_matrix_pruned = pd.read_csv(
    '../csvs/bgg_game_tag_matrix.pruned.csv', index_col=0)
steam_game_tag_matrix_pruned = pd.read_csv(
    '../csvs/steam_game_tag_matrix.pruned.csv', index_col=0)

blacklist = pd.read_csv('user_list.csv', index_col=0)
blacklist = blacklist.loc[(blacklist["brian thinks it's probably a dupe"]=='x')|(blacklist.aaron=='x'),'0']
bgg_steam_data.columns
bgg_steam_data = bgg_steam_data[~bgg_steam_data.user.isin(blacklist)]


steam_data = bgg_steam_data[bgg_steam_data.source=='steam'].merge(steam_game_tag_matrix_pruned, on='game')
user_tags = steam_data.groupby('user').sum()
tags_matrix =  user_tags.drop(columns=['rating', 'rating_normed'])
ratings_vector = user_tags.rating_normed.to_numpy().reshape(len(user_tags), 1)

steam_user_profiles = ratings_vector * tags_matrix
steam_user_profiles = pd.DataFrame(steam_user_profiles)

bgg_data = bgg_steam_data[bgg_steam_data.source=='bgg'].merge(bgg_game_tag_matrix_pruned, on='game')
user_tags = bgg_data.groupby('user').sum()
tags_matrix =  user_tags.drop(columns=['rating', 'rating_normed'])
ratings_vector = user_tags.rating_normed.to_numpy().reshape(len(user_tags), 1)

bgg_user_profiles = ratings_vector * tags_matrix
bgg_user_profiles = pd.DataFrame(bgg_user_profiles)

#normalize by user
bgg_user_profiles = bgg_user_profiles.apply(lambda x: x / bgg_user_profiles.sum(axis=1), raw=True, axis=0)
steam_user_profiles = steam_user_profiles.apply(lambda x: x / steam_user_profiles.sum(axis=1), raw=True, axis=0)


bgg_user_profiles
# Make a corelation matrix between board game tags and steam tags
profiles = pd.concat([bgg_user_profiles, steam_user_profiles], axis=1)
profiles
import numpy as np
profiles = profiles.replace(0, np.nan)

corr_matrix = profiles.corr(method='spearman')[bgg_user_profiles.columns].filter(items=steam_user_profiles.columns, axis=0)
corr_matrix.to_csv('corr_matrix_tags.csv')

corr_matrix = pd.read_csv('../csvs/corr_matrix_tags.csv', index_col=0)
scifi_corrs = corr_matrix.loc['Sci-fi',:].sort_values(ascending=False)
scifi_corrs = scifi_corrs[['1016','1113','5496','4664','1082','1028','5499: Family']]
scifi_corrs
scifi_colnames = {'1016':'Sci-fi',
            '1113':'Space Exploration',
            '5496': 'Thematic Games',
            '4664': 'War Games',
            #'1047':'Miniatures',
            '1082':'Mythology',
            '1028': 'Puzzle',
            '5499: Family': 'Family Games'}
            # ,
            #'2004': 'Set Collection',
            #'2048': 'Pattern Building'}

names = list(scifi_colnames.values())
vals = scifi_corrs.values

import matplotlib.pylab as plt
import seaborn as sns

x = sns.barplot(y=names, x=vals, color='#00a2ed')
x.set(title = 'Correlations between user ratings for sci-fi video games\nand user ratings for board game attributes',
      xlabel = 'Correlation coefficient',
      ylabel = 'Boardgame attributes')

plt.show()
plt.savefig('visualizations/corr_pruned.png')


scifi_corrs.reindex(scifi_colnames)

# Lookup mechanic: https://boardgamegeek.com/boardgamemechanic/2839/
# Lookup gametypes: https://boardgamegeek.com/boardgamesubdomain/5497/strategy-games