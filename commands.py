import datetime
import re
import threading
import time
import secrets

import emoji

import utility as util
import database as opt
import schemes
import messages

db = opt.MongoDatabase
bot_start = time.time()

### User Commands ###

def commands(channel):
    util.send_message(messages.commands, channel)

def nlt2ping(channel):
    util.send_message(messages.nlt2ping, channel)

def ping(channel):
    uptime = int(time.time() - bot_start)
    util.send_message(messages.ping(str(datetime.timedelta(seconds=uptime))), channel)

def leaderboard(channel):
    util.send_message(messages.leaderboard, channel)

def channels(channel):
    util.send_message(messages.channels, channel)

def register(user, display_name, channel):
    registered = db(opt.USERS).find_one_by_id(user)
    if not registered or not registered.get('user_level'):
        db(opt.GENERAL).update_one(0, { '$inc': { 'dungeon_level': 1 } })
        db(opt.USERS).update_one(user, { '$set': schemes.USER }, upsert=True)
        dungeon = db(opt.GENERAL).find_one_by_id(0)
        util.queue_message_to_one(messages.user_register(display_name, str(dungeon['dungeon_level'])), channel)
    else:
        try:
            user_cmd_use_time = db(opt.USERS).find_one_by_id(user)['cmd_use_time']
        except:
            user_cmd_use_time = 0
        user_cooldown = db(opt.CHANNELS).find_one({'name': channel})['user_cooldown']
        global_cmd_use_time = db(opt.CHANNELS).find_one({'name': channel})['cmd_use_time']
        global_cooldown = db(opt.CHANNELS).find_one({'name': channel})['global_cooldown']
        message_queued = db(opt.CHANNELS).find_one({'name': channel})['message_queued']
        if time.time() > global_cmd_use_time + global_cooldown and time.time() > user_cmd_use_time + user_cooldown and message_queued == 0:
            db(opt.CHANNELS).update_one_by_name(channel, { '$set': { 'cmd_use_time': time.time() } }, upsert=True)
            db(opt.USERS).update_one(user, { '$set': { 'cmd_use_time': time.time() } }, upsert=True)
            util.send_message(messages.user_already_registered(display_name), channel)

def enterdungeon(user_id, display_name, channel):
    user = db(opt.USERS).find_one_by_id(user_id)
    if user and user.get('user_level'):
        enter_time = time.time()
        if int(user['next_entry'] - enter_time) <= 0:
            dungeon = db(opt.GENERAL).find_one_by_id(0)
            dungeon_level = dungeon['dungeon_level']
            user_level = user['user_level']

            if user_level > dungeon_level:
                level_run = dungeon_level
                success_rate = 65+((user_level-dungeon_level)*7)
                success_rate = success_rate if success_rate <= 100 else 100
                experience_gain = int(60*dungeon_level)*(1-((user_level-dungeon_level))*0.2)
                experience_gain = experience_gain if experience_gain >= 0 else 0
                dungeon_timeout = 3600
            else:
                level_run = user_level
                success_rate = 65
                experience_gain = int(60*user_level)
                dungeon_timeout = 3600

            if experience_gain == 0:
                util.send_message(messages.dungeon_too_low_level(display_name, str(dungeon_level)), channel)
                return

            dungeon_success = secrets.randbelow(100)+1
            db(opt.USERS).update_one(user['_id'], {'$set': {
                'last_entry': enter_time,
                'next_entry': enter_time + dungeon_timeout
            }})

            if dungeon_success <= success_rate:
                run_quality = secrets.randbelow(100)+1
                if run_quality <= 10:
                    experience_gain = int(experience_gain*0.5)
                    try:
                        message = emoji.emojize(list(db(opt.TEXT).get_random_documents_by_match({'mode': 'vbr'}, 1))[0]['text'])
                    except:
                        message = 'Very Bad Run'
                    util.send_message(messages.dungeon_very_bad_run(display_name, message, str(experience_gain)), channel)
                elif run_quality >= 90:
                    experience_gain = int(experience_gain*1.5)
                    try:
                        message = emoji.emojize(list(db(opt.TEXT).get_random_documents_by_match({'mode': 'vgr'}, 1))[0]['text'])
                    except:
                        message = 'Very Good Run'
                    util.send_message(messages.dungeon_very_good_run(display_name, message, str(experience_gain)), channel)
                else:
                    run_quality = secrets.randbelow(51)+75
                    experience_gain = int(experience_gain*run_quality*0.01)
                    if run_quality < 100:
                        try:
                            message = emoji.emojize(list(db(opt.TEXT).get_random_documents_by_match({'mode': 'br'}, 1))[0]['text'])
                        except:
                            message = 'Bad Run'
                        util.send_message(messages.dungeon_bad_run(display_name, message, str(experience_gain)), channel)
                    else:
                        try:
                            message = emoji.emojize(list(db(opt.TEXT).get_random_documents_by_match({'mode': 'gr'}, 1))[0]['text'])
                        except:
                            message = 'Good Run'
                        util.send_message(messages.dungeon_good_run(display_name, message, str(experience_gain)), channel)
                db(opt.USERS).update_one(user['_id'], {'$inc': {
                    'total_experience': experience_gain,
                    'current_experience': experience_gain,
                    'dungeon_wins': 1
                }})
                db(opt.GENERAL).update_one(0, {'$inc': {
                    'total_experience': experience_gain,
                    'total_wins': 1
                }})
                user_experience = user['current_experience'] + experience_gain
                if (((user_level+1)**2)*10) - user_experience <= 0:
                    db(opt.USERS).update_one(user['_id'], {'$inc': {
                        'user_level': 1,
                        'current_experience': -(((user['user_level']+1)**2)*10)
                    }})
                    level_up_thread = threading.Thread(target = util.queue_message_to_one, args=(messages.user_level_up(display_name, str(user['user_level'] + 1)), channel))
                    level_up_thread.start()
            else:
                db(opt.USERS).update_one(user['_id'], { '$inc': { 'dungeon_losses': 1 } })
                db(opt.GENERAL).update_one(0, { '$inc': { 'total_losses': 1 } })
                try:
                    message = emoji.emojize(list(db(opt.TEXT).get_random_documents_by_match({'mode': 'fail'}, 1))[0]['text'])
                except:
                    message = 'Failed Run'
                util.send_message(messages.dungeon_failed(display_name, message), channel)
            db(opt.USERS).update_one(user['_id'], { '$inc': { 'dungeons': 1 } })
            db(opt.GENERAL).update_one(0, { '$inc': { 'total_dungeons': 1 } })
        else:
            util.send_message(messages.dungeon_already_entered(display_name, str(datetime.timedelta(seconds=(int(user['next_entry']) - enter_time))).split('.')[0]), channel)
    else:
        util.send_message(messages.not_registered(display_name), channel)

def dungeonlvl(channel):
    dungeon = db(opt.GENERAL).find_one_by_id(0)
    util.send_message(messages.dungeon_level(str(dungeon['dungeon_level'])), channel)

def dungeonmaster(channel):
    users_by_xp = db(opt.USERS).find(sort=[('total_experience', -1)])
    while True:
        top_user = users_by_xp.next()
        tags = db(opt.TAGS).find_one_by_id(top_user['_id'])
        if not tags or not tags.get('bot'):
            break
    if top_user and top_user.get('user_level'):
        highest_experience = top_user['total_experience']
        user_level = top_user['user_level']
        number_of_top_users = db(opt.USERS).count_documents( {'total_experience': highest_experience} )
        if number_of_top_users == 1:
            top_user = db(opt.USERS).find_one( {'total_experience': highest_experience} )
            util.send_message(messages.dungeon_master(top_user['username'], str(user_level), str(highest_experience)), channel)
        else:
            util.send_message(messages.dungeon_masters(str(number_of_top_users), str(user_level), str(highest_experience)), channel)
    else:
        util.send_message(messages.dungeon_no_master, channel)

def dungeonstats(channel):
    general = db(opt.GENERAL).find_one_by_id(0)
    try:
        dungeons = general['total_dungeons']
    except:
        dungeons = 0
    try:
        wins = general['total_wins']
    except:
        wins = 0
    try:
        losses = general['total_losses']
    except:
        losses = 0
    if dungeons == 1:
        dungeonword = ' Dungeon'
    else:
        dungeonword = ' Dungeons'
    if wins == 1:
        winword = ' Win'
    else:
        winword = ' Wins'
    if losses == 1:
        loseword = ' Loss'
    else:
        loseword = ' Losses'
    if dungeons != 0:
        util.send_message(messages.dungeon_general_stats(str(dungeons), dungeonword, str(wins), winword, str(losses), loseword, str(round((((wins)/(dungeons))*100), 3))), channel)
    else:
        util.send_message(messages.dungeon_general_stats(str(dungeons), dungeonword, str(wins), winword, str(losses), loseword, '0'), channel)

def raidstats(channel):
    general = db(opt.GENERAL).find_one_by_id(0)
    try:
        raids = general['total_raids']
    except:
        raids = 0
    try:
        wins = general['total_raid_wins']
    except:
        wins = 0
    try:
        losses = general['total_raid_losses']
    except:
        losses = 0
    if raids == 1:
        raidword = ' Raid'
    else:
        raidword = ' Raids'
    if wins == 1:
        winword = ' Win'
    else:
        winword = ' Wins'
    if losses == 1:
        loseword = ' Loss'
    else:
        loseword = ' Losses'
    if raids != 0:
        util.send_message(messages.raid_general_stats(str(raids), raidword, str(wins), winword, str(losses), loseword, str(round((((wins)/(raids))*100), 3))), channel)
    else:
        util.send_message(messages.raid_general_stats(str(raids), raidword, str(wins), winword, str(losses), loseword, '0'), channel)

def xp(user, display_name, channel, message=None):
    if not message or len(message)<3:
        tags = db(opt.TAGS).find_one_by_id(user)
        if tags and tags.get('bot') == 1:
            util.send_message(messages.user_bot_message(display_name), channel)
        else:
            user = db(opt.USERS).find_one_by_id(user)
            if user and user.get('user_level'):
                util.send_message(messages.user_experience(display_name, str(user['total_experience'])), channel)
            else:
                util.send_message(messages.not_registered(display_name), channel)
    else:
        target_user = util.cutusername(message)
        target = db(opt.USERS).find_one({'username': re.compile('^' + re.escape(target_user) + '$', re.IGNORECASE)})
        if target and target.get('user_level'):
            tags = db(opt.TAGS).find_one_by_id(target['_id'])
            if tags and tags.get('bot') == 1:
                util.send_message(messages.user_bot_message(target['username']), channel)
            else:
                util.send_message(messages.user_experience(target['username'], str(target['total_experience'])), channel)
        else:
            util.send_message(messages.user_not_registered(display_name), channel)

def lvl(user, display_name, channel, message=None):
    if not message or len(message)<3:
        tags = db(opt.TAGS).find_one_by_id(user)
        if tags and tags.get('bot') == 1:
            util.send_message(messages.user_bot_message(display_name), channel)
        else:
            user = db(opt.USERS).find_one_by_id(user)
            if user and user.get('user_level'):
                util.send_message(messages.user_level(display_name, str(user['user_level']), str(user['current_experience']), str((((user['user_level']) + 1)**2)*10)), channel)
            else:
                util.send_message(messages.not_registered(display_name), channel)
    else:
        target_user = util.cutusername(message)
        target = db(opt.USERS).find_one({'username': re.compile('^' + re.escape(target_user) + '$', re.IGNORECASE)})
        if target and target.get('user_level'):
            tags = db(opt.TAGS).find_one_by_id(target['_id'])
            if tags and tags.get('bot') == 1:
                util.send_message(messages.user_bot_message(target['username']), channel)
            else:
                util.send_message(messages.user_level(target['username'], str(target['user_level']), str(target['current_experience']), str((((target['user_level']) + 1)**2)*10)), channel)
        else:
            util.send_message(messages.user_not_registered(display_name), channel)

def winrate(user, display_name, channel, message=None):
    if not message or len(message)<3:
        tags = db(opt.TAGS).find_one_by_id(user)
        if tags and tags.get('bot') == 1:
            util.send_message(messages.user_bot_message(display_name), channel)
        else:
            user = db(opt.USERS).find_one_by_id(user)
            if user and user.get('user_level'):
                if user['dungeons'] == 0:
                    util.send_message(messages.no_entered_dungeons(display_name), channel)
                else:
                    dungeons = user['dungeons']
                    wins = user['dungeon_wins']
                    losses = user['dungeon_losses']

                    if wins == 1:
                        win_word = ' Win'
                    else:
                        win_word = ' Wins'
                    if losses == 1:
                        lose_word = ' Loss'
                    else:
                        lose_word = ' Losses'
                    util.send_message(messages.user_stats(display_name, str(wins), win_word, str(losses), lose_word, str(round((((wins)/(dungeons))*100), 3))), channel)
            else:
                util.send_message(messages.not_registered(display_name), channel)
    else:
        target_user = util.cutusername(message)
        target = db(opt.USERS).find_one({'username': re.compile('^' + re.escape(target_user) + '$', re.IGNORECASE)})
        if target and target.get('user_level'):
            tags = db(opt.TAGS).find_one_by_id(target)
            if tags and tags.get('bot') == 1:
                util.send_message(messages.user_bot_message(target['username']), channel)
            else:
                same_user = None
                if user == target['_id']:
                    same_user = True
                if target['dungeons'] == 0:
                    if same_user:
                        util.send_message(messages.no_entered_dungeons(display_name), channel)
                    else:
                        util.send_message(messages.user_no_entered_dungeons(display_name), channel)
                else:
                    dungeons = target['dungeons']
                    wins = target['dungeon_wins']
                    losses = target['dungeon_losses']
                    if wins == 1:
                        win_word = ' Win'
                    else:
                        win_word = ' Wins'
                    if losses == 1:
                        lose_word = ' Loss'
                    else:
                        lose_word = ' Losses'
                    util.send_message(messages.user_stats(target['username'], str(wins), win_word, str(losses), lose_word, str(round((((wins)/(dungeons))*100), 3))), channel)
        else:
            util.send_message(messages.user_not_registered(display_name), channel)

def suggest(user, channel, message):
    if message != '':
        suggestions = db(opt.SUGGESTIONS).count_documents({})
        if suggestions < 500:
            try:
                id = db(opt.SUGGESTIONS).find_one(sort=[('_id', -1)])['_id']
            except:
                id = 0
            else:
                id += 1
            db(opt.SUGGESTIONS).update_one(id, {'$set': {
                'user': user,
                'suggestion': message
            }}, upsert=True)
            suggestion_thread = threading.Thread(target = util.queue_message_to_one, args=(messages.suggestion_message(user, str(id)), channel))
            suggestion_thread.start()
