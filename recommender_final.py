import pandas as pd
import numpy as np
from surprise import Reader, Dataset, KNNBasic

def recommend_game(steam_id, my_key, known_games, k=10):
    new_user = get_games(steam_id, my_key)
    new_user = new_user[new_user.game.isin(known_games.game)]
    all_data = known_games.append(new_user, ignore_index=True)
    reader = Reader(rating_scale=(1, 10))
    data = Dataset.load_from_df(all_data[['user', 'game', 'rating']], reader)
    trainset = data.build_full_trainset()
    algo = KNNBasic()
    algo.fit(trainset)
    list_of_known_board_games = known_games[known_games.source=='bgg'].game.unique()
    testset = [(steam_id, board_game, '?') for board_game in list_of_known_board_games]
    predictions = algo.test(testset)
    board_game_predictions = [(prediction.iid, prediction.est) for prediction in predictions]
    best_board_games = pd.DataFrame(board_game_predictions, columns=['game','rating'])
    best_board_games.sort_values(by='rating', ascending=False, inplace=True)
    return(best_board_games.head(k))

def get_games(steam_id, my_key):
    req = rq.get('https://api.steampowered.com/IPlayerService/GetOwnedGames/v1/?key={key}&steamid={id}&include_played_free_games=1&include_appinfo=1'.format(
            key=my_key, id=steam_id))
    if req.status_code == 500:
        return ("Not a steam user")
    if json.loads(req.text).get('response').get('games') == None:
        return("Your profile has no games or it's set to private")
    else:
        games_list = json.loads(req.text).get('response').get('games')
        for game in games_list:
            game.update({'user': steam_id})
        user_games = pd.DataFrame(games_list)
        user_games = user_games[user_games.playtime_forever>0]
        user_games['game'] = ['steam'+str(game) for game in user_games.appid]
        user_games['rating'] = np.log(user_games.playtime_forever)
        user_games = user_games[['game', 'rating', 'user']]
        return(user_games)

def transform_playtimes_to_ratings(user_game_rating_dataframe:
    '''
    '''








