import requests as rq
import re
import time
import pandas as pd
import glob

# Check lists of ids in steam ids folder
# Two sources:
# 1. list of steam ids from different groups
#    (each id is on a newline)
# 2. reviewers of tabletop simulator


def get_steam_player_info(steam_id, steam_key):
    '''
    Returns a list of tuples containing information about a steam user
    or users.
    :param steam_id: 100 or fewer steam id(s), separated by commas if multiple
    :return: A tuple (vanity_url, display_name, steam_id, privacy_status)
    '''
    r = rq.get('https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key={key}&steamids={id}'.format(
            key=steam_key, id=steam_id))
    players = json.loads(r.text).get('response').get('players')
    output = []
    for player in players:
        steam_id = player.get('steamid')
        profile_state = player.get('communityvisibilitystate')
        url = player.get('profileurl')
        persona_name = player.get('personaname')
        output.append((steam_id, url, profile_state, persona_name))
    return(output)

my_steam_key = open('key.txt').read()

steam_users = []
for file_name in glob.glob('./steam_ids_to_check/*.txt'):
    steam_ids = open(file_name,'r').read().split('\n')
    while len(steam_ids) > 0:
        set_of_ids = ','.join(steam_ids[0:100])
        del steam_ids[0:100]
        print('{} users left in {}'.format(len(steam_ids),file_name))
        steam_users += get_steam_player_info(set_of_ids, my_steam_key)
        time.sleep(2)

steam_users_df = pd.DataFrame(steam_users, columns = ['steam_id', 'url', 'hidden_prof', 'persona_name'])

# Add avatar column, which matches persona name, unless there's a vanity url
# If there's a vanity url, use that

steam_users_df['avatar'] = steam_users_df.persona_name
bool_has_a_vanity_url = steam_users_df.url.str.contains('/id/')
extract_vanity_from_url = lambda x: re.search('(?<=/id/).*?(?=/)', x).group(0)
steam_users_df.loc[bool_has_a_vanity_url, 'avatar'] = \
    steam_users_df.loc[bool_has_a_vanity_url, 'url'].apply(extract_vanity_from_url)

steam_users_df.to_csv('steam_users.csv')