import os
from flask import Flask, request
import telebot

# Токен бота з Environment Variable
TOKEN = os.getenv("MY_BOT_TOKEN")
if TOKEN is None:
    raise ValueError("Токен не знайдено! Встанови MY_BOT_TOKEN у Render.")

from keyboards import (
    main_menu,
    assortment_menu,
    liquid_menu,
    pods_menu,
    components_menu,
    cartridges_menu
)

def register_handlers(bot):

    @bot.message_handler(commands=["start"])
    def start(message):
        bot.send_message(
            message.chat.id,
            "Привіт! Обери категорію 👇",
            reply_markup=main_menu()
        )

    @bot.message_handler(func=lambda m: True)
    def handler(message):
        text = message.text
        chat_id = message.chat.id

        if text == "Асортимент":
            bot.send_message(chat_id, "Обери категорію:", reply_markup=assortment_menu())

        elif text == "Рідина":
            bot.send_message(chat_id, "Обери рідину:", reply_markup=liquid_menu())

        elif text == "Chaser 10 ml":
            bot.send_message(chat_id, "Список наявності Chaser 10 ml")

        elif text == "Chaser 30 ml for pods":
            bot.send_message(chat_id, "Список Chaser 30 ml for pods")

        elif text == "Chaser mix 30 ml":
            bot.send_message(chat_id, "Список Chaser mix 30 ml")

        elif text == "Chaser black 30 ml":
            bot.send_message(chat_id, "Список Chaser black 30 ml")

        elif text == "Chaser lux 30 ml":
            bot.send_message(chat_id, "Список Chaser lux 30 ml")

        elif text == "Chaser black 30 ml 50 mg":
            bot.send_message(chat_id, "Список Chaser black 30 ml 50 mg")

        elif text == "Поди":
            bot.send_message(chat_id, "Обери под:", reply_markup=pods_menu())

        elif text == "Xlim":
            bot.send_message(chat_id, "Поди Xlim")

        elif text == "Vaporesso":
            bot.send_message(chat_id, "Поди Vaporesso")

        elif text == "Компоненти до пода":
            bot.send_message(chat_id, "Обери компонент:", reply_markup=components_menu())

        elif text == "Картриджі":
            bot.send_message(chat_id, "Обери бренд:", reply_markup=cartridges_menu())

        elif text == "Картриджі Xlim":
            bot.send_message(chat_id, "Список картриджів Xlim")

        elif text == "Картриджі Vaporesso":
            bot.send_message(chat_id, "Список картриджів Vaporesso")

        elif text == "Назад":
            bot.send_message(chat_id, "Головне меню:", reply_markup=main_menu())

        else:
            bot.send_message(chat_id, "Обери кнопку 👇")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Render підставляє свій порт
    # Встановлюємо webhook на твій Render домен
    bot.remove_webhook()
    bot.set_webhook(url=f"https://api.render.com/deploy/srv-d503jt7pm1nc73c3oq2g?key=ZAjorDuWwL4{TOKEN}")  L
    app.run(host="0.0.0.0", port=port)




