from telebot import types

# ==================== ГОЛОВНЕ МЕНЮ ====================
def main_menu():
    """Головне меню з 4 основними кнопками"""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    buttons = ["🛍️ Асортимент", "🚚 Доставка", "📦 Замовлення", "ℹ️ Детальніше"]
    for btn in buttons:
        markup.add(types.KeyboardButton(btn))
    return markup

# ==================== МЕНЮ АСОРТИМЕНТУ ====================
def assortment_menu():
    """Меню категорій товарів"""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    buttons = ["💧 Рідини", "🔋 Под-системи", "🎯 Картриджі", "Назад ◀️"]
    for btn in buttons:
        markup.add(types.KeyboardButton(btn))
    return markup

# ==================== МЕНЮ РІДИН ====================
def liquids_menu():
    """Меню рідин з усіма варіантами Chaser"""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    liquids = [
        "Chaser 10 ml", "Chaser 30 ml for pods", 
        "Chaser mix 30 ml", "Chaser black 30 ml",
        "Chaser lux 30 ml", "Chaser black 30 ml 50 mg", 
        "Назад ◀️"
    ]
    for liquid in liquids:
        markup.add(types.KeyboardButton(liquid))
    return markup

# ==================== МЕНЮ ПОД-СИСТЕМ ====================
def pods_menu():
    """Меню под-систем"""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    pods = ["Xlim", "Vaporesso", "Інші бренди", "Назад ◀️"]
    for pod in pods:
        markup.add(types.KeyboardButton(pod))
    return markup

# ==================== МЕНЮ КАРТРИДЖІВ ====================
def cartridges_menu():
    """Меню картриджів"""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    cartridges = ["Картриджі Xlim", "Картриджі Vaporesso", "Назад ◀️"]
    for cartridge in cartridges:
        markup.add(types.KeyboardButton(cartridge))
    return markup

# ==================== МЕНЮ ДОСТАВКИ ====================
def delivery_menu():
    """Меню після інформації про доставку"""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("Так, зрозуміло ✅"))
    markup.add(types.KeyboardButton("Назад ◀️"))
    return markup

# ==================== МЕНЮ ЗАМОВЛЕННЯ ====================
def order_menu():
    """Меню під час оформлення замовлення"""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("Скасувати замовлення ❌"))
    return markup

# ==================== ІНФОРМАЦІЙНЕ МЕНЮ ====================
def info_menu():
    """Меню для інформаційного розділу"""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("Як замовити?"))
    markup.add(types.KeyboardButton("Оплата та доставка"))
    markup.add(types.KeyboardButton("Гарантія"))
    markup.add(types.KeyboardButton("Назад ◀️"))
    return markup
