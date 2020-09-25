from flask import Flask, render_template, redirect
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import InputRequired
from recommender_final import *
import pandas as pd
import re

app = Flask(__name__)
app.config['SECRET_KEY'] = 'our very hard to guess secret key'

class LoginForm(FlaskForm):
    steam_id_form = StringField('', validators=[InputRequired()], default='76561198026189780')

def get_recs_table(steam_id, my_key):
    '''
    Takes a steam id and steam key and calculates recommendations
    Returns a dataframe with all of the recommendation information:
    playing time, game, complexity, bgg ranking
    '''
    user_games = get_games(steam_id, my_key)
    if type(user_games) is not str:
        user_games = normalize_ratings(user_games)
        sim_matrix = pd.read_csv('sim_matrix.txt', index_col=0)
        bg_averages_df = pd.read_csv('bg_average_ratings.csv')
        game_info = pd.read_csv('game_info_lookup.csv', dtype='str', index_col=0)

        known_games = list(sim_matrix.columns)

        predicted_ratings = predict_bg_ratings(known_games, user_games,
                                               sim_matrix, bg_averages_df)
        table_to_print = pd.DataFrame(zip(known_games, predicted_ratings),
                                      columns=['game', 'rating'])
        table_to_print.sort_values(by=['rating'], ascending=False, inplace=True)
        table_to_print.reset_index(inplace=True)

        game_info = game_info.drop_duplicates(subset='Name', keep='last')
        table_to_print = table_to_print.merge(game_info, how='left',
                                              left_on='game', right_on='Name')

        table_to_print['Your ranking'] = pd.Series(table_to_print.index).apply(lambda x: '#'+str(x + 1))
        table_to_print['Ranking'] = table_to_print.Ranking.str.replace('[.]0', '')
        table_to_print['Ranking'] = table_to_print.Ranking.apply(lambda x: '#'+str(x))
        table_to_print['Ranking'] = table_to_print.Ranking.str.replace('#nan', '?')
        table_to_print['Complexity'] = table_to_print.Ranking.str.replace('#nan', '?')

        table_to_print = table_to_print[['Game', 'Your ranking',  'Ranking', 'Players', 'Time', 'Complexity']]

        table_to_print.rename(columns={'Your ranking': 'Your ranking',
                          'Time': 'Playing time',
                          'Complexity': 'Complexity<br>(out of 5)',
                          'Game': 'Game',
                          'Ranking': 'BGG ranking'}, inplace=True)

        return table_to_print
    elif user_games == 'No games':
        return('Error1')
    else:
        return('Error2')

def render_table(table, n_games=20):
    """
    Takes a dataframe of recommendation information
    Returns a table formatted in HTML
    """
    table_head = table.head(n_games)
    table_to_print = table_head.to_html(index=False, escape=False,
                                        justify='center', classes='sortable')
    table_to_print = re.sub('<th>(?=Your ranking</th>)',
                            '<th class="sorttable_numeric">', table_to_print)
    table_to_print = re.sub('<th>(?=BGG ranking</th>)',
                            '<th class="sorttable_numeric">', table_to_print)
    table_to_print = re.sub('<th>(?=Playing time</th>)',
                            '<th class="sorttable_numeric">', table_to_print)
    table_to_print = re.sub('<td>(?=\?</td>)',
                            '<td sorttable_customkey="99999999">',
                            table_to_print)
    return table_to_print

@app.route('/', methods=['GET', 'POST'])
def form():
    form = LoginForm()
    if form.validate_on_submit():
        return redirect(str(form.steam_id_form.data))
    return render_template('index.html', form=form)

@app.route('/<steam_id>', methods=['GET', 'POST'])
def index(steam_id):
    my_key = open('key.txt').read()
    recs_table = get_recs_table(steam_id, my_key)

    if type(recs_table) is str:
        if recs_table == 'Error1':
            return('This user doesn\'t have any accessible game information. Maybe their profile is set to hidden.')
        elif recs_table == 'Error2':
            return('This isn\'t a valid Steam ID.')
    else:
        table_to_print = render_table(recs_table, 20)
        return render_template('form.html', output=table_to_print)

if __name__ == '__main__':
    app.run(debug=False)