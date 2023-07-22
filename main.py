import os
import asyncio
import random
import time

from dotenv import load_dotenv
from datetime import datetime
from database import DataBase
from telebot import types
from telebot.async_telebot import AsyncTeleBot

load_dotenv()

bot = AsyncTeleBot(os.environ.get("BOT_TOKEN"))
image = os.environ.get("IMAGE_PATH")
data_base = DataBase()

with open("jokes.txt", "r", encoding="utf-8") as jokes:
    jokes = [i.rstrip() for i in jokes.readlines()]


def get_time():
    return int(str(time.time()).split(".")[0])


def get_user(message):
    telegram_user = message.from_user
    users = data_base.get_user(telegram_id=message.from_user.id)
    if len(users) == 0:
        data_base.add_user(telegram_user.id, get_time())
        user = data_base.get_user(telegram_id=message.from_user.id)[0]
    else:
        user = users[0]
    return user


@bot.message_handler(commands=["start"])
async def start(message):
    print(f"Logs:\t{datetime.now()}\tmessage from {message.from_user.username}\t\tstart")
    keyboard = types.InlineKeyboardMarkup()
    callback_button = types.InlineKeyboardButton(text="Получить фото", callback_data="get_photo")
    keyboard.add(callback_button)
    await bot.send_message(
        chat_id=message.chat.id,
        text="👋 Привет! Я бот команды Biocad. Нажми на кнопку ниже и получи свое фото 😉",
        reply_markup=keyboard,
    )


async def delay(duration, chat_id):
    msg = await bot.send_message(chat_id, f"{duration}...")
    for i in range(duration - 1, -1, -1):
        await asyncio.sleep(1)
        await bot.edit_message_text(message_id=msg.id, chat_id=chat_id, text=f"{i}...")
    await bot.delete_message(message_id=msg.id, chat_id=chat_id)


async def send_photo(message):
    print(f"Logs:\t{datetime.now()}\tmessage from {message.from_user.username}\t\tphoto")
    try:
        user = get_user(message)
        usages = int(user["usages"])
        last_usage = int(user["last_usage"])
        cur_time = get_time()
        if usages > 10 and cur_time - last_usage < 10 * (usages - 10):
            await bot.send_message(message.chat.id,
                                   f"Вы сможете воспользоваться ботом через {10 * (usages - 10) - cur_time + last_usage} с.")
        else:
            data_base.add_usage(user["telegram_id"], usages + 1, cur_time)
            await delay(4, chat_id=message.chat.id)
            with open(image, "rb") as photo:
                await bot.send_photo(message.chat.id, photo, caption=random.choice(jokes))
    except Exception as e:
        try:
            await bot.send_message(message.chat.id, "Что-то пошло не так 😕")
        except:
            pass
        print(e)


@bot.message_handler(commands=["photo"])
async def take_photo(message):
    await send_photo(message)


@bot.callback_query_handler(func=lambda call: True)
async def callback_inline(call):
    await send_photo(call.message)


@bot.message_handler(commands=["balance"])
async def get_balance(message):
    user = get_user(message)
    await bot.send_message(message.chat.id, f"Ваш баланс {user['balance']} у. е.")


async def main():
    await bot.infinity_polling(timeout=1000)


if __name__ == "__main__":
    asyncio.run(main())
