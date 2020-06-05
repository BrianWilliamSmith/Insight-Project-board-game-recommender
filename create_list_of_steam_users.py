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

# Get list of steam_ids from reviewers of Tabletop simulator
# Have to send the last cursor value to API to get the next page of results

app_id = '286160'
new_cursor = '*'
old_cursor = ''
reviewers=[]
while old_cursor != new_cursor:
    r=rq.get('https://store.steampowered.com/appreviews/{game}?json=1&filter=recent&purchase_type=all&num_per_page=100&cursor={cursor}'.format(game=app_id, cursor=new_cursor))
    old_cursor = new_cursor
    new_cursor = json.loads(r.text)['cursor']
    new_cursor = rq.compat.quote_plus(new_cursor)
    reviewers += re.findall('(?<=steamid":").*?(?=",)', r.text)
    print(old_cursor, new_cursor)
    print('%s reviewers so far' % len(reviewers))

with open('steam_ids_to_check/steam_ids_for_BGG_group_on_steam.txt', 'w+') as file:
    file.write('\n'.join(reviewers))

# Get information about a user using steam_id

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


# Go through all of the lists of ids in steam_id folder

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
