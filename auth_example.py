# Rename this file to auth.py when you're done setting it up

authentication = False
db_user = ''
db_pwd = ''

db_host = 'localhost'
db_port = 27017

token = ''
bearer = 'Bearer ' + '' # Token without oauth:
clientID = ''
nickname = ''
default_channel = ''

default_admin = '' #username of the administrator

reconnect_timer = 10

#0.1 for verified bots 0.580 for normal accs
join_ratelimit = 0.580

website = ''
leaderboard = ''
api_website = ''

userAgent = ''

raid_level_cap = 0 #0 - uncapped, any positive integer - raids' level is capped to this
raid_level_min = 0 #0 - uncapped, any positive integer >1 - minimum raid level. cannot be higher than the maxlevel
