"""
Скрипт для создания таблиц chats и chat_messages
"""
from app.core.database import engine, Base
from app.models.chat import Chat, ChatMessage

def create_tables():
    """Создает таблицы в базе данных"""
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully!")

if __name__ == "__main__":
    create_tables()

