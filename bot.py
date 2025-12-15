import os
from flask import Flask, request
import telebot

# Токен бота з Environment Variable
TOKEN = os.getenv("MY_BOT_TOKEN")
if TOKEN is None:
    raise ValueError("Токен не знайдено! Встанови MY_BOT_TOKEN у Render.")

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# Стартове повідомлення з кнопками
@bot.message_handler(commands=['start'])
def start(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = telebot.types.KeyboardButton("Асортимент")
    btn2 = telebot.types.KeyboardButton("Наявність")
    btn3 = telebot.types.KeyboardButton("Доставка")
    btn4 = telebot.types.KeyboardButton("Контакти")
    markup.add(btn1, btn2)
    markup.add(btn3, btn4)
    bot.send_message(message.chat.id, "Привіт! Обери, що тебе цікавить:", reply_markup=markup)

# Обробка кнопок
@bot.message_handler(func=lambda message: True)
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

# Webhook для Telegram
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    json_str = request.get_data().decode("utf-8")
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "!", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Render підставляє свій порт
    # Встановлюємо webhook на твій Render домен
    bot.remove_webhook()
    bot.set_webhook(url=f"https://api.render.com/deploy/srv-d503jt7pm1nc73c3oq2g?key=ZAjorDuWwL4{TOKEN}")  L
    app.run(host="0.0.0.0", port=port)



