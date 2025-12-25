import time
from telebot import types
from telebot.apihelper import ApiTelegramException
from chat_manager import chat_manager
from config import is_admin
from keyboards import admin_main_menu, main_menu  # Важливо: обидві меню

class AdminPanel:
    def __init__(self, bot):
        self.bot = bot
        self.admin_reply_mode = {}
        self.broadcast_texts = {}  # Для розсилки
    
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
            self.bot.send_message(message.chat.id, 
                                f"👑 *Адмін-панель*\n\n"
                                f"Вітаємо, {message.from_user.first_name}!",
                                parse_mode='Markdown', 
                                reply_markup=admin_main_menu())
        
        # ==================== ГОЛОВНЕ МЕНЮ ====================
        @self.bot.message_handler(func=lambda m: m.text == "🔙 Головне меню" and is_admin(m.from_user.id))
        def back_to_main_from_admin(message):
            self.bot.send_message(message.chat.id, "Головне меню:", reply_markup=main_menu())
        
        # ==================== РОЗСИЛКА ====================
        @self.bot.message_handler(func=lambda m: m.text == "📢 Розсилка" and is_admin(m.from_user.id))
        def broadcast_menu(message):
            # Отримуємо загальну кількість користувачів
            all_users = chat_manager.get_all_users()
            
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
            markup.add(
                types.KeyboardButton(f"✅ Розіслати ({len(all_users)} клієнтів)"),
                types.KeyboardButton("🔙 Назад в адмін-панель")
            )
            self.bot.send_message(message.chat.id, 
                                f"📢 *Меню розсилки*\n\n"
                                f"Зареєстровано користувачів: *{len(all_users)}*\n\n"
                                f"Натисніть кнопку нижче, щоб відправити повідомлення всім, хто коли-небудь натискав /start:",
                                parse_mode='Markdown',
                                reply_markup=markup)
        
        @self.bot.message_handler(func=lambda m: m.text.startswith("✅ Розіслати") and is_admin(m.from_user.id))
        def start_broadcast(message):
            chat_id = message.chat.id
            
            self.bot.send_message(chat_id, 
                                "📝 *Створення розсилки*\n\n"
                                "Будь ласка, напишіть повідомлення для розсилки.\n"
                                "Можна використовувати Markdown форматтування.\n\n"
                                "*Приклад:*\n"
                                "🆕 НОВИНКА! З'явився Chaser 15 ml!\n"
                                "🎯 Нова лінійка рідин для pod-систем\n"
                                "💰 Ціна: 250 грн",
                                parse_mode='Markdown',
                                reply_markup=types.ForceReply(selective=True))
            
            self.bot.register_next_step_handler(message, self.confirm_broadcast)
        
        # ==================== CALLBACK ДЛЯ РОЗСИЛКИ ====================
        @self.bot.callback_query_handler(func=lambda call: call.data.startswith('broadcast_now_'))
        def execute_broadcast(call):
            admin_id = call.from_user.id
            
            # Отримуємо збережений текст
            if admin_id not in self.broadcast_texts:
                self.bot.answer_callback_query(call.id, "❌ Текст не знайдено. Почніть знову.")
                return
            
            broadcast_text = self.broadcast_texts[admin_id]
            all_users = chat_manager.get_all_users()
            total_users = len(all_users)
            
            # Статистика
            successful = 0
            failed = 0
            blocked = 0
            
            # Повідомлення про початок
            status_msg = self.bot.send_message(admin_id,
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
                    
                    self.bot.send_message(int(user_id), final_message, parse_mode='Markdown')
                    successful += 1
                    
                    # Оновлюємо статус кожні 5 повідомлень
                    if i % 5 == 0 or i == total_users:
                        try:
                            self.bot.edit_message_text(
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
            self.broadcast_texts.pop(admin_id, None)
            
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
            
            self.bot.send_message(admin_id, report, parse_mode='Markdown', reply_markup=admin_main_menu())
            self.bot.answer_callback_query(call.id, "✅ Розсилка завершена!")
        
        @self.bot.callback_query_handler(func=lambda call: call.data == "edit_broadcast")
        def edit_broadcast_text(call):
            admin_id = call.from_user.id
            self.bot.send_message(admin_id, 
                                "✏️ *Редагування тексту*\n\n"
                                "Будь ласка, надішліть новий текст для розсилки:",
                                parse_mode='Markdown',
                                reply_markup=types.ForceReply(selective=True))
            
            self.bot.register_next_step_handler_by_chat_id(admin_id, self.confirm_broadcast)
            self.bot.answer_callback_query(call.id, "Напишіть новий текст")
        
        @self.bot.callback_query_handler(func=lambda call: call.data == "cancel_broadcast")
        def cancel_broadcast(call):
            admin_id = call.from_user.id
            
            # Видаляємо тимчасовий текст
            self.broadcast_texts.pop(admin_id, None)
            
            self.bot.send_message(admin_id, "❌ Розсилка скасована.", reply_markup=admin_main_menu())
            self.bot.answer_callback_query(call.id, "Розсилка скасована")
        
        # ==================== ШВИДКА КОМАНДА РОЗСИЛКИ ====================
        @self.bot.message_handler(commands=['broadcast'])
        def quick_broadcast_command(message):
            if not is_admin(message.from_user.id):
                self.bot.reply_to(message, "⛔ Доступ заборонено")
                return
            
            # Показуємо статистику
            all_users = chat_manager.get_all_users()
            
            markup = types.InlineKeyboardMarkup()
            markup.add(
                types.InlineKeyboardButton("📝 Створити розсилку", callback_data="create_broadcast"),
                types.InlineKeyboardButton("📊 Статистика користувачів", callback_data="user_stats")
            )
            
            self.bot.send_message(message.chat.id,
                                f"📢 *Швидка розсилка*\n\n"
                                f"Зареєстровано користувачів: *{len(all_users)}*\n"
                                f"Активних чатів: *{len(chat_manager.get_active_chats())}*\n\n"
                                f"Оберіть дію:",
                                parse_mode='Markdown',
                                reply_markup=markup)
        
        @self.bot.callback_query_handler(func=lambda call: call.data == "create_broadcast")
        def create_broadcast_from_button(call):
            admin_id = call.from_user.id
            self.bot.send_message(admin_id, 
                                "📝 *Створення розсилки*\n\n"
                                "Напишіть текст для розсилки всім користувачам:",
                                parse_mode='Markdown',
                                reply_markup=types.ForceReply(selective=True))
            
            self.bot.register_next_step_handler_by_chat_id(admin_id, self.confirm_broadcast)
            self.bot.answer_callback_query(call.id)
        
        # Решта обробників (активні чати, статистика тощо) залишаються як були...
        # ... (додайте решту обробників з попередньої версії)
    
    def confirm_broadcast(self, message):
        """Підтвердження розсилки (окремий метод)"""
        admin_id = message.from_user.id
        broadcast_text = message.text
        
        if len(broadcast_text.strip()) < 5:
            self.bot.send_message(admin_id, "❌ Текст занадто короткий. Спробуйте ще раз.")
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
        self.broadcast_texts[admin_id] = broadcast_text
        
        self.bot.send_message(admin_id,
                            f"📢 *Попередній перегляд розсилки*\n\n"
                            f"👥 Отримувачі: *{total_users}* користувачів\n\n"
                            f"*Ваше повідомлення:*\n"
                            f"```\n{broadcast_text[:400]}\n```\n\n"
                            f"Відправити розсилку?",
                            parse_mode='Markdown',
                            reply_markup=markup)

