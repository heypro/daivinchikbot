import os
import openai
import sys
import argparse
import json
import multiprocessing

import config
from config import app
from config import app_crash
import asyncio
from pyrogram.handlers import MessageHandler
import time
from pyrogram import filters

openai.api_key = "API_KEY_HERE"

argparser = argparse.ArgumentParser()
argparser.add_argument('--arg_messages_stack', help='messages_stack')
args = argparser.parse_args()

context = {}
messages_stack = {} #{user_id : {chat_id : , last_message_id : , messages : [messages..])}
old_messages_stack = {}
if args.arg_messages_stack:
    old_messages_stack = json.loads(args.arg_messages_stack)

async def get_message(client, message):
    # чекает, не из дайвинчика ли сообщение
    if message.chat.id != config.vinchik_id:
        print("Получено сообщение! Юзер говорит: ", message.text)
        chatid = message.chat.id
        user_id = message.from_user.id
        new_message = message.text
        message_id = 0
        #добавляем сообщение в стек ожидания для пользователя
        if user_id in messages_stack:
            message_id = messages_stack[user_id]['last_message_id'] + 1
            messages_stack[user_id]['message_id'] = message_id
            messages_stack[user_id]['messages'].append(message.text)
        else:
            messages_stack[user_id] = {'chat_id' : chatid, 'last_message_id' : 0, 'messages' : [message.text]}
        await asyncio.sleep(10) #задержка перед ответом на стек сообщений
        #проверяем : если last_message_id совпадает с нашим id, значит новых сообщений не было
        #и можно отправлять в api, если не совпадает, значит пришло новое сообщение
        if messages_stack[user_id]['last_message_id'] == message_id:
            await generate_response(app, '. '.join(messages_stack[user_id]['messages']), chatid, user_id)
            del messages_stack[user_id]


async def generate_response(app, answer, chatid, user_id):
    # заполняет словарь чтобы промпт каждый раз соответствовал контексту,
    # а не был "Привет, как ты?"
    if user_id in context:
        story = context[user_id]["story"]
        prompt = context[user_id]["prompt"]
        prompt_with_answer = prompt + story + "\nДевушка отвечает: " + answer + "\nИлья отвечает: "
    else:
        # If there's no existing story, start with an empty story and the original prompt
        story = ""
        prompt = "Илья - одинокий мужчина, живущий в Москве, точнее, в районе Алтуфьево. Он студент в НИУ МЭИ и любит играть " \
                 "на гитаре и играть в баскетбол. Илья очень смешной. Он очень любопытен и всегда " \
                 "задает много вопросов. Он добрый и всегда хочет узнать больше о других людях.\nОн пользуется приложением " \
                 "для знакомств и общается с девушкой в приложении под названием ДайВинчик. Илья не любит выходить из дома и предпочитает общение в сети. " \
                 "Он не хочет делать что-то с другими людьми. Он очень сильный интроверт. Илья общается с девушкой в телеграме, который еще называется тг." \
                 "\nИлья говорит: Привет, как ты? "
        prompt += prompt
        prompt_with_answer = prompt + "\nДевушка отвечает: " + answer + "\nИлья отвечает: "
    # API OpenAI дополняет ответ Ильи
    try:
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=prompt_with_answer,
            temperature=0.7,
            max_tokens=256,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )
    except openai.error.InvalidRequestError:
        print(json.dumps(messages_stack))
        os.execl(sys.executable, sys.executable, *['ChatGPT.py', '--arg_messages_stack', json.dumps(messages_stack)])
    bot_response = response.choices[0].text
    story += "\nДевушка отвечает: " + answer + "\nИлья отвечает: " + bot_response
    print(prompt_with_answer + bot_response)
    context[user_id] = {"story": story, "prompt": prompt}
    await send_message(app, bot_response, chatid)


async def send_message(app, answer, chatid):
    # спит 10 сек и отправляет сообщение
    await asyncio.sleep(10)
    await app.send_message(chat_id=chatid, text=answer)

def crash_rec():
    app_crash.run(crash_recovery())
async def crash_recovery():
    await app_crash.start()
    for user_id in old_messages_stack:
        await generate_response(
                            app_crash,
                            '. '.join(old_messages_stack[user_id]['messages']),
                            old_messages_stack[user_id]['chat_id'],
                            user_id)
        await app_crash.stop()
response_handler = MessageHandler(get_message, filters.incoming & filters.private)
app.add_handler(response_handler)
crash_rec_proc = multiprocessing.Process(target=crash_rec)
crash_rec_proc.start()
app.run()
