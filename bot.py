import calendar
import random
import re
from datetime import date

import pandas as pd
from telebot import types, TeleBot


bot = TeleBot(token="6506414342:AAGcwehYvYIBlftiAT9cqbUjg42socPNwa0")

df = pd.read_excel("dataset.xlsx")

quotes = pd.read_excel("quotes.xlsx")

user_dict = {}


class User:
    def __init__(self, group):
        self.group = group
        self.language = None


@bot.message_handler(commands=["start"])
def authorize(message):
    msg = bot.send_message(
        message.chat.id,
        text="Чтобы посмотреть расписание, пожалуйста, укажите "
        "название своей группы без пробелов, "
        "используя только цифры и заглавные буквы. Пример: 21ФПЛ1",
    )
    bot.register_next_step_handler(msg, get_group)


def get_group(message):
    group_names = df["Группа"].unique()
    group = message.text.strip()
    chat_id = message.chat.id

    if group not in group_names:
        msg = bot.send_message(
            message.chat.id, "Такой группы нет. Введите другой номер группы."
        )
        bot.register_next_step_handler(msg, get_group)
        return

    user_dict[chat_id] = User(group)

    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.add("Французский", "Немецкий")
    msg = bot.reply_to(
        message, "А теперь, пожалуйста, укажите ваш второй язык.", reply_markup=markup
    )
    bot.register_next_step_handler(msg, get_2nd_lang)


def get_2nd_lang(message):
    try:
        chat_id = message.chat.id
        lang = message.text
        user = user_dict[chat_id]
        if (lang == "Французский") or (lang == "Немецкий"):
            user.language = lang
        else:
            raise Exception("Неизвестный язык")
    except Exception:
        msg = bot.reply_to(
            message,
            "Неизвестный язык. Пожалуйста, проверьте, правильно ли вы написали язык, "
            "и введите ещё раз",
        )


@bot.message_handler(commands=["schedule_day"])
def schedule(message):
    # shows schedule for a chosen day
    msg = bot.send_message(
        message.chat.id, "На какой день недели выхотите посмотреть расписание?"
    )
    bot.register_next_step_handler(msg, schedule_getter)


def output(df, ind):
    return (
        f"{ind+1} пара.\n"
        f'Начало в {df["Время_начала"].iloc[ind]}\n'
        f'Предмет - {df["Предмет"].iloc[ind]}\n'
        f'Аудитория - {df["Аудитория"].iloc[ind]}\n'
        f'Корпус - {df["Корпус"].iloc[ind]}\n'
    )


def schedule_getter(message, text=None):
    msg = text if text else message.text.strip().lower()
    chat_id = message.chat.id
    try:
        lang = user_dict[chat_id].language
        schedule_day = df[
                (df["День_недели"] == msg) & (df["Группа"] == user_dict[chat_id].group)
                ]
        special_subs = schedule_day["Предмет"].str.extract(
            rf"({lang})", flags=re.IGNORECASE
        )
        if lang in special_subs[0].to_list():
            indices = special_subs[special_subs.iloc[:, 0] != lang].index
            schedule_day.drop(index=indices, inplace=True)

        lst = []
        for ind in range(len(schedule_day)):
            string = output(schedule_day, ind)
            lst.append(string)

        bot.send_message(chat_id, "\n\n".join(lst))

    except KeyError:
        bot.send_message(chat_id, "К сожалению, не известен второй язык и номер группы. Пожалуйста, "
                         "нажмите /start для авторизации")


def from_en_to_rus_datetime(string):
    translation = {
        "Monday": "понедельник",
        "Tuesday": "вторник",
        "Wednesday": "среда",
        "Thursday": "четверг",
        "Friday": "пятница",
        "Saturday": "суббота",
    }
    return translation[string]


@bot.message_handler(commands=["schedule_today"])
def schedule(message):
    today_date = date.today()
    day = calendar.day_name[today_date.weekday()]
    rus_day = from_en_to_rus_datetime(day)
    bot.register_next_step_handler(message, schedule_getter, text=rus_day)


@bot.message_handler(commands=["quote"])
def quote(message):
    rand_digit = random.randint(0, len(quotes) - 1)
    msg = quotes.iloc[rand_digit, 0]
    bot.send_message(message.chat.id, msg)


@bot.message_handler(commands=["help"])
@bot.message_handler(content_types=["text"])
def start_message(message):
    with open("bot_text.txt", "r", encoding="utf-8") as f:
        bot.send_message(message.chat.id, text=f.read())


if __name__ == "__main__":
    bot.infinity_polling()
