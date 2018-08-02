# coding: utf8

import datetime
import logging
import random
import re
import ssl
import subprocess
import threading
import time
from multiprocessing import Process as Thread

import telebot
from aiohttp import web
from telebot import types

import api
import cherrypy
import config
import secret_config
import text
import ujson
import utils

WEBHOOK_HOST = utils.get_my_ip()
WEBHOOK_PORT = 8443  # 443, 80, 88 или 8443 (порт должен быть открыт!)
# На некоторых серверах придется указывать такой же IP, что и выше
WEBHOOK_LISTEN = '0.0.0.0'

WEBHOOK_SSL_CERT = './webhook_cert.pem'  # Путь к сертификату
WEBHOOK_SSL_PRIV = './webhook_pkey.pem'  # Путь к приватному ключу

WEBHOOK_URL_BASE = "https://%s:%s" % (WEBHOOK_HOST, WEBHOOK_PORT)
WEBHOOK_URL_PATH = "/%s/" % (secret_config.token)

start_time = int(time.time())

bot = telebot.TeleBot(token = secret_config.token)
my_info = bot.get_me()
telebot_logger = logging.getLogger('telebot')
sqlite_info = logging.getLogger('sqlite')
main_info = logging.getLogger('main_info')
report_info = logging.getLogger('reports')

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
                    level = logging.INFO
                    )

app = web.Application()

t = Thread(target = utils.check_deleting_queue)
t.start()

async def handle(request):
    if request.match_info.get('token') == bot.token:
        request_body_dict = await request.json()
        update = telebot.types.Update.de_json(request_body_dict)
        bot.process_new_updates([update])
        return web.Response()
    else:
        return web.Response(status=403)

app.router.add_post('/{token}/', handle) 

def create_user_language_keyboard():
    lang_keyboard = types.InlineKeyboardMarkup()
    for i in config.languages:
        lang_keyboard.add(types.InlineKeyboardButton(text = i['title'], callback_data = 'lang::{lang_code}'.format(lang_code = i['code'])))
    return lang_keyboard

def group_setting(chat_id):
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    curr_settings = api.get_group_params(chat_id)
    btn = types.InlineKeyboardButton(text = 'Принимать рассылки{}'.format(config.settings_statuses[curr_settings['get_notifications']]), callback_data = 'get_notifications::{chat_id}'.format(chat_id = chat_id))
    keyboard.add(btn)
    btn = types.InlineKeyboardButton(text = 'Удалять ссылки{}'.format(config.settings_statuses[curr_settings['deletions']['url']]), callback_data = 'del_url::{chat_id}'.format(chat_id = chat_id))
    keyboard.add(btn)
    btn = types.InlineKeyboardButton(text = 'Удалять системные сообщения{}'.format(config.settings_statuses[curr_settings['deletions']['system']]), callback_data = 'del_system::{chat_id}'.format(chat_id = chat_id))
    keyboard.add(btn)
    btn = types.InlineKeyboardButton(text = 'Исключать ботов{}'.format(config.settings_statuses[curr_settings['kick_bots']]), callback_data='kick_bots::{chat_id}'.format(chat_id = chat_id))
    keyboard.add(btn)
    btn = types.InlineKeyboardButton(text = 'Фильтры', callback_data='deletions_settings::{chat_id}'.format(chat_id = chat_id))
    keyboard.add(btn)
    btn = types.InlineKeyboardButton(text = 'Ограничения новых пользователей', callback_data = 'new_users_restrictions::{chat_id}'.format(chat_id = chat_id))
    keyboard.add(btn)
    btn = types.InlineKeyboardButton(text = 'Настройка предупреждений', callback_data = 'warns_settings::{chat_id}'.format(chat_id = chat_id))
    keyboard.add(btn)
    btn = types.InlineKeyboardButton(text = 'Настройка приветствий', callback_data = 'welcome_settings::{chat_id}'.format(chat_id = chat_id))
    keyboard.add(btn)
    btn = types.InlineKeyboardButton(text = 'Получить дамп настроек', callback_data = 'get_settings_json::{chat_id}'.format(chat_id = chat_id))
    keyboard.add(btn)
    btn = types.InlineKeyboardButton(text = 'Получить топ инвайтеров', callback_data = 'get_chat_refs::{chat_id}'.format(chat_id = chat_id))
    keyboard.add(btn) 
    keyboard.add(types.InlineKeyboardButton(text = 'К списку групп', callback_data = 'to_groups_list'))
    return keyboard

def welcome_settings_kb(chat_id):
    kb = types.InlineKeyboardMarkup(row_width = 4)
    curr_settings = api.get_group_params(chat_id)
    btn = types.InlineKeyboardButton(text = 'Отправлять приветствие в чат: {}'.format(config.settings_statuses[curr_settings['greeting']['is_enabled']]), callback_data = 'welcome_state::{chat_id}'.format(chat_id = chat_id))
    kb.add(btn)
    btn = types.InlineKeyboardButton(text = 'Задержка перед удалением приветствия: {} сек.'.format(curr_settings['greeting']['delete_timer']), callback_data = 'welcome_get::{chat_id}'.format(chat_id = chat_id))
    kb.add(btn)
    btn1 = types.InlineKeyboardButton(text = '➖10', callback_data = 'welcome_timer_-10::{chat_id}'.format(chat_id = chat_id))
    btn2 = types.InlineKeyboardButton(text = '➖5', callback_data = 'welcome_timer_-5::{chat_id}'.format(chat_id = chat_id))
    btn3 = types.InlineKeyboardButton(text = '➕5', callback_data = 'welcome_timer_+5::{chat_id}'.format(chat_id = chat_id))
    btn4 = types.InlineKeyboardButton(text = '➕10', callback_data = 'welcome_timer_+10::{chat_id}'.format(chat_id = chat_id))
    kb.add(btn1, btn2, btn3, btn4)
    btn = types.InlineKeyboardButton(text = 'Показать приветствие', callback_data = 'welcome_get::{chat_id}'.format(chat_id = chat_id))
    kb.add(btn)
    btn = types.InlineKeyboardButton(text = 'Назад', callback_data='to_group_settings_menu::{chat_id}'.format(chat_id = chat_id))
    kb.add(btn)
    return kb


def new_users_restrictions_kb(chat_id):
    keyboard = types.InlineKeyboardMarkup(row_width = 4)
    curr_settings = api.get_group_params(chat_id)
    btn = types.InlineKeyboardButton(text = 'Автоматический read-only на {} час - {}'.format(curr_settings['restrictions']['for_time'], config.settings_statuses[curr_settings['restrictions']['read_only']]), callback_data = 'read_only::{chat_id}'.format(chat_id = chat_id))
    keyboard.add(btn)
    btn1 = types.InlineKeyboardButton(text = '➖2', callback_data = 'time_ro_-2::{chat_id}'.format(chat_id = chat_id))
    btn2 = types.InlineKeyboardButton(text = '➖1', callback_data = 'time_ro_-1::{chat_id}'.format(chat_id = chat_id))
    btn3 = types.InlineKeyboardButton(text = '➕1', callback_data = 'time_ro_+1::{chat_id}'.format(chat_id = chat_id))
    btn4 = types.InlineKeyboardButton(text = '➕2', callback_data = 'time_ro_+2::{chat_id}'.format(chat_id = chat_id))
    btn5 = types.InlineKeyboardButton(text = 'Навсегда', callback_data = 'time_ro_+10000::{chat_id}'.format(chat_id = chat_id))
    btn6 = types.InlineKeyboardButton(text = 'Сброс', callback_data = 'time_ro_-10000000000::{chat_id}'.format(chat_id = chat_id))
    keyboard.add(btn1, btn2, btn3, btn4)
    keyboard.add(btn5, btn6)
    btn = types.InlineKeyboardButton(text = 'Снятие ограничений разрешено для: {}'.format(config.new_users[curr_settings['restrictions']['admins_only']]), callback_data = 'new_restrictions_admins_only_{state}::{chat_id}'.format(state = config.settings_states[curr_settings['restrictions']['admins_only']], chat_id = chat_id))
    keyboard.add(btn)
    btn = types.InlineKeyboardButton(text = 'Назад', callback_data='to_group_settings_menu::{chat_id}'.format(chat_id = chat_id))
    keyboard.add(btn)
    return keyboard

def warns_settings_kb(chat_id):
    keyboard = types.InlineKeyboardMarkup(row_width = 4)
    curr_settings = api.get_group_params(chat_id)
    btn = types.InlineKeyboardButton(text = 'Максимальное количество исключений: {}'.format(curr_settings['warns']['count']), callback_data = 'empty_callback::{chat_id}'.format(chat_id = chat_id))
    keyboard.add(btn)
    btn1 = types.InlineKeyboardButton(text = '➖2', callback_data = 'warns_count_-2::{chat_id}'.format(chat_id = chat_id))
    btn2 = types.InlineKeyboardButton(text = '➖1', callback_data = 'warns_count_-1::{chat_id}'.format(chat_id = chat_id))
    btn3 = types.InlineKeyboardButton(text = '➕1', callback_data = 'warns_count_+1::{chat_id}'.format(chat_id = chat_id))
    btn4 = types.InlineKeyboardButton(text = '➕2', callback_data = 'warns_count_+2::{chat_id}'.format(chat_id = chat_id))
    
    keyboard.add(btn1, btn2, btn3, btn4)
    btn = types.InlineKeyboardButton(text = 'Действие при максимальном кол-ве варнов: {}'.format(config.warns_states[curr_settings['warns']['action']]), callback_data='empty_callback::{chat_id}'.format(chat_id = chat_id))
    keyboard.add(btn)
    btn1 = types.InlineKeyboardButton(text = 'Ничего', callback_data = 'warns_action_0::{chat_id}'.format(chat_id = chat_id))
    btn2 = types.InlineKeyboardButton(text = 'Кик', callback_data = 'warns_action_1::{chat_id}'.format(chat_id = chat_id))
    btn3 = types.InlineKeyboardButton(text = 'Бан', callback_data = 'warns_action_2::{chat_id}'.format(chat_id = chat_id))
    btn4 = types.InlineKeyboardButton(text = 'Read-only на сутки', callback_data = 'warns_action_3::{chat_id}'.format(chat_id = chat_id))
    keyboard.add(btn1, btn2, btn3, btn4)
    btn = types.InlineKeyboardButton(text = 'Назад', callback_data='to_group_settings_menu::{chat_id}'.format(chat_id = chat_id))
    keyboard.add(btn)
    return keyboard

def remove_warns_kb(user_id):
    kb = types.InlineKeyboardMarkup(row_width=1)
    btn = types.InlineKeyboardButton(text = 'Удалить предупреждения', callback_data = 'delete_warns::{user_id}'.format(user_id = user_id))
    kb.add(btn)
    return kb

def unban_new_user_kb(msg):
    kb = types.InlineKeyboardMarkup(row_width=1)
    btn = types.InlineKeyboardButton(text = 'Разблокировать', callback_data = 'unban_new_user::{chat_id}::{user_id}'.format(user_id = msg.new_chat_member.id, chat_id = msg.chat.id))
    kb.add(btn)
    return kb

def user_settings_main_menu(msg):
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    curr_settings = api.get_user_param(msg.chat.id, 'settings')
    btn = types.InlineKeyboardButton(text = 'Принимать рассылки{}'.format(config.settings_statuses['get_notifications']), callback_data='get_notifications')
    keyboard.add(btn)
    btn = types.InlineKeyboardButton(text = 'Выбор языка'.format(config.settings_statuses['get_notifications']), callback_data='open_lang_menu')
    keyboard.add(btn)
    return keyboard

def delete_settings(chat_id):
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    curr_settings = api.get_group_params(chat_id)
    for cont_type in config.available_attachments:
        btn = types.InlineKeyboardButton(text=config.available_attachments_str[cont_type].format(config.settings_statuses[curr_settings['deletions']['files'][cont_type]]), callback_data='delete::{content_type}::{chat_id}'.format(content_type = cont_type, chat_id = chat_id))
        keyboard.add(btn)
    btn = types.InlineKeyboardButton(text = 'Переключить все', callback_data = 'change_all::{chat_id}'.format(chat_id = chat_id))
    keyboard.add(btn)
    btn = types.InlineKeyboardButton(text = 'Назад', callback_data='to_group_settings_menu::{chat_id}'.format(chat_id = chat_id))
    keyboard.add(btn)
    return keyboard

def generate_leave_kb(msg):
    chat_id = msg.chat.id
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    btn = types.InlineKeyboardButton(text = 'Да, выйди из чата', callback_data='leave_cancel::{chat_id}'.format(chat_id = chat_id))
    keyboard.add(btn)
    btn = types.InlineKeyboardButton(text = 'Нет, останься', callback_data='leave_confirm::{chat_id}'.format(chat_id = chat_id))
    keyboard.add(btn)
    return keyboard

def generate_user_menu_kb(user_id):
    kb = types.InlineKeyboardMarkup(row_width = 1)
    btn1 = types.InlineKeyboardButton(text = 'Мои чаты', callback_data = 'my_chats')
    btn2 = types.InlineKeyboardButton(text = 'Изменить язык', callback_data = 'change_lang')
    kb.add(btn1, btn2)
    if utils.check_super_user(user_id):
        kb.add(types.InlineKeyboardButton(text = 'Админка бота', callback_data = 'admin_menu'))
    return kb
    
def generate_admin_menu_kb():
    kb = types.InlineKeyboardMarkup(row_width = 2)
    btn1 = types.InlineKeyboardButton(text = 'Рассылка', callback_data = 'broadcast_menu')
    btn2 = types.InlineKeyboardButton(text = 'Статистика', callback_data = 'stats_menu')
    kb.add(btn1, btn2)
    kb.add(types.InlineKeyboardButton(text = 'В главное меню', callback_data = 'to_main_menu'))
    return kb
    
def generate_broadcast_vars_menu_kb():
    kb = types.InlineKeyboardMarkup(row_width = 1)
    btn1 = types.InlineKeyboardButton(text = 'Рассылка-проверка', callback_data = 'check_broadcast')
    btn2 = types.InlineKeyboardButton(text = 'Рассылка сообщения', callback_data = 'broadcast_settings')
    kb.add(btn1, btn2)
    kb.add(types.InlineKeyboardButton(text = 'В главное меню', callback_data = 'to_main_menu'))
    return kb

def generate_broadcast_settings_menu_kb():
    kb = types.InlineKeyboardMarkup(row_width = 2)
    btn1 = types.InlineKeyboardButton(text = 'Ввести сообщение', callback_data = 'broadcast_message::input')
    btn2 = types.InlineKeyboardButton(text = 'Просмотреть сообщение', callback_data = 'broadcast_message::show')
    btn3 = types.InlineKeyboardButton(text = 'Начать рассылку', callback_data = 'broadcast_message::start')
    kb.add(btn1, btn2, btn3)
    return kb
    
def generate_broadcast_check_menu_kb():
    kb = types.InlineKeyboardMarkup(row_width = 3)
    curr_settings = ujson.loads(api.get_bot_settings(secret_config.token))
    s = {
        'users': 'пользователи',
        'chats': 'диалоги',
        'all': 'все'
    }
    btn1 = types.InlineKeyboardButton(text = 'Только диалоги', callback_data = 'broadcast_check::users')
    btn2 = types.InlineKeyboardButton(text = 'Только чаты', callback_data = 'broadcast_check::chats')
    btn3 = types.InlineKeyboardButton(text = 'Все', callback_data = 'broadcast_check::all')
    btn4 = types.InlineKeyboardButton(text = 'Сейчас: {}'.format(s[curr_settings['broadcast']['check']['receivers']]), callback_data = 'empty_callback')
    btn5 = types.InlineKeyboardButton(text = 'Начать рассылку', callback_data = 'broadcast_check::start')
    kb.add(btn1, btn2, btn3)
    kb.add(btn4, btn5)
    return kb
    
def generate_user_groups(user_id):
    kb = types.InlineKeyboardMarkup(row_width=2)
    user_settings = ujson.loads(api.get_user_param(user_id, 'settings'))
    btns = []
    for i in user_settings['admined_groups']:
        btn = types.InlineKeyboardButton(text = i['title'], callback_data = 'settings::{chat_id}'.format(chat_id = i['chat_id']))
        btns.append(btn)
    kb.add(*btns)
    kb.add(types.InlineKeyboardButton(text = 'В главное меню', callback_data = 'to_main_menu'))
    return kb
    
@bot.channel_post_handler(content_types=['text'], func = lambda msg: msg.chat.id == secret_config.channel_ID)
def bot_broadcast(msg):
    r = bot.forward_message(secret_config.official_chat, msg.chat.id, msg.message_id)
    bot.pin_chat_message(
        r.chat.id,
        r.message_id
    )

@bot.message_handler(commands =['setlog'], func = lambda msg: 
    msg.chat.type in ['group', 'supergroup'] and
    msg.forward_from_chat is not None and
    utils.check_status(msg.from_user.id, msg.chat.id) and
    not utils.check_log(msg.chat.id)
)
def bot_set_log(msg):
    user_id = msg.from_user.id
    try:
        admins = bot.get_chat_administrators(msg.forward_from_chat.id)
        status1 = False
        status2 = False
        for i in admins:
            if i.user.id == user_id:
                if i.status == 'creator':
                    status1 = True
            if i.user.id == my_info.id:
                status2 = True
        if status1 is True and status2 is True:
            utils.set_log_channel(msg.chat.id, msg.forward_from_chat.id)
        elif status1 is not True:
            bot.send_message(
                msg.chat.id,
                text = text.group_commands[utils.get_group_lang(chat_id)]['log_channel']['confirmation']['errors']['user_is_not_creator']
            )
        elif status2 is not True:
            bot.send_message(
                msg.chat.id,
                text = text.group_commands[utils.get_group_lang(chat_id)]['log_channel']['confirmation']['errors']['bot_is_not_admin']
            )
    except Exception as e:
        print(e)

@bot.message_handler(commands = ['dellog'], func = lambda msg: 
    msg.chat.type in ['group', 'supergroup'] and 
    msg.forward_from_chat is not None and
    utils.check_status(msg.from_user.id, msg.chat.id) and
    msg.forward_from_chat.id == utils.get_log_id(msg.chat.id) and
    utils.check_log(msg.chat.id)
)
def bot_del_log(msg):
    print(1)
    user_id = msg.from_user.id
    try:
        admins = bot.get_chat_administrators(msg.forward_from_chat.id)
        status1 = False
        status2 = False
        for i in admins:
            if i.user.id == user_id:
                if i.status == 'creator':
                    status1 = True
            if i.user.id == my_info.id:
                status2 = True
        if status1 is True and status2 is True:
            utils.remove_log_channel(msg.chat.id)
        elif status1 is not True:
            bot.send_message(
                msg.chat.id,
                text = text.group_commands[utils.get_group_lang(chat_id)]['log_channel']['confirmation']['errors']['user_is_not_creator']
            )
        elif status2 is not True:
            bot.send_message(
                msg.chat.id,
                text = text.group_commands[utils.get_group_lang(chat_id)]['log_channel']['confirmation']['errors']['bot_is_not_admin']
            )
    except Exception as e:
        print(e)

@bot.message_handler(commands = ['infolog'], func = lambda msg: msg.chat.type in ['group', 'supergroup'])
def bot_info_log(msg):
    if utils.check_log(msg.chat.id):
        m = text.group_commands[utils.get_group_lang(msg.chat.id)]['log_channel']['info']['is_on'].format(
            chat_id = utils.get_log_id(msg.chat.id),
            chat_name = bot.get_chat(utils.get_log_id(msg.chat.id)).title
        )
    else:
        m = text.group_commands[utils.get_group_lang(msg.chat.id)]['log_channel']['info']['is_off']
    bot.send_message(
        msg.chat.id,
        m,
        parse_mode = 'HTML'
    )

@bot.message_handler(commands = ['leave'], func = lambda msg: msg.chat.type != 'private' and utils.check_status(msg.from_user.id, msg.chat.id))
def bot_leave(msg):
    bot.send_message(
        msg.chat.id,
        text.group_commands[utils.get_group_lang(msg.chat.id)]['leave']['question'],
        reply_markup = generate_leave_kb(msg),
        parse_mode = 'HTML'
    )  

@bot.message_handler(commands = ['rmkb'], func = lambda msg: msg.chat.type in ['group', 'supergroup'])
def bot_remove_kb(msg):
    kb = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    kb.add(types.KeyboardButton(text='/rmkb'))
    r = bot.send_message(
        msg.chat.id,
        text = text.group_commands[utils.get_group_lang(msg.chat.id)]['remove_keyboard'],
        reply_markup = kb
    )
    bot.delete_message(
        msg.chat.id,
        r.message_id
    )
    bot.delete_message(
        msg.chat.id,
        msg.message_id
    )

@bot.message_handler(commands = ['settings'], func = lambda msg: msg.chat.type == 'supergroup')
def bot_answ(msg):
    start_time = time.time()
    message = msg
    kb = types.InlineKeyboardMarkup()
    
    r = bot.reply_to(
        msg,
        'Настройки отправлены вам в личные сообщения',
    )
    kb.add(types.InlineKeyboardButton(text = 'Удалить', callback_data = 'settings_delete {} {}'.format(msg.message_id, r.message_id)))
    bot.edit_message_reply_markup(
        chat_id = msg.chat.id,
        message_id = r.message_id,
        reply_markup = kb
    )
    bot.send_message(
        msg.from_user.id, 
        '<b>Настройки группы {}</b>'.format(msg.chat.title), 
        reply_markup=group_setting(msg.chat.id),
        parse_mode='HTML'
    )
    utils.new_update(msg, time.time()-start_time)

@bot.message_handler(commands=['start'], func=lambda msg: msg.chat.type == 'private')
def bot_user_start(msg):
    message = msg
    start_time = time.time()
    if utils.is_user_new(msg):
        if utils.have_args(msg):
            referrer = utils.parse_arg(msg)[1]
        bot.send_message(
            msg.chat.id,
            text.user_messages['start'],
            reply_markup=generate_user_menu_kb(msg.from_user.id)
            )
        api.register_new_user(msg.from_user, 'ru')
    else:
        bot.send_message(
            msg.chat.id, 
            text.user_messages[utils.get_user_lang(msg)]['start'], 
            reply_markup=generate_user_menu_kb(msg.from_user.id)
        )
    utils.new_update(msg, time.time()-start_time)

@bot.message_handler(commands=['start'], func=lambda msg: msg.chat.type != 'private')
def bot_group_start(msg):
    start_time = time.time()
    api.register_new_chat(msg.chat)
    utils.new_update(msg, time.time()-start_time)

@bot.message_handler(commands = ['get_logs'], func = lambda msg: msg.chat.id == -1001236256304 and utils.check_super_user(msg.from_user.id))
def bot_logs(msg):
    bot.send_document(msg.chat.id, open('logs.txt', 'rb'))

@bot.message_handler(commands = ['menu'])
def bot_user_menu(msg):
    bot.send_message(
        msg.from_user.id,
        'Ваше меню',
        reply_markup = generate_user_menu_kb(msg.from_user.id)
    )

@bot.message_handler(commands=['set_text'], func = lambda msg: msg.chat.type != 'private')
def bot_set_text(msg):
    start_time = time.time()
    message = msg
    if len(msg.text) not in [9, 21]:
        new_greeting = msg.text[len(msg.text):msg.entities[0].length:-1][::-1]
        if utils.check_text(new_greeting):
            utils.set_greeting(msg, new_greeting)
            bot.send_message(
                msg.chat.id,
                'Приветствие изменено'
            )
        else:
            bot.send_message(
                msg.chat.id,
                text = 'Данное приветствие не работает'
            )
    utils.new_update(msg, time.time()-start_time)

@bot.message_handler(commands=['kick'], func=lambda msg: msg.chat.type != 'private')
def bot_kick(msg):
    start_time = time.time()
    utils.kick_user(msg)
    utils.new_update(msg, time.time()-start_time)

@bot.message_handler(commands = ['ban', 'ban_me_please'], func = lambda msg: msg.chat.type == 'supergroup')
def bot_ban_me_please(msg):
    start_time = time.time()
    if msg.text == '/ban_me_please':
        t = random.randint(1, 10)
        ban_time = 60*t
        try:
            if not utils.check_status(msg.from_user.id, msg.chat.id):
                bot.restrict_chat_member(
                    msg.chat.id,
                    msg.from_user.id,
                    until_date=str(time.time() + ban_time))
                bot.reply_to(
                    msg, 
                    text.group_commands[utils.get_group_lang(msg.chat.id)]['ban_me_please'].format(
                        t = t
                    ), 
                    parse_mode = 'HTML'
                )
            else:
                bot.reply_to(
                    msg,
                    text.group_commands[utils.get_group_lang(msg.chat.id)]['errors']['prefix'].format(
                        reason = text.group_commands[utils.get_group_lang(msg.chat.id)]['errors']['reasons']['user_is_admin']
                    ),
                    parse_mode='HTML'
                )
        except Exception as e:
            logging.error(e)
    else:
        utils.ban_user(msg)
    utils.new_update(msg, time.time()-start_time)

@bot.message_handler(commands=['ping'])
def bot_ping(msg):
    start_timee = time.time()
    uptime = datetime.timedelta(seconds = int(time.time()-start_time))
    working_time = datetime.timedelta(seconds = int(time.time()-msg.date))
    uptime_str = str(uptime).replace('day', 'days').replace('dayss', 'days')
    working_time_str = str(working_time).replace('day', 'days').replace('dayss', 'days')
    if uptime.days != 0:
        uptime_str = uptime_str.replace(uptime_str.split(',')[0], utils.get_text_translation(uptime_str.split(',')[0]), 'ru')
    if working_time.days != 0:
        working_time_str = working_time_str.replace(working_time_str.split(',')[0], utils.get_text_translation(working_time_str.split(',')[0], 'ru'))
    bot.send_message(
        msg.chat.id,
        text.user_messages['ru']['commands']['ping'].format(
            unix_time = datetime.datetime.fromtimestamp(int(time.time())),
            working_time = working_time_str,
            uptime_sec = uptime
        ),
        reply_to_message_id=msg.message_id,
        parse_mode='HTML'
    )
    utils.new_update(msg, time.time()-start_timee)


@bot.message_handler(content_types=['new_chat_members'])
def bot_users_new(msg):
    start_time = time.time()
    api.register_new_chat(msg.chat)
    chat_id = msg.chat.id
    utils.new_member_logs(msg)
    if api.get_group_params(msg.chat.id)['deletions']['system']:
        bot.delete_message(
            msg.chat.id,
            msg.message_id
        )
    if msg.chat.type == 'channel':
        bot.send_message(
            msg.chat.id,
            text.promotion_message,
            parse_mode='HTML'
            )
        bot.leave_chat(
            msg.chat.id
            )
    if msg.new_chat_member.id == 495038140:
        api.change_group_params(msg.chat.id, ujson.dumps(config.default_group_settings))
    else:
        if api.get_group_params(msg.chat.id)['restrictions']['read_only']:
            bot.restrict_chat_member(
                msg.chat.id,
                msg.new_chat_member.id,
                until_date = int(time.time()+api.get_group_params(msg.chat.id)['restrictions']['for_time']*3600)
            )
            r = bot.send_message(
                msg.chat.id,
                text.group_commands['ru']['restricted']['new_user']['read_only'].format(
                    user_id = msg.new_chat_member.id,
                    user_name = api.replacer(msg.new_chat_member.first_name),
                    ban_time = api.get_group_params(msg.chat.id)['restrictions']['for_time']
                ),
                reply_markup = unban_new_user_kb(msg),
                parse_mode = 'HTML'
            )
            utils.add_to_delete_queue(msg.chat.id, r.message_id, api.get_group_params(msg.chat.id)['restrictions']['for_time']*3600)
        if msg.new_chat_member.is_bot and api.get_group_params(msg.chat.id)['kick_bots']:
            bot.kick_chat_member(
                msg.chat.id, 
                msg.new_chat_member.id
            )
            bot.send_message(
                msg.chat.id,
                text.group_commands['ru']['restricted']['bot'],
                parse_mode = 'HTML',
                reply_markup = types.ReplyKeyboardRemove()
            )
        elif utils.check_global_ban(msg):
            bot.kick_chat_member(
                msg.chat.id,
                msg.new_chat_member.id
            )
            bot.send_message(
                msg.chat.id,
                text.group_commands['ru']['restricted']['global_ban'].format(
                    user_id = msg.new_chat_member.id,
                    user_name = msg.new_chat_member.first_name
                ),
                parse_mode = 'HTML'
            )
        else:
            utils.new_user_in_chat(msg)
            if utils.need_greeting(msg):
                r = bot.send_message(
                    msg.chat.id,
                    utils.generate_welcome_text(msg), 
                    parse_mode='HTML'
                )
                utils.add_to_delete_queue(msg.chat.id, r.message_id, api.get_group_params(msg.chat.id)['greeting']['delete_timer'])
    utils.new_update(msg, time.time()-start_time)



@bot.message_handler(content_types=[
    'new_chat_members',
    'left_chat_member', 
    'new_chat_title', 
    'new_chat_photo', 
    'delete_chat_photo', 
    'group_chat_created', 
    'supergroup_chat_created', 
    'channel_chat_created', 
    'migrate_to_chat_id', 
    'migrate_from_chat_id', 
    'pinned_message'
    ])
def bot_check_system(msg):
    start_time = time.time()
    if api.get_group_params(msg.chat.id)['deletions']['system']:
        bot.delete_message(
            msg.chat.id,
            msg.message_id
        )
    utils.new_update(msg, time.time()-start_time)

@bot.message_handler(commands=['report'])
def bot_report(msg):
    start_time = time.time()
    admins = bot.get_chat_administrators(msg.chat.id)
    chat = bot.get_chat(msg.chat.id)
    msg_id = ''
    if chat.username:
        if msg.reply_to_message:
            msg_id = msg.reply_to_message.message_id
            txt = text.reports_messages['report']['to_admin']['have_username']['reply']
        else:
            msg_id = msg.message_id
            txt = text.reports_messages['report']['to_admin']['have_username']['no_reply']
    else:
        txt = text.reports_messages['report']['to_admin']['no_username']
    for i in admins:
        try:
            bot.send_message(
                i.user.id,
                txt.format(
                    group_name = api.replacer(msg.chat.title),
                    group_username = chat.username,
                    message_id = msg_id,
                    user_id = msg.from_user.id,
                    user_name = api.replacer(msg.from_user.first_name),
                ),
                parse_mode='HTML'
            )
        except Exception as e:
            print(e)
    bot.reply_to(
        msg,
        text.reports_messages['report']['to_user'],
        parse_mode = 'HTML'
    )
    utils.new_update(msg, time.time()-start_time)

@bot.message_handler(commands = ['unban'], func = lambda msg: msg.chat.type == 'supergroup')
def bot_user_unban(msg):
    start_time = time.time()
    if utils.check_status(msg.from_user.id, msg.chat.id) and utils.have_args(msg):
        words = utils.parse_arg(msg)[1]
        user_id = int(words)
        utils.unban_user(msg, user_id)
    elif utils.check_status(msg.from_user.id, msg.chat.id) and msg.reply_to_message is not None:
        user_id = msg.reply_to_message.from_user.id
        utils.unban_user(msg, user_id)
    elif utils.check_status(msg.from_user.id, msg.chat.id) and not utils.have_args(msg):
        utils.send_err_report(msg, 'no_args_provided')
    else:
        utils.send_err_report(msg, 'not_enought_rights')
    utils.new_update(msg, time.time()-start_time)

@bot.message_handler(commands = ['reregister'], func = lambda msg: msg.chat.type == 'supergroup')
def bot_reregister(msg):
    start_time = time.time()
    if utils.check_status(msg.from_user.id, msg.chat.id):
        api.register_new_chat(msg.chat)
        api.change_group_params(msg.chat.id, ujson.dumps(config.default_group_settings))
    bot.send_message(
        msg.chat.id,
        text.group_commands[utils.get_group_lang(msg.chat.id)]['registration'],
        parse_mode = 'HTML'
    )

@bot.message_handler(commands=['ro'], func=lambda msg: msg.chat.type == 'supergroup')
def bot_users_ro(msg):
    start_time = time.time()
    if utils.check_status(msg.from_user.id, msg.chat.id):
        utils.read_only(msg)
    else:
        utils.send_err_report(msg, 'not_enought_rights')
    utils.new_update(msg, time.time()-start_time)

@bot.message_handler(commands=['stickerpack_ban'],func=lambda msg: msg.chat.type == 'supergroup')
def bot_stickerpack_ban(msg):
    start_time = time.time()
    if utils.check_status(msg.from_user.id, msg.chat.id):
        utils.ban_stickerpack(msg)
    else:
        utils.send_err_report(msg, 'not_enought_rights')
    utils.new_update(msg, time.time()-start_time)

@bot.message_handler(commands=['stickerpack_unban'], func=lambda msg: msg.chat.type != 'private')
def bot_stickerpack_unban(msg):
    start_time = time.time()
    if utils.check_status(msg.from_user.id, msg.chat.id) and utils.have_args(msg):
        stickerpack_name = utils.parse_arg(msg)[1]
        utils.unban_stickerpack(msg, stickerpack_name)
    utils.new_update(msg, time.time()-start_time)


@bot.message_handler(commands=['sticker_ban'], func=lambda msg: msg.chat.type == 'supergroup')
def bot_sticker_ban(msg):
    start_time = time.time()
    if utils.check_status(msg.from_user.id, msg.chat.id):
        sticker_id = msg.reply_to_message.sticker.file_id
        utils.ban_sticker(msg, sticker_id)
    elif not utils.check_status(msg.from_user.id, msg.chat.id):
        utils.send_err_report(msg, 'not_enought_rights')
    utils.new_update(msg, time.time()-start_time)

@bot.message_handler(commands=['sticker_unban'], func=lambda msg: msg.chat.type == 'supergroup')
def bot_sticker_unban(msg):
    start_time = time.time()
    if utils.have_args(msg) and utils.check_status(msg.from_user.id, msg.chat.id):
        sticker_id = utils.parse_arg(msg)[1]
        utils.unban_sticker(msg, sticker_id)
    elif utils.check_status(msg.from_user.id, msg.chat.id) and not utils.have_args(msg):
        utils.send_err_report(msg, 'not_enought_rights')
    elif utils.have_args(msg) and not check_status(msg.from_user.id):
        utils.send_err_report(msg, 'no_args_provided')
    utils.new_update(msg, time.time()-start_time)

@bot.message_handler(commands=['help'])
def bot_help(msg):
    start_time = time.time()
    bot.send_message(
        msg.from_user.id,
        text.user_messages[utils.get_user_lang(msg)]['help'],
        parse_mode='HTML'
    )
    utils.new_update(msg, time.time()-start_time)

@bot.message_handler(commands=['about'], func=lambda msg: msg.chat.type == 'private')
def bot_about(msg):
    start_time = time.time()
    bot.send_message(
        msg.chat.id,
        text.user_messages[utils.get_user_lang(msg)]['about'],
        parse_mode='HTML'
    )
    utils.new_update(msg, time.time()-start_time)

@bot.message_handler(commands=['warn'], func=lambda msg: msg.chat.type != 'private')
def bot_new_warn(msg):
    start_time = time.time()
    if utils.check_status(msg.from_user.id, msg.chat.id) and msg.reply_to_message is not None and not utils.check_status(msg.reply_to_message.from_user.id, msg.chat.id):
        utils.new_warn(msg)
    elif not utils.check_status(msg.from_user.id, msg.chat.id):
        utils.send_err_report(msg, 'not_enought_rights')
    elif utils.check_status(msg.reply_to_message.from_user.id, msg.chat.id):
        utils.send_err_report(msg, 'user_is_admin')
    utils.new_update(msg, time.time()-start_time)

@bot.message_handler(commands=['donate'])
def bot_donate(msg):
    start_time = time.time()
    bot.send_message(
        msg.chat.id,
        text.group_commands['ru']['donate'],
        parse_mode = 'HTML'
    )
    utils.new_update(msg, time.time()-start_time)

@bot.message_handler(commands = ['get_id'])
def bot_get_id(msg):
    bot.send_message(
        msg.chat.id,
        msg.chat.id
    )

# @bot.message_handler(commands = ['voteban'])
# def bot_voteban(msg):
#     utils.new_voteban(msg)
#     bot.send_message(
#         msg.chat.id,
#         text.
#     )

@bot.message_handler(commands = ['version'])
def bot_version(msg):
    bot.send_message(
        msg.chat.id,
        text.user_messages[utils.get_user_lang(msg)]['commands']['version'].format(version = text.VERSION),
        parse_mode = 'HTML'
    )

    
@bot.message_handler(commands = ['set_rules'], func = lambda msg: utils.check_status(msg.from_user.id, msg.chat.id))
def bot_set_rules(msg):
    start_time = time.time()
    message = msg
    if len(msg.text) not in [9, 21]:
        new_rules = msg.text[len(msg.text):msg.entities[0].length:-1][::-1]
        if utils.check_text(new_rules):
            utils.set_rules(msg, new_rules)
            bot.send_message(
                msg.chat.id,
                'Правила изменены'
            )
        else:
            bot.send_message(
                msg.chat.id,
                text = 'Правила составлены неверно'
            )
    utils.new_update(msg, time.time()-start_time)

@bot.message_handler(commands = ['rules'], func = lambda msg: msg.chat.type != 'private')
def bot_get_rules(msg):
    start_time = time.time()
    try:
        bot.send_message(
            msg.from_user.id,
            utils.generate_rules_text(msg),
            parse_mode = 'HTML'
        )
    except Exception:
        bot.reply_to(
            msg,
            text = ''
        )
    utils.new_update(msg, time.time()-start_time)

@bot.message_handler(commands = ['reset_settings'], func = lambda msg: msg.chat.type != 'private')
def bot_reset_settings(msg):
    start_time = time.time()
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton(text = 'Да, выполнить сброс', callback_data = 'reset_settings_confirmation::{chat_id}'.format(chat_id = msg.chat.id)))
    kb.add(types.InlineKeyboardButton(text = 'Нет, не стоит', callback_data = 'reset_settings_abort::{chat_id}'.format(chat_id = msg.chat.id)))
    if utils.check_status(msg.from_user.id, msg.chat.id):
        bot.send_message(
            msg.chat.id,
            'Вы действительно хотите сбросить настройки?',
            reply_markup = kb
        )
        

@bot.message_handler(commands = ['update_time'], func = lambda msg: utils.check_super_user(msg.from_user.id))
def bot_update_time(msg):
    bot_ping(msg)
    subprocess.run("timedatectl set-time '{time}'".format(time = datetime.datetime.fromtimestamp(msg.date+1).strftime("%Y-%m-%d %H:%M:%S")), shell=True)
    bot_ping(msg)

@bot.message_handler(content_types=['text'], func = lambda msg: msg.chat.type != 'private')
def bot_check_text(msg):
    start_time = time.time()
    msg_text = msg.text
    msg_text_low = msg_text.lower()
    if utils.is_restricted(msg) and not utils.check_status(msg.from_user.id, msg.chat.id):
        bot.delete_message(
            msg.chat.id,
            msg.message_id
        )
        if msg_text_low.startswith('разбан'):
            if utils.check_super_user(msg.from_user.id):
                utils.global_unban(msg)
        elif msg_text.lower() in ['глобал бан']:
                if utils.check_super_user(msg.from_user.id):
                    utils.global_ban(msg)
        elif not utils.check_status(msg.from_user.id, msg.chat.id):
            # if utils.is_new_in_chat(msg) and api.get_group_params(msg.chat.id)['restrict_new'] == '1':
            if utils.check_for_urls(msg) and api.get_group_params(msg.chat.id)['deletions']['url']:
                    bot.delete_message(
                        msg.chat.id,
                        msg.message_id
                    )
                    bot.send_message(
                        msg.chat.id,
                        text.group_commands[utils.get_group_lang(msg.chat.id)]['restricted']['url'].format(
                            user_id = msg.from_user.id,
                            user_name = api.replacer(msg.from_user.first_name)
                        ),
                        parse_mode='HTML'
                    )
                # elif utils.check_for_forward(msg) and api.get_group_params(msg.chat.id)['deletions']['forward']:
                #     bot.delete_message(
                #         msg.chat.id,
                #         msg.message_id
                #     )
                #     bot.send_message(
                #         msg.chat.id,
                #         text.group_commands[utils.get_group_lang(msg.chat.id)]['restricted']['url'].format(
                #             user_id = msg.from_user.id,
                #             user_name = api.replacer(msg.from_user.first_name)
                #         ),
                #         parse_mode='HTML'
                #     )
    utils.new_update(msg, time.time()-start_time)

@bot.message_handler(content_types=['photo'], func = lambda msg: msg.chat.id == 303986717)
def bot_text(msg):
    start_time = time.time()
    bot.reply_to(msg, "<code>'{}': '{}',</code>".format(msg.photo[0].file_id, msg.caption), parse_mode ='HTML')
    utils.new_update(msg, time.time()-start_time)

@bot.message_handler(content_types = ['sticker'], func = lambda msg: not utils.check_status(msg.from_user.id, msg.chat.id))
def bot_check_sticker(msg):
    start_time = time.time()
    if utils.is_restricted(msg) or utils.is_sticker_restricted(msg):
        bot.delete_message(
            msg.chat.id,
            msg.message_id
        )
    utils.new_update(msg, time.time()-start_time)

@bot.message_handler(content_types = ['audio', 'document', 'photo', 'sticker', 'video', 'video_note', 'voice', 'location', 'contact'], func = lambda msg: not utils.check_status(msg.from_user.id, msg.chat.id))
def testt(msg):
    start_time = time.time()
    if utils.is_restricted(msg):
        bot.delete_message(
            msg.chat.id,
            msg.message_id
        )
    utils.new_update(msg, time.time()-start_time)



# Кнопки

@bot.callback_query_handler(func = lambda c: c.data.startswith('get_chat_refs::'))
def bot_get_chat_refs(c):
    chat_id = utils.parse_chat_id(c)
    user_id = c.from_user.id
    inviters = utils.get_top_inviters(chat_id)
    m = text.group_commands[utils.get_group_lang(chat_id)]['refs_stats']['header']
    counter = 0
    for i in inviters:
        inviter_info = bot.get_chat_member(chat_id, i['inviter'])
        counter += 1
        m += text.group_commands[utils.get_group_lang(chat_id)]['refs_stats']['body'].format(
            inviter_pos = counter,
            inviter_id = inviter_info.user.id,
            inviter_firstname = inviter_info.user.first_name,
            invited_count = int(i['COUNT(`inviter`)'])
        )
    bot.send_message(
        user_id,
        m,
        parse_mode = 'HTML'
    )
    bot.answer_callback_query(
        c.id,
        text = 'Список отправлен',
        show_alert = True
    )

@bot.callback_query_handler(func = lambda c: c.data in ['my_chats', 'to_groups_list'])
def my_chats_list(c):
    user_id = c.from_user.id
    user_settings = api.get_user_param(user_id, 'settings')
    bot.edit_message_text(
        chat_id = c.message.chat.id,
        message_id = c.message.message_id,
        text = 'Список ваших групп'
    )
    bot.edit_message_reply_markup(
        chat_id = c.message.chat.id,
        message_id = c.message.message_id,
        reply_markup = generate_user_groups(user_id)
    )
    bot.answer_callback_query(
        callback_query_id = c.id,
        text = 'Переход выполнен'
    )

@bot.callback_query_handler(func = lambda c: c.data.startswith('get_settings_json'))
def bot_get_settings_json(c):
    chat_id = utils.parse_chat_id(c)
    bot.send_message(
        chat_id = c.from_user.id,
        text = 'Эти настройки можно получить в любое время и отправить @f0rden для восстановления их, в случае сбоя:\n'+ujson.dumps(api.get_group_params(chat_id))
    )
    bot.answer_callback_query(
        c.id,
        text = 'Настройки отправлены',
        show_alert = True
    )
    
@bot.callback_query_handler(func = lambda c: c.data == 'stats_menu')
def bot_stats_menu(c):
    bot.edit_message_text(
        chat_id = c.message.chat.id,
        message_id = c.message.message_id,
        text = text.service_messages['stats'].format(
            all_users = api.get_users_count(),
            all_chats = api.get_chats_count(),
            unblocked_users = api.get_unblocked_users_count(),
            unblocked_chats = api.get_unblocked_chats_count()
        )
    )
    
    
@bot.callback_query_handler(func = lambda c: c.data == 'change_lang')
def bot_change_lang(c):
    user_id = c.from_user.id
    bot.edit_message_text(
        chat_id = c.message.chat.id,
        message_id = c.message.message_id,
        text = text.user_messages['start'], 
        parse_mode = 'HTML'
    )
    bot.edit_message_reply_markup(
        chat_id = c.message.chat.id,
        message_id = c.message.message_id,
        reply_markup = create_user_language_keyboard()
    )
    bot.answer_callback_query(
        callback_query_id = c.id,
        text = 'Переход выполнен'
    )   
    
@bot.callback_query_handler(func = lambda c: c.data.startswith('settings::'))
def chat_settings(c):
    chat_id = utils.parse_chat_id(c)
    bot.edit_message_text(
        chat_id = c.message.chat.id,
        message_id = c.message.message_id,
        text = '<b>Настройки группы {}</b>'.format(bot.get_chat(chat_id).title), 
        parse_mode = 'HTML'
    )
    bot.edit_message_reply_markup(
        chat_id = c.message.chat.id,
        message_id = c.message.message_id, 
        reply_markup = group_setting(chat_id),
    )
    
@bot.callback_query_handler(func = lambda c: c.data == 'to_main_menu')
def bot_to_main_menu(c):
    bot.edit_message_text(
        chat_id = c.message.chat.id,
        message_id = c.message.message_id,
        text = 'Ваше меню'
    )
    bot.edit_message_reply_markup(
        chat_id = c.message.chat.id,
        message_id = c.message.message_id,
        reply_markup = generate_user_menu_kb(c.from_user.id)
    )

@bot.callback_query_handler(func = lambda c: c.data == 'broadcast_menu')
def bot_admin_menu(c):
    bot.edit_message_text(
        chat_id = c.message.chat.id,
        message_id = c.message.message_id,
        text = 'Выберите тип рассылки'
    )
    bot.edit_message_reply_markup(
        chat_id = c.message.chat.id,
        message_id = c.message.message_id,
        reply_markup = generate_broadcast_vars_menu_kb()
    )

@bot.callback_query_handler(func = lambda c: c.data == 'check_broadcast')
def bot_admin_menu(c):
    bot.edit_message_text(
        chat_id = c.message.chat.id,
        message_id = c.message.message_id,
        text = 'Рассылка начата'
    )
    bot.edit_message_reply_markup(
        chat_id = c.message.chat.id,
        message_id = c.message.message_id,
        reply_markup = generate_broadcast_check_menu_kb()
    )   
    
@bot.callback_query_handler(func = lambda c: c.data.startswith('broadcast_check'))
def bot_broadcast_check(c):
    arg = c.data.split('::')[1]
    curr_bot_settings = ujson.loads(api.get_bot_settings(secret_config.token))
    if arg in ['users', 'chats', 'all']:
        curr_bot_settings['broadcast']['check']['recievers'] = arg
        api.change_bot_settings(secret_config.token, ujson.dumps(curr_bot_settings))
        bot.edit_message_reply_markup(
            chat_id = c.message.chat.id,
            message_id = c.message.message_id,
            reply_markup = generate_broadcast_check_menu_kb()
        )
        bot.answer_callback_query(
            callback_query_id = c.id,
            text = 'Изменения подтверждены.'
        )
    else:
        t = Thread(target = utils.make_broadcast, kwargs = {
            'is_test': True, 
            'receivers': curr_bot_settings['broadcast']['check']['recievers'], 
            'cont_type': 'text',
            'msg_text': '',
            'file_id': '',
            'user_id': c.from_user.id,
            'message_id': c.message.message_id
            }
        )
        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton(text = 'В главное меню', callback_data = 'to_main_menu'))
        bot.edit_message_reply_markup(
            chat_id = c.message.chat.id,
            message_id = c.message.message_id,
            reply_markup = kb
        )
        t.start()       
        t.join()
    
@bot.callback_query_handler(func = lambda c: c.data == 'admin_menu')
def bot_admin_menu(c):
    bot.edit_message_text(
        chat_id = c.message.chat.id,
        message_id = c.message.message_id,
        text = 'Админка'
    )
    bot.edit_message_reply_markup(
        chat_id = c.message.chat.id,
        message_id = c.message.message_id,
        reply_markup = generate_admin_menu_kb()
    )
    
@bot.callback_query_handler(func=lambda c: c.data.startswith('lang::'))
def change_language(c):
    words = re.split('::', c.data)
    lang = words[1]
    bot.edit_message_text(
        chat_id = c.message.chat.id,
        message_id = c.message.message_id,
        text = text.user_messages[lang]['chosen_language'])
    api.register_new_user(c.from_user, lang)

@bot.callback_query_handler(func = lambda c: c.data.startswith('get_notifications'))
def notify_change(c):
    chat_id = utils.parse_chat_id(c)
    if utils.check_status(c.from_user.id, utils.parse_chat_id(c)):
        utils.change_state_main(chat_id, 'get_notifications')
        bot.edit_message_reply_markup(
            chat_id=c.message.chat.id,
            message_id=c.message.message_id,
            reply_markup=group_setting(utils.parse_chat_id(c))
        )
        bot.answer_callback_query(
            callback_query_id = c.id,
            text = 'Изменения подтверждены. Текущий статус настройки: {}'.format(config.settings_statuses[api.get_group_params(chat_id)[c.data.split('::')[0]]])
        )
    else:
        bot.answer_callback_query(
            callback_query_id = c.id,
            show_alert = True,
            text = 'Вы не являетесь администратором. Текущий статус настройки: {}'.format(config.settings_statuses[api.get_group_params(chat_id)[c.data.split('::')[0]]])
        )

@bot.callback_query_handler(func = lambda c: c.data.startswith('del_url'))
def del_url(c):
    chat_id = utils.parse_chat_id(c)
    if utils.check_status(c.from_user.id, utils.parse_chat_id(c)):
        utils.change_state_deletions_main(chat_id, 'url')
        bot.edit_message_reply_markup(
            chat_id=c.message.chat.id,
            message_id=c.message.message_id,
            reply_markup=group_setting(utils.parse_chat_id(c))
        )
        bot.answer_callback_query(
            callback_query_id = c.id,
            text = 'Изменения подтверждены. Текущий статус настройки: {}'.format(config.settings_statuses[api.get_group_params(chat_id)['deletions']['url']])
        )
    else:
        bot.answer_callback_query(
            callback_query_id = c.id,
            show_alert = True,
            text = 'Вы не являетесь администратором. Текущий статус настройки: {}'.format(config.settings_statuses[api.get_group_params(chat_id)['deletions']['url']])
        )

@bot.callback_query_handler(func = lambda c: c.data.startswith('del_system'))
def del_system(c):
    chat_id = utils.parse_chat_id(c)
    if utils.check_status(c.from_user.id, utils.parse_chat_id(c)):
        utils.change_state_deletions_main(chat_id, 'system')
        bot.edit_message_reply_markup(
            chat_id=c.message.chat.id,
            message_id=c.message.message_id,
            reply_markup=group_setting(utils.parse_chat_id(c))
        )
        bot.answer_callback_query(
            callback_query_id = c.id,
            text = 'Изменения подтверждены. Текущий статус настройки: {}'.format(config.settings_statuses[api.get_group_params(chat_id)['deletions']['system']])
        )
    else:
        bot.answer_callback_query(
            callback_query_id = c.id,
            show_alert = True,
            text = 'Вы не являетесь администратором. Текущий статус настройки: {}'.format(config.settings_statuses[api.get_group_params(chat_id)['deletions']['system']])
        )

@bot.callback_query_handler(func = lambda c: c.data.startswith('kick_bots'))
def kick_bots(c):
    chat_id = utils.parse_chat_id(c)
    if utils.check_status(c.from_user.id, utils.parse_chat_id(c)):
        utils.change_state_main(chat_id, 'kick_bots')
        bot.edit_message_reply_markup(
            chat_id=c.message.chat.id,
            message_id=c.message.message_id,
            reply_markup=group_setting(utils.parse_chat_id(c))
        )
        bot.answer_callback_query(
            callback_query_id = c.id,
            text = 'Изменения подтверждены. Текущий статус настройки: {}'.format(config.settings_statuses[api.get_group_params(chat_id)[c.data.split('::')[0]]])
        )
    else:
        bot.answer_callback_query(
            callback_query_id = c.id,
            show_alert = True,
            text = 'У вас недостаточно прав для выполнения этого действия. Текущий статус настройки: {}'.format(config.settings_statuses[api.get_group_params(chat_id)[c.data.split('::')[0]]])
        )

@bot.callback_query_handler(func = lambda c: c.data.startswith('deletions_settings'))
def to_deletions(c):
    chat_id = utils.parse_chat_id(c)
    bot.edit_message_reply_markup(
        chat_id = c.message.chat.id,
        message_id = c.message.message_id,
        reply_markup = delete_settings(utils.parse_chat_id(c))
    )
    bot.answer_callback_query(
        callback_query_id = c.id,
        text = 'Переход выполнен.'
    )

@bot.callback_query_handler(func = lambda c: c.data.startswith('delete::'))
def group_settings_deletions(c):
    chat_id = utils.parse_chat_id(c)
    cont_type = re.split('::', c.data)[1]
    if utils.check_status(c.from_user.id, utils.parse_chat_id(c)):
        utils.change_state_deletions_files(chat_id, cont_type)
        bot.edit_message_reply_markup(
            chat_id = c.message.chat.id,
            message_id = c.message.message_id,
            reply_markup = delete_settings(utils.parse_chat_id(c))
        )
        bot.answer_callback_query(
            callback_query_id = c.id,
            text = 'Изменения подтверждены. Статус настройки: {}'.format(config.settings_statuses[api.get_group_params(chat_id)['deletions']['files'][cont_type]])
        )
    else:
        bot.answer_callback_query(
            callback_query_id = c.id,
            show_alert = True,
            text = 'У вас недостаточно прав для выполнения этого действия. Текущий статус настройки: {}'.format(config.settings_statuses[api.get_group_params(chat_id)['deletions']['files'][cont_type]])
        )

@bot.callback_query_handler(func = lambda c: c.data.startswith('change_all'))
def group_settings_deletions_all(c):
    chat_id = utils.parse_chat_id(c)
    if utils.check_status(c.from_user.id, utils.parse_chat_id(c)):
        for i in config.available_attachments:
            utils.change_state_deletions_files(chat_id, i)
        bot.edit_message_reply_markup(
            chat_id = c.message.chat.id,
            message_id = c.message.message_id,
            reply_markup = delete_settings(chat_id)
        )
        bot.answer_callback_query(
            callback_query_id = c.id,
            text = 'Изменения подтверждены.'
        )
    else:
        bot.answer_callback_query(
            callback_query_id = c.id,
            show_alert = True,
            text = 'У вас недостаточно прав для выполнения этого действия.'
        )
@bot.callback_query_handler(func = lambda c: c.data.startswith('to_group_settings_menu'))
def group_settings_deletions_photo(c):
    chat_id = utils.parse_chat_id(c)
    bot.edit_message_reply_markup(
        chat_id = c.message.chat.id,
        message_id = c.message.message_id,
        reply_markup=group_setting(utils.parse_chat_id(c))
    )
    bot.answer_callback_query(
        callback_query_id = c.id,
        text = 'Изменения подтверждены.'
    )

@bot.callback_query_handler(func = lambda c: c.data.startswith('warns_del'))
def del_warns(c):
    user_id = utils.parse_user_id(c)
    chat_id = utils.parse_chat_id(c)
    if utils.check_status(c.from_user.id, utils.parse_chat_id(c)):
        api.zeroing_warns(user_id, chat_id)
        bot.edit_message_text(
            text = 'Предупреждения обнулены.',
            chat_id = c.message.chat.id,
            message_id = c.message.message_id
        )
    else:
        bot.answer_callback_query(
            callback_query_id = c.id,
            show_alert = True,
            text = 'У вас недостаточно прав для выполнения этого действия.'
        )

@bot.callback_query_handler(func = lambda c: c.data.startswith('new_users_restrictions'))
def new_users_restrictions(c):
    chat_id = utils.parse_chat_id(c)
    bot.edit_message_reply_markup(
        chat_id = c.message.chat.id,
        message_id = c.message.message_id,
        reply_markup = new_users_restrictions_kb(chat_id)
    )

@bot.callback_query_handler(func = lambda c: c.data.startswith('read_only'))
def new_users_ro(c):
    chat_id = utils.parse_chat_id(c)
    if utils.check_status(c.from_user.id, utils.parse_chat_id(c)):
        settings = api.get_group_params(chat_id)
        settings['restrictions']['read_only'] = config.settings_states[settings['restrictions']['read_only']]
        api.change_group_params(chat_id, ujson.dumps(settings))
        bot.edit_message_reply_markup(
            chat_id = c.message.chat.id,
            message_id = c.message.message_id,
            reply_markup = new_users_restrictions_kb(chat_id)
        )
        bot.answer_callback_query(
            callback_query_id = c.id,
            text = 'Изменения подтверждены.'
        )
    else:
        bot.answer_callback_query(
            callback_query_id = c.id,
            show_alert = True,
            text = 'У вас недостаточно прав для выполнения этого действия.'
        )

@bot.callback_query_handler(func = lambda c: c.data.startswith('time_ro_'))
def ro_time_change(c):
    change_time = int(c.data.split('_')[2].split('::')[0])
    chat_id = utils.parse_chat_id(c)
    if utils.check_status(c.from_user.id, utils.parse_chat_id(c)):
        settings = api.get_group_params(chat_id)
        settings['restrictions']['for_time'] = settings['restrictions']['for_time'] + change_time
        if settings['restrictions']['for_time'] < 1:
            settings['restrictions']['for_time'] = 1
        api.change_group_params(chat_id, ujson.dumps(settings))
        bot.edit_message_reply_markup(
            chat_id = c.message.chat.id,
            message_id = c.message.message_id,
            reply_markup = new_users_restrictions_kb(chat_id)
        )
        bot.answer_callback_query(
            callback_query_id = c.id,
            text = 'Изменения подтверждены.'
        )
    else:
        bot.answer_callback_query(
            callback_query_id = c.id,
            show_alert = True,
            text = 'У вас недостаточно прав для выполнения этого действия.'
        )

@bot.callback_query_handler(func = lambda c: c.data.startswith('warns_count_'))
def ro_time_change(c):
    change_count = int(c.data.split('_')[2].split('::')[0])
    chat_id = utils.parse_chat_id(c)
    if utils.check_status(c.from_user.id, utils.parse_chat_id(c)):
        settings = api.get_group_params(chat_id)
        settings['warns']['count'] = settings['warns']['count'] + change_count
        if settings['warns']['count'] < 1:
            settings['warns']['count'] = 1
        api.change_group_params(chat_id, ujson.dumps(settings))
        bot.edit_message_reply_markup(
            chat_id = c.message.chat.id,
            message_id = c.message.message_id,
            reply_markup = warns_settings_kb(chat_id)
        )
        bot.answer_callback_query(
            callback_query_id = c.id,
            text = 'Изменения подтверждены.'
        )
    else:
        bot.answer_callback_query(
            callback_query_id = c.id,
            show_alert = True,
            text = 'У вас недостаточно прав для выполнения этого действия.'
        )

@bot.callback_query_handler(func = lambda c: c.data.startswith('warns_settings'))
def warns_count_change(c):
    chat_id = utils.parse_chat_id(c)
    bot.edit_message_reply_markup(
        chat_id = c.message.chat.id,
        message_id = c.message.message_id,
        reply_markup = warns_settings_kb(chat_id)
    )
    bot.answer_callback_query(
        callback_query_id = c.id,
        text = 'Изменения подтверждены.'
    )

@bot.callback_query_handler(func = lambda c: c.data.startswith('warns_action_'))
def warns_count_change(c):
    new_mod = int(c.data.split('_')[2].split('::')[0])
    chat_id = utils.parse_chat_id(c)
    if utils.check_status(c.from_user.id, utils.parse_chat_id(c)):
        settings = api.get_group_params(chat_id)
        settings['warns']['action'] = new_mod
        api.change_group_params(chat_id, ujson.dumps(settings))
        bot.edit_message_reply_markup(
            chat_id = c.message.chat.id,
            message_id = c.message.message_id,
            reply_markup = warns_settings_kb(chat_id)
        )
        bot.answer_callback_query(
            callback_query_id = c.id,
            text = 'Изменения подтверждены.'
        )
    else:
        bot.answer_callback_query(
            callback_query_id = c.id,
            show_alert = True,
            text = 'У вас недостаточно прав для выполнения этого действия.'
        )

@bot.callback_query_handler(func = lambda c: c.data.startswith('unban_new_user'))
def unban_new_user(c):
    chat_id = utils.parse_chat_id(c)
    user_id = utils.parse_user_id(c)
    if api.get_group_params(chat_id)['restrictions']['admins_only']:
        if utils.check_status(c.from_user.id, utils.parse_chat_id(c)):
            utils.unban_user_button(c)
            user = bot.get_chat_member(
                chat_id,
                user_id
            )
            bot.edit_message_text(
                text = text.group_commands[utils.get_group_lang(c.message.chat.id)]['restricted']['new_user']['button_pressed'].format(
                    user_id = user.user.id,
                    user_name = api.replacer(user.user.first_name)
                ),
                parse_mode = 'HTML',
                chat_id = c.message.chat.id,
                message_id = c.message.message_id
            )
            utils.add_to_delete_queue(msg.chat.id, r.message_id, api.get_group_params(msg.chat.id)['greeting']['delete_timer'])

        else:
            bot.answer_callback_query(
                callback_query_id = c.id,
                show_alert = True,
                text = 'У вас недостаточно прав для выполнения этого действия.'
            )
    else:
        if c.from_user.id == user_id or utils.check_status(c.from_user.id, utils.parse_chat_id(c)):
            user = bot.get_chat_member(
                chat_id,
                user_id
            )
            if user.status in ['restricted']:
                bot.restrict_chat_member(
                    chat_id,
                    user_id,
                    can_send_media_messages=True,
                    can_add_web_page_previews=True,
                    can_send_messages=True,
                    can_send_other_messages=True
                )
                bot.edit_message_text(
                    text = text.group_commands[utils.get_group_lang(c.message.chat.id)]['restricted']['new_user']['button_pressed'].format(
                        user_id = user.user.id,
                        user_name = api.replacer(user.user.first_name)
                    ),
                    parse_mode = 'HTML',
                    chat_id = c.message.chat.id,
                    message_id = c.message.message_id
                )
                utils.add_to_delete_queue(chat_id, c.message.message_id, api.get_group_params(chat_id)['greeting']['delete_timer'])
        else:
            bot.answer_callback_query(
                callback_query_id = c.id,
                show_alert = True,
                text = 'У вас недостаточно прав для выполнения этого действия.'
            )

@bot.callback_query_handler(func = lambda c: c.data.startswith('new_restrictions_admins_only_'))
def warns_count_change(c):
    chat_id = utils.parse_chat_id(c)
    state = c.data.split('_')[4].split('::')[0]
    if utils.check_status(c.from_user.id, utils.parse_chat_id(c)):
        settings = api.get_group_params(chat_id)
        settings['restrictions']['admins_only'] = utils.to_bool(state)
        api.change_group_params(chat_id, ujson.dumps(settings))
        bot.edit_message_reply_markup(
            chat_id = c.message.chat.id,
            message_id = c.message.message_id,
            reply_markup = new_users_restrictions_kb(chat_id)
        )
        bot.answer_callback_query(
            callback_query_id = c.id,
            text = 'Изменения подтверждены.'
        )
    else:
        bot.answer_callback_query(
            callback_query_id = c.id,
            show_alert = True,
            text = 'У вас недостаточно прав для выполнения этого действия.'
        )

@bot.callback_query_handler(func = lambda c: c.data.startswith('welcome_settings'))
def welcome_settings(c):
    chat_id = utils.parse_chat_id(c)    
    bot.edit_message_reply_markup(
        chat_id = c.message.chat.id,
        message_id = c.message.message_id,
        reply_markup = welcome_settings_kb(chat_id)
    )
    bot.answer_callback_query(
        callback_query_id = c.id,
        text = 'Изменения подтверждены.'
    )

@bot.callback_query_handler(func = lambda c: c.data.startswith('welcome_state'))
def welcome_settings_state(c):
    chat_id = utils.parse_chat_id(c)    
    if utils.check_status(c.from_user.id, utils.parse_chat_id(c)):
        settings = api.get_group_params(chat_id)
        curr_state = settings['greeting']['is_enabled']
        new_state = config.settings_states[curr_state]
        settings['greeting']['is_enabled'] = new_state
        api.change_group_params(chat_id, ujson.dumps(settings))
        bot.edit_message_reply_markup(
            chat_id = c.message.chat.id,
            message_id = c.message.message_id,
            reply_markup = welcome_settings_kb(chat_id)
        )
        bot.answer_callback_query(
            callback_query_id = c.id,
            text = 'Изменения подтверждены.'
        )
    else:
        bot.answer_callback_query(
            callback_query_id = c.id,
            show_alert = True,
            text = 'У вас недостаточно прав для выполнения этого действия.'
        )

@bot.callback_query_handler(func = lambda c: c.data.startswith('welcome_timer'))
def welcome_timer_change(c):
    change_count = int(c.data.split('_')[2].split('::')[0])
    chat_id = utils.parse_chat_id(c)
    if utils.check_status(c.from_user.id, utils.parse_chat_id(c)):
        settings = api.get_group_params(chat_id)
        settings['greeting']['delete_timer'] = settings['greeting']['delete_timer'] + change_count
        if settings['greeting']['delete_timer'] < 0:
            settings['greeting']['delete_timer'] = 0
        api.change_group_params(chat_id, ujson.dumps(settings))
        bot.edit_message_reply_markup(
            chat_id = c.message.chat.id,
            message_id = c.message.message_id,
            reply_markup = welcome_settings_kb(chat_id)
        )
        bot.answer_callback_query(
            callback_query_id = c.id,
            text = 'Изменения подтверждены.'
        )
    else:
        bot.answer_callback_query(
            callback_query_id = c.id,
            show_alert = True,
            text = 'У вас недостаточно прав для выполнения этого действия.'
        )

@bot.callback_query_handler(func = lambda c: c.data.startswith('settings_delete'))
def del_settings(c):
    words = c.data.split()
    bot.delete_message(
        c.message.chat.id,
        words[2]
    )
    bot.delete_message(
        c.message.chat.id,
        words[1]
    )

@bot.callback_query_handler(func = lambda c: c.data.startswith('welcome_get'))
def get_welcome_text(c):
    chat_id = utils.parse_chat_id(c)
    bot.send_message(
        c.message.chat.id,
        utils.get_greeting(chat_id),
        parse_mode = 'HTML'
    )

@bot.callback_query_handler(func = lambda c: c.data.startswith('reset_settings'))
def reset_settings_button(c):
    chat_id = utils.parse_chat_id(c)
    if utils.check_status(c.from_user.id, utils.parse_chat_id(c)):
        if c.data.startswith('reset_settings_confirmation'):
            api.register_new_chat(c.message.chat)
            api.change_group_params(chat_id, ujson.dumps(config.default_group_settings))
            bot.send_message(
                c.message.chat.id,
                'Настройки сброшены.'
            )
            bot.delete_message(
                c.message.chat.id,
                c.message.message_id
            )
        else:
            bot.delete_message(
                c.message.chat.id,
                c.message.message_id
            )
            bot.send_message(
                c.message.chat.id,
                'Сброс отменен'
            )

@bot.callback_query_handler(func = lambda c: c.data.startswith('leave_'))
def bot_leave_cb(c):
    if utils.check_status(c.from_user.id, utils.parse_chat_id(c)):
        if c.data.endswith('confirm'):
            bot.delete_message(
                c.message.chat.id,
                c.message.message_id
            )
            bot.send_message(
                c.message.chat.id,
                text.group_commands[utils.get_group_lang(c.message.chat.id)]['leave']['accepted']
            )
            bot.leave_chat(
                c.message.chat.id
            )
        else:
            bot.send_message(
                c.message.chat.id,
                text.group_commands[utils.get_group_lang(c.message.chat.id)]['leave']['cancelled']
            )
            bot.delete_message(
                c.message.chat.id,
                c.message.message_id
            )

# @bot.callback_query_handler(func = lambda c: c.data.startswith('settings_captcha'))
# def change_captcha_settings(c):
#     chat_id = utils.parse_chat_id(c)
#     if utils.check_status(c.from_user.id, utils.parse_chat_id(c)):
#         settings = api.get_group_params(chat_id)
#         settings['']
#         api.change_group_params(chat_id, )

# Вебхук

bot.remove_webhook()

bot.set_webhook(
    url=WEBHOOK_URL_BASE + WEBHOOK_URL_PATH,
    certificate=open(WEBHOOK_SSL_CERT, 'r'))

context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
context.load_cert_chain(WEBHOOK_SSL_CERT, WEBHOOK_SSL_PRIV)

# Start aiohttp server
web.run_app(
    app,
    host=WEBHOOK_LISTEN,
    port=WEBHOOK_PORT,
    ssl_context=context,
)
# bot.remove_webhook()
# bot.polling()
