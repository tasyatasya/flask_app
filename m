import telebot
from telebot import types

token = "ВАШ ТОКЕН"
bot = telebot.TeleBot(token=token)

@bot.message_handler(commands=["start"])
def repeat_all_messages(message):
    # создаем клавиатуру
    keyboard = types.InlineKeyboardMarkup()

    # добавляем на нее две кнопки
    button1 = types.InlineKeyboardButton(text="Кнопка 1", callback_data="button1")
    button2 = types.InlineKeyboardButton(text="Кнопка 2", callback_data="button2")
    keyboard.add(button1)
    keyboard.add(button2)

    # отправляем сообщение пользователю
    bot.send_message(message.chat.id, "Нажмите кнопку!", reply_markup=keyboard)

# функция запустится, когда пользователь нажмет на кнопку
@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.message:
        if call.data == "button1":
            bot.send_message(call.message.chat.id, "Вы нажали на первую кнопку.")
        if call.data == "button2":
            bot.send_message(call.message.chat.id, "Вы нажали на вторую кнопку.")

bot.polling(none_stop=True)