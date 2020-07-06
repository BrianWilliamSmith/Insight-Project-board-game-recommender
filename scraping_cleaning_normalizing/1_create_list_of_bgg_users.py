import requests as rq
import re
import time
import pandas as pd
import glob

# This script creates a list of BGG users to look up on Steam
# It outputs a csv of bgg users with info

# Create list of BGG users to check on Steam
# Two sources:
# 1. BGG users who have a video game microbadge
# TO DO: 2. BGG users who have reviewed Catan (most popular game on BGG)

# Get BGG microbadge ids from locally-stored html files listing
# all of the video game microbadges. A microbadge indicates a user
# has a particular interest, e.g. the video game Civ III

game_groups = []
for file_name in glob.glob('scraping_cleaning_normalizing/bgg_group_pages/*.html'):
    results_page = open(file_name,'r').read()
    game_groups += re.findall("\/microbadge\/[0-9]+", results_page)

# Clean up extra html
game_groups = [re.sub('\/microbadge\/', '', badge) for badge in game_groups]

# For every video game microbadge, get all of users that have the badge.
# There will be duplicates since some users are in multiple groups.
# Currently grabs location (but I don't use it)

headers = {"user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36'"}
users, locations, new_users = [],[],[]

for badge_id in game_groups[1442:]:
    print(badge_id)
    counter, new_users = 1, 'xxx'
    while len(new_users) > 0:
        group_url = '/microbadge/owners?badgeid={badge}&pageid={page_num}&showrelated=1&sort=user&action=owners&ajax=1'.format(badge=badge_id, page_num=counter)
        url = 'https://boardgamegeek.com' + group_url
        counter += 1
        r= rq.get(url, headers).text
        locations += re.findall("(?<=location\\\'>).*?(?=<\/div)", r)
        new_users = re.findall("(?<=data-urlusername=\\\').*?(?=\\\')", r)
        users += new_users
        time.sleep(2)
        print(str(len(users)) + ',' + str(len(locations)))

bgg_users_df = pd.DataFrame(users, columns=['user_name'])

bgg_users_df.drop_duplicates(inplace=True)

bgg_users_df.to_csv('scraping_cleaning_normalizing/users_from_bgg.csv')