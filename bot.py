import os
import time  # ДОДАЙТЕ ЦЕ!
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

# Автоматично встановлюємо вебхук при запуску
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

# ==================== ДОДАЙТЕ ІНФОРМАЦІЙНІ ОБРОБНИКИ ====================
@bot.message_handler(func=lambda m: m.text == "Як замовити?")
def how_to_order(message):
    response = """
📝 *ЯК ЗАМОВИТИ:*

1. 🛍️ Натисніть *Асортимент*
2. 🔍 Оберіть товари
3. 💬 Натисніть *Написати менеджеру*
4. 📝 Напишіть що хочете замовити
5. ⏳ Чекайте відповіді (5-15 хв)

*Приклад:* "Chaser 30 ml Виноград - 2 шт, XROS 5 - 1 шт"
"""
    bot.send_message(message.chat.id, response, parse_mode='Markdown')

@bot.message_handler(func=lambda m: m.text == "Оплата та доставка")
def payment_delivery(message):
    response = """
💰 *ОПЛАТА:*
• Карта 💳 (Monobank, Privat)
• Готівка при отриманні 💵
• Накладений платіж 📦

🚚 *ДОСТАВКА:*
• Нова Пошта (1-3 дні)
• Самовивіз: Луцьк, Княгининок
• Від 50 грн, безкоштовно від 1000 грн
"""
    bot.send_message(message.chat.id, response, parse_mode='Markdown')

# ==================== ВЕБХУК МАРШРУТИ ====================
@app.route('/')
def index():
    return """
    <h1>🤖 Telegram Bot працює!</h1>
    <p><strong>Статус:</strong> Online ✅</p>
    <p><strong>Доступні сторінки:</strong></p>
    <ul>
        <li><a href="/health">/health</a> - Статус</li>
        <li><a href="/setup">/setup</a> - Встановити вебхук</li>
        <li><a href="/webhook_info">/webhook_info</a> - Інформація про вебхук</li>
    </ul>
    """

@app.route('/health')
def health_check():
    return {
        "status": "online",
        "service": "Telegram Bot",
        "timestamp": time.time(),
        "time": time.ctime(),
        "url": "https://telegram-bot-iss2.onrender.com"
    }

@app.route('/setup')
def setup_webhook():
    """Встановлення вебхука вручну"""
    try:
        webhook_url = f"https://telegram-bot-iss2.onrender.com/{TOKEN}"
        bot.remove_webhook()
        time.sleep(1)
        result = bot.set_webhook(url=webhook_url)
        
        return f"""
        <h1>✅ Вебхук встановлено!</h1>
        <p><strong>URL:</strong> {webhook_url}</p>
        <p><strong>Результат:</strong> {result}</p>
        <p><strong>Наступні кроки:</strong></p>
        <ol>
            <li>Перейдіть до бота в Telegram</li>
            <li>Напишіть <code>/start</code></li>
            <li>Напишіть <code>/test</code> для перевірки</li>
        </ol>
        <p><a href="/">← На головну</a></p>
        """
    except Exception as e:
        return f"""
        <h1>❌ Помилка!</h1>
        <p><strong>Помилка:</strong> {e}</p>
        <p><a href="/">← На головну</a></p>
        """

@app.route('/webhook_info')
def webhook_info():
    """Інформація про вебхук"""
    try:
        info = bot.get_webhook_info()
        return {
            "webhook_info": {
                "url": info.url,
                "has_custom_certificate": info.has_custom_certificate,
                "pending_update_count": info.pending_update_count,
                "last_error_date": info.last_error_date,
                "last_error_message": info.last_error_message,
                "max_connections": info.max_connections,
                "allowed_updates": info.allowed_updates
            }
        }
    except Exception as e:
        return {"error": str(e)}

# ==================== ГЛАВНИЙ ВЕБХУК МАРШРУТ ====================
@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    """Обробник вебхука від Telegram"""
    if request.headers.get('content-type') == 'application/json':
        try:
            json_string = request.get_data().decode('utf-8')
            update = telebot.types.Update.de_json(json_string)
            bot.process_new_updates([update])
            return ''
        except Exception as e:
            print(f"❌ Помилка обробки вебхука: {e}")
            return 'ERROR', 400
    return 'ERROR', 400

# ==================== ЗАПУСК ====================
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    
    print(f"🚀 Запускаю бота на порті {port}")
    print(f"🌐 Основна URL: https://telegram-bot-iss2.onrender.com")
    print(f"🔧 Доступні сторінки:")
    print(f"   • https://telegram-bot-iss2.onrender.com/")
    print(f"   • https://telegram-bot-iss2.onrender.com/health")
    print(f"   • https://telegram-bot-iss2.onrender.com/setup")
    print(f"   • https://telegram-bot-iss2.onrender.com/webhook_info")
    print(f"   • https://telegram-bot-iss2.onrender.com/{TOKEN}")
    
    app.run(host='0.0.0.0', port=port)
