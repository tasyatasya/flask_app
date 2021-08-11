import telebot
from telebot import types
token = "1946009951:AAE6CH-ScRgER8Af6u5YBR4Zy09MuspVyhw"
bot = telebot.TeleBot(token=token)
@bot.message_handler(commands=["start"])