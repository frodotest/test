#coding: utf8

import hashlib
import logging
import time
import cache_worker
import pymysql
import pymysql.cursors
import requests
import telebot
from threading import Thread

import config
import secret_config
import text
import ujson
import utils

bot = telebot.TeleBot(token = secret_config.token)

class DB:
    def __init__(self, host, user, db, password):
        self.host = host
        self.user = user
        self.password = password
        self.db = db
        self.charset = 'utf8mb4'
        self.cursorclass = pymysql.cursors.DictCursor

class DataConn:
    def __init__(self, db_obj):
        self.host = db_obj.host
        self.user = db_obj.user
        self.password = db_obj.password
        self.db = db_obj.db
        self.charset = db_obj.charset
        self.cursorclass = db_obj.cursorclass

    def __enter__(self):
        self.conn = pymysql.connect(
            host = self.host,
            user = self.user,
            password = self.password,
            db = self.db,
            charset = self.charset,
            cursorclass = self.cursorclass
        )
        return self.conn

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()
        if exc_val:
            raise
            
db = DB(
    host = secret_config.host,
    user = secret_config.user,
    password = secret_config.password,
    db = secret_config.db
)

if __name__ == '__main__':
    log_name = 'logs.txt'
    f = open(log_name,'w')
    f.close()
    print('Файл логов создан')

telebot_logger = logging.getLogger('telebot')
mysql_info = logging.getLogger('mysql')
main_info = logging.getLogger('main_info')
report_info = logging.getLogger('reports')
print('Список логгеров создан')

logging.basicConfig(
                    format='%(filename)s [LINE:%(lineno)-3d]# %(levelname)-8s - %(name)-9s [%(asctime)s] - %(message)-50s ',
                    datefmt='%m/%d/%Y %I:%M:%S %p',
                    filename = 'logs.txt',
                    level = logging.INFO
                    )


def replacer(text):
    text_list = list(text)
    for i in range(len(text)):
        if text_list[i] in config.restricted_characters:
            text_list[i] = config.restricted_characters_replace[text_list[i]]
    return ''.join(text_list)



def register_admins(chat_id):
    admins = []
    chat_info = bot.get_chat(chat_id)
    chat = {
        'chat_id': chat_id,
        'title': chat_info.title
    }
    chat_admins = bot.get_chat_administrators(chat_id)
    print('Найдено {} администраторов. Ориентировочное время регистрации {} сек'.format(len(chat_admins), len(chat_admins)/5))
    counter = 0
    for i in chat_admins:
        counter += 1
        print('Зарегистрировано {}/{} администраторов. Чат: {}'.format(counter, len(chat_admins), chat_info.title))
        try:
            register_new_user(i.user, 'ru')
            if i.user.is_bot == False:
                user_settings = ujson.loads(get_user_param(i.user.id, 'settings'))
                checker = False
                for a in user_settings['admined_groups']:
                    if a['chat_id'] == chat_id:
                        checker = True
                        a['title'] = chat_info.title
                if not checker:
                    user_settings['admined_groups'].append(chat)
                change_user_param(i.user.id, 'settings', ujson.dumps(user_settings))
            admin = {
                'user_id': i.user.id,
                'first_name': i.user.first_name,
                'second_name': i.user.last_name,
                'status': i.status
            }
            admins.append(admin)
            time.sleep(0.2)
        except Exception as e:
            print(e)
    curr_settings = get_group_params(chat_id)
    curr_settings['admins'] = admins
    change_group_params(chat_id, ujson.dumps(curr_settings))
    print(admins)

def ban_sticker(msg, sticker_id):
    """
    Банит стикер\n
    :param msg:\n
    :param sticker_id:\n
    """
    with DataConn(db) as conn:
        curs = conn.cursor()
        sql = 'SELECT * FROM `banned_stickers` WHERE `chat_id` = %s AND `sticker_id` = %s'
        curs.execute(sql, (msg.chat.id, sticker_id))
        res = curs.fetchone()
        if res is None:
            sql = 'INSERT INTO `banned_stickers`(`chat_id`, `chat_name`, `sticker_id`, `ban_time`) VALUES (%s, %s, %s, %s)'
            try:
                curs.execute(sql, (msg.chat.id, msg.chat.title, sticker_id, int(time.time())))
                conn.commit()
            except Exception as e:
                print(sql)
                print(e)
        else:
            if res != msg.chat.title:
                sql = 'SELECT * FROM `banned_stickers` WHERE `chat_id` = %s'
                curs.execute(sql, (msg.chat.id, ))
                res = curs.fetchall()
                for i in res:
                    sql = 'UPDATE `banned_stickers` SET `chat_name` = %s WHERE `chat_id` = %s'
                    curs.execute(sql, (msg.chat.title, msg.chat.id))
                    conn.commit()

def unban_sticker(msg, sticker_id):
    """
    Разбанивает стикер\n
    :param msg:\n
    :param sticker_id:\n
    """
    with DataConn(db) as conn:
        curs = conn.cursor()
        sql = 'SELECT * FROM `banned_stickers` WHERE `chat_id` = %s and `sticker_id` = %s'
        curs.execute(sql, (msg.chat.id, sticker_id))
        res = curs.fetchone()
        if res is not None:
            sql = 'DELETE FROM `banned_stickers` WHERE `chat_id` = %s and `sticker_id` = %s'
            curs.execute(sql, (msg.chat.id, sticker_id))
            conn.commit()
            return True
        else:
            return False

def get_creator(chat_obj):
    """
    Возвращает объект создателя чата\n
    :param msg:\n
    """
    creator = bot.get_chat_administrators(chat_obj.id)[0].user
    for i in bot.get_chat_administrators(chat_obj.id):
        if i.status == 'creator':
            creator = i.user
    return creator

def register_new_user(user_obj, lang):
    """
    Регистрирует нового пользователя\n
    :param user_obj:\n
    :param lang:\n
    """
    with DataConn(db) as conn:
        curs = conn.cursor()
        sql = 'SELECT * FROM `users` WHERE `user_id` = %s'
        curs.execute(sql, (user_obj.id, ))
        res = curs.fetchone()
        sec_name = 'None'
        try:
            sec_name = user_obj.second_name
        except Exception as e:
            sec_name = 'None'
            logging.error(e)
        if res is None:
            sql = 'INSERT INTO `users` (`user_id`, `registration_time`, `first_name`, `second_name`, `settings`) VALUES (%s, %s, %s, %s, %s, %s)'
            settings = config.default_user_settings
            settings['language'] = lang
            curs.execute(sql, (user_obj.id, int(time.time()), user_obj.first_name, sec_name, ujson.dumps(settings)))
            conn.commit()
            utils.notify_new_user(user_obj, lang)
        else:
            curr_settings = ujson.loads(get_user_param(user_obj.id, 'settings'))
            curr_settings['language'] = lang
            change_user_param(user_obj.id, 'settings', ujson.dumps(curr_settings))

def change_user_param(user_id, key, value):
    with DataConn(db) as conn:
        curs = conn.cursor()
        sql = 'UPDATE `users` SET `{key}` = %s WHERE `user_id` = %s'.format(key = key)
        curs.execute(sql, (value, user_id))
        conn.commit()
            
def get_bot_settings(token):
    with DataConn(db) as conn:
        curs = conn.cursor()
        sql = 'SELECT `settings` FROM `bot_settings` WHERE `token` = %s'
        curs.execute(sql, (token, ))
        r = curs.fetchone()
        return r['settings']
            
def change_bot_settings(token, new_settings):
    with DataConn(db) as conn:
        curs = conn.cursor()
        sql = 'UPDATE `bot_settings` SET `settings` = %s WHERE `token` = %s'
        curs.execute(sql, (new_settings, token))
        conn.commit()
            
def register_new_chat(chat_obj):
    """
    Регистрирует новый чат\n
    :param msg:\n
    """
    with DataConn(db) as conn:
        curs = conn.cursor()
        sql = 'SELECT * FROM chats WHERE `chat_id` = %s'
        curs.execute(sql, (chat_obj.id, ))
        res = curs.fetchone()
        if res is None:
            creator = get_creator(chat_obj)
            sql = 'INSERT INTO `chats` (`chat_id`, `chat_name`, `creator_name`, `creator_id`, `chat_members_count`, `registration_time`, `settings`) VALUES (%s, %s, %s, %s, %s, %s, %s)'
            try:
                curs.execute(sql, (chat_obj.id, chat_obj.title, creator.first_name, creator.id, bot.get_chat_members_count(chat_obj.id), int(time.time()), ujson.dumps(config.default_group_settings)))
                conn.commit()
                s = ''
                for i in bot.get_chat_administrators(chat_obj.id):
                    print(s)
                    s = s + '<a href="tg://user?id={user_id}">{user_name}</a> '.format(user_id = i.user.id, user_name = i.user.first_name)
                
                bot.send_message(
                    chat_obj.id,
                    text.group_commands['ru']['registration'].format(admins = s),
                    parse_mode = 'HTML'
                )
            except Exception as e:
                logging.error('error: {}'.format(e))
                logging.error(sql)
            utils.notify_new_chat(chat_obj)
            t = Thread(target = register_admins, args = (chat_obj.id, ))
            t.start()
            t.join()

def get_users_count():
    """
    Возвращает количество пользователей в базе\n
    """
    with DataConn(db) as conn:
        curs = conn.cursor()
        sql = 'SELECT COUNT(`user_id`) FROM `users`'
        curs.execute(sql)
        res = curs.fetchone()
        return res['COUNT(`user_id`)']

def get_unblocked_chats_count():
    with DataConn(db) as conn:
        curs = conn.cursor()
        sql = 'SELECT COUNT(`chat_id`) FROM `chats` WHERE `is_blocked` = 1'
        curs.execute(sql)
        res = curs.fetchone()
        return res['COUNT(`chat_id`)']
        
def get_unblocked_users_count():
    with DataConn(db) as conn:
        curs = conn.cursor()
        sql = 'SELECT COUNT(`user_id`) FROM `users` WHERE `is_blocked` = 0'
        curs.execute(sql)
        res = curs.fetchone()
        return res['COUNT(`user_id`)']
        
def get_chats_count():
    """
    Возвращает количество чатов в базе\n
    """
    with DataConn(db) as conn:
        curs = conn.cursor()
        sql = 'SELECT COUNT(`chat_id`) FROM `chats`'
        curs.execute(sql)
        res = curs.fetchone()
        return res['COUNT(`chat_id`)']

def get_user_param(user_id, column):
    """
    Возвращает определенный параметр пользовательских настроек
    :param msg:
    :param column:
    """
    with DataConn(db) as conn:
        curs = conn.cursor()
        sql = 'SELECT * FROM `users` WHERE `user_id` = %s'.format(
            column = column
        )
        curs.execute(sql, (user_id, ))
        res = curs.fetchone()
        try:
            return res[column]
        except Exception as e:
            register_new_user(bot.get_chat_member(-1001236256304, user_id).user, 'ru')
            change_user_param(user_id, 'settings', ujson.dumps(config.default_user_settings))
            res['settings'] = ujson.dumps(default_user_settings)
            return res[column]
            

def get_group_params(chat_id):
    res = cache_worker.group_info_search_in_cache(chat_id)
    if not res['result']:
        with DataConn(db) as conn:
            curs = conn.cursor()
            sql = 'SELECT * FROM `chats` WHERE `chat_id` = %s'
            curs.execute(sql, (chat_id, ))
            res = curs.fetchone()
            try:
                ujson.loads(res['settings'])['get_notifications']
                cache_worker.group_info_update_cache(chat_id, res['settings'])
                return ujson.loads(res['settings'])
            except Exception as e:
                register_new_chat(bot.get_chat(chat_id))
                change_group_params(chat_id, ujson.dumps(config.default_group_settings))
                bot.send_message(
                    chat_id,
                    text.group_commands['ru']['errors']['db_error']['got_error']
                )
                bot.send_message(   
                    chat_id,
                    text.group_commands['ru']['errors']['db_error']['finshed']
                )
                return ujson.loads(res['settings'])['get_notifications']
    else:
        return ujson.loads(res['text'])
        
def change_group_params(chat_id, new_params):
    with DataConn(db) as conn:
        curs = conn.cursor()
        sql = 'UPDATE `chats` SET `settings` = %s WHERE `chat_id` = %s'
        try:
            curs.execute(sql, (new_params, chat_id))
            conn.commit()
            cache_worker.group_info_update_cache(chat_id, new_params)
        except Exception as e:
            print(e)
            print(sql)


def is_user_new(msg):
    with DataConn(db) as conn:
        curs = conn.cursor()
        sql = 'SELECT * FROM users WHERE `user_id` = %s'
        curs.execute(sql, (msg.from_user.id, ))
        r = curs.fetchone()
        if r is None:
            res = True
        else:
            res = False
        return res

def check_sticker(sticker_id, chat_id):
    with DataConn(db) as conn:
        curs = conn.cursor()
        sql = 'SELECT * FROM `banned_stickers` WHERE `sticker_id` = %s AND `chat_id` = %s'
        curs.execute(sql, (sticker_id, chat_id))
        r = curs.fetchone()
        if r is None:
            return False
        else:
            return True

def get_warns(user_id, chat_id):
    with DataConn(db) as conn:
        curs = conn.cursor()
        sql = 'SELECT * FROM `warns` WHERE `user_id` = %s AND `chat_id` = %s'
        curs.execute(sql, (user_id, chat_id))
        res = curs.fetchone()
        if res is None:
            sql = 'INSERT INTO `warns`(`user_id`, `chat_id`, `warns`) VALUES (%s, %s, %s)'
            warns = 0
            curs.execute(sql, (user_id, chat_id, warns))
            conn.commit()
        else:
            warns = int(res['warns'])
        return warns

def new_warn(user_id, chat_id):
    with DataConn(db) as conn:
        curs = conn.cursor()
        warns = get_warns(user_id, chat_id)
        warns += 1
        set_warns(user_id, chat_id, warns)

def zeroing_warns(user_id, chat_id):
    set_warns(user_id, chat_id, 0)

def set_warns(user_id, chat_id, warns):
    with DataConn(db) as conn:
        curs = conn.cursor()
        sql = 'UPDATE `warns` SET `warns` = %s WHERE `user_id` = %s AND `chat_id` = %s'
        curs.execute(sql, (warns, user_id, chat_id))
        conn.commit()

def get_chats():
    with DataConn(db) as conn:
        curs = conn.cursor()
        sql = 'SELECT * FROM `chats` ORDER BY `registration_time` ASC'
        curs.execute(sql)
        res = curs.fetchall()
        return res

def get_users():
    with DataConn(db) as conn:
        curs = conn.cursor()
        sql = 'SELECT * FROM `users` ORDER BY `registration_time` ASC'
        curs.execute(sql)
        res = curs.fetchall()
        return res
        
def get_all():
    all_chats = []
    all_chats.extend(get_chats())
    all_chats.extend(get_users())
    return all_chats

def replacerr(text):
    text_list = list(text) 
    for idx, word in enumerate(text):
        if word in config.restricted_characters:
            text_list[idx] = config.restricted_characters_replace[word]
    return ''.join(text_list)

def escape_string(value):
    # value = value.replace('\\', r'\\\\')
    # value = value.replace('\0', r'\\0')
    # value = value.replace('\n', r'\\n')
    # value = value.replace('\r', r'\\r')
    # value = value.replace('\032', r'\\Z')
    value = value.replace("'", r"\'")
    value = value.replace('"', r'\"')
    return value

def update_stats_bot(count):
    with DataConn(db) as conn:
        curs = conn.cursor()
        sql = 'INSERT INTO `stats` (`amount`, `check_time`) VALUES (%s, %s)'
        curs.execute(sql, (count, int(time.time())))
        conn.commit()

def delete_pending():
    with DataConn(db) as conn:
        curs = conn.cursor()
        sql = 'DELETE * FROM `stats`'
        curs.execute(sql)
        conn.commit()

def check_global_ban(user_id):
    with DataConn(db) as conn:
        curs = conn.cursor()
        sql = 'SELECT * FROM `global_bans` WHERE `user_id` = %s'
        curs.execute(sql, (user_id, ))
        res = curs.fetchone()
        if res is None:
            return False
        else:
            return True

def global_ban(user_id):
    with DataConn(db) as conn:
        if not check_global_ban(user_id):
            curs = conn.cursor()
            sql = 'INSERT INTO `global_bans` (`user_id`) VALUES  (%s)'
            curs.execute(sql, (user_id, ))
            conn.commit()

def global_unban(user_id):
    with DataConn(db) as conn:
        curs = conn.cursor()
        sql = 'DELETE FROM `global_bans` WHERE `user_id` = %s'
        curs.execute(sql, (user_id, ))
        conn.commit()

def new_update(msg, end_time):
    user_id = msg.from_user.id
    chat_id = msg.chat.id
    try:
        new_content(msg, end_time)
    except Exception as e:
        logging.error(e)
    try:
        update_chat_stats(msg)
    except Exception as e:
        logging.error(e)
    try:
        update_user_stats(msg)
    except Exception as e:
        logging.error(e)

def update_user_stats(msg):
    user_id = msg.from_user.id
    chat_id = msg.chat.id
    chat_name = msg.chat.title
    user_name = msg.from_user.first_name
    with DataConn(db) as conn:
        curs = conn.cursor()
        current_updates = get_user_messages_count(user_id, chat_id)
        sql = 'SELECT * FROM `most_active_users` WHERE `user_id` = %s AND `chat_id` = %s'
        curs.execute(sql, (user_id, chat_id))
        res = curs.fetchone()
        if res is None:
            sql = 'INSERT INTO `most_active_users` (`user_id`, `user_name`, `chat_id`, `chat_name`, `amount`) VALUES (%s, %s, %s, %s, %s)'
            curs.execute(sql, (user_id, user_name, chat_id, chat_name, current_updates))
            conn.commit()
        else:
            sql = 'UPDATE `most_active_users` SET `user_name` = %s, `amount` = %s WHERE `user_id` = %s AND `chat_id` = %s'
            curs.execute(sql, (user_name, current_updates, user_id, chat_id))
            sql = 'UPDATE `most_active_users` SET `chat_name` = %s WHERE `chat_id` = %s'
            curs.execute(sql, (chat_name, chat_id))
            conn.commit()
        

def get_user_messages_count(user_id, chat_id):
    with DataConn(db) as conn:
        curs = conn.cursor()
        sql = 'SELECT `amount` FROM `most_active_users` WHERE `chat_id` = %s AND `user_id` = %s'
        curs.execute(sql, (chat_id, user_id))
        res = curs.fetchone()
        return res['amount']

def update_chat_stats(msg):
    with DataConn(db) as conn:
        curs = conn.cursor()
        current_updates = get_chat_updates_count(msg.chat.id)
        sql = 'SELECT * FROM `most_popular_chats` WHERE `chat_id` = %s'
        curs.execute(sql, (msg.chat.id, ))
        res = curs.fetchone()
        if res is None:
            sql = 'INSERT INTO `most_popular_chats` (`updates_count`, `chat_id`, `chat_name`, `last_update`) VALUES (%s, %s, %s, %s)'
            curs.execute(sql, (current_updates, msg.chat.id, msg.chat.title, msg.date))
            try:
                conn.commit()
            except Exception as e:
                logging.error(e)
                logging.error(sql)
        else:
            sql = 'UPDATE `most_popular_chats` SET `updates_count` = %s, `chat_name` = %s, `last_update` = %s WHERE `chat_id` = %s'
            curs.execute(sql, (current_updates, msg.chat.title, msg.date, msg.chat.id))
            try:
                conn.commit()
            except Exception as e:
                logging.error(e)
                logging.error(sql)

def get_chat_updates_count(chat_id):    
    with DataConn(db) as conn:
        curs = conn.cursor()
        sql = 'SELECT `updates_count` FROM `most_popular_chats` WHERE `chat_id` = %s'
        curs.execute(sql, (chat_id, ))
        res = curs.fetchone()
        return int(res['updates_count'])

def get_file_size(msg):
    res = 0
    if msg.content_type == 'audio':
        res = msg.audio.file_size
    elif msg.content_type == 'document':
        res = msg.document.file_size
    elif msg.content_type == 'photo':
        res = msg.photo[-1].file_size
    elif msg.content_type == 'sticker':
        res = msg.sticker.file_size
    elif msg.content_type == 'video':
        res = msg.audio.file_size
    elif msg.content_type == 'video_note':
        res = msg.audio.file_size
    elif msg.content_type == 'voice':
        res = msg.voice.file_size
    return res

def get_file_id(msg):
    res = ''
    if msg.content_type == 'audio':
        res = msg.audio.file_id
    elif msg.content_type == 'document':
        res = msg.document.file_id
    elif msg.content_type == 'photo':
        res = msg.photo[-1].file_id
    elif msg.content_type == 'sticker':
        res = msg.sticker.file_id
    elif msg.content_type == 'video':
        res = msg.audio.file_id
    elif msg.content_type == 'video_note':
        res = msg.audio.file_id
    elif msg.content_type == 'voice':
        res = msg.voice.file_idfile_id
    return res


def new_message(msg, end_time):
    user_id = msg.from_user.id
    chat_id = msg.chat.id
    with DataConn(db) as conn:
        curs = conn.cursor()
        sql = 'INSERT INTO `proceeded_messages` (`user_id`, `chat_id`, `msg_time`, `used_time`, `proceeded_at`, `content_type`) VALUES (%s, %s, %s, %s, %s, %s)'
        curs.execute(sql, (user_id, chat_id, msg.date, end_time*1000, int(time.time()), msg.content_type))
        conn.commit()

def new_content(msg, end_time):
    new_message(msg, end_time)
    if msg.content_type == 'text':
        try:
            with DataConn(db) as conn:
                curs = conn.cursor()
                sql = 'INSERT INTO `text` (`user_id`, `chat_id`, `text`, `msg_date`, `message_id`) VALUES (%s, %s, %s, %s, %s)'
                curs.execute(sql, (msg.from_user.id, msg.chat.id, msg.text, msg.date, msg.message_id))
                conn.commit()
        except Exception as e:
            logging.error(e)
            logging.error(sql)
    else:
        try:
            with DataConn(db) as conn:
                curs = conn.cursor()
                sql = 'INSERT INTO `{cont_type}` (`user_id`, `chat_id`, `file_id`, `file_size`) VALUES (%s, %s, %s, %s)'.format(
                    cont_type = msg.content_type
                )
                curs.execute(sql, (msg.from_user.id, msg.chat.id, get_file_id(msg), get_file_size(msg)))
                conn.commit()
        except Exception as e:
            logging.error(e)
            logging.error(sql)

def get_chat_users(chat_id, limit):
    with DataConn(db) as conn:
        curs = conn.cursor()
        sql = 'SELECT * FROM `most_active_users` WHERE `chat_id` = %s ORDER BY `amount` DESC LIMIT {limit}'.format(limit = limit)
        curs.execute(sql, (chat_id, ))
        r = curs.fetchall()
        return r

def get_chat_users_count(chat_id):
    with DataConn(db) as conn:
        curs = conn.cursor()
        sql = 'SELECT COUNT(`user_id`) FROM `most_active_users` WHERE `chat_id` = %s ORDER BY `amount` DESC'
        curs.execute(sql, (chat_id, ))
        r = curs.fetchone()
        return r['COUNT(`user_id`)']

def new_voteban(chat_id, chat_name, victim_id, victim_name, vote_hash):
    with DataConn(db) as conn:
        curs = conn.cursor()
        sql = 'INSERT INTO `votebans`(`vote_hash`, `victim_id`, `victim_name`, `chat_id`, `chat_name`, `votes_count`, `votes_limit`, `started_at`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)'
        curs.execute(sql, (vote_hash, victim_id, victim_name, chat_id, chat_name, 0, utils.get_voteban_limit(chat_id), int(time.time())))
        conn.commit()

def update_voteban(vote_hash):
    with DataConn(db) as conn:
        curs = conn.cursor()
        curr_votes = get_voteban_votes_count(vote_hash)
        utils.set_voteban_votes_count(vote_hash, curr_votes)
        if utils.get_voteban_limit():
            pass

def get_voteban_votes_count(vote_hash):
    with DataConn(db) as conn:
        curs = conn.cursor()
        sql = 'SELECT COUNT(`vote_id`) FROM `voteban` WHERE `vote_id` = %s'
        curs.execute(sql, (vote_hash, ))
        r = curs.fetchone()
        return r['COUNT(`vote_id`)']

def set_voteban_votes_count(vote_hash, votes_count):
    with DataConn(db) as conn:
        curs = conn.cursor()
        sql = 'UPDATE `votebans SET `votes_count` = %s WHERE `vote_hash` = %s'
        curs.execute(sql, (votes_count, vote_hash))
        conn.commit()

def get_voteban_info(vote_hash):
    with DataConn(db) as conn:
        curs = conn.cursor()
        sql = 'SELECT * FROM `votebans` WHERE `vote_hash` = %s'
        curs.execute(sql, (vote_hash, ))
        r = curs.fetchone()
        return r

def set_voteban_info(column, state, vote_hash):
    with DataConn(db) as conn:
        curs = conn.cursor()
        sql = 'UPDATE `votebans` SET `{column}` = %s WHERE `vote_hash` = %s'.format(column = column)
        curs.execute(state, vote_hash)
        conn.commit()

def new_chat_invite(chat_id, inviter, invited, joined_at):
    with DataConn(db) as conn:
        cursor = conn.cursor()
        sql = 'INSERT INTO `inviters` (`chat_id`, `inviter`, `invited`, `joined_at`) VALUES (%s, %s, %s, %s)'
        cursor.execute(sql, (chat_id, inviter, invited, joined_at))
        conn.commit()

def get_top_inviters(chat_id, limit):
    with DataConn(db) as conn:
        cursor = conn.cursor()
        sql = 'SELECT COUNT(`inviter`), `inviter` FROM `inviters` WHERE `chat_id` = %s ORDER BY COUNT(`inviter`) ASC LIMIT %s'
        cursor.execute(sql, (chat_id, limit))
        return cursor.fetchall()