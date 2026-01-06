import time
import logging
from telebot import types
from config import is_admin

logger = logging.getLogger(__name__)

# Глобальна змінна для chat_manager
chat_manager = None

def set_chat_manager(cm):
    """Функція для встановлення chat_manager ззовні"""
    global chat_manager
    chat_manager = cm

class AdminPanel:
    def __init__(self, bot):
        self.bot = bot
        self.admin_reply_mode = {}  # maps admin_id (int) -> user_id (int or str)
        self._handlers_registered = False

    def setup_handlers(self):
        """Реєстрація всіх адмін-обробників (ігнорується, якщо вже зареєстровано)"""
        if self._handlers_registered:
            logger.debug("Admin handlers already registered, skipping re-registration.")
            return
        self._handlers_registered = True

        # ==================== АДМІН КОМАНДА ====================
        @self.bot.message_handler(commands=['admin'])
        def admin_panel(message):
            user_id = message.from_user.id
            username = message.from_user.username or "немає"

            print(f"\n🔴🔴🔴 /admin від {user_id} (@{username})")

            if not is_admin(user_id):
                self.bot.reply_to(
                    message,
                    f"⛔ *Доступ заборонено*\n\n"
                    f"Ваш ID: `{user_id}`\n"
                    f"Username: @{username}",
                    parse_mode='Markdown'
                )
                return

            # Якщо адмін
            from keyboards import admin_main_menu
            self.bot.send_message(
                message.chat.id,
                f"👑 *Адмін-панель*\n\n"
                f"Вітаємо, {message.from_user.first_name}!",
                parse_mode='Markdown',
                reply_markup=admin_main_menu()
            )

        # ==================== АДМІН МЕНЮ ====================
        @self.bot.message_handler(func=lambda m: m.text == "📋 Активні чати")
        def show_active_chats(message):
            if not is_admin(message.from_user.id):
                return

            # Тепер chat_manager доступний як глобальна змінна
            unread_chats = chat_manager.get_unread_chats()

            if not unread_chats:
                self.bot.send_message(message.chat.id, "✅ Немає нових повідомлень")
                return

            text = "🆕 *Непрочитані повідомлення:*\n\n"
            for user_id, chat in unread_chats.items():
                text += f"👤 {chat.get('user_name', '—')}\n"
                text += f"🆔: `{user_id}`\n"
                if chat.get('messages'):
                    last_msg = chat['messages'][-1].get('text', '')[:50]
                    text += f"💬 {last_msg}...\n"
                text += "⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n"

            markup = types.InlineKeyboardMarkup()
            for user_id in unread_chats.keys():
                short_id = str(user_id)[:6]
                # callback_data повинна бути рядком
                markup.add(types.InlineKeyboardButton(
                    f"📨 Відповісти {short_id}...",
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
                text += f"👤 {chat.get('user_name', '—')}\n"
                text += f"🆔: `{user_id}`\n"
                if chat.get('messages'):
                    last_msg = chat['messages'][-1].get('text', '')[:50]
                    text += f"💬 {last_msg}...\n"
                text += "⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n"

            markup = types.InlineKeyboardMarkup()
            for user_id in unread_chats.keys():
                short_id = str(user_id)[:6]
                markup.add(types.InlineKeyboardButton(
                    f"📨 Відповісти {short_id}...",
                    callback_data=f"reply_{user_id}"
                ))

            self.bot.send_message(message.chat.id, text, parse_mode='Markdown', reply_markup=markup)

        @self.bot.message_handler(func=lambda m: m.text == "📊 Статистика" and is_admin(m.from_user.id))
        def show_statistics(message):
            if not is_admin(message.from_user.id):
                return

            stats = chat_manager.get_user_stats()
            text = f"""📊 *Статистика бота*

 👥 Користувачів всього: *{stats.get('total', 0)}*
 💬 Активних чатів: *{stats.get('active', 0)}*
 📝 Зареєстровано: *{stats.get('registered', 0)}*
 ✅ Завершено: *{stats.get('closed', 0)}*
 🚫 Заблоковано: *{stats.get('blocked', 0)}*
 🔕 Відписались: *{stats.get('unsubscribed', 0)}*

📈 *Загальна активність:* {stats.get('active', 0) + stats.get('registered', 0)}/{stats.get('total', 0)}
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
                short_id = str(user_id)[:6]
                markup.add(types.InlineKeyboardButton(
                    f"💬 {chat.get('user_name', '—')} ({short_id})",
                    callback_data=f"reply_{user_id}"
                ))

            self.bot.send_message(message.chat.id, "Оберіть клієнта для відповіді:", reply_markup=markup)

        # ==================== CALLBACK-ОБРОБНИКИ ====================
        @self.bot.callback_query_handler(func=lambda call: call.data and call.data.startswith('reply_'))
        def start_reply(call):
            admin_id = call.from_user.id
            # Дістати id після першого '_'
            data_id = call.data.split('_', 1)[1]
            # Спробуємо привести до int, але якщо не виходить — використовуємо як рядок
            try:
                user_id = int(data_id)
            except Exception:
                user_id = data_id  # рядковий id

            # зберігаємо user_id (int або str) у режимі відповіді
            self.admin_reply_mode[admin_id] = user_id

            # Створюємо клавіатуру з кнопкою скасування
            cancel_markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
            cancel_markup.add(types.KeyboardButton("/cancel"))

            try:
                self.bot.send_message(
                    admin_id,
                    f"✏️ *Відповідь клієнту {user_id}*\n\nНапишіть ваше повідомлення:\n(або /cancel для скасування)",
                    parse_mode='Markdown',
                    reply_markup=cancel_markup
                )
            except Exception as e:
                logger.exception("Failed to send start-reply prompt to admin %s", admin_id)
            finally:
                self.bot.answer_callback_query(call.id)

        @self.bot.callback_query_handler(func=lambda call: call.data and call.data.startswith('close_'))
        def close_chat(call):
            admin_id = call.from_user.id
            data_id = call.data.split('_', 1)[1]
            try:
                user_id = int(data_id)
            except Exception:
                user_id = data_id

            # знайти чат, пробуємо int ключ, а потім рядковий
            chat = chat_manager.chats.get(user_id) if hasattr(chat_manager, 'chats') else None
            if not chat and hasattr(chat_manager, 'chats'):
                chat = chat_manager.chats.get(str(user_id))

            if not chat:
                self.bot.answer_callback_query(call.id, "Чат не знайдено")
                return

            # Змінюємо статус чату на "завершений"
            chat['status'] = 'closed'
            chat['unread'] = False
            try:
                chat_manager.save_chats()
            except Exception:
                logger.exception("Failed to save chats after closing chat %s", user_id)

            # Повідомлення адміну
            self.bot.send_message(admin_id, f"✅ Чат з {chat.get('user_name', user_id)} (ID: {user_id}) завершено.")

            # Оновлюємо повідомлення з кнопками (ігноруємо помилки)
            try:
                self.bot.edit_message_text(
                    chat_id=admin_id,
                    message_id=call.message.message_id,
                    text=f"✅ *Чат завершено*\n\nКлієнт: {chat.get('user_name', user_id)}\nID: `{user_id}`",
                    parse_mode='Markdown'
                )
            except Exception:
                logger.debug("Could not edit callback message for admin %s", admin_id)

            self.bot.answer_callback_query(call.id, "Чат завершено")

        # ==================== ОБРОБКА ВІДПОВІДЕЙ АДМІНА ====================
        @self.bot.message_handler(commands=['cancel'])
        def cancel_reply_mode(message):
            admin_id = message.from_user.id
            if admin_id in self.admin_reply_mode:
                user_id = self.admin_reply_mode[admin_id]
                del self.admin_reply_mode[admin_id]
                remove_markup = types.ReplyKeyboardRemove()
                self.bot.send_message(
                    message.chat.id,
                    f"❌ Режим відповіді клієнту {user_id} скасовано.",
                    reply_markup=remove_markup
                )
            else:
                self.bot.send_message(message.chat.id, "ℹ️ Ви не в режимі відповіді.")

        @self.bot.message_handler(func=lambda m: m.from_user and m.from_user.id in self.admin_reply_mode)
        def send_reply_to_client(message):
            admin_id = message.from_user.id
            user_id = self.admin_reply_mode.get(admin_id)

            # Без user_id нічого не робимо
            if not user_id:
                return

            # Безпечна обробка тексту (message.text може бути None)
            text = message.text or ""

            # Якщо адмін відправляє команду /cancel
            if text.strip() == '/cancel':
                if admin_id in self.admin_reply_mode:
                    del self.admin_reply_mode[admin_id]
                    remove_markup = types.ReplyKeyboardRemove()
                    self.bot.send_message(admin_id, "❌ Режим відповіді скасовано.", reply_markup=remove_markup)
                return

            # Якщо це команда (інша, ніж /cancel) або пусте повідомлення — ігноруємо
            if not text or text.startswith('/'):
                return

            try:
                # переконатись, що user_id має правильний тип при відправці (telebot приймає int або str)
                # Відправляємо клієнту
                self.bot.send_message(
                    user_id,
                    f"📨 *Від менеджера:*\n\n{text}",
                    parse_mode='Markdown'
                )

                # Зберігаємо в історію (chat_manager очікує тип ключа, тому передаємо як було збережено)
                try:
                    chat_manager.add_message(user_id, text, from_admin=True)
                except Exception:
                    # Спроба з іншим типом ключа (рядок)
                    try:
                        chat_manager.add_message(str(user_id), text, from_admin=True)
                    except Exception:
                        logger.exception("Failed to add message to chat_manager for user %s", user_id)

                # Підтвердження адміну
                self.bot.send_message(admin_id, f"✅ Відповідь надіслана клієнту {user_id}")

                # Прибираємо спеціальну клавіатуру
                remove_markup = types.ReplyKeyboardRemove()
                self.bot.send_message(admin_id, "✅ Режим відповіді завершено.", reply_markup=remove_markup)

                # Виходимо з режиму відповіді
                if admin_id in self.admin_reply_mode:
                    del self.admin_reply_mode[admin_id]

            except Exception as e:
                logger.exception("Error while admin %s trying to send message to user %s", admin_id, user_id)
                # Детальний текст помилки адміну (можливо приховати для продуктивного середовища)
                self.bot.send_message(admin_id, f"❌ Помилка при відправці: {e}")
