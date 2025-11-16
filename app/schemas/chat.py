from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, List

# === ChatMessage Schemas ===
class ChatMessageBase(BaseModel):
    role: str  # user, assistant, system
    content: str
    message_type: str = "text"  # text, mcp, file, long_text

class ChatMessageCreate(ChatMessageBase):
    pass

class ChatMessageResponse(ChatMessageBase):
    id: int
    chat_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

# === Chat Schemas ===
class ChatBase(BaseModel):
    title: Optional[str] = None
    model: str = "meituan/longcat-flash-chat:free"
    system_prompt: Optional[str] = None

class ChatCreate(ChatBase):
    pass

class ChatUpdate(BaseModel):
    title: Optional[str] = None
    system_prompt: Optional[str] = None

class ChatResponse(ChatBase):
    id: int
    external_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    messages: List[ChatMessageResponse] = []

    model_config = ConfigDict(from_attributes=True)

# === Запрос на отправку сообщения ===
class SendMessageRequest(BaseModel):
    content: str
    chat_id: Optional[int] = None  # Если None, создается новый чат
    model: Optional[str] = "meituan/longcat-flash-chat:free"
    system_prompt: Optional[str] = None

class SendMessageResponse(BaseModel):
    chat_id: int
    user_message: ChatMessageResponse
    assistant_message: Optional[ChatMessageResponse] = None
    assistant_messages: List[ChatMessageResponse] = []  # Все распарсенные сообщения

