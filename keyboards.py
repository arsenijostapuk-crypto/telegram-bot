from telebot import types

# Головне меню
def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        types.KeyboardButton("🛍️ Асортимент"),
        types.KeyboardButton("🚚 Доставка"),
        types.KeyboardButton("📦 Замовлення"),
        types.KeyboardButton("ℹ️ Детальніше")
    )
    return markup

# Меню асортименту
def assortment_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        types.KeyboardButton("💧 Рідини"),
        types.KeyboardButton("🔋 Под-системи"),
        types.KeyboardButton("🎯 Картриджі"),
        types.KeyboardButton("⬅️ Назад")
    )
    return markup

# Меню рідин
def liquids_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        types.KeyboardButton("Chaser 10 ml"),
        types.KeyboardButton("Chaser 30 ml for pods"),
        types.KeyboardButton("Chaser mix 30 ml"),
        types.KeyboardButton("Chaser black 30 ml"),
        types.KeyboardButton("Chaser lux 30 ml"),
        types.KeyboardButton("Chaser black 30 ml 50 mg"),
        types.KeyboardButton("⬅️ Назад")
    )
    return markup

# Меню под-систем
def pods_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        types.KeyboardButton("Xlim"),
        types.KeyboardButton("Vaporesso"),
        types.KeyboardButton("Інші бренди"),
        types.KeyboardButton("⬅️ Назад")
    )
    return markup

# Меню картриджів
def cartridges_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        types.KeyboardButton("Картриджі Xlim"),
        types.KeyboardButton("Картриджі Vaporesso"),
        types.KeyboardButton("⬅️ Назад")
    )
    return markup

# Меню доставки
def delivery_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("✅ Зрозуміло"))
    markup.add(types.KeyboardButton("⬅️ Назад"))
    return markup

# Меню замовлення
def order_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("❌ Скасувати замовлення"))
    return markup

# Інформаційне меню
def info_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(
        types.KeyboardButton("📝 Як замовити?"),
        types.KeyboardButton("💳 Оплата та доставка"),
        types.KeyboardButton("🛡️ Гарантія"),
        types.KeyboardButton("⬅️ Назад")
    )
    return markup
