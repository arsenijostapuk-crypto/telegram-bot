import os
import time
import logging
from flask import Flask, request
import telebot
from telebot import types

# Налаштування логування
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)

# Налаштування
TOKEN = os.getenv("MY_BOT_TOKEN")
if not TOKEN:
    raise ValueError("❌ Токен не знайдено!")

bot = telebot.TeleBot(TOKEN)

# Імпорти після ініціалізації бота
try:
    from products import get_product_response
    from keyboards import (
        main_menu, assortment_menu, liquids_menu, pods_menu,
        cartridges_menu, order_menu, info_menu
    )
    from config import ADMIN_IDS, is_admin
    from chat_manager import chat_manager
    from admin_panel import AdminPanel
except ImportError as e:
    print(f"❌ Помилка імпорту: {e}")
    raise

ADMIN_GROUP_ID = -1003654920245

# Автоматично встановлюємо вебхук
print("🔄 Встановлюю вебхук...")
try:
    webhook_url = f"https://telegram-bot-iss2.onrender.com/{TOKEN}"
    bot.remove_webhook()
    time.sleep(1)
    bot.set_webhook(url=webhook_url)
    print(f"✅ Вебхук встановлено на: {webhook_url}")
except Exception as e:
    print(f"❌ Помилка встановлення вебхука: {e}")

# Ініціалізуємо адмін-панель
admin_panel = AdminPanel(bot)
admin_panel.setup_handlers()

# Тексти
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
"Chaser 30 ml for pods Виноград- 2 шт, Vaporesso XROS 5 - 1 шт"

Наш менеджер зв'яжеться з вами протягом 5-15 хвилин.
"""

# ==================== КЛІЄНТСЬКІ ОБРОБНИКИ ====================

# ДЕБАГ ВСІХ ПОВІДОМЛЕНЬ
@bot.message_handler(func=lambda m: True)
def debug_all_messages(message):
    if message.text:
        print(f"📥 Повідомлення: '{message.text}' від {message.from_user.id}")

# Це МАЄ БУТИ ПЕРШИМ обробником:
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    print(f"🚀 /start від {message.from_user.id}")
    bot.send_message(message.chat.id, WELCOME_TEXT, 
                    parse_mode='Markdown', reply_markup=main_menu())

# А цей обробник МАЄ БУТИ ПІСЛЯ /start:
@bot.message_handler(func=lambda m: True)
def debug_all_messages(message):
    if message.text:
        print(f"📥 Повідомлення: '{message.text}' від {message.from_user.id}")

@bot.message_handler(commands=['test', 'ping'])
def test_command(message):
    bot.reply_to(message, "✅ Бот працює! Напишіть /start")

@bot.message_handler(func=lambda m: m.text == "🛍️ Асортимент")
def handle_assortment(message):
    print(f"🔄 Обробка 'Асортимент' від {message.from_user.id}")
    bot.send_message(message.chat.id, "Оберіть категорію товарів:", 
                    reply_markup=assortment_menu())

@bot.message_handler(func=lambda m: m.text == "💬Написати менеджеру")
def handle_order_request(message):
    print(f"🔄 Обробка 'Написати менеджеру' від {message.from_user.id}")
    bot.send_message(message.chat.id, ORDER_TEXT, 
                    parse_mode='Markdown', reply_markup=order_menu())
    bot.register_next_step_handler(message, process_order)

@bot.message_handler(func=lambda m: m.text == "ℹ️ Детальніше")
def handle_info(message):
    print(f"🔄 Обробка 'Детальніше' від {message.from_user.id}")
    bot.send_message(message.chat.id, "Оберіть пункт:", reply_markup=info_menu())

# ==================== КАТЕГОРІЇ ТОВАРІВ ====================
@bot.message_handler(func=lambda m: m.text in ["💧 Рідини", "🔋 Под-системи", "🎯 Картриджі"])
def handle_categories(message):
    print(f"🔄 Обробка категорії: {message.text} від {message.from_user.id}")
    
    text = message.text
    if text == "💧 Рідини":
        bot.send_message(message.chat.id, "Оберіть рідину:", reply_markup=liquids_menu())
    elif text == "🔋 Под-системи":
        bot.send_message(message.chat.id, "Оберіть под-систему:", reply_markup=pods_menu())
    elif text == "🎯 Картриджі":
        bot.send_message(message.chat.id, "Оберіть картриджі:", reply_markup=cartridges_menu())

# ==================== ТОВАРИ ====================
@bot.message_handler(func=lambda m: m.text in [
    "Chaser 10 ml", "Chaser 30 ml for pods", "Chaser mix 30 ml",
    "Chaser black 30 ml", "Chaser lux 30 ml", "Chaser black 30 ml 50 mg",
    "Xlim", "Vaporesso", "Інші бренди",
    "Картриджі Xlim", "Картриджі Vaporesso",
    "Картриджі NeXlim", "Картриджі Ursa V3"
])
def handle_products(message):
    print(f"🔄 Обробка товару: {message.text} від {message.from_user.id}")
    response = get_product_response(message.text)
    bot.send_message(message.chat.id, response, parse_mode='Markdown')

# ==================== НАЙВАЖЛИВІШЕ: ОБРОБНИК "НАЗАД ◀️" ====================
@bot.message_handler(func=lambda m: m.text == "Назад ◀️")
def handle_back(message):
    print(f"🎯 КНОПКА 'НАЗАД' НАТИСНУТА від {message.from_user.id}")
    
    # Просто відправляємо головне меню
    try:
        bot.send_message(message.chat.id, "🏠 Головне меню:", reply_markup=main_menu())
        print(f"✅ Головне меню відправлено для {message.from_user.id}")
    except Exception as e:
        print(f"❌ Помилка: {e}")
        bot.send_message(message.chat.id, "🏠 Головне меню", reply_markup=main_menu())

# ==================== ІНФОРМАЦІЯ ====================
@bot.message_handler(func=lambda m: m.text == "Як замовити?")
def how_to_order(message):
    response = """
📝 *ЯК ЗАМОВИТИ:*

1. 🛍️ Натисніть *Асортимент*
2. 🔍 Оберіть товари
3. 💬 Натисніть *Написати менеджеру*
4. 📝 Напишіть що хочете
5. ⏳ Чекайте відповіді (5-15 хв)
"""
    bot.send_message(message.chat.id, response, parse_mode='Markdown')

@bot.message_handler(func=lambda m: m.text == "Оплата та доставка")
def payment_delivery(message):
    response = """
💰 *ОПЛАТА:*
• Карта 💳
• Готівка 💵
• Накладений платіж 📦

🚚 *ДОСТАВКА:*
• Нова Пошта (1-3 дні)
• Самовивіз: Луцьк, Княгининок
"""
    bot.send_message(message.chat.id, response, parse_mode='Markdown')

# ==================== ЗАМОВЛЕННЯ ====================
def process_order(message):
    if message.text == "Скасувати надсилання ❌":
        bot.send_message(message.chat.id, "✅ Скасовано", reply_markup=main_menu())
        return
    
    user = message.from_user
    chat_manager.start_chat(user.id, user.first_name, user.username)
    chat_manager.add_message(user.id, message.text, from_admin=False)
    
    bot.send_message(
        message.chat.id,
        f"✅ *Повідомлення відправлено!*\nМенеджер зв'яжеться за 5-15 хв.",
        parse_mode='Markdown',
        reply_markup=main_menu()
    )
    
    # Відправка в групу
    try:
        admin_msg = f"📦 НОВЕ ЗАМОВЛЕННЯ\n👤 {user.first_name}\n📝 {message.text}"
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("💬 Відповісти", callback_data=f"reply_{user.id}"))
        bot.send_message(ADMIN_GROUP_ID, admin_msg, reply_markup=markup)
    except Exception as e:
        print(f"❌ Помилка відправки в групу: {e}")

# ==================== ВЕБХУК МАРШРУТИ ====================
@app.route('/')
def index():
    return "🤖 Бот працює!"

@app.route('/health')
def health_check():
    return {"status": "online", "time": time.ctime()}

@app.route('/setup')
def setup_webhook():
    try:
        webhook_url = f"https://telegram-bot-iss2.onrender.com/{TOKEN}"
        bot.remove_webhook()
        result = bot.set_webhook(url=webhook_url)
        return f"✅ Вебхук встановлено: {webhook_url}"
    except Exception as e:
        return f"❌ Помилка: {e}"

@app.route('/test-bot')
def test_bot():
    try:
        bot_info = bot.get_me()
        return f"✅ Бот активний: {bot_info.first_name} (@{bot_info.username})<br>Token: {TOKEN[:10]}..."
    except Exception as e:
        return f"❌ Помилка бота: {e}<br>Token: {TOKEN[:10]}..."

@app.route('/test-webhook')
def test_webhook():
    try:
        webhook_info = bot.get_webhook_info()
        return f"""
        <h1>📊 Стан вебхука</h1>
        <p>URL: {webhook_info.url}</p>
        <p>Has custom certificate: {webhook_info.has_custom_certificate}</p>
        <p>Pending update count: {webhook_info.pending_update_count}</p>
        <p>Last error date: {webhook_info.last_error_date}</p>
        <p>Last error message: {webhook_info.last_error_message}</p>
        """
    except Exception as e:
        return f"❌ Помилка: {e}"

@app.route('/debug')
def debug_info():
    return f"""
    <h1>🔧 Інформація про бота</h1>
    <p>🌐 URL: https://telegram-bot-iss2.onrender.com</p>
    <p>🔑 Token: {TOKEN[:10]}...</p>
    <p>🕐 Time: {time.ctime()}</p>
    <p>📊 <a href="/health">Health Check</a></p>
    <p>⚙️ <a href="/setup">Setup Webhook</a></p>
    <p>🤖 <a href="/test-bot">Test Bot</a></p>
    <p>🔗 <a href="/test-webhook">Test Webhook</a></p>
    """

# Вебхук для Telegram (ЦЕЙ МАРШРУТ МАЄ БУТИ ОСТАННІМ!)
@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return ''
    return 'ERROR', 400

# ==================== ЗАПУСК ====================
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    print(f"🚀 Запускаю бота на порті {port}")
    print(f"🌐 URL: https://telegram-bot-iss2.onrender.com")
    print(f"🔧 Тестуйте: /start → Натисніть 'Назад ◀️'")
    app.run(host='0.0.0.0', port=port)

