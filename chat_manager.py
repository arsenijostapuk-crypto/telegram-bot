import json
import os
from datetime import datetime

class ChatManager:
    def __init__(self, filename='chats.json'):
        self.filename = filename
        self.chats = self.load_chats()
    
    def load_chats(self):
        if os.path.exists(self.filename):
            with open(self.filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def save_chats(self):
        with open(self.filename, 'w', encoding='utf-8') as f:
            json.dump(self.chats, f, ensure_ascii=False, indent=2)
    
    def get_chat(self, user_id):
        """Отримати чат за user_id"""
        return self.chats.get(str(user_id))
    
    def start_chat(self, user_id, user_name, username):
        user_id_str = str(user_id)
        
        if user_id_str not in self.chats:
            # Новий користувач - статус "registered"
            self.chats[user_id_str] = {
                "user_name": user_name,
                "username": username or "немає",
                "started": str(datetime.now()),
                "last_active": str(datetime.now()),
                "messages": [],
                "status": "registered",  # Статус при першому старті
                "unread": False
            }
            print(f"DEBUG: Створено нового користувача {user_id_str} зі статусом 'registered'")
        else:
            # Оновлюємо існуючого користувача
            self.chats[user_id_str]["last_active"] = str(datetime.now())
            self.chats[user_id_str]["user_name"] = user_name
            self.chats[user_id_str]["username"] = username or "немає"
            
            # Відновлюємо статус, якщо користувач повертається
            current_status = self.chats[user_id_str].get("status")
            if current_status in ["unsubscribed", "closed"]:
                self.chats[user_id_str]["status"] = "registered"
                print(f"DEBUG: Користувач {user_id_str} повернувся, статус змінено на 'registered'")
        
        self.save_chats()
        return self.chats[user_id_str]
    
    def add_message(self, user_id, text, from_admin=False):
        user_id_str = str(user_id)
        
        if user_id_str not in self.chats:
            # Якщо чату немає, створюємо його
            self.start_chat(user_id, "Unknown", "немає")
        
        message = {
            "text": text,
            "from_admin": from_admin,
            "time": str(datetime.now())
        }
        
        self.chats[user_id_str]["messages"].append(message)
        self.chats[user_id_str]["unread"] = not from_admin
        
        # Оновлюємо статус
        if from_admin:
            # Якщо повідомлення від адміна - чат активний
            self.chats[user_id_str]["status"] = "active"
        elif self.chats[user_id_str].get("status") == "registered":
            # Якщо це перше повідомлення від користувача
            self.chats[user_id_str]["status"] = "active"
        
        self.save_chats()
        return True
    
    def update_status(self, user_id, status):
        """Оновити статус чату"""
        user_id_str = str(user_id)
        
        if user_id_str in self.chats:
            self.chats[user_id_str]["status"] = status
            self.save_chats()
            return True
        return False
    
    def get_active_chats(self):
        return {uid: chat for uid, chat in self.chats.items() 
                if chat.get("status") == "active"}
    
    def get_unread_chats(self):
        return {uid: chat for uid, chat in self.chats.items() 
                if chat.get("unread") == True}
    
    def get_all_users(self):
        """Отримати всіх користувачів, які натиснули /start і не відписались"""
        return {uid: chat for uid, chat in self.chats.items() 
                if chat.get("status") not in ["unsubscribed", "blocked"]}
    
    def get_user_stats(self):
        """Отримати статистику по користувачам"""
        stats = {
            'total': len(self.chats),
            'active': 0,
            'registered': 0,
            'blocked': 0,
            'unsubscribed': 0,
            'closed': 0
        }
        
        for chat in self.chats.values():
            status = chat.get('status', 'registered')
            print(f"DEBUG: Статус чату: {status}")
            
            if status == 'active':
                stats['active'] += 1
            elif status == 'registered':
                stats['registered'] += 1
            elif status == 'blocked':
                stats['blocked'] += 1
            elif status == 'unsubscribed':
                stats['unsubscribed'] += 1
            elif status == 'closed':
                stats['closed'] += 1
        
        print(f"DEBUG: Загальна статистика: {stats}")
        return stats
    
    def mark_as_unsubscribed(self, user_id):
        """Позначити користувача як відписаного"""
        return self.update_status(user_id, "unsubscribed")
    
    def mark_as_closed(self, user_id):
        """Позначити чат як завершений"""
        return self.update_status(user_id, "closed")


# Глобальний екземпляр
chat_manager = ChatManager()
