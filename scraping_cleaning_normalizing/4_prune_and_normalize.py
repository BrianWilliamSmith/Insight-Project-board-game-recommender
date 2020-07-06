import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# This script prepares the dataset for analysis, pruning inactive users and
# underplayed games, and normalizing playtimes and ratings
# It outputs a csv containing the final dataset

# Load two datasets to be combined
bgg_users_games = pd.read_csv('scraping_cleaning_normalizing/boardgame_ratings.csv', index_col=0)
steam_users_games = pd.read_csv('scraping_cleaning_normalizing/steam_playtimes.csv', index_col=0)

# Dedupe both datasets (just in case -- shouldn't be necessary)
bgg_users_games.drop_duplicates(inplace=True, ignore_index=True)
steam_users_games.drop_duplicates(inplace=True, ignore_index=True)

# Process steam data first
# Remove games with zero playtime or extreme playtimes
# (Extreme playtime > 3sds above global mean)
stdev_playtime = steam_users_games.playtime_forever.std()
mean_playtime = steam_users_games.playtime_forever.mean()
playtime_cutoff = 3 * stdev_playtime + mean_playtime

steam_users_games = steam_users_games[steam_users_games.playtime_forever > 0]
steam_users_games = steam_users_games[steam_users_games.playtime_forever < playtime_cutoff]
steam_users_games.reset_index(drop=True, inplace=True)

# Log-transform steam playtimes
steam_users_games['rating'] = np.log(steam_users_games.playtime_forever)

# Normalization
# Calculate average and SD by user
average_rating_by_user_steam = steam_users_games.groupby('steam_id').mean().rating
sd_by_user_steam = steam_users_games.groupby('steam_id').std().rating

# Subtract the mean and divide by .75 sds (so the final sd is 1.5)
# and matches the regular rating distribution
steam_users_games.reset_index(drop=True, inplace=True)
steam_ratings_normed = []
for i in range(len(steam_users_games)):
    user = steam_users_games.steam_id[i]
    mean = average_rating_by_user_steam[user]
    sd = sd_by_user_steam[user]
    rating = steam_users_games.rating[i]
    new_rating = (rating - mean)/(.75*sd+0.0000000000001)
    new_rating = new_rating + 5.5
    steam_ratings_normed.append(new_rating)

# Create a new 'rating_normed' column and make sure every rating is between
# 1 and 10
steam_users_games['rating_normed'] = steam_ratings_normed
steam_users_games.loc[steam_users_games.rating_normed < 1, 'rating_normed'] = 1
steam_users_games.loc[steam_users_games.rating_normed > 10, 'rating_normed'] = 10

# Save transformed steam data
steam_users_games.to_csv('steam_playtimes_normed.csv')

# Now process BGG data

# Only keep boardgames (no expansions). Use a lookup table with boardgame info
no_expansions = pd.read_csv('csvs/bgg_GameItem.csv')
no_expansions = set(no_expansions.name)
bgg_users_games = bgg_users_games[bgg_users_games.game.isin(no_expansions)]

# Normalize bgg rating data using the same technique used for steam ratings
# Ideally, I'd write a function for this -- very repetitive right now
average_rating_by_user_bgg = bgg_users_games.groupby('steam_id').mean().rating
sd_by_user_bgg = bgg_users_games.groupby('steam_id').std().rating

bgg_users_games.reset_index(drop=True, inplace=True)
bgg_ratings_normed = []
for i in range(len(bgg_users_games)):
    user = bgg_users_games.steam_id[i]
    mean = average_rating_by_user_bgg[user]
    sd = sd_by_user_bgg[user]
    rating = bgg_users_games.rating[i]
    new_rating = (rating - mean)/(.75*sd+0.0000000000001)
    new_rating = new_rating + 5.5
    bgg_ratings_normed.append(new_rating)

# Create a new 'rating_normed' column and make sure every rating is between
# 1 and 10
bgg_users_games['rating_normed'] = bgg_ratings_normed
bgg_users_games.loc[bgg_users_games.rating_normed < 1, 'rating_normed'] = 1
bgg_users_games.loc[bgg_users_games.rating_normed > 10, 'rating_normed'] = 10

# Save transformed bgg data
steam_users_games.to_csv('boardgame_ratings_normed.csv')

# Merge bgg data and steam data
# Make sure both data sets have these three columns
keep_these_columns = ['steam_id', 'game', 'rating', 'rating_normed']

# Get steam data ready for merge
steam_users_games.rename(columns={'name':'game'}, inplace=True)
steam_users_games = steam_users_games[keep_these_columns]
steam_users_games['source'] = 'steam'

# Get bgg data ready for merge
bgg_users_games = bgg_users_games[keep_these_columns]
bgg_users_games['source'] = 'bgg'

# Merge dataframes by combining rows
all_users_games = pd.concat([steam_users_games, bgg_users_games], axis=0, ignore_index=True)

# Identify shared users and drop the rest
shared_users = set(bgg_users_games.steam_id).intersection(steam_users_games.steam_id)
all_users_games = all_users_games[all_users_games.steam_id.isin(shared_users)]

# Don't confuse steam games and bgg games
# Keep track by combining source + game columns, e.g. "steam UNO"
all_users_games['game'] = all_users_games.source + ' ' + all_users_games.game

# Only include common games
# Common games are reviewed or played by at least 10 users
common_games = all_users_games.game.value_counts()
common_games = common_games.where(common_games>9).dropna().index.tolist()

all_users_games = all_users_games[all_users_games.game.isin(common_games)]

# Save final and complete users games data frame
all_users_games.to_csv('scraping_cleaning_normalizing/bgg_steam_data_normed.csv')