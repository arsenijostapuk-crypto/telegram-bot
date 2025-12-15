import telebot
from telebot import types

bot = telebot.TeleBot("8504700222:AAHdZSwvPUtc-bLQGSd_uLOEahBvPy4-edo")

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    btn1 = types.KeyboardButton("Асортимент")
    btn2 = types.KeyboardButton("Наявність")
    btn3 = types.KeyboardButton("Доставка")
    btn4 = types.KeyboardButton("Контакти")

    markup.add(btn1, btn2)
    markup.add(btn3, btn4)

    bot.send_message(
        message.chat.id,
        "Привіт! Обери, що тебе цікавить:",
        reply_markup=markup
    )

@bot.message_handler()
def handler(message):
    if message.text == "Асортимент":
        bot.send_message(message.chat.id, "Тут буде асортимент.")
    elif message.text == "Наявність":
        bot.send_message(message.chat.id, "Тут буде інформація про наявність.")
    elif message.text == "Доставка":
        bot.send_message(message.chat.id, "Тут буде про доставку.")
    elif message.text == "Контакти":
        bot.send_message(message.chat.id, "Тут будуть контакти.")
    else:
        bot.send_message(message.chat.id, "Не розумію. Обери кнопку.")

bot.infinity_polling()


