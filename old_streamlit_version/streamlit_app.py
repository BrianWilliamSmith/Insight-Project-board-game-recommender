import streamlit as st
import pandas as pd
import numpy as np
import requests as rq
import json

st.title('Go Analog')

steam_id = st.sidebar.text_input("Enter Steam ID", '76561198026189780')

sort_by_column = st.sidebar.selectbox(
    "Sort by column…",
    ("Your ranking", "BGG ranking", "Complexity (out of 5)"))

recommend_n_games = st.sidebar.selectbox(
    "Recommendations this many board games…",
    (10, 20, 50, 100, 250))

# Checkboxes for columns
st.sidebar.markdown('Show columns')
show_bgg_ranking = st.sidebar.checkbox("BGG ranking", True)
show_players = st.sidebar.checkbox("Players", True)
show_playing_time = st.sidebar.checkbox("Playing time", True)
show_complexity = st.sidebar.checkbox("Complexity (out of 5)", True)

def get_games(steam_id, my_key):
    '''
    Takes a steam id and api key and creates dataframe of video game playtimes
    for user
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
                       min_support=5, k_neighbors=25):
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

@st.cache
def get_recs_table(steam_id, my_key):
    user_games = get_games(steam_id, my_key)
    if type(user_games) is not str:
        user_games = normalize_ratings(user_games)
        sim_matrix = pd.read_csv('sim_matrix.txt', index_col=0)
        known_games = list(sim_matrix.columns)

        predicted_ratings = predict_bg_ratings(known_games, user_games, sim_matrix)
        table_to_print = pd.DataFrame(zip(known_games, predicted_ratings),
                                      columns=['game', 'rating'])
        table_to_print.sort_values(by=['rating'], ascending=False, inplace=True)
        table_to_print.reset_index(inplace=True)

        game_info = pd.read_csv('game_info_lookup.csv', dtype='str', index_col=0)
        game_info = game_info.drop_duplicates(subset='Name', keep='last')
        table_to_print = table_to_print.merge(game_info, how='left', left_on='game', right_on='Name')
        table_to_print['Your ranking'] = pd.Series(table_to_print.index) + 1
        table_to_print = table_to_print[['rating', 'Game', 'Your ranking',  'Ranking', 'Players', 'Time', 'Complexity']]
        table_to_print['Ranking'] = table_to_print.Ranking.str.replace('[.]0', '')
        table_to_print.rename(columns={'Time': 'Playing time',
                          'Complexity': 'Complexity (out of 5)',
                          'Game': 'Game',
                          'Ranking': 'BGG ranking'}, inplace=True)
        return table_to_print
    elif user_games == 'No games':
        return('Error1')
    else:
        return('Error2')

def render_table(table):
    table.sort_values(by="Your ranking", inplace=True)
    table_head = table_to_print.head(recommend_n_games)
    table_head['BGG ranking'] = pd.to_numeric(table_head['BGG ranking'])
    table_head.sort_values(by=[sort_by_column], inplace=True)
    table_head = table_head.replace(np.nan, '—')

    column_settings = {'BGG ranking': show_bgg_ranking,
                       'Playing time': show_playing_time,
                       'Players' : show_players,
                       'Complexity (out of 5)' : show_complexity}

    columns_to_render = ['Game', 'Your ranking']
    columns_to_render += [key for key in column_settings if column_settings.get(key)]
    table_head = table_head[columns_to_render]
    st.write(table_head.to_html(index=False, justify = 'center', escape=False),
         unsafe_allow_html=True)

my_key = open('key.txt').read()
bg_averages_df = pd.read_csv('bg_average_ratings.csv')

table_to_print = get_recs_table(steam_id, my_key)

if type(table_to_print) is str:
    if table_to_print == 'Error1':
        st.write('This user doesn\'t have any accessible game information. Maybe their profile is set to hidden.')
    elif table_to_print == 'Error2':
        st.write('This isn\'t a valid Steam ID.')
else:
    render_table(table_to_print)
