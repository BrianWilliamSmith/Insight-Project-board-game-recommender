import pandas as pd
import numpy as np
import requests as rq
import json

def get_games(steam_id, my_key):
    '''
    Takes a steam id and api key and returns a dataframe of video game play times
    for the user
    '''
    req = rq.get('https://api.steampowered.com/IPlayerService/GetOwnedGames/v1/?key={key}&steamid={id}&include_played_free_games=1&include_appinfo=1'.format(key=my_key, id=steam_id))
    if req.status_code == 500:
        return("500")
    if json.loads(req.text).get('response').get('games') == None:
        return("No games")
    else:
        games_list = json.loads(req.text).get('response').get('games')
        for game in games_list:
            game.update({'user': steam_id})
        user_games = pd.DataFrame(games_list)
        user_games['game'] = ['steam' + str(game) for game in user_games.appid]
        user_games['rating'] = user_games.playtime_forever
        user_games = user_games[['game', 'rating', 'user']]
        return(user_games)

def normalize_ratings(user_games):
    '''
    Takes a user-game-rating dataframe and adds a column named
    'rating_normed' with normalized ratings
    '''

    # Must play for at least 10 minutes
    user_games = user_games[user_games.rating>10]

    # Log transform (playtimes are very left skewed)
    user_games['rating'] = np.log(user_games.rating)

    # Normalize so mean = 5.5 and sd = 1.5
    ratings = user_games.rating.copy()
    mean = user_games.rating.mean()
    sd = user_games.rating.std()
    user_games['rating_normed'] =  (ratings - mean) / (.75 * sd + 0.0000000000001)
    user_games['rating_normed'] = user_games['rating_normed'] + 5.5

    # Make sure every rating is between 0 and 1
    user_games.loc[user_games.rating_normed < 1, 'rating_normed'] = 1
    user_games.loc[user_games.rating_normed > 10, 'rating_normed'] = 10
    return(user_games)


def predict_bg_ratings(boardgame_names, user_game_ratings, similarity_matrix,
                       bg_averages_df, min_support=5, k_neighbors=25):
    '''
    Takes a list of boardgames and returns a list of predicted values

    Parameters:
        boardgame_names = list of boardgames
        user_game_ratings = dataframe with three columns (user, game, rating_normed)
        similarity_matrix = a matrix with rows as vgs and columns as bgs
        min_support = minimum number of neighbors for rating prediction
        k_neighbors = max number of neighbors for rating prediction
    '''

    # Games must be in dataset
    user_game_ratings = user_game_ratings[user_game_ratings.game.isin(similarity_matrix.index)]

    # Only consider video games the user has rated
    similarity_matrix = similarity_matrix.loc[user_game_ratings.game]
    boardgame_ratings = []
    for boardgame in boardgame_names:
        try:
            all_similar_games = similarity_matrix.loc[
                similarity_matrix[boardgame] > 0, boardgame]
        except:
            predicted_rating = np.nan
            boardgame_ratings.append(predicted_rating)
            continue
        k_similar_games = all_similar_games.sort_values(ascending=False)[
                          0:k_neighbors]
        if len(k_similar_games) < min_support:
            predicted_rating = bg_averages_df.loc[
                bg_averages_df.game == boardgame, 'rating_normed'].values[0]
        else:
            k_similar_games_ratings = user_game_ratings.loc[
                user_game_ratings.game.isin(
                    k_similar_games.index), 'rating_normed']
            weighted_sum = np.dot(k_similar_games_ratings, k_similar_games)
            total = k_similar_games.sum()
            weighted_average = weighted_sum / total
            predicted_rating = weighted_average
        boardgame_ratings.append(predicted_rating)
    return boardgame_ratings




