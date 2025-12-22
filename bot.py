import os
from flask import Flask, request
import telebot
from telebot import types
from products import get_product_response
# Імпорти
from keyboards import (
    main_menu, assortment_menu, liquids_menu, pods_menu,
    cartridges_menu, delivery_menu, order_menu, info_menu,
    admin_main_menu
)
from config import ADMIN_IDS, is_admin
ADMIN_GROUP_ID = -1003654920245
from chat_manager import chat_manager

app = Flask(__name__)

# Налаштування
TOKEN = os.getenv("MY_BOT_TOKEN")
if not TOKEN:
    raise ValueError("❌ Токен не знайдено!")

bot = telebot.TeleBot(TOKEN)

# Для відповідей адміна
admin_reply_mode = {}

# Тексти повідомлень
WELCOME_TEXT = """
👋 *Вітаємо в нашому боті!*

Обирайте необхідний розділ:

🛍️ *Асортимент* - переглянути товари
📦 *Замовлення* - створити замовлення
ℹ️ *Детальніше* - інформація про бота

Оберіть пункт меню 👇
"""

ORDER_TEXT = """
📦 *Оформлення замовлення*

Напишіть що вас цікавать
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
3. Для замовлення натисніть 📦 Замовлення
4. Напишіть що вас цікавить
5. Очікуйте відповідь від менеджера

"""

# ==================== КЛІЄНТИ: ГОЛОВНЕ МЕНЮ ====================
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.send_message(message.chat.id, WELCOME_TEXT, 
                    parse_mode='Markdown', reply_markup=main_menu())

@bot.message_handler(func=lambda m: m.text in ["🛍️ Асортимент",
                                              "📦 Замовлення", "ℹ️ Детальніше"])
def handle_main_menu(message):
    text = message.text
    chat_id = message.chat.id
    
    if text == "🛍️ Асортимент":
        bot.send_message(chat_id, "Оберіть категорію товарів:", 
                        reply_markup=assortment_menu())
    
    elif text == "📦 Замовлення":
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
    "Chaser 10 ml", "Chaser 30 ml for pods", "Chaser mix 30 ml",
    "Chaser black 30 ml", "Chaser lux 30 ml", "Chaser black 30 ml 50 mg",
    "Xlim", "Vaporesso", "Інші бренди",
    "Картриджі Xlim", "Картриджі Vaporesso"
])
def handle_products(message):
    """Обробка вибору товарів (проста версія)"""
    text = message.text
    chat_id = message.chat.id
    
    # Отримуємо текст з products.py
    response = get_product_response(text)
    
    bot.send_message(chat_id, response, parse_mode='Markdown', reply_markup=markup)

# ==================== КЛІЄНТИ: ІНФОРМАЦІЯ ====================
@bot.message_handler(func=lambda m: m.text in ["Як замовити?", "Оплата та доставка",
                                              "Гарантія"])
def handle_info_menu(message):
    text = message.text
    chat_id = message.chat.id
    
    if text == "Як замовити?":
        response = """
📝 *Як зробити замовлення:*
        
1. Натисніть 🛍️ Асортимент
2. Оберіть товари
3. Натисніть 📦 Замовлення
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
                                              "Скасувати замовлення ❌"])
def handle_back(message):
    text = message.text
    chat_id = message.chat.id
    
    if text == "Скасувати замовлення ❌":
        bot.send_message(chat_id, "✅ Замовлення скасовано.", reply_markup=main_menu())
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
        f"✅ *Повідомлення повідомлення відправлене!*\n\nВаше повідомлення:\n{order_text}\n\nМенеджер зв'яжеться протягом 5-15 хвилин.",
        parse_mode='Markdown',
        reply_markup=main_menu()
    )
    
    # Повідомлення в групу
    send_to_admin_group(user, order_text)
    
    # Повідомлення адмінам для чату
    notify_admins_about_order(user, order_text)

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

# ==================== АДМІНИ ====================
@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "⛔ Доступ заборонено")
        return
    
    bot.send_message(message.chat.id, "👑 *Адмін-панель*", 
                    parse_mode='Markdown', reply_markup=admin_main_menu())

@bot.message_handler(func=lambda m: m.text == "📋 Активні чати")
def show_active_chats(message):
    if not is_admin(message.from_user.id):
        return
    
    active_chats = chat_manager.get_active_chats()
    
    if not active_chats:
        bot.send_message(message.chat.id, "📭 Немає активних чатів")
        return
    
    text = "📋 *Активні чати/замовлення:*\n\n"
    for user_id, chat in active_chats.items():
        text += f"👤 {chat['user_name']}\n"
        text += f"🆔: `{user_id}`\n"
        text += f"💬 Повідомлень: {len(chat['messages'])}\n"
        if chat.get('unread'):
            text += "🔴 *НЕПРОЧИТАНЕ*\n"
        text += "⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n"
    
    markup = types.InlineKeyboardMarkup()
    for user_id in active_chats.keys():
        markup.add(types.InlineKeyboardButton(
            f"💬 Чат з {user_id[:6]}...", 
            callback_data=f"open_{user_id}"
        ))
    
    bot.send_message(message.chat.id, text, parse_mode='Markdown', reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "🆕 Нові повідомлення")
def show_unread_chats(message):
    if not is_admin(message.from_user.id):
        return
    
    unread_chats = chat_manager.get_unread_chats()
    
    if not unread_chats:
        bot.send_message(message.chat.id, "✅ Немає нових повідомлень")
        return
    
    text = "🆕 *Непрочитані повідомлення:*\n\n"
    for user_id, chat in unread_chats.items():
        text += f"👤 {chat['user_name']}\n"
        text += f"🆔: `{user_id}`\n"
        if chat['messages']:
            last_msg = chat['messages'][-1]['text'][:50]
            text += f"💬 {last_msg}...\n"
        text += "⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n"
    
    markup = types.InlineKeyboardMarkup()
    for user_id in unread_chats.keys():
        markup.add(types.InlineKeyboardButton(
            f"📨 Відповісти {user_id[:6]}...", 
            callback_data=f"reply_{user_id}"
        ))
    
    bot.send_message(message.chat.id, text, parse_mode='Markdown', reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "💬 Відповісти клієнту")
def select_client_to_reply(message):
    if not is_admin(message.from_user.id):
        return
    
    active_chats = chat_manager.get_active_chats()
    
    if not active_chats:
        bot.send_message(message.chat.id, "📭 Немає активних чатів")
        return
    
    markup = types.InlineKeyboardMarkup()
    for user_id, chat in active_chats.items():
        markup.add(types.InlineKeyboardButton(
            f"💬 {chat['user_name']} ({user_id[:6]})", 
            callback_data=f"reply_{user_id}"
        ))
    
    bot.send_message(message.chat.id, "Оберіть клієнта для відповіді:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('open_'))
def open_chat(call):
    admin_id = call.from_user.id
    user_id = call.data.split('_')[1]
    
    chat = chat_manager.chats.get(user_id)
    if not chat:
        bot.answer_callback_query(call.id, "Чат не знайдено")
        return
    
    # Позначаємо як прочитаний
    chat['unread'] = False
    chat_manager.save_chats()
    
    # Показуємо історію
    history = f"💬 *Чат з {chat['user_name']}*\n"
    history += f"👤 @{chat['username']}\n"
    history += f"🆔 `{user_id}`\n\n"
    
    for msg in chat['messages'][-10:]:
        sender = "👨‍💼 Ви" if msg['from_admin'] else "👤 Клієнт"
        history += f"{sender}: {msg['text']}\n"
        history += f"⏰ {msg['time'][11:16]}\n\n"
    
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("✏️ Відповісти", callback_data=f"reply_{user_id}"),
        types.InlineKeyboardButton("✅ Завершити", callback_data=f"close_{user_id}")
    )
    
    bot.send_message(admin_id, history, parse_mode='Markdown', reply_markup=markup)
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data.startswith('reply_'))
def start_reply(call):
    admin_id = call.from_user.id
    user_id = call.data.split('_')[1]
    
    admin_reply_mode[admin_id] = user_id
    
    bot.send_message(admin_id, f"✏️ *Відповідь клієнту {user_id}*\n\nНапишіть ваше повідомлення:")
    bot.answer_callback_query(call.id)

# Обробка повідомлень адміна для клієнтів
@bot.message_handler(func=lambda m: m.from_user.id in admin_reply_mode)
def send_reply_to_client(message):
    admin_id = message.from_user.id
    user_id = admin_reply_mode.get(admin_id)
    
    if not user_id or message.text.startswith('/'):
        return
    
    try:
        # Відправляємо клієнту
        bot.send_message(
            user_id, 
            f"📨 *Від менеджера:*\n\n{message.text}",
            parse_mode='Markdown'
        )
        
        # Зберігаємо в історію
        chat_manager.add_message(user_id, message.text, from_admin=True)
        
        # Підтвердження адміну
        bot.send_message(admin_id, f"✅ Відповідь надіслана клієнту {user_id}")
        
        # Виходимо з режиму відповіді
        del admin_reply_mode[admin_id]
        
    except Exception as e:
        bot.send_message(admin_id, f"❌ Помилка: {e}")

@bot.message_handler(func=lambda m: m.text == "📊 Статистика")
def show_stats(message):
    if not is_admin(message.from_user.id):
        return
    
    active_chats = chat_manager.get_active_chats()
    total_chats = len(chat_manager.chats)
    
    text = f"📊 *Статистика:*\n\n"
    text += f"• Активних чатів: {len(active_chats)}\n"
    text += f"• Всього клієнтів: {total_chats}\n"
    text += f"• Адмінів онлайн: {len(ADMIN_IDS)}\n"
    
    bot.send_message(message.chat.id, text, parse_mode='Markdown')

@bot.message_handler(func=lambda m: m.text == "🔙 Головне меню")
def back_to_main(message):
    bot.send_message(message.chat.id, "Головне меню:", reply_markup=main_menu())

# Допоміжна функція
def notify_admins_about_order(user, order_text):
    """Сповістити адмінів про нове замовлення"""
    for admin_id in ADMIN_IDS:
        try:
            text = f"🆕 *Нове замовлення!*\n\n"
            text += f"👤 {user.first_name}\n"
            text += f"📱 @{user.username if user.username else 'немає'}\n"
            text += f"🆔 `{user.id}`\n\n"
            text += f"💬 {order_text[:100]}..."
            
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton(
                "💬 Відповісти", 
                callback_data=f"reply_{user.id}"
            ))
            
            bot.send_message(admin_id, text, parse_mode='Markdown', reply_markup=markup)
        except:
            pass

# ==================== ВЕБХУК ====================
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

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))

    app.run(host='0.0.0.0', port=port)








