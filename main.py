import os
import time

import telebot
from telebot import types
from dotenv import load_dotenv
from datetime import datetime
from database import DataBase

load_dotenv()

bot = telebot.TeleBot(os.environ.get("BOT_TOKEN"))
image = os.environ.get("IMAGE_PATH")
data_base = DataBase()


def get_user(message):
    telegram_user = message.from_user
    user = data_base.get_user(username=message.from_user.username)
    if len(user) == 0:
        data_base.add_user(telegram_user.id, telegram_user.username, "3", "0")
    user = data_base.get_user(username=message.from_user.username)[0]
    return user


@bot.message_handler(commands=["start"])
def start(message):
    print(f"Logs:\t{datetime.now()}\tmessage from {message.from_user.username}")
    keyboard = types.InlineKeyboardMarkup()
    callback_button = types.InlineKeyboardButton(text="Получить фото", callback_data="get_photo")
    keyboard.add(callback_button)
    bot.send_message(
        chat_id=message.chat.id,
        text="👋 Привет! Я бот команды Biocad. Нажми на кнопку ниже и получи свое фото 😉",
        reply_markup=keyboard,
    )


@bot.message_handler(commands=["start"])
def start(message):
    print(f"Logs:\t{datetime.now()}\tmessage from {message.from_user.username}")
    keyboard = types.InlineKeyboardMarkup()
    callback_button = types.InlineKeyboardButton(text="Получить фото", callback_data="get_photo")
    keyboard.add(callback_button)
    bot.send_message(
        chat_id=message.chat.id,
        text="👋 Привет! Я бот команды Biocad. Нажми на кнопку ниже и получи свое фото 😉",
        reply_markup=keyboard,
    )


def send_photo(message):
    print(f"Logs:\t{datetime.now()}\tmessage from {message.from_user.username}")
    try:
        user = get_user(message)
        balance = int(user["balance"])
        if balance <= 0:
            bot.send_message(message.chat.id, "Лимит фото исчерпан. Далее 1 фото стоит 1 у. е.")
        else:
            balance -= 1
            data_base.update_balance(str(balance), username=user["username"])
            msg = bot.send_message(message.chat.id, "7...")
            for i in range(6, -1, -1):
                time.sleep(1)
                bot.edit_message_text(message_id=msg.id, chat_id=message.chat.id, text=f"{i}...")
            bot.delete_message(message_id=msg.id, chat_id=message.chat.id)
            with open(image, "rb") as photo:
                bot.send_photo(message.chat.id, photo)
    except Exception as e:
        try:
            bot.send_message(message.chat.id, "Что-то пошло не так 😕")
        except:
            pass
        print(e)


@bot.message_handler(commands=["photo"])
def photo(message):
    send_photo(message)


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    send_photo(call.message)


@bot.message_handler(commands=["balance"])
def get_balance(message):
    user = get_user(message)
    bot.send_message(message.chat.id, f"Ваш баланс {user['balance']} у. е.")


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    user = get_user(message)
    if int(user["admin"]):
        username, addition = message.text.split()
        user = data_base.get_user(username=username)[0]
        balance = int(user["balance"]) + int(addition)
        data_base.update_balance(str(balance), username=username)
        bot.send_message(message.chat.id, "Баланс успешно пополнен!")


bot.infinity_polling(timeout=1000, long_polling_timeout=5)
print("OK")
