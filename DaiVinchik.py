import asyncio
from pyrogram.handlers import MessageHandler
import re
import sys

from config import app_daivinchik, vinchik_id
from pyrogram import filters


async def handle_message(client, message):
    await asyncio.sleep(2)
    print("спим 2 секунды...")
    # чекает, подпись к фото или просто текст.
    if message.text is not None:
        print(message.text)
        sympathy = "Есть взаимная симпатия! Начинай общаться"
        if sympathy in message.text:
            if message.entities:
                await sympathyChecker(message)
        new_message = message.text
        await adChecker(new_message)
        # await sympathyChecker(new_message)
    elif message.caption is not None:
        # Ищет, есть ли в подписи цифры
        digits = re.findall(r'\d+', message.caption)
        if digits:
            if 17 < int(digits[0]) < 30:
                # Если есть от 18 до 30, то отправляет сердечко
                print("спим 5 секунд...")
                await asyncio.sleep(5)
                await client.send_message(chat_id=vinchik_id, text="❤️")
                print(message.caption, " Отправлено сердечко! возраст: ", digits[0])
            else:
                # если нет, то отправляет палец вниз
                print("спим 5 секунд...")
                await asyncio.sleep(5)
                await client.send_message(chat_id=vinchik_id, text="\U0001F44E")
                print(message.caption, " Отправлен палец вниз! возраст: ", digits[0])

        else:
            print(message.caption, " passed NO DIGITS FOUND")
    else:
        print("passed NO message.text, NO message.caption")


async def adChecker(message):
    ad_phrases = ["Лайк отправлен, ждем ответа.", "\U0001F44E", "❤️", "❤", "Бот знакомств", "варианта ответа", "анкеты",
                  "🔍", "✨", "✨🔍", "1", "2", "3", "4" "Нет", "Возможно позже"]
    for ad_phrase in ad_phrases:
        if ad_phrase in message:
            print("passed because ", ad_phrase, " was found in message")
        else:
            await stopChecker(message)


async def stopChecker(message):
    stop_phrases = ["Слишком много", "слишком много", "пока все", "пока всё"]
    for stop_phrase in stop_phrases:
        if stop_phrase in message:
            print("Работа завершена потому что ", message)
            sys.exit()
        else:
            await likeChecker(message)


async def likeChecker(message):
    like_phrases = ["понравился", "панравился", "1. Смотреть анкеты.", "Смотреть"]
    for like_phrase in like_phrases:
        if like_phrase in message:
            print("спим 5 секунд...")
            await asyncio.sleep(5)
            await app_daivinchik.send_message(chat_id=vinchik_id, text="1 🚀")
            print("Отправляем '1 🚀' в ответ на ", message, " потому что была найдена ", like_phrase)
        else:
            print("passed в ответ на ", message)

async def marketChecker(message):
    market_phrases = ["TG", "VK", "ТГ", "ВК", "Telegram"]
    for market_phrase in market_phrases:
        if market_phrase in message:
            await asyncio.sleep(5)
            print("Спим 5 секунд...")
            await app_daivinchik.send_message(chat_id=vinchik_id, text="Анкеты в Telegram")
            print("Отправляем 'Анкеты в телеграм' в ответ на ", market_phrase)

async def sympathyChecker(message):
    url = message.entities[0].url
    username = url.replace("https://t.me/", "")
    print("Есть симпатия! Ссылка на девушку: ", url, " \nUsername: ", username)
    print("Пишем девушке...")
    user = await app_daivinchik.get_users(username)
    await app_daivinchik.send_message(username, "Привет, как ты?")


my_handler = MessageHandler(handle_message, filters.chat(vinchik_id))
app_daivinchik.add_handler(my_handler)

app_daivinchik.run()
