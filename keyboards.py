from telebot import types

def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("💬 Написати менеджеру"))
    markup.add(types.KeyboardButton("📦 Зробити замовлення"))
    markup.add(types.KeyboardButton("ℹ️ Інформація"))
    return markup

def admin_main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        types.KeyboardButton("📋 Активні чати"),
        types.KeyboardButton("🆕 Нові повідомлення"),
        types.KeyboardButton("💬 Відкрити чат"),
        types.KeyboardButton("📊 Статистика"),
        types.KeyboardButton("🔙 Вихід")
    )
    return markup

def order_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        types.KeyboardButton("💧 Рідини"),
        types.KeyboardButton("🔋 Поди"),
        types.KeyboardButton("🎯 Картриджі"),
        types.KeyboardButton("⬅️ Назад")
    )
    return markup

def liquids_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        types.KeyboardButton("Chaser 10 ml"),
        types.KeyboardButton("Chaser 30 ml"),
        types.KeyboardButton("⬅️ Назад")
    )
    return markup

def pods_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        types.KeyboardButton("Xlim"),
        types.KeyboardButton("Vaporesso"),
        types.KeyboardButton("⬅️ Назад")
    )
    return markup

def info_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(
        types.KeyboardButton("🚚 Доставка"),
        types.KeyboardButton("💳 Оплата"),
        types.KeyboardButton("🛡️ Гарантія"),
        types.KeyboardButton("⬅️ Назад")
    )
    return markup