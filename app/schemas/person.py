from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime, date
from typing import Optional

class PersonBase(BaseModel):
    first_name: str
    last_name: str
    gender: str
    email: EmailStr
    bio: Optional[str] = None
    country: Optional[str] = "Russia"
    date_of_birth: Optional[date] = None

class PersonCreate(PersonBase):
    password: str

class PersonResponse(PersonBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
