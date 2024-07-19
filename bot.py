# -*- coding: utf-8 -*-

API_TOKEN = '7185791418:AAFrwICeIz5Z6LC5cc5_nlzRgc4qwzdrztQ'

import telebot
import mysql.connector
from telebot import types
import logging

CHANNEL_ID = '@projectaprils' # Замените на ваш ID канала

# Функция для подключения к базе данных
def db_connect():
    try:
        conn = mysql.connector.connect(
            host='server41.hosting.reg.ru',
            user='u2722842_eugpriv',
            passwd='eugprivEUGPRIV',
            database='u2722842_referal'
        )
        return conn
    except mysql.connector.Error as err:
        logging.error(f"Error: {err}")
        return None

# Функция для инициализации базы данных
def initialize_database():
    conn = db_connect()
    if conn is None:
        logging.error("Не удалось подключиться к базе данных для инициализации.")
        return
    cursor = conn.cursor()
    try:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS referrals (
                userId INT PRIMARY KEY,
                userName VARCHAR(255),
                referralId INT,
                score INT DEFAULT 0,
                last_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        logging.info("Таблица referrals успешно создана или уже существует.")
    except mysql.connector.Error as err:
        logging.error(f"Ошибка создания таблицы: {err}")
    finally:
        conn.close()

# Создание экземпляра бота
bot = telebot.TeleBot(API_TOKEN)

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def start(message, call=None):
    user_info = message.from_user
    referral_id = None
    if len(message.text.split()) > 1:
        ref_arg = message.text.split()[1]
        if ref_arg.startswith('ref'):
            referral_id = ref_arg[3:]
            if not referral_id.isdigit():
                referral_id = None
        else:
            referral_id = None
    save_referral(user_id=user_info.id, user_name=user_info.first_name, referral_id=referral_id)
    
    conn = db_connect()
    if conn is None:
        logging.error("Не удалось подключиться к базе данных.")
        return
    cursor = conn.cursor()
    cursor.execute('SELECT score FROM referrals WHERE userId = %s', (user_info.id,))
    result = cursor.fetchone()
    conn.close()
    
    if result is None:
        score = 0
    else:
        score = result[0]
    
    welcome_text = (
        f"Привет {user_info.first_name}!\n"
        f"На текущий момент у тебя {score} 🧀.\n"
        "Сейчас они ничего не стоят, но всё может измениться в будущем, кто знает...\n"
        "Приумножайте свои монетки, выполняя задания и приглашая друзей. И помни, что всё зависит только от тебя!"
    )
    
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton('Mini app SOON', callback_data='mini_app')
    btn2 = types.InlineKeyboardButton('Пригласить друзей', callback_data='invite_friends')
    btn3 = types.InlineKeyboardButton('Задания', callback_data='tasks')
    btn4 = types.InlineKeyboardButton('Заработано', callback_data='score')
    markup.add(btn1)
    markup.add(btn2)
    markup.add(btn3)
    markup.add(btn4)
    
    if call:
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=welcome_text, reply_markup=markup)
    else:
        bot.send_message(message.chat.id, welcome_text, reply_markup=markup)

@bot.message_handler(commands=['ref'])
def ref(message, call=None):
    user_info = message.from_user
    user_id = user_info.id
    referral_link = f"https://t.me/ProjectAprilBot?start=ref{user_id}"
    markup = types.InlineKeyboardMarkup()
    forward_button = types.InlineKeyboardButton('Переслать ссылку', switch_inline_query=f"{referral_link}")
    tasks_button = types.InlineKeyboardButton('Задания', callback_data='tasks')
    score_button = types.InlineKeyboardButton('Заработано', callback_data='score')
    markup.add(forward_button)
    markup.add(tasks_button)
    markup.add(score_button)
    if call:
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f"Твоя реферальная ссылка для приглашения друзей: {referral_link}", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, f"Твоя реферальная ссылка для приглашения друзей: {referral_link}", reply_markup=markup)
        
# Обработчик команды /tasks
@bot.message_handler(commands=['tasks'])
def tasks(message, call=None):
    user_info = message.from_user
    task_text = "Выполни задания для получения дополнительных наград."
    button = types.InlineKeyboardButton(text="Подпишись на группу - 100 🧀", url="https://t.me/projectaprils")
    score_button = types.InlineKeyboardButton('Заработано', callback_data='score')
    reply_markup = types.InlineKeyboardMarkup().add(button).add(score_button)
    if call:
        msg = bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=task_text, reply_markup=reply_markup)
    else:
        msg = bot.send_message(message.chat.id, task_text, reply_markup=reply_markup)
    
    if check_subscription(user_info.id):
        add_score(user_info.id, 100)
        new_button = types.InlineKeyboardButton(text="Задание выполнено ✅", callback_data="subscribed")
        new_reply_markup = types.InlineKeyboardMarkup().add(new_button).add(score_button)
        bot.edit_message_reply_markup(chat_id=message.chat.id, message_id=msg.message_id, reply_markup=new_reply_markup)

# Обработчик команды /score
@bot.message_handler(commands=['score'])
def score(message, call=None):
    user_info = message.from_user
    conn = db_connect()
    if conn is None:
        logging.error("Не удалось подключиться к базе данных.")
        return
    cursor = conn.cursor()
    cursor.execute('SELECT score FROM referrals WHERE userId = %s', (user_info.id,))
    result = cursor.fetchone()
    conn.close()
    
    if result is None:
        score = 0
    else:
        score = result[0]
    
    score_text = f"Заработано {score} 🧀"
    tasks_button = types.InlineKeyboardButton('Задания', callback_data='tasks')
    invite_button = types.InlineKeyboardButton('Пригласить друзей', callback_data='invite_friends')
    reply_markup = types.InlineKeyboardMarkup().add(tasks_button).add(invite_button)
    
    if call:
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=score_text, reply_markup=reply_markup)
    else:
        bot.send_message(message.chat.id, score_text, reply_markup=reply_markup)

# Обработчик нажатий на кнопки
@bot.callback_query_handler(func=lambda call: call.data in ['invite_friends', 'tasks', 'score'])
def handle_inline_buttons(call):
    print(f"Button pressed: {call.data}")
    if call.data == 'invite_friends':
        ref(call.message, call)
    elif call.data == 'tasks':
        tasks(call.message, call)
    elif call.data == 'score':
        score(call.message, call)

# Функция для сохранения рефералов
def save_referral(user_id, user_name, referral_id):
    conn = db_connect()
    if conn is None:
        logging.error("Не удалось подключиться к базе данных.")
        return
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO referrals (userId, userName, referralId, last_used)
        VALUES (%s, %s, %s, CURRENT_TIMESTAMP)
        ON DUPLICATE KEY UPDATE last_used = CURRENT_TIMESTAMP
    ''', (user_id, user_name, referral_id))
    conn.commit()
    conn.close()

# Функция для проверки подписки
def check_subscription(user_id):
    # Логика проверки подписки
    return True

# Функция для добавления очков
def add_score(user_id, score):
    conn = db_connect()
    if conn is None:
        logging.error("Не удалось подключиться к базе данных.")
        return
    cursor = conn.cursor()
    cursor.execute('UPDATE referrals SET score = score + %s WHERE userId = %s', (score, user_id))
    conn.commit()
    conn.close()

# Инициализация базы данных
initialize_database()

# Запуск бота
bot.polling(none_stop=True)
