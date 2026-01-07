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

user_reply_mode = {}
# Змінна для відстеження очікування тексту розсилки
broadcast_waiting = {}

try:
    from products import get_product_response
    from keyboards import (
        main_menu, assortment_menu, liquids_menu, pods_menu,
        cartridges_menu, order_menu, info_menu, admin_main_menu
    )
    from config import ADMIN_IDS, is_admin
    from chat_manager import chat_manager
    from admin_panel import AdminPanel, set_chat_manager  # ДОДАТИ set_chat_manager
except ImportError as e:
    print(f"❌ Помилка імпорту: {e}")
    raise

ADMIN_GROUP_ID = -1003654920245

# Передаємо chat_manager в admin_panel
set_chat_manager(chat_manager)

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
"""

# ==================== КЛІЄНТСЬКІ ОБРОБНИКИ ====================
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    print(f"🚀 /start від {message.from_user.id}")
    bot.send_message(message.chat.id, WELCOME_TEXT, 
                    parse_mode='Markdown', reply_markup=main_menu())

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
    "Chaser black 30 ml", "Chaser My Mint 30 ml", "Chaser lux 30 ml",
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
    
    # Перевіряємо, чи користувач у активному чаті
    user_chat = chat_manager.get_chat(message.from_user.id)
    
    if user_chat and user_chat.get('status') == 'active':
        # Якщо активний чат, пропонуємо завершити спілкування
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(types.KeyboardButton("Завершити спілкування ✅"))
        markup.add(types.KeyboardButton("Назад ◀️"))
        
        bot.send_message(
            message.chat.id,
            "💬 *Ви в активному спілкуванні з менеджером*\n\n"
            "Якщо хочете повернутися до головного меню, завершіть спілкування.",
            parse_mode='Markdown',
            reply_markup=markup
        )
    else:
        # Якщо немає активного чату, повертаємо до головного меню
        bot.send_message(message.chat.id, "🏠 Головне меню:", reply_markup=main_menu())
# ==================== ОБРОБНИК "🔙 ГОЛОВНЕ МЕНЮ" ====================
@bot.message_handler(func=lambda m: m.text == "🔙 Головне меню")
def handle_admin_back(message):
    print(f"🎯 Кнопка '🔙 Головне меню' від {message.from_user.id}")
    
    # Завжди повертаємо до головного меню (WELCOME_TEXT)
    bot.send_message(message.chat.id, WELCOME_TEXT, 
                    parse_mode='Markdown', reply_markup=main_menu())

# ==================== ОБРОБНИК "👑 АДМІН-ПАНЕЛЬ" (тільки для адмінів) ====================
@bot.message_handler(func=lambda m: m.text == "👑 Адмін-панель" and is_admin(m.from_user.id))
def handle_admin_panel_button(message):
    print(f"👑 Кнопка 'Адмін-панель' від адміна {message.from_user.id}")
    from keyboards import admin_main_menu
    bot.send_message(message.chat.id, "👑 Адмін-панель:", reply_markup=admin_main_menu())

# ==================== ОБРОБНИК "📢 РОЗСИЛКА" ====================
@bot.message_handler(func=lambda m: m.text == "📢 Розсилка" and is_admin(m.from_user.id))
def handle_broadcast(message):
    print(f"📢 Кнопка 'Розсилка' від адміна {message.from_user.id}")
    
    # Позначаємо, що очікуємо текст від цього адміна
    broadcast_waiting[message.from_user.id] = True
    
    bot.send_message(message.chat.id, 
                     "✍️ *Напишіть повідомлення для розсилки:*\n\n"
                     "⚠️ _Для скасування напишіть /cancel_",
                     parse_mode='Markdown')
# ==================== ОБРОБКА ВІДПОВІДЕЙ КЛІЄНТА ====================
@bot.message_handler(func=lambda m: str(m.from_user.id) in chat_manager.chats and 
                    chat_manager.chats[str(m.from_user.id)].get('status') == 'active' and
                    m.text not in ["Скасувати надсилання ❌", "Назад ◀️", "Завершити спілкування ✅"])
def handle_client_reply(message):
    """Обробка відповіді клієнта після відповіді менеджера"""
    user_id = message.from_user.id
    user_chat = chat_manager.get_chat(user_id)
    
    if not user_chat or user_chat.get('status') != 'active':
        return
    
    # Якщо це команда /cancel, виходимо з режиму відповіді
    if message.text == '/cancel':
        if user_id in user_reply_mode:
            del user_reply_mode[user_id]
        bot.send_message(user_id, "❌ Відповідь скасована.", reply_markup=main_menu())
        return
    
    # Додаємо повідомлення від клієнта
    chat_manager.add_message(user_id, message.text, from_admin=False)
    
    # Відправляємо в адмін-групу
    try:
        admin_msg = (
            f"💬 *ВІДПОВІДЬ ВІД КЛІЄНТА*\n\n"
            f"👤 {message.from_user.first_name}\n"
            f"🆔 ID: `{user_id}`\n"
            f"📝 {message.text}"
        )
        
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            types.InlineKeyboardButton("💬 Відповісти", callback_data=f"reply_{user_id}"),
            types.InlineKeyboardButton("✅ Завершити", callback_data=f"close_{user_id}")
        )
        
        bot.send_message(ADMIN_GROUP_ID, admin_msg, parse_mode='Markdown', reply_markup=markup)
                # Підтвердження клієнту
        bot.send_message(
            user_id,
            "✔ *Повідомлення відправлено менеджеру!*",
            parse_mode='Markdown'
        )
        
        # Показуємо, що можна продовжувати спілкування
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(types.KeyboardButton("Завершити спілкування ✅"))
        
        bot.send_message(
            user_id,
            "📌 *Повідомлення*\n\n"
            "Надішліть своє повідомлення нижче або завершіть розмову",
            parse_mode='Markdown',
            reply_markup=markup
        )
        
        bot.send_message(
            user_id,
            "💬 *Ви можете продовжувати спілкування*\n\n"
            "Напишіть ще повідомлення або натисніть 'Завершити спілкування ✅'",
            parse_mode='Markdown',
            reply_markup=markup
        )
        
    except Exception as e:
        print(f"❌ Помилка при відправці відповіді клієнта: {e}")
        bot.send_message(user_id, "❌ Помилка відправки. Спробуйте ще раз.")
        # ==================== ЗАВЕРШЕННЯ СПІЛКУВАННЯ ====================
@bot.message_handler(func=lambda m: m.text == "Завершити спілкування ✅")
def handle_end_conversation(message):
    """Клієнт завершує спілкування"""
    user_id = message.from_user.id
    user_chat = chat_manager.get_chat(user_id)
    
    if user_chat:
        user_chat['status'] = 'closed'
        user_chat['unread'] = False
        chat_manager.save_chats()
    
    # Повідомляємо адмінів
    try:
        bot.send_message(
            ADMIN_GROUP_ID,
            f"✅ *Клієнт завершив спілкування*\n\n"
            f"👤 {message.from_user.first_name}\n"
            f"🆔 ID: `{user_id}`",
            parse_mode='Markdown'
        )
    except Exception as e:
        print(f"❌ Помилка при відправці в адмін-групу: {e}")
    
    # Повертаємо головне меню клієнту
    bot.send_message(
        user_id,
        "✅ *Спілкування завершено*\n\nДякуємо за звернення! 🛍️",
        parse_mode='Markdown',
        reply_markup=main_menu()
    )
# ==================== ОБРОБНИК ТЕКСТУ РОЗСИЛКИ ====================
@bot.message_handler(func=lambda m: is_admin(m.from_user.id) and broadcast_waiting.get(m.from_user.id, False))
def handle_broadcast_text_input(message):
    print(f"📝 Адмін {message.from_user.id} ввів текст для розсилки")
    
    # Знімаємо прапор очікування
    broadcast_waiting[message.from_user.id] = False
    
    # Обробка тексту розсилки
    if message.text == '/cancel':
        bot.send_message(message.chat.id, "❌ Розсилку скасовано")
        return
    
    admin_id = message.from_user.id
    broadcast_text = message.text
    
    # Підтвердження
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("✅ Так, надіслати", callback_data=f"broadcast_confirm_{admin_id}"),
        types.InlineKeyboardButton("❌ Ні, скасувати", callback_data=f"broadcast_cancel_{admin_id}")
    )
    
    bot.send_message(
        message.chat.id,
        f"📋 *Попередній перегляд розсилки:*\n\n{broadcast_text}\n\n*Підтверджуєте розсилку?*",
        parse_mode='Markdown',
        reply_markup=markup
    )
    
    # Зберігаємо текст
    if not hasattr(bot, 'temp_broadcasts'):
        bot.temp_broadcasts = {}
    bot.temp_broadcasts[admin_id] = broadcast_text

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
        f"✔ *Повідомлення відправлено!*\nМенеджер зв'яжеться за 5-15 хв.",
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

# ==================== CALLBACK ДЛЯ РОЗСИЛКИ ====================
@bot.callback_query_handler(func=lambda call: call.data.startswith('broadcast_'))
def handle_broadcast_confirmation(call):
    admin_id = call.from_user.id
    action = call.data.split('_')[1]  # confirm або cancel
    
    if action == 'cancel':
        bot.answer_callback_query(call.id, "❌ Розсилку скасовано")
        bot.edit_message_text(
            "❌ Розсилку скасовано",
            call.message.chat.id,
            call.message.message_id
        )
        if hasattr(bot, 'temp_broadcasts') and admin_id in bot.temp_broadcasts:
            del bot.temp_broadcasts[admin_id]
        return
    
    # Підтверджено розсилку
    if action == 'confirm' and hasattr(bot, 'temp_broadcasts') and admin_id in bot.temp_broadcasts:
        broadcast_text = bot.temp_broadcasts[admin_id]
        
        bot.edit_message_text(
            "🔄 *Розсилка розпочата...*",
            call.message.chat.id,
            call.message.message_id,
            parse_mode='Markdown'
        )
        
        # Отримуємо всіх користувачів
        users = chat_manager.get_all_users()
        total_users = len(users)
        successful = 0
        failed = 0
        
        # Розсилка
        for user_id_str in users.keys():
            try:
                user_id = int(user_id_str)
                bot.send_message(user_id, f"📢 *Розсилка:*\n\n{broadcast_text}", parse_mode='Markdown')
                successful += 1
                time.sleep(0.05)  # Невелика затримка
            except Exception as e:
                failed += 1
                print(f"❌ Помилка відправки {user_id_str}: {e}")
        
        # Результат
        result_text = (
            f"✅ *Розсилка завершена!*\n\n"
            f"👥 Загальна кількість: {total_users}\n"
            f"✅ Успішно: {successful}\n"
            f"❌ Не вдалося: {failed}"
        )
        
        bot.edit_message_text(
            result_text,
            call.message.chat.id,
            call.message.message_id,
            parse_mode='Markdown'
        )
        
        bot.answer_callback_query(call.id, "✅ Розсилку завершено")
        
        # Видаляємо тимчасові дані
        del bot.temp_broadcasts[admin_id]

# ==================== ДЕБАГ ВСІХ ПОВІДОМЛЕНЬ (МАЄ БУТИ ОСТАННІМ!) ====================
@bot.message_handler(func=lambda m: True)
def debug_all_messages(message):
    if message.text:
        print(f"📥 Повідомлення: '{message.text}' від {message.from_user.id}")

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











