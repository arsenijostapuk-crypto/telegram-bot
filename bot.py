import os
from flask import Flask, request
import telebot
from telebot import types
from products import get_product_response
from keyboards import (
    main_menu, assortment_menu, liquids_menu, pods_menu,
    cartridges_menu, delivery_menu, order_menu, info_menu
)
from config import ADMIN_IDS, is_admin
from chat_manager import chat_manager
from admin_panel import AdminPanel

ADMIN_GROUP_ID = -1003654920245

app = Flask(__name__)

# Налаштування
TOKEN = os.getenv("MY_BOT_TOKEN")
if not TOKEN:
    raise ValueError("❌ Токен не знайдено!")

bot = telebot.TeleBot(TOKEN)

# Ініціалізуємо адмін-панель (ВАЖЛИВО: це має бути ПЕРЕД реєстрацією інших обробників)
admin_panel = AdminPanel(bot)
admin_panel.setup_handlers()

# Тексти повідомлень
WELCOME_TEXT = """
👋 *Вітаємо в нашому боті!*
...
"""

# Решта клієнтських обробників залишається як було...
# ... (ваш поточний клієнтський код)
