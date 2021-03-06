# -*- coding: utf-8 -*-

restricted_characters = [
    '<',
    '>',
    '&'
]

available_languages = [
    'ru',
    'en',
    'uz'
]

available_attachments = [
    'audio',
    'photo',
    'voice',
    'sticker',
    'document',
    'video',
    'video_note',
    'location',
    'contact',
    'text'
]

available_attachments_str = {
    'audio': 'Удалять аудио{}',
    'photo': 'Удалять фотографии{}',
    'voice': 'Удалять аудиосообщения{}',
    'sticker': 'Удалять стикеры{}',
    'document': 'Удалять файлы{}',
    'video': 'Удалять видео{}',
    'video_note': 'Удалять видеосообщения{}',
    'location': 'Удалять геолокации{}',
    'contact': 'Удалять контакты{}',
    'text': 'Удалять текстовые сообщения{}',
}

restricted_characters_replace = {
    '<': '&lt;',
    '>': '&gt;',
    '&': '&amp;'
}

languages = [
    {'title': '🇷🇺 Русский', 'code': 'ru'},
    {'title': '🇬🇧 English', 'code': 'en'},
    {'title': '🇺🇿 O\'zbek', 'code': 'uz'},
    {'title': '🇺🇦 Українська', 'code': 'ukr'},
]

human_langs = {
    'ru' : '🇷🇺 Русский',
    'en' : '🇬🇧 English',
    'uz' : '🇺🇿 O\'zbek',
    'ukr': '🇺🇦 Українська'
}

default_group_settings = {
    'language': 'ru',
    'get_notifications': True,
    'restrict_new': False,
    'additional_admins': [],
    'greeting': {
        'is_enabled': True,
        'text': 'Добро пожаловать в чат {chat_title}, <a href="tg://user?id={new_user_id}">{new_user_firstname}</a>',
        'delete_timer': 15
    },
    'rules': {
        'is_enabled': True,
        'text': 'Стандартные правила, для смены используйте команду /set_rules',
        'delete_timer': 15
    },
    'deletions': {
        'url': False,
        'system': False,
        'forwards': False,
        'files': {
            'audio': False,
            'photo': False,
            'voice': False,
            'document': False,
            'video': False,
            'video_note': False,
            'location': False,
            'contact': False,
            'text': False,
            'sticker': False
        }
    },
    'restrictions': {
        'read_only': False,
        'for_time': 1,
        'admins_only': True,
    },
    'captcha': {
        'is_on': False,
		'type': 'math'
    },
    'warns': {
        'count': 3,
        'action': 2,
        'for_time': 1
    },
    'kick_bots': False,
    'silent_mode': True,
    'logs_channel': {
        'is_on': False,
        'chat_id': 0
    }
}

warns_states = [
    'Ничего',
    'Кик',
    'Бан',
    'Read-only на сутки'
]

new_users = {
    False: 'новенького',
    True: 'администраторов'
}

default_user_settings = {
    'language': 'ru',
    'get_notifications': True,
    'admined_groups': []
}

settings_statuses = {
    False: '❌',
    True: '✅'
}

settings_states = {
    False: True,
    True: False
}

available_commands = [
    '/'
]

user_states_num_to_str = {
    0: 'menu',
    1: 'greeting',
    2: 'rules',
    3: 'log_channel'
}

user_states_str_to_num = {
    'menu': 0,
    'greeting': 1,
    'rules': 2,
    'log_channel': 3
}