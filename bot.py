import os
from flask import Flask, request
import telebot
from telebot import types

# Імпорт меню
from keyboards import (
    main_menu, assortment_menu, liquids_menu, pods_menu,
    cartridges_menu, delivery_menu, order_menu, info_menu
)

app = Flask(__name__)

# Конфігурація
TOKEN = os.getenv("MY_BOT_TOKEN")
if not TOKEN:
    raise ValueError("❌ Токен не знайдено! Встанови MY_BOT_TOKEN у Render.")

bot = telebot.TeleBot(TOKEN)

# ID групи для замовлень (замінити на свій!)
ADMIN_GROUP_ID = -1003654920245

# Словник для станів користувачів
user_states = {}

# Тексти повідомлень
WELCOME_TEXT = """👋 *Вітаємо!*

Оберіть розділ:

🛍️ *Асортимент* — товари
🚚 *Доставка* — умови доставки
📦 *Замовлення* — створити замовлення
ℹ️ *Детальніше* — інформація про бота"""

DELIVERY_TEXT = """🚚 *Доставка*

📍 *Способи:*
• Нова пошта
• Укрпошта
• Самовивіз (Київ)

⏰ *Терміни:*
• Київ: 1-2 дні
• Україна: 2-5 днів

💰 *Вартість:*
• Від 50 грн
• Безкоштовно від 1000 грн

📞 *Контакти:*
+380XXXXXXXXX
@ваш_контакт"""

ORDER_TEXT = """📦 *Замовлення*

Напишіть:
• Назва товару
• Кількість
• Контакти
• Спосіб доставки

*Приклад:*
"Chaser 30 ml - 2 шт, доставка Нова Пошта, телефон 0991234567"

Менеджер зв'яжеться за 5-15 хвилин.

*Напишіть нижче:*"""

INFO_TEXT = """ℹ️ *Про бота*

🤖 *Як користуватись:*
1. 🛍️ Асортимент → товари
2. 📦 Замовлення → напишіть що потрібно
3. Очікуйте дзвінка

💳 *Оплата:*
• Карта
• При отриманні
• Google/Apple Pay

🛡️ *Гарантія:*
• 14 днів
• Оригінальна упаковка"""

# Команди
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.send_message(message.chat.id, WELCOME_TEXT, 
                     parse_mode='Markdown', reply_markup=main_menu())

# Головне меню
@bot.message_handler(func=lambda m: m.text in [
    "🛍️ Асортимент", "🚚 Доставка", "📦 Замовлення", "ℹ️ Детальніше"
])
def handle_main_menu(message):
    text = message.text
    chat_id = message.chat.id
    
    if text == "🛍️ Асортимент":
        bot.send_message(chat_id, "Оберіть категорію:", reply_markup=assortment_menu())
    
    elif text == "🚚 Доставка":
        bot.send_message(chat_id, DELIVERY_TEXT, parse_mode='Markdown', reply_markup=delivery_menu())
    
    elif text == "📦 Замовлення":
        bot.send_message(chat_id, ORDER_TEXT, parse_mode='Markdown', reply_markup=order_menu())
        user_states[message.from_user.id] = "waiting_order"
    
    elif text == "ℹ️ Детальніше":
        bot.send_message(chat_id, INFO_TEXT, parse_mode='Markdown', reply_markup=info_menu())

# Асортимент
@bot.message_handler(func=lambda m: m.text in ["💧 Рідини", "🔋 Под-системи", "🎯 Картриджі"])
def handle_assortment(message):
    text = message.text
    chat_id = message.chat.id
    
    if text == "💧 Рідини":
        bot.send_message(chat_id, "Оберіть рідину:", reply_markup=liquids_menu())
    elif text == "🔋 Под-системи":
        bot.send_message(chat_id, "Оберіть под:", reply_markup=pods_menu())
    elif text == "🎯 Картриджі":
        bot.send_message(chat_id, "Оберіть картриджі:", reply_markup=cartridges_menu())

# Інформаційне меню
@bot.message_handler(func=lambda m: m.text in ["📝 Як замовити?", "💳 Оплата та доставка", "🛡️ Гарантія"])
def handle_info_submenu(message):
    text = message.text
    chat_id = message.chat.id
    
    if text == "📝 Як замовити?":
        response = "📝 *Як замовити:*\n\n1. Обирайте товари\n2. Натискайте '📦 Замовлення'\n3. Пишіть що потрібно\n4. Очікуйте дзвінка"
    elif text == "💳 Оплата та доставка":
        response = "💳 *Оплата:*\n• Карта\n• При отриманні\n\n🚚 *Доставка:*\n• Нова пошта\n• Укрпошта\n• Самовивіз"
    else:  # Гарантія
        response = "🛡️ *Гарантія:*\n• 14 днів\n• Оригінальна упаковка\n• Обмін/повернення"
    
    bot.send_message(chat_id, response, parse_mode='Markdown')

# Товари
@bot.message_handler(func=lambda m: m.text in [
    "Chaser 10 ml", "Chaser 30 ml for pods", "Chaser mix 30 ml",
    "Chaser black 30 ml", "Chaser lux 30 ml", "Chaser black 30 ml 50 mg",
    "Xlim", "Vaporesso", "Інші бренди", "Картриджі Xlim", "Картриджі Vaporesso"
])
def handle_products(message):
    text = message.text
    chat_id = message.chat.id
    
    if text == "Інші бренди":
        response = "Інші бренди:\n• SMOK\n• GeekVape\n• Voopoo\n• OXVA"
    else:
        response = f"🏷️ *{text}*\n\n💰 Ціна: від 299 грн\n📦 В наявності\n⭐ 4.8/5\n\nДля замовлення натисніть '📦 Замовлення'"
    
    bot.send_message(chat_id, response, parse_mode='Markdown')

# Назад та скасування
@bot.message_handler(func=lambda m: m.text in ["⬅️ Назад", "✅ Зрозуміло", "❌ Скасувати замовлення"])
def handle_back(message):
    text = message.text
    chat_id = message.chat.id
    user_id = message.from_user.id
    
    # Очистити стан
    if user_id in user_states:
        del user_states[user_id]
    
    if text == "❌ Скасувати замовлення":
        bot.send_message(chat_id, "✅ Замовлення скасовано", reply_markup=main_menu())
    else:
        bot.send_message(chat_id, "Головне меню:", reply_markup=main_menu())

# Загальний обробник
@bot.message_handler(func=lambda m: True)
def handle_all_messages(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    text = message.text
    
    # Якщо користувач чекає на замовлення
    if user_id in user_states and user_states[user_id] == "waiting_order":
        if text == "❌ Скасувати замовлення":
            del user_states[user_id]
            bot.send_message(chat_id, "✅ Замовлення скасовано", reply_markup=main_menu())
            return
        
        # Обробити замовлення
        process_order(message)
        if user_id in user_states:
            del user_states[user_id]
        return
    
    # Інакше показати меню
    bot.send_message(chat_id, "Оберіть пункт з меню 👇", reply_markup=main_menu())

# Обробка замовлення
def process_order(message):
    chat_id = message.chat.id
    user = message.from_user
    order_text = message.text
    
    # Повідомлення користувачу
    bot.send_message(
        chat_id,
        f"✅ *Замовлення прийнято!*\n\nВаше повідомлення:\n{order_text}\n\nМенеджер зв'яжеться за 5-15 хвилин.",
        parse_mode='Markdown',
        reply_markup=main_menu()
    )
    
    # Повідомлення в групу
    try:
        admin_msg = f"""📦 НОВЕ ЗАМОВЛЕННЯ

👤 {user.first_name} (@{user.username if user.username else 'без username'})
🆔 {user.id}

📝 {order_text}

💬 Відповісти: tg://user?id={user.id}"""
        
        bot.send_message(ADMIN_GROUP_ID, admin_msg)
        print(f"✅ Замовлення відправлено: {user.first_name}")
    except Exception as e:
        print(f"❌ Помилка: {e}")

# Вебхук
@app.route('/')
def index():
    return "🤖 Бот працює!"

@app.route('/set_webhook')
def set_webhook():
    bot.remove_webhook()
    bot.set_webhook(f"https://telegram-bot-iss2.onrender.com/{TOKEN}")
    return "✅ Вебхук встановлено"

@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return ''
    return 'ERROR', 400

# Запуск
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
