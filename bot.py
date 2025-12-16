import os
from flask import Flask, request
import telebot
import time

# Ініціалізація Flask app
app = Flask(__name__)

# Токен бота з Environment Variable
TOKEN = os.getenv("MY_BOT_TOKEN")
if TOKEN is None:
    raise ValueError("Токен не знайдено! Встанови MY_BOT_TOKEN у Render.")

# Ініціалізація бота
bot = telebot.TeleBot(TOKEN)

# Імпортуємо меню
from keyboards import (
    main_menu,
    assortment_menu,
    liquid_menu,
    pods_menu,
    components_menu,
    cartridges_menu
)

# Обробник команди /start
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        "Привіт! Обери категорію 👇",
        reply_markup=main_menu()
    )

# Обробник текстових повідомлень
@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    text = message.text.strip()
    chat_id = message.chat.id

    if text == "Асортимент":
        bot.send_message(chat_id, "Обери категорію:", reply_markup=assortment_menu())
    
    elif text == "Рідина":
        bot.send_message(chat_id, "Обери рідину:", reply_markup=liquid_menu())
    
    elif text == "Chaser 10 ml":
        bot.send_message(chat_id, "Список наявності Chaser 10 ml:\n\n1. Chaser 10ml - Salt 20mg\n2. Chaser 10ml - Freebase 6mg\n3. Chaser 10ml - Salt 10mg")
    
    elif text == "Chaser 30 ml for pods":
        bot.send_message(chat_id, "Список Chaser 30 ml for pods:\n\n1. Манго-Льодяна малина\n2. Ананас-Кокос\n3. Полуниця-Кавун")
    
    elif text == "Chaser mix 30 ml":
        bot.send_message(chat_id, "Список Chaser mix 30 ml:\n\n1. Berry Mix\n2. Tropical Mix\n3. Ice Mix")
    
    elif text == "Chaser black 30 ml":
        bot.send_message(chat_id, "Список Chaser black 30 ml:\n\n1. Black Ice\n2. Black Mint\n3. Black Berry")
    
    elif text == "Chaser lux 30 ml":
        bot.send_message(chat_id, "Список Chaser lux 30 ml:\n\n1. Lux Mango\n2. Lux Strawberry\n3. Lux Grape")
    
    elif text == "Chaser black 30 ml 50 mg":
        bot.send_message(chat_id, "Список Chaser black 30 ml 50 mg:\n\n1. Black 50mg - Ice\n2. Black 50mg - Berry\n3. Black 50mg - Tobacco")
    
    elif text == "Поди":
        bot.send_message(chat_id, "Обери под:", reply_markup=pods_menu())
    
    elif text == "Xlim":
        bot.send_message(chat_id, "Поди Xlim:\n\n1. Xlim Pro\n2. Xlim SQ\n3. Xlim C")
    
    elif text == "Vaporesso":
        bot.send_message(chat_id, "Поди Vaporesso:\n\n1. XROS 3\n2. XROS 3 Mini\n3. XROS 4")
    
    elif text == "Компоненти до пода":
        bot.send_message(chat_id, "Обери компонент:", reply_markup=components_menu())
    
    elif text == "Картриджі":
        bot.send_message(chat_id, "Обери бренд:", reply_markup=cartridges_menu())
    
    elif text == "Картриджі Xlim":
        bot.send_message(chat_id, "Список картриджів Xlim:\n\n1. Xlim 0.6Ω Pod\n2. Xlim 0.8Ω Pod\n3. Xlim 1.2Ω Pod")
    
    elif text == "Картриджі Vaporesso":
        bot.send_message(chat_id, "Список картриджів Vaporesso:\n\n1. XROS 0.6Ω Pod\n2. XROS 0.8Ω Pod\n3. XROS 1.0Ω Pod")
    
    elif text == "Назад":
        bot.send_message(chat_id, "Головне меню:", reply_markup=main_menu())
    
    else:
        bot.send_message(chat_id, "Обери кнопку з меню 👇", reply_markup=main_menu())

# Flask роут для вебхука
@app.route('/' + TOKEN, methods=['POST'])
def get_message():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200

@app.route("/")
def webhook():
    bot.remove_webhook()
    # Встановіть свій реальний URL Render тут
    bot.set_webhook(url=f"https://your-app-name.onrender.com/{TOKEN}")
    return "Webhook set!", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)