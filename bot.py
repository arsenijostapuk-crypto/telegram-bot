import os
import time
from flask import Flask, request
import telebot
from telebot import types
from telebot.apihelper import ApiTelegramException

app = Flask(__name__)

# Налаштування
TOKEN = os.getenv("MY_BOT_TOKEN")
if not TOKEN:
    raise ValueError("❌ Токен не знайдено!")

bot = telebot.TeleBot(TOKEN)
print("✅ Бот ініціалізовано")

# ==================== ІМПОРТ МОДУЛІВ ====================
try:
    from products import get_product_response
    from keyboards import (
        main_menu, assortment_menu, liquids_menu, pods_menu,
        cartridges_menu, delivery_menu, order_menu, info_menu
    )
    from config import ADMIN_IDS, is_admin
    from chat_manager import chat_manager
    print("✅ Всі модулі імпортовано")
except Exception as e:
    print(f"❌ Помилка імпорту модулів: {e}")
    raise

ADMIN_GROUP_ID = -1003654920245

# ==================== КЛІЄНТСЬКІ ОБРОБНИКИ ====================
# Тексти повідомлень
WELCOME_TEXT = """
👋 *Вітаємо в нашому боті!*

Обирайте необхідний розділ:

🛍️ *Асортимент* - переглянути товари
📦 *💬Написати менеджеру* - створити замовлення
ℹ️ *Детальніше* - інформація про бота

Оберіть пункт меню 👇
"""

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.send_message(message.chat.id, WELCOME_TEXT, 
                    parse_mode='Markdown', reply_markup=main_menu())

@bot.message_handler(func=lambda m: m.text in ["🛍️ Асортимент"])
def handle_assortment(message):
    bot.send_message(message.chat.id, "Оберіть категорію товарів:", 
                    reply_markup=assortment_menu())

@bot.message_handler(func=lambda m: m.text in ["💧 Рідини", "🔋 Под-системи", "🎯 Картриджі"])
def handle_categories(message):
    text = message.text
    chat_id = message.chat.id
    
    if text == "💧 Рідини":
        bot.send_message(chat_id, "Оберіть рідину:", reply_markup=liquids_menu())
    elif text == "🔋 Под-системи":
        bot.send_message(chat_id, "Оберіть под-систему:", reply_markup=pods_menu())
    elif text == "🎯 Картриджі":
        bot.send_message(chat_id, "Оберіть картриджі:", reply_markup=cartridges_menu())

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

# ==================== ОБРОБНИК "НАЗАД" ====================
@bot.message_handler(func=lambda m: m.text == "Назад ◀️")
def handle_back(message):
    bot.send_message(message.chat.id, "Головне меню:", reply_markup=main_menu())

# ==================== ІНШІ КЛІЄНТСЬКІ ОБРОБНИКИ ====================
@bot.message_handler(func=lambda m: m.text == "💬Написати менеджеру")
def handle_order_request(message):
    ORDER_TEXT = """
📦 *Оформлення замовлення*
Напишіть що вас цікавить
*Приклад повідомлення:*
"Chaser 30 ml for pods Виноград- 2 шт, Vaporesso XROS 5 - 1 шт"
"""
    bot.send_message(message.chat.id, ORDER_TEXT, 
                    parse_mode='Markdown', reply_markup=order_menu())
    bot.register_next_step_handler(message, process_order)

def process_order(message):
    if message.text == "Скасувати надсилання ❌":
        bot.send_message(message.chat.id, "✅ Надсилання скасовано.", reply_markup=main_menu())
        return
    
    user = message.from_user
    chat_manager.start_chat(user.id, user.first_name, user.username)
    chat_manager.add_message(user.id, message.text, from_admin=False)
    
    bot.send_message(
        message.chat.id,
        f"✅ *Повідомлення відправлене!*\n\nМенеджер зв'яжеться протягом 5-15 хвилин.",
        parse_mode='Markdown',
        reply_markup=main_menu()
    )
    
    # Відправка в групу
    try:
        admin_msg = f"📦 НОВЕ ПОВІДОМЛЕННЯ\n👤 {user.first_name}\n📝 {message.text}"
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("💬 Відповісти", callback_data=f"reply_{user.id}"))
        bot.send_message(ADMIN_GROUP_ID, admin_msg, reply_markup=markup)
    except Exception as e:
        print(f"❌ Помилка відправки в групу: {e}")

@bot.message_handler(func=lambda m: m.text == "ℹ️ Детальніше")
def handle_info(message):
    bot.send_message(message.chat.id, "Оберіть пункт для детальнішої інформації:",
                    reply_markup=info_menu())

# ==================== АДМІН-ПАНЕЛЬ ====================
# Додамо просту адмін-панель без окремого файлу
admin_reply_mode = {}

@bot.message_handler(commands=['admin'])
def admin_panel(message):
    user_id = message.from_user.id
    
    if not is_admin(user_id):
        bot.reply_to(message, f"⛔ Доступ заборонено\nВаш ID: `{user_id}`", parse_mode='Markdown')
        return
    
    from keyboards import admin_main_menu
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

@bot.message_handler(func=lambda m: m.text == "🔙 Головне меню" and is_admin(m.from_user.id))
def back_to_main(message):
    bot.send_message(message.chat.id, "Головне меню:", reply_markup=main_menu())

@bot.message_handler(func=lambda m: m.text == "🔙 Назад в адмін-панель" and is_admin(m.from_user.id))
def back_to_admin(message):
    from keyboards import admin_main_menu
    bot.send_message(message.chat.id, "Адмін-панель:", reply_markup=admin_main_menu())

# ==================== ТЕСТОВІ КОМАНДИ ====================
@bot.message_handler(commands=['ping', 'test'])
def ping_command(message):
    bot.reply_to(message, f"🏓 Понг! Бот працює!\nЧас: {time.ctime()}\nВаш ID: {message.from_user.id}")

@bot.message_handler(commands=['debug'])
def debug_command(message):
    bot.reply_to(message, f"🔍 Дебаг:\nТекст: '{message.text}'\nID: {message.from_user.id}\nЧат: {message.chat.id}")

# ==================== CALLBACK ОБРОБНИКИ ====================
@bot.callback_query_handler(func=lambda call: call.data.startswith('reply_'))
def handle_reply(call):
    admin_id = call.from_user.id
    user_id = call.data.split('_')[1]
    admin_reply_mode[admin_id] = user_id
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(types.KeyboardButton("/cancel"))
    
    bot.send_message(
        admin_id, 
        f"✏️ Відповідь клієнту {user_id}",
        reply_markup=markup
    )
    bot.answer_callback_query(call.id)

@bot.message_handler(commands=['cancel'])
def cancel_reply(message):
    if message.from_user.id in admin_reply_mode:
        del admin_reply_mode[message.from_user.id]
        bot.send_message(message.chat.id, "❌ Режим відповіді скасовано.")
# ==================== ОБРОБНИКИ ІНФОРМАЦІЙНОГО МЕНЮ ====================
@bot.message_handler(func=lambda m: m.text == "Як замовити?")
def how_to_order(message):
    response = """
📝 *ЯК ЗАМОВИТИ:*

1️⃣ *Оберіть товари:*
   • Натисніть 🛍️ *Асортимент*
   • Перегляньте категорії: 💧 Рідини, 🔋 Под-системи, 🎯 Картриджі
   • Обирайте конкретні товари

2️⃣ *Напишіть менеджеру:*
   • Натисніть 💬 *Написати менеджеру*
   • Напишіть повідомлення з вашим замовленням

3️⃣ *Приклад повідомлення:*
   "Chaser 30 ml for pods Виноград - 2 шт, Vaporesso XROS 5 - 1 шт, на завтра 14:00 в с.Княгининок"

4️⃣ *Очікуйте відповідь:*
   • Менеджер зв'яжеться протягом 5-15 хвилин
   • Узгодять деталі, оплату та доставку

📞 *Додатково:* 
Можете написати напряму у телеграм: @ваш_менеджер
"""
    bot.send_message(message.chat.id, response, parse_mode='Markdown')

bot.message_handler(func=lambda m: m.text == "ℹ️ Детальніше")
def handle_info(message):
    info_text = """
📚 *Розділ інформації:*

Тут ви можете дізнатися все про:
• 📝 Як зробити замовлення
• 💰 Умови оплати та доставки

Оберіть потрібний пункт нижче 👇
"""
    bot.send_message(message.chat.id, info_text, parse_mode='Markdown')
    bot.send_message(message.chat.id, "Що вас цікавить?", reply_markup=info_menu())
@bot.message_handler(func=lambda m: m.text == "Оплата та доставка")
def payment_delivery(message):
    response = """
💰 *ОПЛАТА:*

💳 *Способи оплати:*
• ✅ *На карту* (Monobank, PrivatBank)
• ✅ *Готівкою* при отриманні
• ✅ *Накладений платіж* (Нова Пошта)

📝 *Умови:*
• Замовлення Новою Поштою - **передоплата 50%** або повна оплата
• Самовивіз - оплата при отриманні
• Для постійних клієнтів - індивідуальні умови

🚚 *ДОСТАВКА:*

📦 *Нова Пошта:*
• Термін: 1-3 дні
• Вартість: від 50 грн
• Безкоштовно від 1000 грн
• Відділення або адресна доставка

🏪 *Самовивіз:*
• Луцьк (вул. Центральна, 123)
• Княгининок (магазин "Vape Shop")
• Рожище, Копачівка (за попереднім узгодженням)

⏰ *Час доставки:*
• Замовлення до 16:00 - відправка в той же день
• Після 16:00 - наступного дня

📞 *Контакти для питань:*
• Телеграм: @ваш_менеджер
• Телефон: +380XXXXXXXXX
• Графік роботи: 10:00-20:00 щоденно
""" 
    bot.send_message(message.chat.id, response, parse_mode='Markdown())
# ==================== ВЕБХУК ====================
if __name__ == '__main__':
    print("🚀 Запускаю в режимі polling...")
    bot.remove_webhook()
    bot.polling(none_stop=True, interval=0)

