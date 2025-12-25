import os
import time
from flask import Flask, request
import telebot
from telebot import types
from telebot.apihelper import ApiTelegramException
from products import get_product_response
from keyboards import (
    main_menu, assortment_menu, liquids_menu, pods_menu,
    cartridges_menu, delivery_menu, order_menu, info_menu
)
from config import ADMIN_IDS, is_admin
from chat_manager import chat_manager

ADMIN_GROUP_ID = -1003654920245

app = Flask(__name__)

# Налаштування
TOKEN = os.getenv("MY_BOT_TOKEN")
if not TOKEN:
    raise ValueError("❌ Токен не знайдено!")

bot = telebot.TeleBot(TOKEN)
print("✅ Бот ініціалізовано")

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

INFO_TEXT = """
ℹ️ *Інформація про бота*

🤖 *Як користуватися ботом:*
1. Оберіть 🛍️ Асортимент для перегляду товарів
2. Обирайте категорії та товари
3. Для замовлення натисніть 💬Написати менеджеру
4. Напишіть що вас цікавить
5. Очікуйте відповідь від менеджера

"""

# ==================== ДЕБАГОВИЙ ОБРОБНИК ====================
@bot.message_handler(func=lambda m: True)
def debug_all_messages(message):
    if message.text and message.text.startswith('/'):
        print(f"📥 Отримано команду: {message.text} від {message.from_user.id}")

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
        bot.send_message(chat_id, INFO_TEXT, parse_mode='Markdown')
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

# ==================== КЛІЄНТИ: ІНФОРМАЦІЯ ====================
@bot.message_handler(func=lambda m: m.text in ["Як замовити?", "Оплата та доставка"])
def handle_info_menu(message):
    text = message.text
    chat_id = message.chat.id
    
    if text == "Як замовити?":
        response = """
📝 *Як зробити замовлення:*
        
1. Натисніть 🛍️ Асортимент
2. Оберіть товари
3. Натисніть 💬Написати менеджеру
4. Напишіть що вас цікавить
5. Очікуйте відповідь менеджера
        
Це просто! 😊
        """
    
    elif text == "Оплата та доставка":
        response = """
💳 *Оплата та доставка:*
        
💸 *Способи оплати:*
• На карту
• Оплата при отриманні
(При замовленні Новою поштою предоплата або повна оплата на карту)
        
🚚 *Доставка:*
• Нова пошта (1-3 дні)
• Самовивіз (Луцьк, Княгининок, Рожище, Копачівка)
(Або по договіру)
        
💰 *Вартість:*
• Від 50 грн
• Безкоштовно від 1000 грн
        """
    
    bot.send_message(chat_id, response, parse_mode='Markdown')
    bot.send_message(chat_id, "Ще питання?", reply_markup=info_menu())

# ==================== КЛІЄНТИ: НАЗАД ====================
@bot.message_handler(func=lambda m: m.text in ["Назад ◀️", "Так, зрозуміло ✅", 
                                              "Скасувати надсилання ❌"])
def handle_back(message):
    text = message.text
    chat_id = message.chat.id
    
    # Якщо це адмін - не обробляємо тут (це буде в адмін-панелі)
    if is_admin(message.from_user.id):
        return
    
    if text == "Скасувати надсилання ❌":
        bot.send_message(chat_id, "✅ Надсилання скасоване.", reply_markup=main_menu())
    else:
        bot.send_message(chat_id, "Головне меню:", reply_markup=main_menu())

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
    send_to_admin_group(user, order_text)

def send_to_admin_group(user, order_text):
    """Відправляє замовлення в групу"""
    try:
        admin_msg = f"""
📦 *НОВЕ ПОВІДОМЛЕННЯ*

👤 {user.first_name} (@{user.username if user.username else 'без username'})
🆔 {user.id}

📝 {order_text}

💬 Відповісти: tg://user?id={user.id}"""
        
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(
            "💬 Відповісти клієнту", 
            callback_data=f"reply_{user.id}"
        ))
        
        bot.send_message(ADMIN_GROUP_ID, admin_msg, parse_mode='Markdown', reply_markup=markup)
    except Exception as e:
        print(f"❌ Помилка відправки в групу: {e}")

# ==================== ОБРОБНИК КОМАНДИ /STOP ====================
@bot.message_handler(commands=['stop'])
def handle_stop_command(message):
    user_id = message.from_user.id
    
    bot.send_message(user_id,
                    "🔕 *Ви відписались від розсилок*\n\n"
                    "Ви більше не будете отримувати повідомлення про новинки та акції.\n\n"
                    "Якщо захочете повернутись, просто напишіть /start",
                    parse_mode='Markdown')
    
    # Позначаємо користувача як такого, що відписався
    if str(user_id) in chat_manager.chats:
        chat_manager.chats[str(user_id)]["status"] = "unsubscribed"
        chat_manager.save_chats()

# ==================== ІМПОРТ ТА ІНІЦІАЛІЗАЦІЯ АДМІН-ПАНЕЛІ ====================
# Імпорт тут, щоб уникнути циркулярних залежностей
from admin_panel import AdminPanel

# Ініціалізуємо адмін-панель ПІСЛЯ визначення всіх клієнтських обробників
try:
    admin_panel = AdminPanel(bot)
    admin_panel.setup_handlers()
    print("✅ Адмін-панель ініціалізована")
except Exception as e:
    print(f"❌ Помилка ініціалізації адмін-панелі: {e}")

# ==================== ТЕСТОВА КОМАНДА ====================
@bot.message_handler(commands=['ping', 'test'])
def ping_command(message):
    bot.reply_to(message, f"🏓 Понг! Бот працює!\nЧас: {time.ctime()}\nВаш ID: {message.from_user.id}")

# ==================== ВЕБХУК ====================
@app.route('/')
def index():
    return "🤖 Бот працює!"

@app.route('/health')
def health_check():
    return {
        "status": "online",
        "time": time.ctime(),
        "bot_token_set": bool(TOKEN),
        "token_length": len(TOKEN) if TOKEN else 0
    }

@app.route('/set_webhook')
def set_webhook():
    bot.remove_webhook()
    webhook_url = f"https://kobraua_bot.onrender.com/{TOKEN}"
    result = bot.set_webhook(webhook_url)
    return f"✅ Вебхук встановлено на {webhook_url}<br>Результат: {result}"

@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        
        try:
            update = telebot.types.Update.de_json(json_string)
            bot.process_new_updates([update])
            return ''
        except Exception as e:
            print(f"❌ Помилка обробки вебхука: {e}")
            return 'ERROR', 400
    else:
        print(f"❌ Неправильний content-type")
        return 'ERROR', 400

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    
    print(f"🚀 Запускаю бота на порті {port}")
    print(f"🌐 URL бота: https://kobraua_bot.onrender.com/")
    print(f"🩺 Health check: https://kobraua_bot.onrender.com/health")
    
    app.run(host='0.0.0.0', port=port)
