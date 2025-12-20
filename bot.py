import os
from flask import Flask, request
import telebot
from telebot import types

# Імпорти
from keyboards import (
    main_menu, admin_main_menu, order_menu,
    liquids_menu, pods_menu, info_menu
)
from config import ADMIN_IDS, is_admin
from chat_manager import chat_manager

app = Flask(__name__)

# Налаштування
TOKEN = os.getenv("MY_BOT_TOKEN")
if not TOKEN:
    raise ValueError("❌ Токен не знайдено!")

bot = telebot.TeleBot(TOKEN)

# Для відповідей адміна
admin_reply_mode = {}

# ==================== КЛІЄНТИ ====================
@bot.message_handler(commands=['start'])
def start(message):
    user = message.from_user
    chat_id = message.chat.id
    
    chat = chat_manager.start_chat(user.id, user.first_name, user.username)
    
    welcome_text = """
👋 *Вітаємо в підтримці!*

Оберіть дію:
💬 Написати менеджеру
📦 Зробити замовлення
ℹ️ Інформація
"""
    bot.send_message(chat_id, welcome_text, parse_mode='Markdown', reply_markup=main_menu())
    
    notify_admins(f"🆕 Клієнт {user.first_name} (@{user.username}) запустив бота")

@bot.message_handler(func=lambda m: m.text == "💬 Написати менеджеру")
def write_to_manager(message):
    bot.send_message(message.chat.id, "✍️ *Напишіть ваше повідомлення:*", parse_mode='Markdown')
    bot.register_next_step_handler(message, save_client_message)

def save_client_message(message):
    user = message.from_user
    chat_id = message.chat.id
    
    chat_manager.add_message(user.id, message.text, from_admin=False)
    bot.send_message(chat_id, "✅ Надіслано менеджеру!", reply_markup=main_menu())
    
    # Сповістити адмінів
    for admin_id in ADMIN_IDS:
        try:
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton(
                "💬 Відповісти", 
                callback_data=f"reply_{user.id}"
            ))
            
            text = f"👤 *Нове повідомлення від {user.first_name}*\n"
            text += f"🆔: `{user.id}`\n\n"
            text += f"💬 {message.text}"
            
            bot.send_message(admin_id, text, parse_mode='Markdown', reply_markup=markup)
        except:
            pass

@bot.message_handler(func=lambda m: m.text == "📦 Зробити замовлення")
def make_order(message):
    bot.send_message(message.chat.id, "Оберіть категорію:", reply_markup=order_menu())

@bot.message_handler(func=lambda m: m.text == "ℹ️ Інформація")
def show_info(message):
    bot.send_message(message.chat.id, "Оберіть розділ:", reply_markup=info_menu())

@bot.message_handler(func=lambda m: m.text in ["💧 Рідини", "🔋 Поди", "🎯 Картриджі"])
def handle_categories(message):
    text = message.text
    chat_id = message.chat.id
    
    if text == "💧 Рідини":
        bot.send_message(chat_id, "Оберіть рідину:", reply_markup=liquids_menu())
    elif text == "🔋 Поди":
        bot.send_message(chat_id, "Оберіть под:", reply_markup=pods_menu())
    elif text == "🎯 Картриджі":
        bot.send_message(chat_id, "🎯 *Картриджі:*\n\n• Xlim\n• Vaporesso\n• Інші", parse_mode='Markdown')

@bot.message_handler(func=lambda m: m.text in ["Chaser 10 ml", "Chaser 30 ml"])
def handle_liquids(message):
    response = f"""
🏷️ *{message.text}*
💰 250 грн
📦 ✅ В наявності
⭐ 4.8/5
💬 Напишіть менеджеру для замовлення
"""
    bot.send_message(message.chat.id, response, parse_mode='Markdown')

@bot.message_handler(func=lambda m: m.text in ["Xlim", "Vaporesso"])
def handle_pods(message):
    response = f"""
🔋 *{message.text}*
💰 від 1200 грн
📦 ✅ В наявності
⭐ 4.9/5
💬 Напишіть менеджеру для замовлення
"""
    bot.send_message(message.chat.id, response, parse_mode='Markdown')

@bot.message_handler(func=lambda m: m.text in ["🚚 Доставка", "💳 Оплата", "🛡️ Гарантія"])
def handle_info(message):
    text = message.text
    chat_id = message.chat.id
    
    if text == "🚚 Доставка":
        response = "🚚 *Доставка:*\n• Нова пошта (1-3 дні)\n• Укрпошта (2-5 днів)\n• Самовивіз (Київ)\n• Від 50 грн"
    elif text == "💳 Оплата":
        response = "💳 *Оплата:*\n• Карта\n• При отриманні\n• Google/Apple Pay"
    else:
        response = "🛡️ *Гарантія:*\n• 14 днів\n• Оригінальна упаковка\n• Обмін/повернення"
    
    bot.send_message(chat_id, response, parse_mode='Markdown')

@bot.message_handler(func=lambda m: m.text == "⬅️ Назад")
def go_back(message):
    bot.send_message(message.chat.id, "Головне меню:", reply_markup=main_menu())

# ==================== АДМІНИ ====================
@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if not is_admin(message.from_user.id):
        return
    
    bot.send_message(message.chat.id, "👑 *Адмін-панель*", 
                    parse_mode='Markdown', reply_markup=admin_main_menu())

@bot.message_handler(func=lambda m: m.text == "📋 Активні чати")
def show_chats(message):
    if not is_admin(message.from_user.id):
        return
    
    active_chats = chat_manager.get_active_chats()
    
    if not active_chats:
        bot.send_message(message.chat.id, "📭 Немає активних чатів")
        return
    
    text = "📋 *Активні чати:*\n\n"
    for user_id, chat in active_chats.items():
        text += f"👤 {chat['user_name']} (@{chat['username']})\n"
        text += f"🆔: `{user_id}`\n"
        text += f"💬 Повідомлень: {len(chat['messages'])}\n"
        text += "⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n"
    
    markup = types.InlineKeyboardMarkup()
    for user_id in active_chats.keys():
        markup.add(types.InlineKeyboardButton(
            f"💬 Чат {user_id[:6]}...", 
            callback_data=f"open_{user_id}"
        ))
    
    bot.send_message(message.chat.id, text, parse_mode='Markdown', reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('open_'))
def open_chat(call):
    admin_id = call.from_user.id
    user_id = call.data.split('_')[1]
    
    chat = chat_manager.chats.get(user_id)
    if not chat:
        bot.answer_callback_query(call.id, "Чат не знайдено")
        return
    
    history = f"💬 *Чат з {chat['user_name']}*\n"
    history += f"👤 @{chat['username']}\n"
    history += f"🆔 `{user_id}`\n\n"
    
    for msg in chat['messages'][-5:]:
        sender = "👨‍💼 Ви" if msg['from_admin'] else "👤 Клієнт"
        history += f"{sender}: {msg['text']}\n"
        history += f"⏰ {msg['time'][11:16]}\n\n"
    
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("✏️ Відповісти", callback_data=f"reply_{user_id}"),
        types.InlineKeyboardButton("❌ Закрити", callback_data=f"close_{user_id}")
    )
    
    bot.send_message(admin_id, history, parse_mode='Markdown', reply_markup=markup)
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data.startswith('reply_'))
def start_reply(call):
    admin_id = call.from_user.id
    user_id = call.data.split('_')[1]
    
    admin_reply_mode[admin_id] = user_id
    
    bot.send_message(admin_id, f"✏️ *Відповідь клієнту {user_id}*\n\nНапишіть повідомлення:")
    bot.answer_callback_query(call.id)

# Обробка повідомлень адміна
@bot.message_handler(func=lambda m: m.from_user.id in admin_reply_mode)
def send_reply_to_client(message):
    admin_id = message.from_user.id
    user_id = admin_reply_mode.get(admin_id)
    
    if not user_id:
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
        bot.send_message(admin_id, "✅ Надіслано клієнту")
        
        # Виходимо з режиму відповіді
        del admin_reply_mode[admin_id]
        
    except Exception as e:
        bot.send_message(admin_id, f"❌ Помилка: {e}")

# Допоміжні функції
def notify_admins(text):
    for admin_id in ADMIN_IDS:
        try:
            bot.send_message(admin_id, text, parse_mode='Markdown')
        except:
            pass

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

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)