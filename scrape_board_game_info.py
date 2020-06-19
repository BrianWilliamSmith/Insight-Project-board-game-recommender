import requests as rq
import pandas as pd
import time
import re

games = pd.read_csv('csvs/bgg_steam_data_normed.csv', index_col=0)
games = games[games.source=='bgg']
important_games = list(set(games.game))

# Get id for important games from game lookup table
game_lookup = pd.read_csv('csvs/bgg_GameItem.csv', index_col=0)
game_ids = []
for game in important_games:
    game_id = game_lookup[game_lookup.name==game].index[0]
    game_ids.append((game, game_id))
    #print(game + ' , ' + str(game_id))

# Dataframe of name and id for important games
game_ids_df = pd.DataFrame(game_ids, columns=['name', 'id'])

# Scrape image urls for important games
image_urls = []
for game_id in game_ids_df.id:
    r = rq.get('https://api.geekdo.com/xmlapi2/thing?id={}&stats=1&marketplace=1'.format(game_id))
    time.sleep(2)
    image_links = re.search('<thumbnail>(.*?)</thumbnail>\s+?<image>(.*?)</image>',r.text)
    try:
        url_info = (game_id, image_links.group(1), image_links.group(2))
    except:
        url_info = (game_id,'none', 'none')
    image_urls.append(url_info)
    print(url_info)

game_info = pd.DataFrame(image_urls, columns=['game_id', 'thumbnail_url', 'cover_url'])

# Combine game ids and image urls and other info

game_info = pd.concat([game_ids_df, game_info[['cover_url', 'thumbnail_url']]], axis=1)
game_info_2 = game_lookup[['name',
                           'year',
                           'min_age',
                           'min_players',
                           'max_players',
                           'min_time',
                           'max_time',
                           'complexity',
                           'avg_rating',
                           'rank'
                           ]]

game_info

lookup_important_games = game_info.merge(game_info_2, left_on='name', right_on='name', how='left')
lookup_important_games.to_csv('important_games_info.csv')

ratings = list(lookup_important_games.avg_rating.round(1))
complexity = list(lookup_important_games.complexity.round(1))
names = list(lookup_important_games.name)
years = list(lookup_important_games.year)
ranks = list(lookup_important_games['rank'])

times = []
for i in range(len(lookup_important_games)):
    min_time = lookup_important_games.min_time[i]
    max_time = lookup_important_games.max_time[i]
    if min_time == max_time:
        time_range = '{:.0f} minutes'.format(min_time)
    else:
        time_range = '{:.0f}-{:.0f} minutes'.format(min_time, max_time)
    times.append(time_range)

players = []
for i in range(len(lookup_important_games)):
    min_players = lookup_important_games.min_players[i]
    max_players = lookup_important_games.max_players[i]
    if min_players == max_players:
        if min_players == 1:
            player_range = 'One player'
        else:
            player_range = '{:.0f} players'.format(min_players)
    else:
        player_range = '{:.0f} to {:.0f} players'.format(min_players, max_players)
    players.append(player_range)

game_urls = ['https://boardgamegeek.com/boardgame/' + str(id) for id in lookup_important_games.id]
urls = ['<img src="' + url for url in lookup_important_games.thumbnail_url]
name_urls = ['<div class="game"><a href="'+ game_url + '">' + game + '</a> </div> <br/>' + url + '" alt=' + game + '">' for (game_url, game, url) in list(zip(game_urls, names, urls))]
name_urls

game_info = pd.DataFrame(list(zip(names, name_urls, ratings, times, players, complexity, ranks)),
             columns = ['Name', 'Game', 'BGG rating', 'Time', 'Players', 'Complexity', 'Ranking'])

game_info.to_csv('game_info_lookup.csv')