import json
import requests as rq

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

with open('steam_ids_for_BGG_group_on_steam.txt', 'w+') as file:
    file.write('\n'.join(reviewers))