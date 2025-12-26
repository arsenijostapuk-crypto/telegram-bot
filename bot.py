import os
import time
from flask import Flask, request
import telebot
from telebot import types
from telebot.apihelper import ApiTelegramException

app = Flask(__name__)

# ==================== НАЛАШТУВАННЯ ====================
TOKEN = os.getenv("MY_BOT_TOKEN")
if not TOKEN:
    raise ValueError("❌ Токен не знайдено!")

bot = telebot.TeleBot(TOKEN)
print(f"✅ Бот ініціалізовано")

# ==================== ІМПОРТ МОДУЛІВ ====================
try:
    from products import get_product_response
    from keyboards import (
        main_menu, assortment_menu, liquids_menu, pods_menu,
        cartridges_menu, order_menu, info_menu, admin_main_menu
    )
    from config import ADMIN_IDS, is_admin
    from chat_manager import chat_manager
    print("✅ Всі модулі імпортовано")
except Exception as e:
    print(f"❌ Помилка імпорту модулів: {e}")
    raise

ADMIN_GROUP_ID = -1003654920245

# ==================== ДЕБАГ ВСІХ ПОВІДОМЛЕНЬ ====================
@bot.message_handler(func=lambda m: True)
def debug_all_messages(message):
    if message.text:
        print(f"📥 Отримано: '{message.text}' від {message.from_user.id}")

# ==================== ОСНОВНІ КОМАНДИ ====================
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    print(f"✅ /start від {message.from_user.id}")
    WELCOME_TEXT = """
👋 *Вітаємо в нашому боті!*

Обирайте необхідний розділ:

🛍️ *Асортимент* - переглянути товари
📦 *💬Написати менеджеру* - створити замовлення
ℹ️ *Детальніше* - інформація про бота

Оберіть пункт меню 👇
"""
    bot.send_message(message.chat.id, WELCOME_TEXT, 
                    parse_mode='Markdown', reply_markup=main_menu())

@bot.message_handler(commands=['test', 'ping'])
def test_command(message):
    bot.reply_to(message, 
                f"✅ *Бот працює!*\n\n"
                f"Час: {time.ctime()}\n"
                f"Ваш ID: `{message.from_user.id}`",
                parse_mode='Markdown')

# ==================== ГОЛОВНЕ МЕНЮ ====================
@bot.message_handler(func=lambda m: m.text == "🛍️ Асортимент")
def handle_assortment(message):
    bot.send_message(message.chat.id, "Оберіть категорію товарів:", 
                    reply_markup=assortment_menu())

@bot.message_handler(func=lambda m: m.text == "💬Написати менеджеру")
def handle_order_request(message):
    ORDER_TEXT = """
📦 *Оформлення замовлення*

Напишіть що вас цікавить
*Приклад повідомлення:*
"Chaser 30 ml for pods Виноград- 2 шт, Vaporesso XROS 5 - 1 шт"

Наш менеджер зв'яжеться з вами протягом 5-15 хвилин.
"""
    bot.send_message(message.chat.id, ORDER_TEXT, 
                    parse_mode='Markdown', reply_markup=order_menu())
    bot.register_next_step_handler(message, process_order)

@bot.message_handler(func=lambda m: m.text == "ℹ️ Детальніше")
def handle_info(message):
    bot.send_message(message.chat.id, "Оберіть пункт:", reply_markup=info_menu())

# ==================== КАТЕГОРІЇ ТОВАРІВ ====================
@bot.message_handler(func=lambda m: m.text in ["💧 Рідини", "🔋 Под-системи", "🎯 Картриджі"])
def handle_categories(message):
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
    response = get_product_response(message.text)
    bot.send_message(message.chat.id, response, parse_mode='Markdown')

# ==================== НАЙВАЖЛИВІШЕ: ОБРОБНИК "НАЗАД ◀️" ====================
@bot.message_handler(func=lambda m: m.text == "Назад ◀️")
def handle_back(message):
    print(f"🎯 КНОПКА 'НАЗАД' НАТИСНУТА від {message.from_user.id}")
    bot.send_message(message.chat.id, "Головне меню:", reply_markup=main_menu())

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
    bot.send_message(message.chat.id, "Ще питання?", reply_markup=info_menu())

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
    bot.send_message(message.chat.id, "Ще питання?", reply_markup=info_menu())

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
        admin_msg = f"""
📦 *НОВЕ ЗАМОВЛЕННЯ*

👤 {user.first_name} (@{user.username if user.username else 'без username'})
🆔 {user.id}

📝 {message.text}"""
        
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(
            "💬 Відповісти клієнту", 
            callback_data=f"reply_{user.id}"
        ))
        
        bot.send_message(ADMIN_GROUP_ID, admin_msg, parse_mode='Markdown', reply_markup=markup)
    except Exception as e:
        print(f"❌ Помилка відправки в групу: {e}")

# ==================== АДМІН ПАНЕЛЬ ====================
admin_reply_mode = {}
broadcast_texts = {}

@bot.message_handler(commands=['admin'])
def admin_panel(message):
    user_id = message.from_user.id
    
    if not is_admin(user_id):
        bot.reply_to(message, f"⛔ Доступ заборонено\nВаш ID: `{user_id}`", parse_mode='Markdown')
        return
    
    bot.send_message(message.chat.id, 
                    f"👑 *Адмін-панель*\nВітаємо, {message.from_user.first_name}!",
                    parse_mode='Markdown', 
                    reply_markup=admin_main_menu())

@bot.message_handler(func=lambda m: m.text == "📢 Розсилка" and is_admin(m.from_user.id))
def broadcast_menu(message):
    all_users = chat_manager.get_all_users()
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        types.KeyboardButton(f"✅ Розіслати ({len(all_users)} клієнтів)"),
        types.KeyboardButton("🔙 Назад в адмін-панель")
    )
    
    bot.send_message(message.chat.id, 
                    f"📢 *Меню розсилки*\nКористувачів: *{len(all_users)}*",
                    parse_mode='Markdown',
                    reply_markup=markup)

@bot.message_handler(func=lambda m: m.text.startswith("✅ Розіслати") and is_admin(m.from_user.id))
def start_broadcast(message):
    bot.send_message(message.chat.id, 
                    "📝 *Створення розсилки*\nНапишіть текст розсилки:",
                    parse_mode='Markdown',
                    reply_markup=types.ForceReply(selective=True))
    
    bot.register_next_step_handler(message, confirm_broadcast)

def confirm_broadcast(message):
    admin_id = message.from_user.id
    broadcast_text = message.text
    
    if len(broadcast_text.strip()) < 5:
        bot.send_message(admin_id, "❌ Текст занадто короткий.")
        return
    
    all_users = chat_manager.get_all_users()
    total_users = len(all_users)
    
    broadcast_texts[admin_id] = broadcast_text
    
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("🚀 Розіслати зараз", callback_data="broadcast_now"),
        types.InlineKeyboardButton("❌ Скасувати", callback_data="broadcast_cancel")
    )
    
    bot.send_message(admin_id,
                    f"📢 *Попередній перегляд:*\n\n{broadcast_text[:200]}...\n\n"
                    f"Отримувачі: *{total_users}*",
                    parse_mode='Markdown',
                    reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "broadcast_now")
def execute_broadcast(call):
    admin_id = call.from_user.id
    
    if admin_id not in broadcast_texts:
        bot.answer_callback_query(call.id, "❌ Текст не знайдено")
        return
    
    broadcast_text = broadcast_texts[admin_id]
    all_users = chat_manager.get_all_users()
    total_users = len(all_users)
    
    bot.send_message(admin_id, f"📤 Розсилка розпочата для {total_users} користувачів...")
    
    successful = 0
    failed = 0
    
    for user_id in all_users.keys():
        try:
            bot.send_message(int(user_id), 
                           f"📢 *ПОВІДОМЛЕННЯ ВІД МАГАЗИНУ:*\n\n{broadcast_text}",
                           parse_mode='Markdown')
            successful += 1
        except Exception as e:
            failed += 1
    
    report = f"✅ *РОЗСИЛКА ЗАВЕРШЕНА!*\n\n"
    report += f"👥 Загальна кількість: {total_users}\n"
    report += f"✅ Успішно: {successful}\n"
    report += f"❌ Не вдалося: {failed}\n"
    
    if successful > 0:
        report += f"📈 Ефективність: {successful/total_users*100:.1f}%\n"
    
    bot.send_message(admin_id, report, parse_mode='Markdown', reply_markup=admin_main_menu())
    bot.answer_callback_query(call.id, "✅ Розсилка завершена!")

@bot.callback_query_handler(func=lambda call: call.data == "broadcast_cancel")
def cancel_broadcast(call):
    admin_id = call.from_user.id
    broadcast_texts.pop(admin_id, None)
    bot.send_message(admin_id, "❌ Розсилка скасована.", reply_markup=admin_main_menu())
    bot.answer_callback_query(call.id, "Скасовано")

@bot.message_handler(func=lambda m: m.text == "🔙 Головне меню" and is_admin(m.from_user.id))
def back_to_main_admin(message):
    bot.send_message(message.chat.id, "Головне меню:", reply_markup=main_menu())

@bot.message_handler(func=lambda m: m.text == "🔙 Назад в адмін-панель" and is_admin(m.from_user.id))
def back_to_admin(message):
    bot.send_message(message.chat.id, "Адмін-панель:", reply_markup=admin_main_menu())

# ==================== CALLBACK ОБРОБНИКИ ====================
@bot.callback_query_handler(func=lambda call: call.data.startswith('reply_'))
def handle_reply(call):
    admin_id = call.from_user.id
    user_id = call.data.split('_')[1]
    admin_reply_mode[admin_id] = user_id
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(types.KeyboardButton("/cancel"))
    
    bot.send_message(admin_id, f"✏️ Відповідь клієнту {user_id}", reply_markup=markup)
    bot.answer_callback_query(call.id)

# ==================== ВЕБХУК МАРШРУТИ ====================
@app.route('/')
def index():
    return "🤖 Бот працює!"

@app.route('/health')
def health_check():
    return {
        "status": "online", 
        "time": time.ctime(),
        "service": "Telegram Bot"
    }

@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        try:
            json_string = request.get_data().decode('utf-8')
            update = telebot.types.Update.de_json(json_string)
            bot.process_new_updates([update])
            return ''
        except Exception as e:
            print(f"❌ Помилка вебхука: {e}")
            return 'ERROR', 400
    return 'ERROR', 400

# ==================== ЗАПУСК ====================
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    
    print(f"🚀 Запускаю бота на порті {port}")
    print(f"🌐 URL: https://telegram-bot-iss2.onrender.com")
    print(f"📱 Тестуйте: /start → Натисніть 'Назад ◀️'")
    print(f"👑 Адмін: /admin")
    
    # Автоматично встановлюємо вебхук
    try:
        webhook_url = f"https://telegram-bot-iss2.onrender.com/{TOKEN}"
        bot.remove_webhook()
        time.sleep(1)
        bot.set_webhook(url=webhook_url)
        print(f"✅ Вебхук встановлено: {webhook_url}")
    except Exception as e:
        print(f"⚠️ Помилка вебхука: {e}")
    
    app.run(host='0.0.0.0', port=port)
