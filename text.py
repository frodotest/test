# coding: utf8

import random

VERSION = '1.6'

user_messages = {
    'start': '👋',
    'ru': {
        'chosen_language': 'Привет! Ты выбрал русский язык. Чтобы изменить его в дальнейшем - напиши команду /language. Теперь еще раз напиши /start, чтобы получить доступ к боту',

        'start': 'Привет! Я твой новый помощник в чате! Чтобы использовать весь мой функционал, добавь меня в подконтрольную тебе группу, выдай все права (последний необязателен), и напиши сюда /help',
        
        'help': 'Итак, мои команды написаны ниже: \n'
                '/start - Начинает диалог с ботом\n'
                '/help - Выводит это сообщение\n'
                '/about - Выводит контакты разработчика и дополнительную информацию\n'
                '/language - Сбрасывает выбранный язык и позволяет сменить его\n'
                '/sticker_ban - Банит стикер и удаляет все сообщения, содержащие его, пока один из администраторов его не разбанит. Доступно только администраторам\n'
                '/sticker_unban - Разбанивает стикер и прекращает его удаление. Доступно только администраторам\n'
                '/ro - Запрещает пользователю писать на некоторое время. \n    Поддерживаемые параметры: секунды (s), минуты (m), часы (h) и дни (d). Если команда отправлена без параметров, то автоматически выдается запрет на 1 минуту\n'
                '/ping - Проверяет доступность бота. Работает везде и доступна для всех. Если бот не ответил на нее в течение первых 5 секунд - либо конкретно сейчас обрабатывается множество других сообщений, либо что-то случилось с сервером\n'
                '<a href="http://telegra.ph/Manual-po-ispolzovaniyu-bota-02-03">Мануал по использованию бота</a>',
            
        'about': 'Бот написан <a href="tg://user?id=303986717">F0rden</a>\n',

        'commands': {
            'sticker_ban': 'Стикер <b>{sticker_id}</b> заблокирован. Для разблокировки введите команду <code>/unban {sticker_id}</code>',
            'stickerpack_banned': 'Заблокирован стикерпак <b>{stickerpack_name}</b>, содержащий <code>{count}</code> шт. стикеров.\n'
                                  'Для разблокировки попросите администратора ввести команду <code>/stickerpack_unban {stickerpack_name}</code>',
            'stickerpack_unbanned': 'Стикерпак <b>{stickerpack_name}</b> разблокирован.',
            'sticker_unban': 'Стикер <b>{sticker_id}</b> разблокирован.',
            'ro': '<a href="tg://user?id={admin_id}">{admin}</a> попросил <a href="tg://user?id={user_id}">{user} помолчать на {time_sec} сек.</a>',
            'ping': 'Бот функционирует нормально. \n'
                    'Серверное время: <code>{unix_time}</code>\n'
                    'Бот отреагировал на сообщение за <code>{working_time}</code>.\n'
                    'Бот не перезагружался уже <code>{uptime_sec}</code>.',
            'ban': 'Пользователь <a href="tg://user?id={user_id}">{user}</a> забанен администратором <a href="tg://user?id={admin_id}">{admin}</a>. \nДля разбана используйте команду <code>/unban {user_id}</code>.',
            'unban': 'Пользователь <a href="tg://user?id={user_id}">{user}</a> разбанен администратором <a href="tg://user?id={admin_id}">{admin}</a>',
            'kick': 'Пользователь <a href="tg"//user?id={user_id}>{user}</a> исключен администратором <a href="tg://user?id={admin_id}">{admin}</a>',
            'get_users': {
                'title': 'Список активных пользователей чата <b>{chat_name}</b>: \n',
                'body_notify': '\n{user_number}. <a href="tg://user?id={user_id}">{user_name}</a> - <b>{user_count}</b> (<b>{percent}%</b>)',
                'body_silence': '\n{user_number}. {user_name} - <b>{user_count}</b> (<b>{percent}%</b>)',
                'end': '\n\nВсего пользователей зафиксировано в чате: <b>{users_count}</b>\n'
                       'Всего сообщений зафиксировано в чате: <b>{messages_count}</b>\n'
                       'Вы находитесь на <b>{user_place}-м</b> месте\n'
                       'Сообщение сформированно за <code>{used_time}</code> сек.',
                'chat_response': {
                    'success': 'Результат отправлен вам в личные сообщения',
                    'fault': 'Напишите боту в личных сообщениях /start, чтобы он смог отправлять вам сообщения'
                },
            },
            'version': 'Текущая версия бота: <b>{version}</b>'
        }
    },
    'en': {
        'chosen_language': "Hi! You've chosen English language. To change it, send command /language. Now send me /start again",

        'start': "Hi! I'm your new chat admin.To use all my power, please, add me to group, where you are admin and then text /start there. For help, use commands /help",
        
        'help': 'So, my commands are written below\n'
                '/start - Start dialog with bot\n'
                '/help - Show this message\n'
                "/about - Show developer's contacts\n"
                '/language - Let you change chosen language\n'
                '/sticker_ban - Ban sticker and delete it automatically\n'
                '/sticker_unban - Unban sticker and lets everyone send it\n'
                '/kick - Kick user from group\n'
                '/ban - Ban user forever in group\n'
                '/ro - Restrict user from writing in group and for some time. \nSupports next args: seconds (s), minutes (s), hours (h) and even days (d). If no args are provided, user will be restricted for 1 minute\n'
                '/ping - Check the availability of the bot\n',
                'about': 'Bot created by <a href="tg://user?id=303986717">F0rden</a>\n'
                         'P.S. If you found any mistakes, please, contact <a href="tg://user?id=303986717">F0rden</a>',
                
		'commands': {
			'version': 'Bot version: <b>{version}</b>'
		}
    },
        'ukr': {
        'chosen_language': 'Ти обрав українську мову. Щоб змінити його - напиши команду /language. Тепер ще раз напиши /start, щоб отримати доступ до бота',

        'start': 'Привіт! Я твій новий помічник в чаті! Щоб використовувати мене на максимум, додай мене в підконтрольну тобі группу, видай всі привилегії, а сюди напиши /help',
        
        'help': 'Отже, мої команди: \n'
                '/start - Починає роботу з ботом\n'
                '/help - Виводить це повідомлення\n'
                '/about - Контакти розробника і додаткова інформація\n'
                '/language - Можливість вибрати нову мову\n'
                '/sticker_ban - Банить стікер і видаляє все повідомлення, що містять його, поки один из админістраторів його не розбанить. Доступно тільки адміністраторам\n'
                '/sticker_unban - Розбанює стікер і приняє його видалення. Доступно тільки адміністраторам\n'
                '/ro - Забороняє користовачу писати на деякий час. \nПідтримувані параметри: секунди (s), хвилини (m), годинник (h) і дні (d). Якщо команда відправлена ​​без параметрів, то автоматично видається заборона на 1 хвилину\n'
                '/ping - Перевіряє доступність бота. Працює скрізь і доступна для всіх. Якщо бот не відповів на неї протягом перших 5 секунд, то саме зараз обробляється безліч інших повідомлень, або щось трапилося з сервером\n'
                    '<a href="http://telegra.ph/Manual-po-ispolzovaniyu-bota-02-03">Мануал по використанню бота</a>',
            
        'about': 'Бот написаний <a href="tg://user?id=303986717">F0rden</a>\n',

        'commands': {
            'sticker_ban': 'Стікер <b>{sticker_id}</b> заблокован. Для розблокування введіть команду <code>/unban {sticker_id}</code>',
            'stickerpack_banned': 'Заблоковано стікерпак <b>{stickerpack_name}</b>, що містить <code>{count}</code> кількість стікерів.\n'
                                  'Для розблокування попросіть адміністратора ввести команду <code>/stickerpack_unban {stickerpack_name}</code>',
            'stickerpack_unbanned': 'Стікерпак <b>{stickerpack_name}</b> розблоковано.',
            'sticker_unban': 'Стікер <b>{sticker_id}</b> розблокований.',
            'ro': '<a href="tg://user?id={admin_id}">{admin}</a> попросив <a href="tg://user?id={user_id}">{user} помовчати на {time_sec} сек.</a>',
            'ping': 'Бот функціонує нормально. Серверний час: <code>{unix_time}</code>\n'
                    'Бот відреагував на повідомлення за <code>{working_time}</code> сек.\n'
                    'Бот не перезапускається вже <code>{uptime_sec}</code> сек.',
            'ban': 'Користувач <a href="tg://user?id={user_id}">{user}</a> забанений адміністратором <a href="tg://user?id={admin_id}">{admin}</a>. \nДля розбана використайте команду <code>/unban {user_id}</code>.',
            'unban': 'Користувач <a href="tg://user?id={user_id}">{user}</a> розбанений адміністратором <a href="tg://user?id={admin_id}">{admin}</a>',
            'kick': 'Користувач <a href="tg"//user?id={user_id}>{user}</a> виключений адміністратором <a href="tg://user?id={admin_id}">{admin}</a>',
            'get_users': {
                'title': 'Список активних користувачей чата <b>{chat_name}</b>: \n',
                'body_notify': '\n{user_number}. <a href="tg://user?id={user_id}">{user_name}</a> - <b>{user_count}</b> (<b>{percent}%</b>)',
                'body_silence': '\n{user_number}. {user_name} - <b>{user_count}</b> (<b>{percent}%</b>)',
                'end': '\n\Всього користувачів зафіксовано в чаті: <b>{users_count}</b>\n'
                       'Всього повідомлень зафіксовано в чаті: <b>{messages_count}</b>\n'
                       'Вы знаходитесь на <b>{user_place}-м</b> місці\n'
                       'Повідомлення сформовано за <code>{used_time}</code> сек.',
                'chat_response': {
                    'success': 'Результат відправлений вам в приватні повідомлення',
                    'fault': 'Напишіть боту в приватних повідомленнях / start, щоб він зміг відправляти вам повідомлення'
                },
            },
            'version': 'Версія бота: <b>{version}</b>'
        }
    },
    'uz': {
        'chosen_language': "Salom! Siz O‘zbek tilini tanladingiz. Keinchalik tilni o‘zgartirish uchun /language komandasini yuboring. \nEndi botdan foydalanish uchun yana bir bor /start ni bosing.",
        'start': 'Salom, men sizning guruhdagi yangi yordamchingizman. Mendan to‘liq foydalanish uchun o‘zingiz administrator bo‘lgan guruhga qo‘shib,menga ham administratorlik bering. So‘ngra shu yerga /help deb yozing',
        'help': 'Demak,menda bor buyuruqlar ro‘yxati:\n'
                '/start - Bot bilan muloqotni boshlaydi\n'
                '/help - Ushbu habarni jo‘natadi\n'
                '/about - Bot yaratuvchisi bilan aloqa va qo‘shimcha ma‘lumot\n'
                '/sticker_ban - Stikerni banlaydi, va shunday stikerli habarlarni o‘chiradi\n'
                '/ro - Biron bir foydalanuvchini bir qancha vaqt yoza olmaydigan qilib qo‘yadi.\n    Mavjud vaqt o‘lchamlari: sekund(s), minut(m), soat(h), kun(d). Agarda ushbu buyuruq aniq vaqtsiz jo‘natilsa,avtomatik tarzda 1 daqiqaga o‘qiy olmaydigan qilib qo‘yadi.\n'
                '/ping -Botning ish faoliyatini tekshiradi. Agarda bot 5 sekund ichida javob bermasa, ayni payitda juda ko‘p habarlar qayta ishlanyabdi,yoki server bilan bog‘liq muammo.',

        'about': 'Bot dan <a href="tg://user?id=303986717">F0rden</a>',

        'commands': {
            'sticker_ban':'Stiker <b>{0}</b> qora ro‘yxatga qo‘shildi. \nOlib tashlash uchun <code>/sticker_unban {0}</code> ni jo‘nating.',
            'sticker_unban':'<b>{}</b> qora ro‘yxatdan olib tashlandi.',
            'ro':'{} {} dan {} sec jim turishini so‘radi',
            'ping':'Men tirikman! Hozirgi UNIX-vaqt: <b>{}</b> sec.',
			'version': 'Bot versiya: <b>{version}</b>'
        }
    }
}

group_commands = {
    'ru': {
        'registration': 'Отлично! Я ваш новый админ и помогу в управлении чатом! \n'
                        'Чтобы получить справку - используйте команду /help (сначала нужно активировать бота, отправив ему в личные сообщения команду /start)\n'
                        'Пожалуйста, все администраторы группы, активируйте бота. Это необходимо для корректной работы всех функций',
        'ban_me_please': 'Твой выигрыш: {t} мин. рид-онли. Поздравляем✨✨\n',
        'errors':{
            'prefix': 'Извините, но я не могу вам помочь в этом: \n<b>{reason}</b>',
            'reasons':{
                'not_enough_rights': 'у вас недостаточно прав для совершения этого действия.',
                'no_such_sticker': 'данный стикер еще не был заблокирован.',
                'no_args_provided': 'не предоставлено ни одного аргумента.',
                'not_restricted': 'данный пользователь не был ограничен.',
                'global_not_banned': 'данный пользователь не находится в Глобальном Бане',
                'user_is_admin': 'пользователь является администратором',   
            },
            'db_error': {
                'got_error': 'Произошла ошибка, связанная с настройками вашего чата, выполняется сброс.',
                'finshed': 'Настройки чата сброшены, работа бота продолжится.'
            },
        },

        'stickers': {
            'banned': 'Стикер <b>{sticker_id}</b> заблокирован.\n'
                      'Для разблокировки попросите любого администратора ввести команду <code>/sticker_id {sticker_id}</code>',
            'unbanned': 'Стикер <b>{sticker_id}</b> разаблокирован.',
            'pack_banned': 'Заблокирован стикерпак <b>{stickerpack_name}</b>, содержащий <code>{count}</code> шт. стикеров.\n'
                           'Для разблокировки попросите администратора ввести команду <code>/stickerpack_unban {stickerpack_name}</code>',
            'pack_unbanned': 'Стикерпак <b>{stickerpack_name}</b> разблокирован.',
        },

        'restricted': {
            'url': 'Удалена ссылка от <a href="tg://user?id={user_id}">{user_name}</a>, так как в чате ссылки разрешены только для администрации.',
            'content': 'Сообщение от <a href="tg://user?id={user_id}">{user_name}</a> удалено, так как такие тип сообщений запрещен в чате.',
            'bot': 'Бот исключен, так как в чате запрещены боты.',
            'global_ban': '<a href="tg://user?id={user_id}">{user_name}</a> исключен, т.к. находится в Глобальном Бане.\n',
            'new_user': {
                'read_only': 'Пользователь <a href="tg://user?id={user_id}">{user_name}</a> ограничен на {ban_time} час.\n'
                             'Блокировка будет действовать до: {until_date}.',
                'button_pressed': 'Нажата кнопка, <a href="tg://user?id={user_id}">{user_name}</a> разблокирован.'
            }
        },
        
        'log_channel': {
            'confirmation': {
                'channel': 'Теперь сюда будут присылаться логи работы бота',
                'chat': 'Канала с логами установлен',
                'errors': {
                    'user_is_not_creator': 'Вы не являетесь создателем канала, у вас недостаточно прав.',
                    'bot_is_not_admin': 'Бот не является администратором канала и не может публиковать записи'
                }
            },
            'deletion': {
                'channel': 'Канал отключен',
                'chat': 'Канал с логами удален',
            },
            'new_chat_user': 'Новый пользователь <a href="tg://user?id={new_user_id}">{new_user_firstname}</a> в чате <b>{chat_name}</b>\n'
                             'ID: <code>{new_user_id}</code>\n'
                             'Имя: <b>{new_user_firstname}</b>\n'
                             'Фамилия: <b>{new_user_lastname}</b>\n'
                             'Юзернейм: @{new_user_username}\n\n'
                             'Время вступления: <b>{curr_date}</b>',
            'info': {
                'is_on': 'Канал подключен\n'
                         'ID канала: <code>{chat_id}</code>\n'
                         'Название канала: <b>{chat_name}</b>',
                'is_off': 'Канал не подключен'
            },
        },

        'users': {
            'global_ban': '<a href="tg://user?id={user_id}">{user_name}</a> попадает в Глобальный Бан.',
            'global_unban': '<a href="tg://user?id={user_id}">{user_name}</a> теперь не находится в глобальном бане',
            'warn': 'Пользователь <a href="tg://user?id={user_id}">{user_name}</a> предупрежден.\n'
                    'Кол-во предупреждений: <b>{current_warns}</b>.\n'
                    'Максимальное количество предупреждений, после которых пользователь исключается из группы: <b>{max_warns}</b>.',
            'kick': 'Пользователь <a href="tg://user?id={user_id}">{user_name}</a> исключен администратором <a href="tg://user?id={admin_id}">{admin_name}</a>.',
            'ro': '<a href="tg://user?id={admin_id}">{admin_name}</a> попросил <a href="tg://user?id={user_id}">{user_name}</a> помолчать на <code>{time_sec}</code>.\n'
                  'Блокировка будет действовать до: {until_date}.',
            'banned': 'Пользователь <a href="tg://user?id={user_id}">{user_name}</a> заблокирован администратором <a href="tg://user?id={admin_id}">{admin_name}</a>.\n'
                      'Для разблокировки введите команду <code>/unban {user_id}</code>',
            'unbanned': 'Пользователь <a href="tg://user?id={user_id}">{user_name}</a> разблокирован администратором <a href="tg://user?id={admin_id}">{admin_name}</a>.',
            'kicked_warns': 'Пользователь <a href="tg://user?id={user_id}">{user_name}</a> исключен за превышение допустимого числа предупреждений: <b>{count_warns}</b>',
            'ro_warns': 'Пользователь <a href="tg://user?id={user_id}">{user_name}</a> лишен права писать за превышение допустимого числа предупреждений: <b>{count_warns}</b>',
        },

        'refs_stats': {
            'header': 'Топ-10 пользователей чата по количеству приглашенных\n',
            'body': '{inviter_pos}. <a href="tg://user?id={inviter_id}">{inviter_firstname}</a> - <b>{invited_count}</b> шт.'
        },

        'donate': 'Ого, кто-то сюда зашел..\n'
                  'Ну, по такому поводу я могу предложить вам немного покормить разработчика любым из приведенных ниже способов:\n\n'
                  '<a href="https://money.yandex.ru/to/410012441742057">Яндекс.Деньги</a>: <code>410012441742057</code>\n'
                  '<a href="https://qiwi.me/b9ea24a2-7fb0-4094-9b30-fc128ff35c64">QIWI</a>\n'
                  'Банковская карта: <code>5106 2110 1622 4243</code>',
        
        'get_users': {
                'title': 'Список активных пользователей чата <b>{chat_name}</b>: \n',
                'body_notify': '\n{user_number}. <a href="tg://user?id={user_id}">{user_name}</a> - <b>{user_count}</b> (<b>{percent}%</b>)',
                'body_silence': '\n{user_number}. {user_name} - <b>{user_count}</b> (<b>{percent}%</b>)',
                'end': '\n\nВсего пользователей зафиксировано в чате: <b>{users_count}</b>\n'
                       'Всего сообщений зафиксировано в чате: <b>{messages_count}</b>\n'
                       'Вы находитесь на <b>{user_place}-м</b> месте\n'
                       'Сообщение сформированно за <code>{used_time}</code> сек.',
        },

        'chat_response': {
            'success': 'Результат отправлен вам в личные сообщения',
            'error': 'Напишите боту в личных сообщениях /start, чтобы он смог отправлять вам сообщения'
        },

        'remove_keyboard': 'Удаление клавиатуры..',

        'leave': {
            'question': 'Вы хотите изгнать меня из чата?..',
            'accepted': 'Ладно, прощайте, я старался быть полезным для вас..',
            'cancelled': 'Спасибо что дали мне шанс! Я не подведу!'
        }
    },
    'en': {},
    'ukr': {
        'ban_me_please': 'Твій виграш {t} мін. рід-онлі. Вітаємо✨✨',
        'errors':{
            'prefix': 'Вибач, але я не можу вам допомогти в цьому. Причина описана нижче: \n<b>{reason}</b>',
            'reasons': {
                'not_enough_rights': 'у вас недостатньо прав для вчинення цього діяння.',
                'no_such_sticker': 'цей стікер ще не заблокований.',
                'no_args_provided': 'не надано жодного аргументу.',
                'not_restricted': 'даний користувач не був обмежений.',
                'global_not_banned': 'даний користувач не знаходиться в Глобальному Бані.',
                'user_id_admin': 'користувач є адміністратором',
            },
            'db_error': {
                'got_error': 'Сталася помилка, повязана з налаштуваннями вашого чату, виконується скидання.',
                'finshed': 'Настройки чату скинуті, робота бота продовжиться.'
            },
        },

        'stickers': {
            'banned': 'Стікер <b>{sticker_id}</b> заблокований.\n'
                      'Для розблокування попросіть будь-якого адміністратора ввести команду <code>/sticker_id {sticker_id}</code>',
            'unbanned': 'Стікер <b>{sticker_id}</b> розблокований.',
            'pack_banned': 'Заблокований стікерпак <b>{stickerpack_name}</b>, містить <code>{count}</code> кількість стікерів.\n'
                           'Для розблокування попросіть адміністратора ввести команду <code>/stickerpack_unban {stickerpack_name}</code>',
            'pack_unbanned': 'Стікерпак <b>{stickerpack_name}</b> розблокований.',
        },

        'restricted': {
            'url': 'Видалено посилання від <a href="tg://user?id={user_id}">{user_name}</a>, так як в чаті посилання дозволені тільки для адміністрації.',
            'content': 'Повідомлення від <a href="tg://user?id={user_id}">{user_name}</a> видалено, так як такий тип повідомлень заборонений в чаті.',
            'bot': 'Бот вилучений, так як в чаті заборонені боти. Для того щоб додати його, незважаючи на це обмеження, необхідно додавати бота з правами адміністратора. Підійдуть будь-які права, а відразу після запрошення їх можна забрати.',
            'global_ban': '<a href="tg://user?id={user_id}">{user_name}</a> вилучений, т.к. знаходиться в Глобальному Бані.\n'
                          'Тепер, щоб додати його в чат є лише 3 варіанти: \n'
                          '1. Написати <a href="tg://user?id=303986717">мне</a> з докладною причиною, чому я повинен розбанити цю людину (просто так до Глобального Бану не потрапляють)\n'
                          '2. Додати користувача відразу адміністратором \n'
                          '3. Забрати права видалення користувачів у цього бота\n',
            'new_user': {
                'read_only': 'Користувач <a href="tg://user?id={user_id}">{user_name}</a> обмежений на {ban_time} годину, Тому що включена опція строгості до новачків. Вимкнути у налаштуваннях.\n',
                'button_pressed': 'Натиснута кнопка, <a href="tg://user?id={user_id}">{user_name}</a> розблокований.'
            }
        },

        'users': {
            'global_ban': '<a href="tg://user?id={user_id}">{user_name}</a> попадає в Глобальный Бан.',
            'global_unban': '<a href="tg://user?id={user_id}">{user_name}</a> тепер не знаходиттся в Глобальному Бані',
            'warn': 'Користувач <a href="tg://user?id={user_id}">{user_name}</a> попереджений.\n'
                    'Кількість попереджень: <b>{current_warns}</b>.\n'
                    'Максимальна кількість попереджень, після яких користувач вилучається з групи: <b>{max_warns}</b>.',
            'kick': 'Користувач <a href="tg://user?id={user_id}">{user_name}</a> вилучений адміністратором <a href="tg://user?id={admin_id}">{admin_name}</a>.',
            'ro': '<a href="tg://user?id={admin_id}">{admin_name}</a> попросив <a href="tg://user?id={user_id}">{user_name}</a> помовчати <code>{time_sec}</code> сек.',
            'banned': 'Користувач <a href="tg://user?id={user_id}">{user_name}</a> заблокований адміністратором <a href="tg://user?id={admin_id}">{admin_name}</a>.\n'
                      'Для разблокировки введите команду <code>/unban {user_id}</code>',
            'unbanned': 'Користувач <a href="tg://user?id={user_id}">{user_name}</a> розблокований адміністратором <a href="tg://user?id={admin_id}">{admin_name}</a>.',
            'kicked_warns': 'Користувач <a href="tg://user?id={user_id}">{user_name}</a> вилучений за перевішення допустимого числа попереджень: <b>{count_warns}</b>',
            'ro_warns': 'Користувач <a href="tg://user?id={user_id}">{user_name}</a> позбавлений права писати за перевищення допустимого числа попередження: <b>{count_warns}</b>',
        },
        'donate': 'Ого, хтось сюди зайшов ..\n'
                   'Ну, по такому приводу я можу запропонувати тобі трохи погодувати розробника будь-яким з наведених нижче способів:\n\n'
                  '<a href="https://money.yandex.ru/to/410012441742057">Яндекс.Деньги</a>: <code>410012441742057</code>\n'
                  '<a href="https://qiwi.me/b9ea24a2-7fb0-4094-9b30-fc128ff35c64">QIWI</a>\n'
                  'Банківська карта: <code>5106 2110 1622 4243</code>'
    },
    'uz': {},
}

service_messages = {
    'new_user': 'Зарегистрирован новый пользователь. \n' \
                'Имя: <a href="tg://user?id={user_id}">{user_name}</a>\n' \
                'ID: <code>{user_id}</code>\n' \
                'Всего пользователей в базе: <b>{user_amount}</b>\n'
                'Выбранный язык: <b>{user_lang}</b>',

    'new_chat': 'Зарегистрирован новый чат\n'
                'Название: <b>{chat_name}</b>\n'
                'Создатель: <a href="tg://user?id={admin_id}">{admin_name}</a>\n'
                'ID: <code>{chat_id}</code>\n'
                'Численность группы: <b>{chat_users_amount}</b> чел.\n'
                'Всего чатов в базе: <b>{chat_amount}</b> шт.',
                
    'broadcast': {
        'users': 'Рассылка началась\n'
                 'Сообщение получило <code>{chats_sent}/{all_chats}</code> ({all_perc}%) чел.\n'
                 'Успешно отправлено (пользователи): <b>{successfully_sent_users}</b> ({perc_suc_users}%)\n'
                 'Неудачно отправлено (пользователи): <b>{errors_sent_users}</b> ({perc_err_users}%)\n'
                 '[{pbar_users:<20}]\n'
                 'Средняя скорость: <b>{speed}</b> чел/сек.\n'
                 'Прошло: <code>{spent_time}</code>\n'
                 'Осталось: <code>{eta}</code>\n'
                 '[{pbar:<20}]',
                 
        'chats': 'Рассылка началась\n'
                 'Сообщение получило <code>{chats_sent}/{all_chats}</code> ({all_perc}%) чатов\n'
                 'Успешно отправлено (чаты): <b>{successfully_sent_chats}</b> ({perc_suc_chats}%)\n'
                 'Неудачно отправлено (чаты): <b>{errors_sent_chats}</b> ({perc_err_chats}%)\n'
                 '[{pbar_chats:<20}]\n'
                 'Средняя скорость: <b>{speed}</b> чатов/сек.\n'
                 'Прошло: <code>{spent_time}</code>\n'
                 'Осталось: <code>{eta}</code>\n'
                 '[{pbar:<20}]',
        
        'all': 'Рассылка началась\n'
               'Сообщение получило <code>{chats_sent}/{all_chats}</code> ({all_perc}%) \n'
               'Успешно отправлено (пользователи): <b>{successfully_sent_users}</b> ({perc_suc_users}%)\n'
               'Неудачно отправлено (пользователи): <b>{errors_sent_users}</b> ({perc_err_users}%)\n'
               '[{pbar_users:<20}]\n'
               'Успешно отправлено (чаты): <b>{successfully_sent_chats}</b> ({perc_suc_chats}%)\n'
               'Неудачно отправлено (чаты): <b>{errors_sent_chats}</b> ({perc_err_chats}%)\n'
               '[{pbar_chats:<20}]\n'
               'Средняя скорость: <b>{speed}</b> сообщений/сек.\n'
               'Прошло: <code>{spent_time}</code>\n'
               'Осталось: <code>{eta}</code>\n'
               '[{pbar:<20}]',
    },
                 
                 
    'stats': 'Статистика\n'
             'Всего пользователей: <code>{all_users}</code>\n'
             'Всего чатов: <code>{all_chats}</code>\n'
             'Бот работает в <b>{unblocked_chats}</b> чатах\n'
             'Бот активирован у <b>{unblocked_users}</b> человек\n'
             'Статистика обновляется после каждой тестовой или настоящей рассылки. Это сообщение обновляется после нажатия на кнопку'
}

promotion_message = '<b>Лучший бот для администраторов групп - </b>t.me/zukuzukubot'
    
reports_messages = {
    'report': {
       'to_admin': { 
                'no_username': 'Вас вызвали в группе <b>{group_name}</b>, прошу обратить внимание.\n'
                               'Отправитель - <a href="tg://user?id={user_id}">{user_name}</a>.',
                'have_username': {
                    'reply': 'Вас вызвали в группе <a href="t.me/{group_username}/{message_id}">{group_name}</a>, прошу обратить внимание.\n'
                             'Отправитель - <a href="tg://user?id={user_id}">{user_name}</a>.',
                    'no_reply': 'Вас вызвали в группе <a href="t.me/{group_username}">{group_name}</a>, прошу обратить внимание.\n'
                             'Отправитель - <a href="tg://user?id={user_id}">{user_name}</a>.',
                }
        },
       'to_user': 'Спасибо, мы обработаем ваше обращение.\n' 
                  '<b>Учтите, что спам данной командой часто влечет за собой наказание со стороны администрации чата.</b>'
    }
}
