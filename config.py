# Конфігурація
ADMIN_IDS = [5587016153]  # ваш Telegram ID
SUPPORT_CHAT_ID = -1003654920245  # група для спілкування

# Функції перевірки
def is_admin(user_id):
    return user_id in ADMIN_IDS
