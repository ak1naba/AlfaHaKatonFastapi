from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class Chat(Base):
    """Чат с OpenRouter"""
    __tablename__ = "chats"

    id = Column(Integer, primary_key=True, index=True)
    external_id = Column(String(255), nullable=False, index=True)  # ID пользователя из внешней системы
    title = Column(String(500), nullable=True)  # Название чата
    model = Column(String(200), nullable=False)  # Модель OpenRouter
    system_prompt = Column(Text, nullable=True)  # Системный промпт
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Связь
    messages = relationship("ChatMessage", back_populates="chat", cascade="all, delete-orphan")

class ChatMessage(Base):
    """Сообщение в чате"""
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(Integer, ForeignKey("chats.id"), nullable=False, index=True)
    role = Column(String(50), nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)
    message_type = Column(String(50), nullable=False, default="text")  # text, mcp, file, long_text
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Связь
    chat = relationship("Chat", back_populates="messages")


