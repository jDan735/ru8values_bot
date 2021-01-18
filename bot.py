# -*- coding: utf8 -*-
from aiogram import executor

import logging
import json
import yaml
import math

from os import environ
from aiogram import Bot, Dispatcher
from aiogram import types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

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

max_econ, max_dipl, max_govt, max_scty = 0, 0, 0, 0
for question in questions:
    max_econ += question["effect"]["econ"]
    max_dipl += question["effect"]["dipl"]
    max_govt += question["effect"]["govt"]
    max_scty += question["effect"]["scty"]

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=["start"])
async def start(message):
    q = 1
    call = f"{{q: {q}, econ: 0, dipl: 0, govt: 0, scty: 0}}"

    start_btn = InlineKeyboardButton(text="Начать тест",
                                     callback_data=call)
    keyboard = InlineKeyboardMarkup().add(start_btn)

    await message.reply('<b>8values</b> — это, по сути, политическая викторина, которая пытается присвоить проценты восьми различным политическим ценностям. Вам будут даны утверждения, по каждому из которых вы должны ответить своим мнением, от <b>🟢 (Полностью согласен)</b> до <b>🔴 (Полностью не согласен)</b>, каждый ответ будет слегка влиять на ваши значения по каждой оси. В конце викторины, ваши ответы будут сравниваться с максимально возможным для каждого значения, таким образом, давая вам процент. Отвечайте честно!\n\nВ данном тесте <b>69</b> вопросов.\n\nФорк и часть перевода сделаны <a href="https://t.me/ysamtme">@ysamtme</a> (буду рад сообщениям об ошибках и неточностях). Бот сделан <a href="t.me/jdan734">@jDan734</a>', disable_web_page_preview=True, parse_mode="HTML", reply_markup=keyboard)  # noqa: E501


def calc_score(score, max_):
    return (100 * (max_ + score) / (2 * max_))


@dp.callback_query_handler(lambda call: call.data.startswith("{"))
async def process_callback_button1(call: types.CallbackQuery):
    data = yaml.load(call.data)
    q_max = len(questions) - 1
    q_id = int(data["q"])

    if data["q"] > q_max:
        await bot.answer_callback_query(call.id)

        equality = calc_score(data["econ"], max_econ)
        peace = calc_score(data["dipl"], max_dipl)
        liberty = calc_score(data["govt"], max_govt)
        progress = calc_score(data["scty"], max_scty)

        ideology = ""

        for ideology in ideologies:
            dist = 0
            dist += (ideology["stats"]["econ"] - equality) ** 2
            dist += (ideology["stats"]["govt"] - liberty) ** 2
            dist += (ideology["stats"]["dipl"] - peace) ** 1.73856063
            dist += (ideology["stats"]["scty"] - progress) ** 1.73856063
            if isinstance(dist, complex):
                ideology_ = ideology["name"]

        ideology = f"Ваша идеология: <b>{ideology_}</b>"

        await bot.edit_message_text(chat_id=call.message.chat.id,
                                    message_id=call.message.message_id,
                                    text=ideology, parse_mode="HTML")
        return

    data["q"] += 1
    question = questions[q_id]

    keyboard = InlineKeyboardMarkup()

    btns = []
    for num, btn_text in enumerate(["🟢", "🟩", "⬜️", "🟥", "🔴"]):
        new_data = data.copy()
        prop = [1, 0.5, 0, -0.5, -1]
        del_ = prop[num]

        for param in ["econ", "dipl", "govt", "scty"]:
            new_data[param] += question["effect"][param] * del_

        new_data = yaml.dump(new_data).replace("\n", ", ")[0:-2]
        new_data = f"{{{new_data}}}"

        btn = InlineKeyboardButton(text=btn_text,
                                   callback_data=new_data)
        btns.append(btn)

    keyboard.row(*btns)
    question_text = question["question"][0:-1]
    text = f"Вопрос {q_id} из {q_max}: <b>{question_text}</b>"

    await bot.answer_callback_query(call.id)
    await bot.edit_message_text(chat_id=call.message.chat.id,
                                message_id=call.message.message_id,
                                text=text, parse_mode="HTML",
                                reply_markup=keyboard)

executor.start_polling(dp)
