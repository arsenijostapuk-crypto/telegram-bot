from telebot import types

# Головне меню
def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn1 = types.KeyboardButton("Асортимент")
    btn2 = types.KeyboardButton("Рідина")
    btn3 = types.KeyboardButton("Поди")
    btn4 = types.KeyboardButton("Компоненти до пода")
    btn5 = types.KeyboardButton("Картриджі")
    markup.add(btn1, btn2, btn3, btn4, btn5)
    return markup

# Меню асортименту
def assortment_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    # Додайте сюди свої категорії асортименту
    btn1 = types.KeyboardButton("Категорія 1")
    btn2 = types.KeyboardButton("Назад")
    markup.add(btn1, btn2)
    return markup

# Меню рідин
def liquid_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn1 = types.KeyboardButton("Chaser 10 ml")
    btn2 = types.KeyboardButton("Chaser 30 ml for pods")
    btn3 = types.KeyboardButton("Chaser mix 30 ml")
    btn4 = types.KeyboardButton("Chaser black 30 ml")
    btn5 = types.KeyboardButton("Chaser lux 30 ml")
    btn6 = types.KeyboardButton("Chaser black 30 ml 50 mg")
    btn7 = types.KeyboardButton("Назад")
    markup.add(btn1, btn2, btn3, btn4, btn5, btn6, btn7)
    return markup

# Меню подів
def pods_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn1 = types.KeyboardButton("Xlim")
    btn2 = types.KeyboardButton("Vaporesso")
    btn3 = types.KeyboardButton("Назад")
    markup.add(btn1, btn2, btn3)
    return markup

# Меню компонентів
def components_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    # Додайте свої компоненти
    btn1 = types.KeyboardButton("Батарея")
    btn2 = types.KeyboardButton("Назад")
    markup.add(btn1, btn2)
    return markup

# Меню картриджів
def cartridges_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn1 = types.KeyboardButton("Картриджі Xlim")
    btn2 = types.KeyboardButton("Картриджі Vaporesso")
    btn3 = types.KeyboardButton("Назад")
    markup.add(btn1, btn2, btn3)
    return markup