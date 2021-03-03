# -*- coding: utf8 -*-
import yaml

from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

import json
import logging

from os import environ

try:
    with open("config.json") as file:
        config = json.loads(file.read())
except FileNotFoundError:
    config = {}

TOKEN = environ.get("TOKEN") or config.get("token")

with open("data/ideologies.json", encoding="UTF8") as file:
    ideologies = json.loads(file.read())

with open("data/questions.json", encoding="UTF8") as file:
    questions = json.loads(file.read())

max_econ, max_dipl, max_govt, max_scty = 0, 0, 0, 0
for question in questions:
    max_econ += abs(question["effect"]["econ"])
    max_dipl += abs(question["effect"]["dipl"])
    max_govt += abs(question["effect"]["govt"])
    max_scty += abs(question["effect"]["scty"])

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=["test"])
async def test(message):
    call = "{q: 70, econ: 58.5, dipl: 48.9, govt: 40.0, scty: 54.4}"

    start_btn = InlineKeyboardButton(text="TEST",
                                     callback_data=call)
    keyboard = InlineKeyboardMarkup().add(start_btn)

    await message.reply('test', parse_mode="HTML", reply_markup=keyboard)


@dp.message_handler(commands=["start"])
async def start(message):
    q = 1
    call = f"{{q: {q}, econ: 0, dipl: 0, govt: 0, scty: 0}}"

    start_btn = InlineKeyboardButton(text="Начать тест",
                                     callback_data=call)
    keyboard = InlineKeyboardMarkup().add(start_btn)

    await message.reply('<b>8values</b> — это, по сути, политическая викторина, которая пытается присвоить проценты восьми различным политическим ценностям. Вам будут даны утверждения, по каждому из которых вы должны ответить своим мнением, от <b>🟢 (Полностью согласен)</b> до <b>🔴 (Полностью не согласен)</b>, каждый ответ будет слегка влиять на ваши значения по каждой оси. В конце викторины, ваши ответы будут сравниваться с максимально возможным для каждого значения, таким образом, давая вам процент. Отвечайте честно!\n\nВ данном тесте <b>69</b> вопросов.\n\nФорк и часть перевода сделаны <a href="https://t.me/ysamtme">@ysamtme</a> (буду рад сообщениям об ошибках и неточностях).', disable_web_page_preview=True, parse_mode="HTML", reply_markup=keyboard)  # noqa: E501


def calc_score(score, max_):
    return round((100 * (max_ + score) / (2 * max_)), 1)


@dp.callback_query_handler(lambda call: call.data.startswith("{"))
async def process_callback_button1(call: types.CallbackQuery):
    data = yaml.safe_load(call.data)
    q_max = len(questions) - 1
    q_id = int(data["q"])

    if data["q"] > q_max:
        await bot.answer_callback_query(call.id)

        equality = calc_score(data["econ"], max_econ)
        peace = calc_score(data["dipl"], max_dipl)
        liberty = calc_score(data["govt"], max_govt)
        progress = calc_score(data["scty"], max_scty)

        ideology = ""
        ideodist = float("inf")

        for ideology in ideologies:
            dist = 0
            dist += abs(ideology["stats"]["econ"] - equality) ** 2
            dist += abs(ideology["stats"]["govt"] - liberty) ** 2
            dist += abs(ideology["stats"]["dipl"] - peace) ** 1.73856063
            dist += abs(ideology["stats"]["scty"] - progress) ** 1.73856063

            if dist < ideodist:
                ideology_ = ideology["name"]
                ideodist = dist

        ideology = f"Ваша идеология: <b>{ideology_}</b>"

        await bot.edit_message_text(chat_id=call.message.chat.id,
                                    message_id=call.message.message_id,
                                    text=ideology, parse_mode="HTML")
        return

    data["q"] += 1
    question = questions[q_id - 1]

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
    text = f"Вопрос {q_id} из {q_max + 1}: <b>{question_text}</b>"

    await bot.answer_callback_query(call.id)
    await bot.edit_message_text(chat_id=call.message.chat.id,
                                message_id=call.message.message_id,
                                text=text, parse_mode="HTML",
                                reply_markup=keyboard)

executor.start_polling(dp)
