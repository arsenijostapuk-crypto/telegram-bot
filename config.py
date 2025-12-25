
ADMIN_IDS = [5587016153, 6165680123]  
ADMIN_USERNAMES = ["Arsen"]  # Необов'язково

def is_admin(user_id):
    """Перевіряє, чи є користувач адміністратором"""
    return user_id in ADMIN_IDS


