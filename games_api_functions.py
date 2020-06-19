import requests as rq
import urllib.parse
import re

def get_user_info_bgg(username):
    '''
    Returns a tuple containing information about a bgg user.
    Returns a tuple ('none', 'none', 'none', 'none') if user not on BGG.
    Input: username on bgg
    Output: tuple of (bgg id, state, country, steam id)
    '''
    username = urllib.parse.quote_plus(username)
    r = rq.get('https://www.boardgamegeek.com/xmlapi2/user?name={user_url}'.format(user_url=username))
    if '<user id=""' in r.text:
        bgg_id, bgg_state, bgg_country, bgg_steam_id = 'none', 'none', 'none', 'none'
    else:
        bgg_id = re.search('(?<=user id=")[0-9]*?(?=")', r.text).group(0)
        bgg_country = re.search('(?<=<stateorprovince value=").*?(?=")', r.text).group(0)
        bgg_state = re.search('(?<=<country value=").*?(?=")', r.text).group(0)
        bgg_steam_id = re.search('(?<=steamaccount value=").*?(?=")', r.text).group(0)
    return(bgg_id, bgg_state, bgg_country, bgg_steam_id)

def get_steam_games(steam_id, steam_api_key):
    '''
    Returns a dictionary with the steam user's game play info,
    including an entry for steam_id with the user's steam id
    Input: steam id and steam api key
    Output: a dictionary
    '''
    if steam_id == None or steam_id == 'none':
        return None
    req = rq.get('https://api.steampowered.com/IPlayerService/GetOwnedGames/v1/?key={key}&steamid={id}&include_played_free_games=1&include_appinfo=1'.format(key=key, id=steam_id))
    if json.loads(req.text).get('response').get('games') != None:
        games_list = json.loads(req.text).get('response').get('games')
        for game in games_list:
            game.update({'steam_id': steam_id})
        return games_list
    else:
        return None

def get_steam_id(username, steam_api_key):
    '''
    Get a steam_id from a username.
    Returns 'none' if there's no steam_id for the username
    Input: steam username and steam api key
    Output: steam_id
    '''
    usrname = urllib.parse.quote_plus(username)
    r = rq.get('http://api.steampowered.com/ISteamUser/ResolveVanityURL/v0001/?key={my_key}&vanityurl={username}'.format(key=steam_api_key, username=username))
    if json.loads(r.text).get('response').get('message') == None:
        steam_id = json.loads(r.text).get('response').get('steamid')
        return steam_id
    else:
        return 'none'

def get_steam_player_info(steam_id, steam_api_key):
    '''
    Takes a list of steam ids
    Returns a dictionary for every steam id containing player info
    '''
    r = rq.get(
        'http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key={}&steamids={}'.format(steam_api_key, steam_id))
    user_info = json.loads(r.text)
    return(user_info.get('response').get('players'))