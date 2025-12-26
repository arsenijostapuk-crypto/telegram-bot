import os
from flask import Flask, request
import telebot
from telebot import types
from products import get_product_response
from keyboards import (
    main_menu, assortment_menu, liquids_menu, pods_menu,
    cartridges_menu, delivery_menu, order_menu, info_menu
)
from config import ADMIN_IDS, is_admin
from chat_manager import chat_manager
from admin_panel import AdminPanel  # Імпортуємо адмін-панель

ADMIN_GROUP_ID = -1003654920245

app = Flask(__name__)

# Налаштування
TOKEN = os.getenv("MY_BOT_TOKEN")
if not TOKEN:
    raise ValueError("❌ Токен не знайдено!")

bot = telebot.TeleBot(TOKEN)

# Ініціалізуємо адмін-панель
admin_panel = AdminPanel(bot)
admin_panel.setup_handlers()  # Реєструємо адмін-обробники

# Тексти повідомлень
WELCOME_TEXT = """
👋 *Вітаємо в нашому боті!*

Обирайте необхідний розділ:

🛍️ *Асортимент* - переглянути товари
📦 *💬Написати менеджеру* - створити замовлення
ℹ️ *Детальніше* - інформація про бота

Оберіть пункт меню 👇
"""
ORDER_TEXT = """
📦 *Оформлення замовлення*

Напишіть що вас цікавить
*Приклад повідомлення:*
"Chaser 30 ml for pods Виноград- 2 шт, Vaporesso XROS 5 - 1 шт, на завтра 14 годину с.Княгининок "

Наш менеджер зв'яжеться з вами протягом 5-15 хвилин.

*Просто напишіть своє повідомлення нижче:*
"""

# ==================== КЛІЄНТИ: ГОЛОВНЕ МЕНЮ ====================
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.send_message(message.chat.id, WELCOME_TEXT, 
                    parse_mode='Markdown', reply_markup=main_menu())

@bot.message_handler(func=lambda m: m.text in ["🛍️ Асортимент",
                                              "💬Написати менеджеру", "ℹ️ Детальніше"])
def handle_main_menu(message):
    text = message.text
    chat_id = message.chat.id
    
    if text == "🛍️ Асортимент":
        bot.send_message(chat_id, "Оберіть категорію товарів:", 
                        reply_markup=assortment_menu())
    
    elif text == "💬Написати менеджеру":
        bot.send_message(chat_id, ORDER_TEXT, 
                        parse_mode='Markdown', reply_markup=order_menu())
        bot.register_next_step_handler(message, process_order)
    
    elif text == "ℹ️ Детальніше":
        from keyboards import info_menu
        bot.send_message(chat_id, "Оберіть пункт для детальнішої інформації:",
                        reply_markup=info_menu())

# ==================== КЛІЄНТИ: АСОРТИМЕНТ ====================
@bot.message_handler(func=lambda m: m.text in ["💧 Рідини", "🔋 Под-системи", 
                                              "🎯 Картриджі"])
def handle_assortment(message):
    text = message.text
    chat_id = message.chat.id
    
    if text == "💧 Рідини":
        bot.send_message(chat_id, "Оберіть рідину:", reply_markup=liquids_menu())
    
    elif text == "🔋 Под-системи":
        bot.send_message(chat_id, "Оберіть под-систему:", reply_markup=pods_menu())
    
    elif text == "🎯 Картриджі":
        bot.send_message(chat_id, "Оберіть картриджі:", reply_markup=cartridges_menu())

# ==================== КЛІЄНТИ: ТОВАРИ ====================
@bot.message_handler(func=lambda m: m.text in [
    # Рідини
    "Chaser 10 ml", "Chaser 30 ml for pods", "Chaser mix 30 ml",
    "Chaser black 30 ml", "Chaser lux 30 ml", "Chaser black 30 ml 50 mg",
    
    # Поди
    "Xlim", "Vaporesso", "Інші бренди",
    
    # Картриджі
    "Картриджі Xlim", "Картриджі Vaporesso",
    "Картриджі NeXlim", "Картриджі Ursa V3"
])
def handle_products(message):
    """Обробка вибору товарів"""
    text = message.text
    chat_id = message.chat.id
    
    # Отримуємо текст з products.py
    response = get_product_response(text)
    
    # Просто відправляємо текст без кнопки замовлення
    bot.send_message(chat_id, response, parse_mode='Markdown')

# ==================== КЛІЄНТИ: ЗАМОВЛЕННЯ ====================
def process_order(message):
    chat_id = message.chat.id
    user = message.from_user
    order_text = message.text
    
    if order_text == "Скасувати надсилання ❌":
        bot.send_message(chat_id, "✅ Надсилання скасовано.", reply_markup=main_menu())
        return
    
    # Зберігаємо замовлення
    chat_manager.start_chat(user.id, user.first_name, user.username)
    chat_manager.add_message(user.id, order_text, from_admin=False)
    
    # Повідомлення клієнту
    bot.send_message(
        chat_id,
        f"✅ *Повідомлення відправлене!*\n\nВаше повідомлення:\n{order_text}\n\nМенеджер зв'яжеться протягом 5-15 хвилин.",
        parse_mode='Markdown',
        reply_markup=main_menu()
    )
    
    # Повідомлення в групу
    try:
        admin_msg = f"""
📦 *НОВЕ ПОВІДОМЛЕННЯ*

👤 {user.first_name} (@{user.username if user.username else 'без username'})
🆔 {user.id}

📝 {order_text}"""
        
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(
            "💬 Відповісти клієнту", 
            callback_data=f"reply_{user.id}"
        ))
        
        bot.send_message(ADMIN_GROUP_ID, admin_msg, parse_mode='Markdown', reply_markup=markup)
    except Exception as e:
        print(f"❌ Помилка відправки в групу: {e}")

# ==================== ВЕБХУК ====================
@app.route('/')
def index():
    return "🤖 Бот працює!"

@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return ''
    return 'ERROR', 400

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    print(f"🚀 Запускаю бота на порті {port}")
    app.run(host='0.0.0.0', port=port)3