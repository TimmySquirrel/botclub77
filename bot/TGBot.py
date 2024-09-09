# from telegram.ext import Updater         # пакет называется python-telegram-bot, но Python-
# from telegram.ext import CommandHandler  # модуль почему-то просто telegram ¯\_(ツ)_/¯

token_telegram = "7001360047:AAGs1JvzlL3czxfS9OjnyRZJz8uZYiljuLY"

# def start(bot, update):
#     # подробнее об объекте update: https://core.telegram.org/bots/api#update
#     bot.sendMessage(chat_id=update.message.chat_id, text="Здравствуйте.")

# updater = Updater(bot=token_telegram)  # тут токен, который выдал вам Ботский Отец!

# start_handler = CommandHandler('start', start)  # этот обработчик реагирует
#                                                 # только на команду /start

# updater.dispatcher.add_handler(start_handler)   # регистрируем в госреестре обработчиков
# updater.start_polling()  # поехали!


import telebot

botTimeWeb = telebot.TeleBot(token_telegram)

from telebot import types


@botTimeWeb.message_handler(commands=['start'])
def startBot(message):
    first_mess = f"<b>{message.from_user.first_name} {message.from_user.last_name}</b>, привет!"
    botTimeWeb.send_message(message.chat.id, first_mess, parse_mode='html')

botTimeWeb.infinity_polling()