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
    
    def start_chat(self, user_id, user_name, username):
        if str(user_id) not in self.chats:
            self.chats[str(user_id)] = {
                "user_name": user_name,
                "username": username or "немає",
                "started": str(datetime.now()),
                "last_active": str(datetime.now()),
                "messages": [],
                "status": "registered",  # Новий статус для зареєстрованих
                "unread": False
            }
        else:
            # Оновлюємо час останньої активності
            self.chats[str(user_id)]["last_active"] = str(datetime.now())
            self.chats[str(user_id)]["user_name"] = user_name
            self.chats[str(user_id)]["username"] = username or "немає"
            # Якщо користувач був відписаний, знову підписуємо
            if self.chats[str(user_id)].get("status") == "unsubscribed":
                self.chats[str(user_id)]["status"] = "registered"
        
        self.save_chats()
        return self.chats[str(user_id)]
    
    def add_message(self, user_id, text, from_admin=False):
        if str(user_id) not in self.chats:
            return False
        
        message = {
            "text": text,
            "from_admin": from_admin,
            "time": str(datetime.now())
        }
        
        self.chats[str(user_id)]["messages"].append(message)
        self.chats[str(user_id)]["unread"] = not from_admin
        self.chats[str(user_id)]["status"] = "active"  # Стає активним при спілкуванні
        self.save_chats()
        return True
    
    def get_active_chats(self):
        return {uid: chat for uid, chat in self.chats.items() 
                if chat.get("status") == "active"}
    
    def get_unread_chats(self):
        return {uid: chat for uid, chat in self.chats.items() 
                if chat.get("unread") == True}
    
    # =============== НОВІ ФУНКЦІЇ ДЛЯ РОЗСИЛКИ ===============
    
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
        
        return stats

# Створюємо глобальний екземпляр
chat_manager = ChatManager()
