import emoji
import auth

nlt2ping = 'monkaLaugh' + emoji.emojize(':thumbs_up:', language='alias') + 'I\'m here'

commands = emoji.emojize(':memo:', language="alias") + ('For a list of commands, visit ' + auth.website if len(auth.website)>0 else 'No command list website is currently set :( ')

leaderboard = emoji.emojize(':trophy:', language="alias") + ('Check the leaderboard here: ' + auth.leaderboard if len(auth.leaderboard) >0 else 'Leaderboard currently not available :( ')

def ping(uptime):
    return emoji.emojize(' :stopwatch:', language="alias") + ' Dungeon Bot Uptime: ' + uptime + ' | For more information, visit ' + auth.api_website

def startup_message(branch, sha):
    return emoji.emojize(':arrow_right:', language="alias") + ' Dungeon Bot (' + branch + ', ' + sha[0:7] + ')'

def dungeon_too_low_level(username, dungeon_level):
    return username + ', the Dungeon [' + dungeon_level + "] is too low level for you to enter. You won't gain any experience!" + emoji.emojize(':crossed_swords:', language="alias")

def dungeon_very_bad_run(username, message, experience_gain):
    return username + ' | ' + message + ' | Experience Gained: ' + experience_gain + emoji.emojize(':gem:', language="alias")

def dungeon_very_good_run(username, message, experience_gain):
    return username + ' | ' + message + ' | Experience Gained: ' + experience_gain + emoji.emojize(':gem:', language="alias")

def dungeon_bad_run(username, message, experience_gain):
    return username + ' | ' + message + ' | Experience Gained: ' + experience_gain + emoji.emojize(':gem:', language="alias")

def dungeon_good_run(username, message, experience_gain):
    return username + ' | ' + message + ' | Experience Gained: ' + experience_gain + emoji.emojize(':gem:', language="alias")

def dungeon_failed(username, message):
    return username + ' | ' + message + ' | No experience gained! FeelsBadMan'

def dungeon_already_entered(username, time_remaining):
    return username + ', you have already entered the dungeon recently, ' + time_remaining + ' left until you can enter again!' + emoji.emojize(' :hourglass:', language="alias")

def dungeon_level(dungeon_level):
    return emoji.emojize(':shield:', language="alias") + ' Dungeon Level: [' + dungeon_level + ']'

def dungeon_master(top_user, user_level, highest_experience):
    return top_user + ' is the current Dungeon Master at Level [' + user_level + '] with ' + highest_experience + ' experience!' + emoji.emojize(' :crown:', language="alias")

def dungeon_masters(number_of_top_users, user_level, highest_experience):
    return 'There are ' + number_of_top_users + ' users at Level [' + user_level + '] with ' + highest_experience + ' experience, no one is currently Dungeon Master! FeelsBadMan'

dungeon_no_master = 'There is currently no Dungeon Master! FeelsBadMan'

def dungeon_general_stats(dungeons, dungeon_word, wins, win_word, losses, lose_word, winrate):
    return 'General Dungeon Stats: ' + dungeons + dungeon_word + ' / ' + wins + win_word +' / ' + losses + lose_word + ' = ' + winrate + '% Winrate' + emoji.emojize(' :large_blue_diamond:', language="alias")

def raid_general_stats(raids, raid_word, wins, win_word, losses, lose_word, winrate):
    return 'General Raid Stats: ' + raids + raid_word + ' / ' + wins + win_word +' / ' + losses + lose_word + ' = ' + winrate + '% Winrate' + emoji.emojize(' :large_orange_diamond:', language="alias")

def raid_event_appear(raid_level, time):
    return 'A Raid Event at Level [' + raid_level + '] has appeared. Type +join to join the raid! The raid will begin in ' + time + ' seconds!' + emoji.emojize(':zap:', language="alias")

def raid_event_countdown(time):
    return 'The raid will begin in ' + time + ' seconds. Type +join to join the raid!' + emoji.emojize(':zap:', language="alias")

raid_event_no_users = '0 users joined the raid!' + emoji.emojize(':skull_and_crossbones:', language="alias")

def raid_event_start(users, user_word, success_rate):
    return 'The raid has begun with ' + users + user_word + '! [' + success_rate + '%]' + emoji.emojize(':crossed_swords:', language="alias")

def raid_event_win(users, user_word, raid_level, experience_gain):
    return users + user_word + ' beat the raid level [' + raid_level + '] - ' + experience_gain + ' experience rewarded!' + emoji.emojize(':gem:', language="alias")

def raid_event_failed(users, user_word, raid_level):
    return users + user_word + ' failed to beat the raid level [' + raid_level + '] - No experience rewarded!' + emoji.emojize(':skull:', language="alias")

def user_register(username, dungeon_level):
    return 'DING ' + emoji.emojize(':bell:', language="alias") + ' Thank you for registering ' + username + ' | Dungeon leveled up! Level [' + dungeon_level + ']'

def user_level_up(username, user_level):
    return username + ' just leveled up! Level [' + user_level + '] PogChamp'

def users_level_up(users):
    return ', '.join(users) + ' just leveled up! PogChamp'

def user_register(username, dungeon_level):
    return 'DING ' + emoji.emojize(':bell:', language="alias") + ' Thank you for registering ' + username + ' | Dungeon leveled up! Level [' + dungeon_level + ']'

def user_already_registered(username):
    return username + ', you are already registered! ' + emoji.emojize(':warning:', language="alias")

def user_experience(username, user_experience):
    return username + "'s total experience: " +  user_experience + emoji.emojize(' :diamonds:', language="alias")

def user_level(username, user_level, current_experience, next_experience):
    return username + "'s current level: [" + user_level + '] - XP (' + current_experience + ' / ' + next_experience + ')' + emoji.emojize(' :diamonds:', language="alias")

def no_entered_dungeons (username):
    return username + ", you haven't entered any dungeons!" + emoji.emojize(' :warning:')

def user_stats(username, wins, win_word, losses, lose_word, winrate):
    return username + "'s winrate: " + wins + win_word +' / ' + losses + lose_word + ' = ' + winrate + '% Winrate' + emoji.emojize(' :diamonds:', language="alias")

def user_no_entered_dungeons(username):
    return username + ", that user hasn't entered any dungeons!" + emoji.emojize(' :warning:')

def not_registered(username):
    return username + ', you are not a registered user, type +register to register!' + emoji.emojize(' :game_die:', language="alias")

def user_not_registered(username):
    return username + ', that user is not registered!' + emoji.emojize(' :warning:', language="alias")

def suggestion_message(username, id):
    return username + ', thanks for your suggestion! ' + emoji.emojize(':memo:', language="alias") + ' [ID ' + id + ']'

def no_channel_error(channel):
    return emoji.emojize(':x: ', language="alias") + 'channel ' + channel + ' does not exist'

def leaving_channel(name):
    return emoji.emojize(':rewind:', language="alias") + ' Leaving ' + name + ' FeelsBadMan'

channels = emoji.emojize(':tv:', language="alias") + ('For a list of channels check ' + auth.api_website if len(auth.api_website)>0 else 'API/Channel list website is not currently set :( ')

def list_suggestions(list):
    return '[' + ', '.join(str(i) for i in list) + ']'

reset_cooldown = 'Cooldowns reset for all users' + emoji.emojize(' :stopwatch:', language="alias")

def tag_message(user, tag):
    return user + ' set to ' + tag.capitalize() + emoji.emojize(' :bell:', language="alias")

def already_tag_message(user, tag):
    return user + ' is already ' + tag.capitalize() + emoji.emojize(' :bell:', language="alias")

def error_message(error):
    return emoji.emojize(':x: ', language="alias") + str(error)

def set_event_message(mode, channel):
    return 'Raid Events ' + mode + ' in ' + channel + emoji.emojize(' :bell:', language="alias")

def user_bot_message(user):
    return user + ' is tagged as a Bot ' + emoji.emojize(':robot_face:', language="alias")

add_text_error = emoji.emojize(':warning: ', language="alias") + 'Insufficient parameters - usage: +text <vgr/vbr/gr/br/fail> <message>)'

add_channel_error = emoji.emojize(':warning: ', language="alias") + 'Insufficient parameters - usage: +add <name> (optional: <global cooldown> <user cooldown>)'

part_channel_error = emoji.emojize(':warning: ', language="alias") + 'Insufficient parameters - usage: +part <name>'

set_events_error_admin = emoji.emojize(':warning: ', language="alias") + 'Insufficient parameters - usage: +events <channel> <on/off>'

set_events_error_mod = emoji.emojize(':warning: ', language="alias") + 'Insufficient parameters - usage: +events <on/off>'

set_cooldown_error = emoji.emojize(':warning: ', language="alias") + 'Insufficient parameters - usage: +cd <channel> <global/user> <cooldown>'

tag_error = emoji.emojize(':warning: ', language="alias") + 'Insufficient parameters - usage: +tag <user> <role>'

restart_message = emoji.emojize(':arrows_counterclockwise:', language="alias") + ' Restarting...'

banphrased = '[Banphrased]'

banphrase_api_offline = 'Banphrase API did not send a response back.'

banphrased_name = '[Banphrased Name]'

banphrase_name_api_offline = '[Banphrase API ' + emoji.emojize(':electric_plug:', language="alias") + ']'
