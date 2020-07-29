from flask import Flask, render_template, redirect
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import InputRequired
from recommender_final import recommend_game, get_games
import pandas as pd
import re

app = Flask(__name__)
app.config['SECRET_KEY'] = 'our very hard to guess secret key'

class LoginForm(FlaskForm):
    steam_id_form = StringField('', validators=[InputRequired()], default='76561198026189780')

@app.route('/', methods=['GET', 'POST'])
def form():
    form = LoginForm()
    if form.validate_on_submit():
        return redirect(str(form.steam_id_form.data))
    return render_template('index.html', form=form)

@app.route('/<steam_id>', methods=['GET', 'POST'])
def index(steam_id):
    my_key = open('key.txt').read()
    user_games = get_games(steam_id, my_key)
    if type(user_games) is not str:
        known_games = pd.read_csv('bgg_steam_data_normed.csv')
        x = recommend_game(user_games, known_games)
        game_info = pd.read_csv('game_info_lookup.csv', dtype='str', index_col=0)
        x = x.merge(game_info, how='left', left_on='game', right_on='Name')
        x['Your ranking'] = pd.Series(x.index).apply(lambda x: '#'+str(x + 1))
        x = x[['Game', 'Your ranking',  'Ranking', 'Players', 'Time', 'Complexity']]
        x['Ranking'] = x.Ranking.str.replace('[.]0', '')
        x['Ranking'] = x.Ranking.apply(lambda x: '#'+str(x))
        x['Ranking'] = x.Ranking.str.replace('#nan', '?')
        x.rename(columns={'Time': 'Playing time',
                          'Complexity': 'Complexity<br>(out of 5)',
                          'Game': 'Game',
                          'Ranking': 'BGG ranking'}, inplace=True)
        table_to_print = x.head(20).to_html(index=False, escape=False, justify='center', classes='sortable')
        table_to_print = re.sub('<th>(?=Your ranking</th>)', '<th class="sorttable_numeric">', table_to_print)
        table_to_print = re.sub('<th>(?=BGG ranking</th>)', '<th class="sorttable_numeric">', table_to_print)
        table_to_print = re.sub('<th>(?=Playing time</th>)', '<th class="sorttable_numeric">', table_to_print)
        table_to_print = re.sub('<td>(?=\?</td>)', '<td sorttable_customkey="99999999">', table_to_print)
        return render_template('form.html',  output=table_to_print)
    elif user_games == 'No games':
        return('Steam profile set to hidden.')
    else:
        return('This doesn\'t seem to be a valid Steam id')

if __name__ == '__main__':
    app.run(debug=False)