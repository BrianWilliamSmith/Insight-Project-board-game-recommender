from flask import Flask, render_template, request, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import InputRequired
from recommender_final import recommend_game, get_games
import pandas as pd

app = Flask(__name__)
app.config['SECRET_KEY'] = 'our very hard to guess secretfir'

class LoginForm(FlaskForm):
    steam_id_form = StringField('steam_id', validators=[InputRequired()])

# @app.route('/')
# def index():
#     return render_template('index.html')

@app.route('/', methods=['GET', 'POST'])
def form():
    form = LoginForm()
    if form.validate_on_submit():
        return redirect(str(form.steam_id_form.data))
        # return('<h1>The username is {}. The password is {}'.format(form.username.data, form.password.data))
    return render_template('index.html', form=form)

@app.route('/<steam_id>', methods=['GET', 'POST'])
def index(steam_id):
    my_key = open('key.txt').read()
    user_games = get_games(steam_id, my_key)
    if type(user_games) is not str:
        known_games = pd.read_csv('bgg_steam_data_pruned.csv')
        x = recommend_game(user_games, known_games)
        return render_template('form.html',  output =x.head(25).to_html(index=False))
    elif user_games == 'No games':
        return('Steam profile set to hidden.')
    else:
        return('This doesn\'t seem to be a valid Steam id')

if __name__ == '__main__':
    app.run(debug=True)
#
# # Simple form handling using raw HTML forms
# @app.route('/sign-up', methods=['GET', 'POST'])
# def sign_up():
#     error = ""
#     if request.method == 'POST':
#         # Form being submitted; grab data from form.
#         first_name = request.form['firstname']
#         last_name = request.form['lastname']
#         # Validate form data
#         if len(first_name) == 0 or len(last_name) == 0:
#             # Form data failed validation; try again
#             error = "Please supply both first and last name"
#         else:
#             # Form data is valid; move along
#             return redirect(url_for('thank_you'))
#
#     # Render the sign-up page
#     return render_template('sign-up.html', message=error)
#
# # More powerful approach using WTForms
# class RegistrationForm(Form):
#     first_name = TextField('First Name')
#     last_name = TextField('Last Name')
#
# @app.route('/register', methods=['GET', 'POST'])
# def register():
#     error = ""
#     form = RegistrationForm(request.form)
#
#     if request.method == 'POST':
#         first_name = form.first_name.data
#         last_name = form.last_name.data
#
#         if len(first_name) == 0 or len(last_name) == 0:
#             error = "Please supply both first and last name"
#         else:
#             return redirect(url_for('thank_you'))
#
#     return render_template('register.html', form=form, message=error)
#
# # Run the application
# app.run(debug=True)
