import time
from telebot import types
from chat_manager import chat_manager
from config import is_admin

class AdminPanel:
    def __init__(self, bot):
        self.bot = bot
        self.admin_reply_mode = {}
    
    def setup_handlers(self):
        """Реєстрація всіх адмін-обробників"""
        
        # ==================== АДМІН КОМАНДА ====================
        @self.bot.message_handler(commands=['admin'])
        def admin_panel(message):
            user_id = message.from_user.id
            username = message.from_user.username or "немає"
            
            print(f"\n🔴🔴🔴 /admin від {user_id} (@{username})")
            
            if not is_admin(user_id):
                self.bot.reply_to(message, 
                                f"⛔ *Доступ заборонено*\n\n"
                                f"Ваш ID: `{user_id}`\n"
                                f"Username: @{username}",
                                parse_mode='Markdown')
                return
            
            # Якщо адмін
            from keyboards import admin_main_menu
            self.bot.send_message(message.chat.id, 
                                f"👑 *Адмін-панель*\n\n"
                                f"Вітаємо, {message.from_user.first_name}!",
                                parse_mode='Markdown', 
                                reply_markup=admin_main_menu())
        
        # ==================== АДМІН МЕНЮ ====================
        @self.bot.message_handler(func=lambda m: m.text == "📋 Активні чати")
        def show_active_chats(message):
            if not is_admin(message.from_user.id):
                return
            
            unread_chats = chat_manager.get_unread_chats()
            
            if not unread_chats:
                self.bot.send_message(message.chat.id, "✅ Немає нових повідомлень")
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
            
            self.bot.send_message(message.chat.id, text, parse_mode='Markdown', reply_markup=markup)
        
        @self.bot.message_handler(func=lambda m: m.text == "🆕 Нові повідомлення" and is_admin(m.from_user.id))
        def show_new_messages(message):
            if not is_admin(message.from_user.id):
                return
            
            unread_chats = chat_manager.get_unread_chats()
            
            if not unread_chats:
                self.bot.send_message(message.chat.id, "✅ Немає нових повідомлень")
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
            
            self.bot.send_message(message.chat.id, text, parse_mode='Markdown', reply_markup=markup)
        
        @self.bot.message_handler(func=lambda m: m.text == "📊 Статистика" and is_admin(m.from_user.id))
        def show_statistics(message):
            if not is_admin(message.from_user.id):
                return
            
            stats = chat_manager.get_user_stats()
            text = f"""📊 *Статистика бота*

👥 Користувачів всього: *{stats['total']}*
💬 Активних чатів: *{stats['active']}*
📝 Зареєстровано: *{stats['registered']}*
✅ Завершено: *{stats['closed']}*
🚫 Заблоковано: *{stats['blocked']}*
🔕 Відписались: *{stats['unsubscribed']}*

📈 *Загальна активність:* {stats['active'] + stats['registered']}/{stats['total']}
"""
            
            self.bot.send_message(message.chat.id, text, parse_mode='Markdown')
        
        @self.bot.message_handler(func=lambda m: m.text == "💬 Відповісти клієнту")
        def select_client_to_reply(message):
            if not is_admin(message.from_user.id):
                return
            
            active_chats = chat_manager.get_active_chats()
            
            if not active_chats:
                self.bot.send_message(message.chat.id, "📭 Немає активних чатів")
                return
            
            markup = types.InlineKeyboardMarkup()
            for user_id, chat in active_chats.items():
                markup.add(types.InlineKeyboardButton(
                    f"💬 {chat['user_name']} ({user_id[:6]})", 
                    callback_data=f"reply_{user_id}"
                ))
            
            self.bot.send_message(message.chat.id, "Оберіть клієнта для відповіді:", reply_markup=markup)
        
        # ==================== CALLBACK-ОБРОБНИКИ ====================
        @self.bot.callback_query_handler(func=lambda call: call.data.startswith('reply_'))
        def start_reply(call):
            admin_id = call.from_user.id
            user_id = call.data.split('_')[1]
            
            self.admin_reply_mode[admin_id] = user_id
            
            # Створюємо клавіатуру з кнопкою скасування
            cancel_markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
            cancel_markup.add(types.KeyboardButton("/cancel"))
            
            self.bot.send_message(
                admin_id, 
                f"✏️ *Відповідь клієнту {user_id}*\n\nНапишіть ваше повідомлення:\n(або /cancel для скасування)",
                parse_mode='Markdown',
                reply_markup=cancel_markup
            )
            self.bot.answer_callback_query(call.id)
        
        @self.bot.callback_query_handler(func=lambda call: call.data.startswith('close_'))
        def close_chat(call):
            admin_id = call.from_user.id
            user_id = call.data.split('_')[1]
            
            chat = chat_manager.chats.get(user_id)
            if not chat:
                self.bot.answer_callback_query(call.id, "Чат не знайдено")
                return
            
            # Змінюємо статус чату на "завершений"
            chat['status'] = 'closed'
            chat['unread'] = False
            chat_manager.save_chats()
            
            # Повідомлення адміну
            self.bot.send_message(admin_id, f"✅ Чат з {chat['user_name']} (ID: {user_id}) завершено.")
            
            # Оновлюємо повідомлення з кнопками
            try:
                self.bot.edit_message_text(
                    chat_id=admin_id,
                    message_id=call.message.message_id,
                    text=f"✅ *Чат завершено*\n\nКлієнт: {chat['user_name']}\nID: `{user_id}`",
                    parse_mode='Markdown'
                )
            except:
                pass
            
            self.bot.answer_callback_query(call.id, "Чат завершено")
        
        # ==================== ОБРОБКА ВІДПОВІДЕЙ АДМІНА ====================
        @self.bot.message_handler(commands=['cancel'])
        def cancel_reply_mode(message):
            if message.from_user.id in self.admin_reply_mode:
                user_id = self.admin_reply_mode[message.from_user.id]
                del self.admin_reply_mode[message.from_user.id]
                remove_markup = types.ReplyKeyboardRemove()
                self.bot.send_message(
                    message.chat.id, 
                    f"❌ Режим відповіді клієнту {user_id} скасовано.",
                    reply_markup=remove_markup
                )
            else:
                self.bot.send_message(message.chat.id, "ℹ️ Ви не в режимі відповіді.")
        
        @self.bot.message_handler(func=lambda m: m.from_user.id in self.admin_reply_mode)
        def send_reply_to_client(message):
            admin_id = message.from_user.id
            user_id = self.admin_reply_mode.get(admin_id)
            
            if not user_id or message.text.startswith('/'):
                return
            
            # Якщо адмін відправляє команду /cancel
            if message.text.strip() == '/cancel':
                if admin_id in self.admin_reply_mode:
                    del self.admin_reply_mode[admin_id]
                    remove_markup = types.ReplyKeyboardRemove()
                    self.bot.send_message(admin_id, "❌ Режим відповіді скасовано.", reply_markup=remove_markup)
                return
            
            try:
                # Відправляємо клієнту
                self.bot.send_message(
                    user_id, 
                    f"📨 *Від менеджера:*\n\n{message.text}",
                    parse_mode='Markdown'
                )
                
                # Зберігаємо в історію
                chat_manager.add_message(user_id, message.text, from_admin=True)
                
                # Підтвердження адміну
                self.bot.send_message(admin_id, f"✅ Відповідь надіслана клієнту {user_id}")
                
                # Прибираємо спеціальну клавіатуру
                remove_markup = types.ReplyKeyboardRemove()
                self.bot.send_message(admin_id, "✅ Режим відповіді завершено.", reply_markup=remove_markup)
                
                # Виходимо з режиму відповіді
                if admin_id in self.admin_reply_mode:
                    del self.admin_reply_mode[admin_id]
                
            except Exception as e:
                self.bot.send_message(admin_id, f"❌ Помилка: {e}")