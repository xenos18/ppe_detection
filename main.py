import os
import asyncio

from dotenv import load_dotenv
from datetime import datetime
from database import DataBase
from telebot import types
from telebot.async_telebot import AsyncTeleBot

load_dotenv()

# Initialize the bot with async_telebot
bot = AsyncTeleBot(os.environ.get("BOT_TOKEN"))
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
async def start(message):
    print(f"Logs:t{datetime.now()}tmessage from {message.from_user.username}")
    keyboard = types.InlineKeyboardMarkup()
    callback_button = types.InlineKeyboardButton(text="Получить фото", callback_data="get_photo")
    keyboard.add(callback_button)
    await bot.send_message(
        chat_id=message.chat.id,
        text="👋 Привет! Я бот команды Biocad. Нажми на кнопку ниже и получи свое фото 😉",
        reply_markup=keyboard,
    )


@bot.message_handler(commands=["start"])
async def start(message):
    print(f"Logs:t{datetime.now()}tmessage from {message.from_user.username}")
    keyboard = types.InlineKeyboardMarkup()
    callback_button = types.InlineKeyboardButton(text="Получить фото", callback_data="get_photo")
    keyboard.add(callback_button)
    await bot.send_message(
        chat_id=message.chat.id,
        text="👋 Привет! Я бот команды Biocad. Нажми на кнопку ниже и получи свое фото 😉",
        reply_markup=keyboard,
    )


async def send_photo(message):
    print(f"Logs:t{datetime.now()}tmessage from {message.from_user.username}")
    try:
        user = get_user(message)
        balance = int(user["balance"])
        if balance <= 0:
            await bot.send_message(message.chat.id, "Лимит фото исчерпан. Далее 1 фото стоит 1 у. е.")
        else:
            balance -= 1
            data_base.update_balance(str(balance), username=user["username"])
            msg = await bot.send_message(message.chat.id, "7...")
            for i in range(6, -1, -1):
                await asyncio.sleep(1)
                await bot.edit_message_text(message_id=msg.id, chat_id=message.chat.id, text=f"{i}...")
            await bot.delete_message(message_id=msg.id, chat_id=message.chat.id)
            with open(image, "rb") as photo:
                await bot.send_photo(message.chat.id, photo)
    except Exception as e:
        try:
            await bot.send_message(message.chat.id, "Что-то пошло не так 😕")
        except:
            pass
        print(e)


@bot.message_handler(commands=["photo"])
async def photo(message):
    await send_photo(message)


@bot.callback_query_handler(func=lambda call: True)
async def callback_inline(call):
    await send_photo(call.message)


@bot.message_handler(commands=["balance"])
async def get_balance(message):
    user = get_user(message)
    await bot.send_message(message.chat.id, f"Ваш баланс {user['balance']} у. е.")


@bot.message_handler(content_types=['text'])
async def get_text_messages(message):
    user = get_user(message)
    if int(user["admin"]):
        username, addition = message.text.split()
        user = data_base.get_user(username=username)[0]
        balance = int(user["balance"]) + int(addition)
        data_base.update_balance(str(balance), username=username)
        await bot.send_message(message.chat.id, "Баланс успешно пополнен!")


async def main():
    await bot.polling()


if __name__ == "__main__":
    asyncio.run(main())
