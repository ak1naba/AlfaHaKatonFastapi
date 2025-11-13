# app/schemas/message.py
from pydantic import BaseModel, ConfigDict
from typing import Optional, Dict, Any
from datetime import datetime

class MessageBase(BaseModel):
    prompt: str

class MessageCreate(MessageBase):
    gender: Optional[str] = None
    country: Optional[str] = "Russia"

class MessageResponse(BaseModel):
    id: int
    prompt: str
    response: Dict[str, Any]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

# Дополнительная схема для профиля
class PersonProfile(BaseModel):
    first_name: str
    last_name: str
    gender: str
    email: str
    password: str
    bio: str