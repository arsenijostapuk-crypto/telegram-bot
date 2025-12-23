import os
import time
from flask import Flask, request
import telebot
from telebot import types
from telebot.apihelper import ApiTelegramException
from products import get_product_response
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
📦 *💬Написати менеджеру* - створити замовлення
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
3. Для замовлення натисніть 💬Написати менеджеру
4. Напишіть що вас цікавить
5. Очікуйте відповідь від менеджера

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
                                              "Скасувати замовлення ❌"])
def handle_back(message):
    text = message.text
    chat_id = message.chat.id
    
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
@bot.message_handler(commands=['admin'])  # <-- ОСЬ ТУТ ПОЧИНАЄТЬСЯ
def admin_panel(message):
    user_id = message.from_user.id
    username = message.from_user.username or "немає"
    
    print(f"🛠️ DEBUG /admin: Користувач {user_id} (@{username})")
    print(f"🛠️ DEBUG /admin: Перевірка is_admin({user_id}) = {is_admin(user_id)}")
    
    if not is_admin(user_id):
        bot.reply_to(message, 
                    f"⛔ *Доступ заборонено*\n\n"
                    f"Ваш ID: `{user_id}`\n"
                    f"Username: @{username}\n"
                    f"ADMIN_IDS: {ADMIN_IDS}\n\n"
                    f"Зв'яжіться з адміністратором для доступу.",
                    parse_mode='Markdown')
        return
    
    # Якщо адмін
    bot.send_message(message.chat.id, 
                    f"👑 *Адмін-панель*\n\n"
                    f"Вітаємо, {message.from_user.first_name}!\n"
                    f"ID: `{user_id}`\n"
                    f"Username: @{username}",
                    parse_mode='Markdown', 
                    reply_markup=admin_main_menu())

# Наступна функція (вже є у вас)
@bot.message_handler(func=lambda m: m.text == "📋 Активні чати")
def show_active_chats(message):
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
    
    # Створюємо клавіатуру з кнопкою скасування
    cancel_markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    cancel_markup.add(types.KeyboardButton("/cancel"))
    
    bot.send_message(
        admin_id, 
        f"✏️ *Відповідь клієнту {user_id}*\n\nНапишіть ваше повідомлення:\n(або /cancel для скасування)",
        parse_mode='Markdown',
        reply_markup=cancel_markup
    )
    bot.answer_callback_query(call.id)
# Обробник для скасування режиму відповіді адміна
@bot.message_handler(commands=['cancel'])
def cancel_reply_mode(message):
    if message.from_user.id in admin_reply_mode:
        user_id = admin_reply_mode[message.from_user.id]
        del admin_reply_mode[message.from_user.id]
        # Прибираємо спеціальну клавіатуру
        remove_markup = types.ReplyKeyboardRemove()
        bot.send_message(
            message.chat.id, 
            f"❌ Режим відповіді клієнту {user_id} скасовано.",
            reply_markup=remove_markup
        )
    else:
        bot.send_message(message.chat.id, "ℹ️ Ви не в режимі відповіді.")

# Обробка повідомлень адміна для клієнтів
@bot.message_handler(func=lambda m: m.from_user.id in admin_reply_mode)
def send_reply_to_client(message):
    admin_id = message.from_user.id
    user_id = admin_reply_mode.get(admin_id)
    
    if not user_id or message.text.startswith('/'):
        return
    
    # Якщо адмін відправляє команду /cancel - скасувати режим
    if message.text.strip() == '/cancel':
        if admin_id in admin_reply_mode:
            del admin_reply_mode[admin_id]
            remove_markup = types.ReplyKeyboardRemove()
            bot.send_message(admin_id, "❌ Режим відповіді скасовано.", reply_markup=remove_markup)
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
        
        # Прибираємо спеціальну клавіатуру
        remove_markup = types.ReplyKeyboardRemove()
        bot.send_message(admin_id, "✅ Режим відповіді завершено.", reply_markup=remove_markup)
        
        # Виходимо з режиму відповіді
        if admin_id in admin_reply_mode:
            del admin_reply_mode[admin_id]
        
    except ApiTelegramException as e:
        error_msg = str(e).lower()
        if "bot was blocked" in error_msg or "chat not found" in error_msg:
            bot.send_message(admin_id, f"❌ Не вдалося надіслати. Клієнт заблокував бота або чат недоступний.")
            # Позначаємо чат як недоступний
            chat = chat_manager.chats.get(str(user_id))
            if chat:
                chat['status'] = 'blocked'
                chat_manager.save_chats()
        else:
            bot.send_message(admin_id, f"❌ Помилка: {e}")
        # Не видаляємо admin_reply_mode, щоб адмін міг спробувати ще раз
    except Exception as e:
        bot.send_message(admin_id, f"❌ Невідома помилка: {e}")
# ОБРОБНИК ДЛЯ КНОПКИ "ЗАВЕРШИТИ" - ЦЕ ГОЛОВНЕ ЩО ПОТРІБНО!
@bot.callback_query_handler(func=lambda call: call.data.startswith('close_'))
def close_chat(call):
    admin_id = call.from_user.id
    user_id = call.data.split('_')[1]
    
    chat = chat_manager.chats.get(user_id)
    if not chat:
        bot.answer_callback_query(call.id, "Чат не знайдено")
        return
    
    # Змінюємо статус чату на "завершений"
    chat['status'] = 'closed'
    chat['unread'] = False
    chat_manager.save_chats()
    
    # Повідомлення адміну
    bot.send_message(admin_id, f"✅ Чат з {chat['user_name']} (ID: {user_id}) завершено.")
    
    # Оновлюємо повідомлення з кнопками (прибираємо їх)
    try:
        bot.edit_message_text(
            chat_id=admin_id,
            message_id=call.message.message_id,
            text=f"✅ *Чат завершено*\n\nКлієнт: {chat['user_name']}\nID: `{user_id}`",
            parse_mode='Markdown'
        )
    except:
        pass
    
    bot.answer_callback_query(call.id, "Чат завершено")

# Обробник для скасування режиму відповіді
# ==================== РОЗСИЛКА ВСІМ КОРИСТУВАЧАМ ====================
@bot.message_handler(func=lambda m: m.text == "📢 Розсилка" and is_admin(m.from_user.id))
def broadcast_menu(message):
    # Отримуємо загальну кількість користувачів
    all_users = chat_manager.get_all_users()
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        types.KeyboardButton(f"✅ Розіслати ({len(all_users)} клієнтів)"),
        types.KeyboardButton("🔙 Назад в адмін-панель")
    )
    bot.send_message(message.chat.id, 
                    f"📢 *Меню розсилки*\n\n"
                    f"Зареєстровано користувачів: *{len(all_users)}*\n\n"
                    f"Натисніть кнопку нижче, щоб відправити повідомлення всім, хто коли-небудь натискав /start:",
                    parse_mode='Markdown',
                    reply_markup=markup)

@bot.message_handler(func=lambda m: m.text.startswith("✅ Розіслати") and is_admin(m.from_user.id))
def start_broadcast(message):
    chat_id = message.chat.id
    
    bot.send_message(chat_id, 
                    "📝 *Створення розсилки*\n\n"
                    "Будь ласка, напишіть повідомлення для розсилки.\n"
                    "Можна використовувати Markdown форматтування.\n\n"
                    "*Приклад:*\n"
                    "🆕 НОВИНКА! З'явився Chaser 15 ml!\n"
                    "🎯 Нова лінійка рідин для pod-систем\n"
                    "💰 Ціна: 250 грн",
                    parse_mode='Markdown',
                    reply_markup=types.ForceReply(selective=True))
    
    bot.register_next_step_handler(message, confirm_broadcast)

def confirm_broadcast(message):
    admin_id = message.from_user.id
    broadcast_text = message.text
    
    if len(broadcast_text.strip()) < 5:
        bot.send_message(admin_id, "❌ Текст занадто короткий. Спробуйте ще раз.")
        return
    
    all_users = chat_manager.get_all_users()
    total_users = len(all_users)
    
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("🚀 Розіслати зараз", callback_data=f"broadcast_now_{hash(broadcast_text) % 10000}"),
        types.InlineKeyboardButton("✏️ Редагувати текст", callback_data="edit_broadcast"),
        types.InlineKeyboardButton("❌ Скасувати", callback_data="cancel_broadcast")
    )
    
    # Зберігаємо текст для подальшого використання
    bot.send_message(admin_id,
                    f"📢 *Попередній перегляд розсилки*\n\n"
                    f"👥 Отримувачі: *{total_users}* користувачів\n\n"
                    f"*Ваше повідомлення:*\n"
                    f"```\n{broadcast_text[:400]}\n```\n\n"
                    f"Відправити розсилку?",
                    parse_mode='Markdown',
                    reply_markup=markup)
    
    # Зберігаємо текст в тимчасовому словнику
    if not hasattr(bot, 'broadcast_texts'):
        bot.broadcast_texts = {}
    bot.broadcast_texts[admin_id] = broadcast_text

@bot.callback_query_handler(func=lambda call: call.data.startswith('broadcast_now_'))
def execute_broadcast(call):
    admin_id = call.from_user.id
    
    # Отримуємо збережений текст
    if not hasattr(bot, 'broadcast_texts') or admin_id not in bot.broadcast_texts:
        bot.answer_callback_query(call.id, "❌ Текст не знайдено. Почніть знову.")
        return
    
    broadcast_text = bot.broadcast_texts[admin_id]
    all_users = chat_manager.get_all_users()
    total_users = len(all_users)
    
    # Статистика
    successful = 0
    failed = 0
    blocked = 0
    
    # Повідомлення про початок
    status_msg = bot.send_message(admin_id,
                                 f"📤 *Початок розсилки...*\n\n"
                                 f"Кількість отримувачів: {total_users}\n"
                                 f"Статус: 0/{total_users}\n"
                                 f"⏳ Почекайте, це може зайняти деякий час...",
                                 parse_mode='Markdown')
    
    # Відправляємо повідомлення всім користувачам
    for i, (user_id, user_data) in enumerate(all_users.items(), 1):
        try:
            # Форматуємо повідомлення
            final_message = f"📢 *ПОВІДОМЛЕННЯ ВІД МАГАЗИНУ:*\n\n{broadcast_text}\n\n"
            final_message += f"_Якщо ви більше не бажаєте отримувати повідомлення, напишіть /stop_"
            
            bot.send_message(int(user_id), final_message, parse_mode='Markdown')
            successful += 1
            
            # Оновлюємо статус кожні 5 повідомлень
            if i % 5 == 0 or i == total_users:
                try:
                    bot.edit_message_text(
                        f"📤 *Розсилка...*\n\n"
                        f"Кількість отримувачів: {total_users}\n"
                        f"✅ Успішно: {successful}\n"
                        f"❌ Не вдалося: {failed}\n"
                        f"🚫 Заблоковано: {blocked}\n"
                        f"📊 Прогрес: {i}/{total_users} ({i/total_users*100:.1f}%)\n\n"
                        f"⏳ Триває...",
                        chat_id=admin_id,
                        message_id=status_msg.message_id,
                        parse_mode='Markdown'
                    )
                except:
                    pass
            time.sleep(0.05)
            
        except ApiTelegramException as e:
            error_msg = str(e).lower()
            if "bot was blocked" in error_msg or "user is deactivated" in error_msg:
                blocked += 1
                # Оновлюємо статус у базі
                chat_manager.chats[user_id]["status"] = "blocked"
            else:
                failed += 1
        except Exception as e:
            failed += 1
    
    # Зберігаємо зміни
    chat_manager.save_chats()
    
    # Видаляємо тимчасовий текст
    if hasattr(bot, 'broadcast_texts'):
        bot.broadcast_texts.pop(admin_id, None)
    
    # Фінальний звіт
    report = f"✅ *РОЗСИЛКА ЗАВЕРШЕНА!*\n\n"
    report += f"📊 *Результати:*\n"
    report += f"• 👥 Загальна кількість: {total_users}\n"
    report += f"• ✅ Успішно доставлено: {successful}\n"
    report += f"• ❌ Не вдалося відправити: {failed}\n"
    report += f"• 🚫 Заблоковані користувачі: {blocked}\n\n"
    
    if successful > 0:
        report += f"📈 *Ефективність:* {successful/total_users*100:.1f}%\n"
    
    report += f"💬 *Текст розсилки був доданий в історію чатів.*"
    
    # Додаємо повідомлення в історію чатів
    for user_id in all_users.keys():
        if chat_manager.chats.get(user_id):
            chat_manager.add_message(int(user_id), 
                                   f"📢 РОЗСИЛКА: {broadcast_text[:100]}...", 
                                   from_admin=True)
    
    bot.send_message(admin_id, report, parse_mode='Markdown', reply_markup=admin_main_menu())
    bot.answer_callback_query(call.id, "✅ Розсилка завершена!")

@bot.callback_query_handler(func=lambda call: call.data == "edit_broadcast")
def edit_broadcast_text(call):
    admin_id = call.from_user.id
    bot.send_message(admin_id, 
                    "✏️ *Редагування тексту*\n\n"
                    "Будь ласка, надішліть новий текст для розсилки:",
                    parse_mode='Markdown',
                    reply_markup=types.ForceReply(selective=True))
    
    bot.register_next_step_handler_by_chat_id(admin_id, confirm_broadcast)
    bot.answer_callback_query(call.id, "Напишіть новий текст")

@bot.callback_query_handler(func=lambda call: call.data == "cancel_broadcast")
def cancel_broadcast(call):
    admin_id = call.from_user.id
    
    # Видаляємо тимчасовий текст
    if hasattr(bot, 'broadcast_texts'):
        bot.broadcast_texts.pop(admin_id, None)
    
    bot.send_message(admin_id, "❌ Розсилка скасована.", reply_markup=admin_main_menu())
    bot.answer_callback_query(call.id, "Розсилка скасована")

# Обробник команди /stop для користувачів
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

# ШВИДКА КОМАНДА ДЛЯ РОЗСИЛКИ
@bot.message_handler(commands=['broadcast'])
def quick_broadcast_command(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "⛔ Доступ заборонено")
        return
    
    # Показуємо статистику
    all_users = chat_manager.get_all_users()
    
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("📝 Створити розсилку", callback_data="create_broadcast"),
        types.InlineKeyboardButton("📊 Статистика користувачів", callback_data="user_stats")
    )
    
    bot.send_message(message.chat.id,
                    f"📢 *Швидка розсилка*\n\n"
                    f"Зареєстровано користувачів: *{len(all_users)}*\n"
                    f"Активних чатів: *{len(chat_manager.get_active_chats())}*\n\n"
                    f"Оберіть дію:",
                    parse_mode='Markdown',
                    reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "create_broadcast")
def create_broadcast_from_button(call):
    admin_id = call.from_user.id
    bot.send_message(admin_id, 
                    "📝 *Створення розсилки*\n\n"
                    "Напишіть текст для розсилки всім користувачам:",
                    parse_mode='Markdown',
                    reply_markup=types.ForceReply(selective=True))
    
    bot.register_next_step_handler_by_chat_id(admin_id, confirm_broadcast)
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data == "user_stats")
def show_user_stats(call):
    admin_id = call.from_user.id
    all_users = chat_manager.get_all_users()
    
    # Аналізуємо статуси
    active = 0
    registered = 0
    blocked = 0
    closed = 0
    unsubscribed = 0
    
    for user_data in all_users.values():
        status = user_data.get('status', 'registered')
        if status == 'active':
            active += 1
        elif status == 'registered':
            registered += 1
        elif status == 'blocked':
            blocked += 1
        elif status == 'closed':
            closed += 1
        elif status == 'unsubscribed':
            unsubscribed += 1
    
    # Отримуємо всіх користувачів (включаючи відписаних)
    total_all = len(chat_manager.chats)
    
    stats_text = f"📊 *Статистика користувачів*\n\n"
    stats_text += f"• 👥 Всього зареєстровано: {total_all}\n"
    stats_text += f"• ✅ Для розсилки доступно: {len(all_users)}\n"
    stats_text += f"• 💬 Активні чати: {active}\n"
    stats_text += f"• 📝 Зареєстровані: {registered}\n"
    stats_text += f"• ✅ Завершені чати: {closed}\n"
    stats_text += f"• 🚫 Заблоковані: {blocked}\n"
    stats_text += f"• 🔕 Відписались: {unsubscribed}\n\n"
    
    if total_all > 0:
        coverage = len(all_users)/total_all*100
        stats_text += f"📈 *Охоплення розсилки:* {coverage:.1f}%\n"
    
    bot.send_message(admin_id, stats_text, parse_mode='Markdown')
    bot.answer_callback_query(call.id)
# ==================== ВЕБХУК ====================
@app.route('/')
def index():
    return "🤖 Бот працює!"

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
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return ''
    return 'ERROR', 400

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    print(f"🚀 Запускаю бота на порті {port}")
    app.run(host='0.0.0.0', port=port)









