import os
import random
import re
import socket
import sys
import threading
import time
import json

import datetime

import requests
import emoji
import git

import auth
import database as opt
import schemes
import messages

db = opt.MongoDatabase

server = 'irc.chat.twitch.tv'
port = 6667

def connect(manual = False):
    global sock
    sock = socket.socket()
    try:
        printtolog("Socket connecting...")
        sock.connect((server, port))
        sock.send(('PASS ' + auth.token + '\r\n').encode('utf-8'))
        sock.send(('NICK ' + auth.nickname + '\r\n').encode('utf-8'))
        printtolog("Logged in, requesting capabilities and joinig channels.")
        sock.send(("CAP REQ :twitch.tv/tags\r\n").encode('utf-8'))
        channel_list = db(opt.CHANNELS).find({}).distinct('name')
        for c in channel_list:
            joinIRCChannel(c)
        printtolog("Channels joined successfully.")
    except socket.error as e:
        printtolog('Socket error: ' + str(e.errno))
        if not manual:
            time.sleep(auth.reconnect_timer)
        else:
            os._exit(1) # Shuts down script if called from initialization

def joinIRCChannel(channel):
    printtolog("Joining #"+channel)
    sock.send(('JOIN #' + channel + '\r\n').encode('utf-8'))
    time.sleep(auth.join_ratelimit)

def get_display_name(id, list = None):
    headers = { 'Authorization': auth.bearer, 'Client-ID': auth.clientID }
    if list:
        params = (('id', list),)
    else:
        params = (('id', id),)
    response = requests.get('https://api.twitch.tv/helix/users', headers=headers, params=params).json()
    if list:
        try:
            name_list = []
            for user in response['data']:
                name_list.append(user['display_name'])
            return name_list
        except:
            return
    else:
        try:
            return response['data'][0]['display_name']
        except:
            return

def get_user_id(user):
    headers = { 'Authorization': auth.bearer, 'Client-ID': auth.clientID }
    params = (('login', user),)
    response = requests.get('https://api.twitch.tv/helix/users', headers=headers, params=params).json()
    try:
        return response['data'][0]['id']
    except:
        return

def pong():
    sock.send(('PONG :tmi.twitch.tv\r\n').encode('utf-8'))

def printtolog(sText):
    t = time.localtime()
    current_time = time.strftime("%Y-%m-%d %H:%M:%S", t)
    sys.stdout.write(current_time+" "+sText+"\n")
    sys.stdout.flush()

def cutusername(unick):
    retval = unick.strip()
    if retval.startswith("@"):
        retval = retval[1:]
    if retval.endswith(","):
        retval = retval[:-1]
    return retval

def restart_on_reconnect():
    printtolog('TMI asked us to reconnect, restarting bot')
    os._exit(0)

last_time_symbol = 0
def get_cooldown_bypass_symbol():
    global last_time_symbol
    if last_time_symbol == 0:
        last_time_symbol = 1
        return ''
    else:
        last_time_symbol = 0
        return ' \U000e0000'

def send_message_old(message, channel):
    message = sanitize_message(message, channel)
    msg = 'PRIVMSG #' + channel + ' :' + message + get_cooldown_bypass_symbol()
    sock.send((msg + '\r\n').encode('utf-8'))

def send_message(message, channel):
    headers = { 'Authorization': auth.bearer, 'Client-ID': auth.clientID, 'Content-Type': 'application/json' }
    message = sanitize_message(message, channel)
    msg = message + get_cooldown_bypass_symbol()
    chid = db(opt.CHANNELS).find_one({'name': channel})['_id']
    myid = db(opt.CHANNELS).find_one({'name': auth.nickname.lower()})['_id']
    params = {'message': message, 'broadcaster_id': chid, 'sender_id': myid}
    response = requests.post('https://api.twitch.tv/helix/chat/messages', headers=headers, json=params, timeout=5)
    #TODO: handle non-200 replies here
    #response.raise_for_status()
    response = response.json()
    if 'error' in response:
        #printtolog('Helix: Unable to post message to #' +channel+ ':' +response.status+ ' ' +response.error+ ' ' +response.message)
        printtolog('Helix: Unable to post "'+ message +'" to #' +channel+ ', reason:')
        printtolog(json.dumps(response, indent=2))
        return
    if not ('data' in response):
        printtolog('Unhandled: Helix reply to post message is missing the "data" structure doctorWTF')
        return
    else:
        b = response["data"][0]
        if not b["is_sent"]:
            #printtolog('Error while trying to post "'+message+'" to #'+channel+': '+b["drop_reason"].code+' '+b["drop_reason"].message)
            printtolog('Helix: message "'+ message +'" was not sent to #' +channel+ ', reason:')
            printtolog(json.dumps(response, indent=2))

queue_message_lock = threading.Lock()

def queue_message_to_one(message, channel, is_sanitized=False):
    queue_message_lock.acquire()
    db(opt.CHANNELS).update_one_by_name(channel, { '$set': { 'message_queued': 1 } } )
    time.sleep(1)

    # We don't need to do another API call if a message is already sanitized.
    # Currently only set by raid's users' level up messages.
    if not is_sanitized:
        message = sanitize_message(message, channel)

    #msg = 'PRIVMSG #' + channel + ' :' + message + get_cooldown_bypass_symbol()
    #sock.send((msg + '\r\n').encode('utf-8'))
    send_message(message, channel)
    time.sleep(1)
    db(opt.CHANNELS).update_one_by_name(channel, { '$set': { 'message_queued': 0 } } )
    queue_message_lock.release()

def queue_message_to_some(message, channels):
    queue_message_lock.acquire()
    db(opt.CHANNELS).update_many({}, { '$set': { 'message_queued': 1 } } )
    time.sleep(1.25)
    msg = 'PRIVMSG #' + 'PRIVMSG #'.join(('{0} :' + message + get_cooldown_bypass_symbol() + '\r\n').format(c) for c in channels)
    sock.send((msg).encode('utf-8'))
    time.sleep(1.1)
    db(opt.CHANNELS).update_many({}, { '$set': { 'message_queued': 0 } } )
    queue_message_lock.release()

def queue_message_to_all(message):
    queue_message_lock.acquire()
    db(opt.CHANNELS).update_many({}, { '$set': { 'message_queued': 1 } } )
    time.sleep(1.25)
    channel_list = db(opt.CHANNELS).find({'online': 0}).distinct('name')
    msg = 'PRIVMSG #' + 'PRIVMSG #'.join(('{0} :' + message + get_cooldown_bypass_symbol() + '\r\n').format(c) for c in channel_list)
    sock.send((msg).encode('utf-8'))
    time.sleep(1.1)
    db(opt.CHANNELS).update_many({}, { '$set': { 'message_queued': 0 } } )
    queue_message_lock.release()

# def whisper(message, user):
#     msg = 'PRIVMSG #' + user + ' :.w ' + user + ' ' + message
#     sock.send((msg + '\r\n').encode('utf-8'))

def git_info():
    repo = git.Repo(search_parent_directories=True)
    branch = repo.active_branch.name
    sha = repo.head.object.hexsha
    queue_message_to_all(messages.startup_message(branch, sha))
    #queue_message_to_one(messages.startup_message(branch, sha), auth.default_channel.lower())

def start():
    default_admin_id = get_user_id(auth.default_admin)
    default_admin = db(opt.TAGS).find_one_by_id(default_admin_id)
    if default_admin == None:
        db(opt.TAGS).update_one(default_admin_id, {'$set': { 'admin': 1 } }, upsert=True)
    default_channel_id = get_user_id(auth.default_channel)
    default_channel = db(opt.CHANNELS).find_one_by_id(default_channel_id)
    if default_channel == None:
        db(opt.CHANNELS).update_one(default_channel_id, { '$set': schemes.CHANNELS }, upsert=True)
        db(opt.CHANNELS).update_one(default_channel_id, { '$set': { 'name': auth.default_channel } }, upsert=True)
    connect(True) # True for initialization
    default_dungeon = db(opt.GENERAL).find_one_by_id(0)
    if default_dungeon == None:
        db(opt.GENERAL).update_one(0, { '$set': schemes.GENERAL }, upsert=True)
    git_info()

### Admin Commands ###

def dungeon_text(mode, message):
    texts = db(opt.TEXT).count_documents({})
    try:
        id = db(opt.TEXT).find_one(sort=[('_id', -1)])['_id']
    except:
        id = 0
    else:
        id += 1
    db(opt.TEXT).update_one(id, {'$set': {
        'mode': mode,
        'text': message
    }}, upsert=True)

def join_channel(current_channel, channel, global_cooldown, user_cooldown):
    try:
        user = get_user_id(channel)
        if user:
            db(opt.CHANNELS).update_one(user, {'$set': {
                'name': channel,
                'online': 1,
                'cmd_use_time': time.time(),
                'last_message_time': time.time(),
                'global_cooldown': global_cooldown,
                'user_cooldown': user_cooldown,
                'message_queued': 0,
                'raid_events': 1,
                'banphrase_api': ''
            }}, upsert=True)
            db(opt.TAGS).update_one(user, {'$set': { 'moderator': 1 } }, upsert=True)
            sock.send(('JOIN #' + channel + '\r\n').encode('utf-8'))
            repo = git.Repo(search_parent_directories=True)
            branch = repo.active_branch.name
            sha = repo.head.object.hexsha
            send_message(messages.startup_message(branch, sha), channel)
    except AttributeError:
        queue_message_to_one(messages.no_channel_error(channel), current_channel)

def part_channel(channel):
    user = db(opt.CHANNELS).find_one({'name': channel})
    if user:
        part_channel_thread = threading.Thread(target = queue_message_to_one, args=(messages.leaving_channel(get_display_name(user['_id'])), channel))
        part_channel_thread.start()
        db(opt.CHANNELS).delete_one(user['_id'])
        db(opt.TAGS).update_one(user['_id'], {'$unset': { 'moderator': '' } }, upsert=True)
        sock.send(('PART #' + channel + '\r\n').encode('utf-8'))

def set_events(channel, mode, current_channel):
    try:
        if mode == 'off' and db(opt.CHANNELS).find_one({'name': channel})['raid_events'] == 1:
            queue_message_to_one(messages.set_event_message('disabled', channel), channel)
            db(opt.CHANNELS).update_one_by_name(channel, { '$set': { 'raid_events': 0 } } )

        elif mode == 'on' and db(opt.CHANNELS).find_one({'name': channel})['raid_events'] == 0:
            queue_message_to_one(messages.set_event_message('enabled', channel), channel)
            db(opt.CHANNELS).update_one_by_name(channel, { '$set': { 'raid_events': 1 } } )

    except Exception as e:
        queue_message_to_one(messages.error_message(e), current_channel)

def set_cooldown(channel, mode, cooldown, current_channel):
    if mode == 'global':
        try:
            db(opt.CHANNELS).update_one_by_name(channel, { '$set': { 'global_cooldown': cooldown } } )
        except Exception as e:
            queue_message_to_one(messages.error_message(e), current_channel)
    elif mode == 'user':
        try:
            db(opt.CHANNELS).update_one_by_name(channel, { '$set': { 'user_cooldown': cooldown } } )
        except Exception as e:
            queue_message_to_one(messages.error_message(e), current_channel)
    else:
        queue_message_to_one(messages.set_cooldown_error, current_channel)

def run_eval(expression, channel):
    try:
        queue_message_to_one(str(eval(expression)), channel)
    except Exception as e:
        queue_message_to_one(messages.error_message(e), channel)

def run_exec(code, channel):
    try:
        exec(code)
    except Exception as e:
        queue_message_to_one(messages.error_message(e), channel)

def reset_cooldown(channel):
    db(opt.USERS).update_many({}, { '$set': {
        'last_entry': 0,
        'next_entry': 0
    }})
    queue_message_to_all(messages.reset_cooldown)

def restart():
    queue_message_to_all(messages.restart_message)
    repo = git.Repo(search_parent_directories=True)
    repo.git.reset('--hard')
    repo.remotes.origin.pull()
    sock.send(('QUIT\r\n').encode('utf-8'))
    sock.close()
    os._exit(1)

def tag_user(user, tag, channel):
    tag_list = ['admin', 'moderator', 'bot']
    user_id = get_user_id(user)
    if user:
        if tag.lower() in tag_list:
            user = db(opt.TAGS).find_one_by_id(user_id)
            if not user or not user.get(tag.lower()):
                db(opt.TAGS).update_one(user_id, {'$set': {tag.lower(): 1} }, upsert=True)
                queue_message_to_one(messages.tag_message(get_display_name(user_id), tag), channel)
            else:
                queue_message_to_one(messages.already_tag_message(get_display_name(user_id), tag), channel)

### Banphrase API ###

def check_banphrase(message, channel_name):
    headers = { 'User-Agent': ('dungeonbot (custom instance)' if len(auth.userAgent)==0 else auth.userAgent) }
    params = {'message': message}

    banphrase_api =  db(opt.CHANNELS).find_one({'name': channel_name})['banphrase_api']

    if not banphrase_api:
        return False

    time.sleep(random.uniform(0.1, 1))
    response = requests.post('https://' + banphrase_api + '/api/v1/banphrases/test', headers=headers, json=params, timeout=5)
    response.raise_for_status()
    response = response.json()
    return response

def sanitize_display_names(channel_name, display_names):
    if display_names:
        display_name_list = []
        for display_name in display_names:
            try:
                banphrase_api_check = check_banphrase(display_name, channel_name)
                display_name_list.append(messages.banphrased_name if banphrase_api_check and banphrase_api_check['banned'] else display_name)
            except requests.exceptions.RequestException:
                display_name_list.append(messages.banphrase_name_api_offline)
        return display_name_list

def sanitize_message(message, channel):
    try:
        banphrase_api_check = check_banphrase(message, channel)
        if banphrase_api_check and banphrase_api_check['banned']:
            phrase = banphrase_api_check['banphrase_data']['phrase']
            banned_phrase = r'\w*' + re.search(phrase, message, flags=re.IGNORECASE).group() + r'\w*'
            message = re.sub(banned_phrase, messages.banphrased, message, flags=re.IGNORECASE)
        return message
    except requests.exceptions.RequestException:
        return messages.banphrase_api_offline
