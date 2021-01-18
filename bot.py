# -*- coding: utf8 -*-
from aiogram import executor

import logging
import sqlite3
import json

from os import environ
from aiogram import Bot, Dispatcher

if "TOKEN" in environ:
    TOKEN = environ["TOKEN"]

else:
    with open("token.json") as file:
        token = json.loads(file.read())
        TOKEN = token["token"]

        heroku = False

with open("data/ideologies.json", encoding="UTF8") as file:
    ideologies = json.loads(file.read())

with open("data/questions.json", encoding="UTF8") as file:
    questions = json.loads(file.read())

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=["start"])
async def start(message):
    await message.reply("<b>8values</b> — это, по сути, политическая викторина, которая пытается присвоить проценты восьми различным политическим ценностям. Вам будут даны утверждения, по каждому из которых вы должны ответить своим мнением, от <b>Полностью согласен</b> до <b>Полностью не согласен</b>, каждый ответ будет слегка влиять на ваши значения по каждой оси. В конце викторины, ваши ответы будут сравниваться с максимально возможным для каждого значения, таким образом, давая вам процент. Отвечайте честно!\n\nВ данном тесте <b>70</b> вопросов.", parse_mode="HTML")  # noqa: E501

executor.start_polling(dp)
