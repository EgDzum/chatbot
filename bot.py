from telebot import types, TeleBot
# from config_reader import config


bot = TeleBot(token='6506414342:AAGcwehYvYIBlftiAT9cqbUjg42socPNwa0')


def bot_menu(message):
    c1 = types.BotCommand(command='help', description='Показать информацию о боте')
    c2 = types.BotCommand(command='schedule_today', description='Показать расписание на ')
    c3 = types.BotCommand(command='schedule', description='Показать расписание на неделю')
    c4 = types.BotCommand(command='quote', description='Прочитать смешную цитату')
    bot.set_my_commands([c1, c2, c3, c4])
    bot.set_chat_menu_button(message.chat.id, types.MenuButtonCommands('commands'))


@bot.message_handler(commands=['schedule'])
def schedule(message):
    bot.send_message(message.chat.id, 'in progress')


@bot.message_handler(commands=['schedule_today'])
def schedule(message):
    bot.send_message(message.chat.id, 'in progress too')


@bot.message_handler(commands=['quote'])
def schedule(message):
    bot.send_message(message.chat.id, 'Когда меня рожали, собственно тогда я и родился © Джейсон Стэтхема')


@bot.message_handler(commands=['help'])
@bot.message_handler(content_types=['text'])
def start_message(message):
    with open('bot_text.txt', 'r', encoding='utf-8') as f:
        bot.send_message(message.chat.id, text=f.read())


if __name__ == "__main__":
    bot.infinity_polling()
