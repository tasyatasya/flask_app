import telebot
from random import randint
import hashlib
import sqlite3
import time

token = "1946009951:AAE6CH-ScRgER8Af6u5YBR4Zy09MuspVyhw"
bot = telebot.TeleBot(token=token)
a = ["viole2taa", "taisiaaaa", "prplkn"]


def is_in_whitelist(message):
    if message.from_user.username not in a:
        return False
    else:
        return True


@bot.message_handler(commands=['start'])
def start(message):
    if (is_in_whitelist(message)):

        num = randint(1, 9999999)
        token2 = message.from_user.username + str(num)
        token1 = hashlib.md5(token2.encode())
        tok = token1.hexdigest()
        link = "http://127.0.0.1:5000/" + token1.hexdigest()
        bot.send_message(message.chat.id, "Вы есть в списке. У вас есть 2 миинуты, чтобы перейти по ссылкe.")
        bot.send_message(message.chat.id, link)
        name = message.from_user.username

        if name and token1:
            with sqlite3.connect('fincher.db') as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO fincher (name, tok) VALUES (?, ?)", (name, tok))
                print(cursor.fetchone())
                conn.commit()
    else:
        bot.send_message(message.chat.id, "Вас нет в списке.")


bot.polling(none_stop=True)